extends Spatial


#onready var main_label:Node = get_node("Label")
onready var out_stack:Node = $VLabelStack # $VLabelStack # $HLabelStack

const HLabel = preload("res://assets/HLabel.tscn")
const HProgressBarStack = preload("res://assets/HProgressBarStack.tscn")

var labelmap = {}

func log_print(name, strings):
	out(name, strings)


func out(name, strings, config=null):
	var label = labelmap.get(name)
	if label == null:
		label = create_label(name, config)
		
	to_label(label, strings)

var lines = []

func println(string, config=null):
	"""Print a string as a devlog line
	"""
	var la = create_label("label-%s" % str(lines.size()))
	la.set_text(str(string))
	lines.append(la)


func create_label(name, config=null):
	"""Create a label and stack it to the view.
	"""
	var la
	var types = {
		'label': HLabel,
		'slider': HProgressBarStack,
	}
	
	if config is Dictionary:
		print('Config ', str(config))
		var _type = config.get('type')
		
		if types.has(_type):
			print('Setup type: ', _type)
			la = types.get(_type)
			la = la.instance()
		else:
			print('No Setup type: ', _type, ', using HLabel')
			la = HLabel.instance()
	else:	
		la = HLabel.instance()
	la.label = name 
	# la.text = name 
	if out_stack == null:
		print('Outstack is null')
		return la
	out_stack.add_child(la)
	labelmap[name] = la
	return la


func to_label(name, strings):
	"""Apply the strings to the named label
	"""
	var label = name
	if typeof(name) == TYPE_STRING:
		label = labelmap[name]
	label.render(strings)



"""Table Graph Sequence

Capture user key sequence input for string detection, lookahead input strings,
key sequence trainers - or generally any input string catpure.

Definition:
	
	name_1: "the string"
	name_2: "string two"
	name_3: "ring"
	
			   --name_1--
			   |     ---|---name_3
			   |     |  |
User Input:    the string will match 
			   |	   | x...
			   ---------name_2 fail
			
Given a dictionary of {key:"my string"}, a user presses the target keys to match "my string"
When the user successfully inputs the key string, an event of _"key"_ is dispathed.

The Table Graph is designed to be lightweight and quick to implement. Some built-in features
provide _the basics_ for you to continue using the available hooks. 

## How it Works

A target value is sequenced with an index position similar to an AB tree. For each
event the given keychar or button code is tested for a sequence starts, and sequence drops. 
If the event key matches the first char within a sequence, the Tree Graph initiates a start 
and an index position of `1` is set within `sequence_flags`.

Each event applies the next index within the char sequence. If the event key does not
match the expected char within sequence, the sequence is dropped. 
If a matching position index meets the length of the target value, we've hit a match 
and dispatch a "finish_sequence" event.

Personally I wanted a _no interface_ key input, for typed codes without spawning a console.
Similar to GTA cheat codes, simply _entering_ a key sequence until a match occurs.

## Usages

Given the features, some considerations of how it can be used:

+ _GTA Style_ cheat code input
+ Button Sequence and input Training
+ Lookahead word suggestion 
+ key-like state machine.


## Input Codes

By default the TGS will capture input strings. When a user enters the keys or 
buttons in order, the key event announces a success. In this example when a 
user types "green", the TGS announces `color`.
	
	var sequences = {
		"color": "green"
	}

## Lookahead (suggestions)

By nature of the code, performing _typed suggestions_ is relatively cheap. For
every sequence with an index of >1 is a _currently valid_ lookahead

	
	var sequences = {
		"alpha": "sunlight",
		"beta": "sunlit",
		"charlie": "sunset"
	}
	
	
"""

var hotstart = ''

# Upon instansiation all sequence keys flag -1 (never used),
# when a user enter a key the index is moved to the next index.
var sequence_flags = {}
enum Reason {IGNORE,RESTART,NONE=-1}


export var sequences:Dictionary = {
	'wind': "wind",
	'just': "just wind",
	'name': "eric",
	'open': "window",
	'nearly': "windof",
	'also_nearly': "windof",
	'sentence': "wind in the willows",
	'one': 'uni',
	'study': 'university',
	'animal': 'unicorn',
	'food': 'corn',
	'dog': 'doggy',
	'spam_14': 'qqqqqqqqqqqq',
	'arrows': ['up', 'down', 'left', 'right'],
	'dev': ['f12']
}	


func _ready():
	log_print('FPS', 'Not Set')
	hotwire_sequences()
	if get_node_or_null('./Sequences'):
		$Sequences.create_string_chars(sequences)
	
	
func _unhandled_input(event):
	if event is InputEventKey and event.is_pressed():
		stack_key(event)


func hotwire_sequences():
	"""Build a 'hotstart' string of all first chars within the sequences.
	When an event occurs, the key is tested against the 'hotstart' string
	rather than iterating the entire sequence dictionary.
	"""
	# To hotwire the boot speed, All first elements from sequences are stored as 
	# 'starts'. ensuring when a key event occurs, we can check the thin array, 
	# rather than (potentially for no reason), scanning all sequences.
	for key in sequences:
		# literal string concat
		hotstart += sequences[key][0]
		sequence_flags[key] = -1
		
	print('hotstart: ', hotstart)
	
	
func stack_key(event):
	"""Given an event, extract the chat string and perform a drop or start
	sequence as required.
	"""
	var str_code = OS.get_scancode_string(event.scancode).to_lower()
	return push_char(str_code, event)
	
func push_char(str_code, event=null):
	"""Push the string value code into the sequence handler as the _next_ key
	"""
	var in_str = str_code in hotstart
	log_print('Key ', str(str_code, ' ', in_str, ': ', event))
	var complete = drop_check_sequence(str_code, event)
	
	if in_str:
		return start_sequence(str_code, event, complete)

	return complete 
	
	
func drop_check_sequence(str_code, event):
	"""For each flagged sequence, check if the given string is the expected
	next key within the sequence, if false, reset the sequence flag index.
	"""
	var finished:Array = []
	for key in sequence_flags:
		
		var position:int = sequence_flags[key]
		if position < 1:
			continue
		
		var value = sequences[key]
		# if the stack position is past the string length,
		# or if the value is an array, check the position to the length.
		if (position >= len(value)
			or ( value is Array and (position >= len(value) ))):
			
			if safe_append(key, event, finished) == null:
				continue
				
		print('value: ', key, ' ', value, ' ', value[position], '#', str_code)
		
		var _match = value[position] == str_code
		if str_code == 'space':
			if value[position] == ' ':
				_match = true 
				
		if _match:
			step_key(key, str_code, position + 1, event)
			sequence_flags[key] += 1
		else:
			fail_key(key, str_code, event)
			sequence_flags[key] = 0
		
		if (sequence_flags[key] >= len(value)
			or (value is Array and (position >= len(value) ))):
			safe_append(key, event, finished)
#			
	return finished 


func safe_append(key, event, finished):
	var fi = finish_sequence(key, event)
	if fi != null:
		finished.append(fi)
		return finished
	return null


func start_key(key, str_code, event):
	# api handler for the 'start' of a key sequence.
	if $Sequences == null:
		return
	$Sequences.update_key(key, 1)


func fail_key(key, str_code, event):
	# api handler for the 'start' of a key sequence.
	#print('Failed: ', key)
	if $Sequences == null:
		return
	$Sequences.update_key(key, 0)
	
	
func step_key(key, str_code, index, event):
	"""The given key has bumped by 1 due to a successfull match at index
	"""
	if $Sequences == null:
		return
	$Sequences.update_key(key, index)

	
func refuse_key(key, str_code, reason_state=Reason.NONE):
	#print('Refuse key: ', key, ' because: ', reason_state)
	$Sequences.update_key(key, 0)
	
	
func finish_sequence(key, event):
	#print('Hit! ', key)
	sequence_flags[key] = 0 
	if $Sequences == null:
		return
	$Sequences.hit(key)
	return key 

func get_active() -> Array:
	"""Return a list of sequence keys with a position index of >= 1.
	"""
	var res = []
	for key in sequence_flags:
		if key > 0:
			res.append(key)
	return res 
	
func start_sequence(str_code, event, ignore=null):
	"""A Sequence should start"""
	var names:Array = [] if ignore == null else ignore
	var finished:Array = []
	for key in sequences:
		
		if sequences[key] is Array:
			var value:Array = sequences[key]
			if value[0] != str_code:
				continue
		else:
			var value:String = sequences[key]
			if value.begins_with(str_code) == false:
				continue
		
		if sequence_flags[key] > 0:
			refuse_key(key, str_code, Reason.RESTART)
			continue
		
		if names.has(key):
			refuse_key(key, str_code, Reason.IGNORE)
			continue 
		
		start_key(key, str_code, event)
		sequence_flags[key] = 1
		if sequence_flags[key] == len(sequences[key]):
			print('Early hit: ', key)
			var fi = finish_sequence(key, event)
			if fi != null:
				finished.append(fi)
	return finished 
	
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	log_print('FPS', Engine.get_frames_per_second())
