extends Spatial


# The URL we will connect to
export var websocket_url = "ws://127.0.0.1:9000"

# Our WebSocketClient instance
var _client = WebSocketClient.new()

func _ready():
	# Connect base signals to get notified of connection open, close, and errors.
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	# This signal is emitted when not using the Multiplayer API every time
	# a full packet is received.
	# Alternatively, you could check get_peer(1).get_available_packets() in a loop.
	_client.connect("data_received", self, "_on_data")

	# Initiate connection to the given URL.
	var err = _client.connect_to_url(websocket_url)
	if err != OK:
		print("Unable to connect")
		set_process(false)

func _closed(was_clean = false):
	# was_clean will tell you if the disconnection was correctly notified
	# by the remote peer before closing the socket.
	print("Closed, clean: ", was_clean)
	set_process(false)

func _connected(proto = ""):
	# This is called on connection, "proto" will be the selected WebSocket
	# sub-protocol (which is optional)
	print("Connected with protocol: ", proto)
	# You MUST always use get_peer(1).put_packet to send data to server,
	# and not put_packet directly when not using the MultiplayerAPI.
	send(open_message())

func send(data):
	send_str(to_json(data))
	
func send_str(string):
	_client.get_peer(1).put_packet(string.to_utf8())

func _on_data():
	# Print the received packet, you MUST always use get_peer(1).get_packet
	# to receive data from server, and not get_packet directly when not
	# using the MultiplayerAPI.
	var body = _client.get_peer(1).get_packet().get_string_from_utf8()
	var json = JSON.parse(body)
	run_message(json.result)

func run_message(data):
	var parent = null
	print(data)
	
	if 'type' in data:
		if data['type'] != 'node':
			return run_typed_message(data)
	
	if ('parent' in data):
		if (data['parent'] == 'tree'):
			print('Tree')
			parent = get_tree()
	
	if parent == null:
		parent = get_tree().get_root()

	if 'node' in data:
		print("Node is: ", parent, ' > ', data['node'])
		parent = parent.get_node(data['node'])

	if ('is_func' in data) == false:
		return 
	
	var res = null 
#
#	if not 'path' in data:
#		return 
#
	var nodepath = null
	 
	if data.get('path'):
		nodepath = NodePath(data.get('path'))
		print('nodepath: ', nodepath)
		print('absolute: ', nodepath.is_absolute())
	
	if data['is_func']:
		
		print('Calling: ', data['method'], ' ',' on ', parent)
		if ('method' in data) == false:
				return 
		if nodepath:
			res = parent.call(data['method'], nodepath, data.get('value') or [0])
		else:
			res = parent.call(data['method'], data.get('value') or [0])
	else:
		if 'value' in data:
			parent.set(data['path'], data['value'])
		else:
			nodepath = NodePath(data.get('path'))
			res = parent.get(nodepath)
			print('.get() Result: ', res)
			
	if res != null:
		print('Result', res)	
		send({ 
			'value': res,
			'type': typeof(res),
			'message_id': data.get('message_id')
		})
		
		
func run_typed_message(data):
	if data['type'] == 'subscriptions':
		for item in data['items']:
			_subscribe(item)
			return 
	if data['type'] == 'subscribe':
		_subscribe(data)
		
		
func _subscribe(data):
	var nodepath = NodePath(data.get('path'))
	print('nodepath ', nodepath)
	var node = get_tree().current_scene.get_node_or_null(nodepath)
	var property_path = nodepath.get_as_property_path()
	print('concat names: ', nodepath.get_concatenated_subnames()) # texture:load_path
	print('node ', node, ' == ', property_path, ' == ', nodepath.get_subname_count())
	var propertyList = node.get_property_list()
	print('property count: ', len(propertyList))
	var lstack = node 
	var last_key = null
	
	for index in range(nodepath.get_subname_count()):
		var key = nodepath.get_subname(index)
		
		print('typeof ', typeof(lstack))
		var _method = get_match(lstack)
		lstack = call(_method, lstack, key, index, node, last_key, data)
		last_key = key 
#		for item in propertyList:
#			print(item)
	if lstack != null:
		var _method = get_match(lstack)
		var index = nodepath.get_subname_count() - 1
		var key = nodepath.get_subname(index)
		lstack = call(_method, lstack, key, index, node, key, data)
		subscriptions[node.get_path()] = [node, key, data] # [last_key, key, data]
	print(' A thing ', lstack)

func get_match(lstack):
	var _method = 'no_action_call'
	match typeof(lstack):
		7: # vector3
			_method = 'subscribe_vector3'#(lstack, key, data)
		17: # node
			_method = 'step_node' # (lstack, key, data)
		# _:
			# no_action method
	return _method
		
# warning-ignore:unused_argument
func no_action_call(lstack, key, _index, _node, _last_key, _data):
	print('Key "', key, '" is not a child of the current: ', lstack)

			
func step_node(lstack, key, index, _node, _last_key, _data):
	# node
	if lstack.has_method('get'):
		var prop = lstack.get(key)
			
		if prop:
			print('Found prop: ', key)
			return lstack[key]
		
			
	if lstack.has_method(key):
		print('Found method "', key, '" in', lstack)
		lstack = lstack[key]
	
	return lstack 

var subscriptions = {}

func subscribe_vector3(lstack, key, _index, node, last_key, data):
	# Execute.send({ type: 'subscribe', path: 'firetruck:translation:y', check: true, tag: 'mike' })
	
	print('subscribe vector3: ', node, ' ', last_key, ': ', lstack, ' = ', key)
	subscriptions[node.get_path()] = [last_key, key, data]
	# convert key to corrections if required, Apply the 
	# converted nodepath to the wait list.
	
func update_subscriptions(_tick):
	#print('update ', v)
	var messages = []
	for key in subscriptions:
		var attrs = subscriptions[key]
		# print('  ', key, ' ', attrs)
		var val = get_node_or_null(key)
		if val: 
			
			var entity = val.get(attrs[0]) if attrs[0] != val else val
			var value = entity[attrs[1]]
			
			if attrs[2].get('check'):
				if attrs[2].get('last_value') == value:
					continue
				
				attrs[2]['last_value'] = value
			
			messages.append({
				"value": value,
				"path": key,
				"id": val.get_instance_id(),
				"entity": attrs[0],
				"type": typeof(entity),
				"key": attrs[1],
				"tag": attrs[2].get('tag'),
				"uuid": attrs[2].get('uuid') 
			})
	
	if messages.size() == 0:
		return
		
	send({'type': 'subscriptions', 'messages': messages})
	
func open_message():
	
	return {
		'type': 'init',
		'scene': get_tree().current_scene.get_path(),
		'parent': str(get_parent().get_path())
	}

var counter = 1
var tick = 0
export (int) var MODULO = 1

func _process(delta):
	# Call this in _process or _physics_process. Data transfer, and signals
	# emission will only happen when calling this function.
	# print(delta)
	var v = int(counter * delta)
	counter += 1 * MODULO
	if v >= 1:
		tick += 1
		#print("tick: ", tick)
		update_subscriptions(tick)
		counter = 0 
	_client.poll()
