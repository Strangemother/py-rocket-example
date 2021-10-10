extends Spatial

export(NodePath) var node
# Declare member variables here. Examples:
# var a = 2
# var b = "text"
export var power_axis = 7
export var power_axis_deadzone = .00
export var power_multiplier = 100
export var power_falloff = .99

export var brake_axis = 6
export var brake_multiplier = 5
export var brake_falloff = .99
export var brake_reverse = 18

export var direction_axis = 0
export var direction_multiplier = -.3
export var direction_axis_deadzone = .2

export var reset_button = 3

var flip = false 

# Called when the node enters the scene tree for the first time.
func _ready():
	pass


# Called every frame. 'delta' is the elapsed time since the previous frame.
func x_process(delta):
	#$fps_label.set_text(str(Engine.get_frames_per_second()))

	process_node(delta)
	


func process_node(_delta):
	var target = get_node_or_null(node)
	
	if not target:
		return 
		
	var current_power = current_value(power_axis, power_multiplier * power_falloff, null, 2.6)
	var current_steering = current_value(direction_axis, direction_multiplier, 
			direction_axis_deadzone, 1.4)
	var brake = current_value(brake_axis,  target.brake_multiplier * brake_falloff)
	var v = target.linear_velocity.length()
	
	if current_power > .1 and brake == 0:
		flip = false 
		
	if current_power == 0 and v < 2 and brake > 0 and brake_reverse != null:
		flip = true
	
	if flip:
		current_power = -(brake * brake_reverse)
	#$Power.text = str(target.linear_velocity.length())
	target.engine_force = current_power 
	target.steering = current_steering
	target.brake = brake

func reset_node(_event=null):
	var target = get_node_or_null(node)
	if target:	
		target.translation = Vector3(0,8,0)
		target.rotation.z = 0
		target.rotation.y = 0
		target.linear_velocity = Vector3(0,0,0)


func current_value(index, multiplier=1, deadzone=null, curve=1, default=0):
	var res = values[index] if (index in values) else default
	if res < 0:
		res = -ease(abs(res), curve)
	else:
		res = ease(res, curve)
	if deadzone == null:
		return res * multiplier
	res = 0 if abs(res) < deadzone else res

	return res * multiplier


func _input(event):
	if event.is_action_pressed("rotate_control"):
		rotate_control(event)

export var controls_rotated = false 

func rotate_control(event):
	# Spin axis control, left is front, back in right - with toggle.
	controls_rotated = not controls_rotated
	var engines = get_node('/root/World/Rocket/Engines')
	
	var nodes = ['FrontLeft',
		'FrontRight',
		'BackLeft',
		'BackRight']

	var controls = [
		'Trigger_Left',
		'Trigger_Right',
		'Trigger_Left',
		'Trigger_Right'
		]


	if controls_rotated:
		controls = [ 
			'Trigger_Left',
			'Trigger_Left',
			'Trigger_Right',
			'Trigger_Right' 
		]
	
	for i in range(nodes.size()):
		engines.get_node(nodes[i]).key_thrust = controls[i]

var values = {}

func _unhandled_input(event):
	#$EventOut.text = event.as_text()
#	if event is InputEventMouseMotion:
#		return
#
#	if event is InputEventMouseButton:
#		print('Mouse',
#		' button_index ', event.button_index,
#		' pressed ', event.pressed,
#		' doubleclick ', event.doubleclick
#		)
#		return
	if event is InputEventJoypadButton:
		if event.button_index == reset_button and event.pressed:
			reset_node(event)
#		print('Joypad Button',
#			' button_index ', event.button_index,
#			' pressure ', event.pressure,
#			' pressed ', event.pressed
#			)
#		return
	if event is InputEventJoypadMotion:
		values[event.axis] = event.axis_value
