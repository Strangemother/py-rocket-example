extends Spatial
# onready var controller:Spatial = get_node('/root/World/Controller')

# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass


var values = {}

export var reset_button = 3
export(NodePath) var node

export var power_axis = 7
export var power_axis_deadzone = .00
export var power_multiplier = 1
export var power_falloff = .99

export var brake_axis = 6
export var brake_multiplier = 5
export var brake_falloff = .99
export var brake_reverse = 18


onready var DevTools = get_node('/root/World/DevTools')

var current_power = 0.0
# Power amount applied by arrows
export var key_power = 0.0
# Amount to add per step
var power_step = 0.01


func refuel_node(_event=null):
	
	var target:RigidBody = get_node(node)
	target.fuel = 10_000
	
func reset_node(_event=null):
	
	var target:RigidBody = get_node(node)
	target.translation = Vector3(0,4,0)
	target.rotation = Vector3.ZERO
	target.linear_velocity = Vector3.ZERO
	target.angular_velocity = Vector3.ZERO


func get_current_power() -> float: 
	var res = values[power_axis] if (power_axis in values) else 0	
	
	return res * key_power * 20
	# return current_value(power_axis, power_multiplier * power_falloff, null, 1)
	
var power_label_setup = {
	'type': 'slider'
}

func _process(delta):
	current_power = get_current_power()
	DevTools.out('Controller Power', str(current_power), power_label_setup)
	
func current_value(index, multiplier=1, deadzone=null, curve=1, default=0):
	"""Request the current value for the given button index
	"""
	var res = values[index] if (index in values) else default
	if res < 0:
		res = -ease(abs(res), curve)
	else:
		res = ease(res, curve)
	if deadzone == null:
		return res * multiplier
	res = 0 if abs(res) < deadzone else res

	return res * multiplier

	
func _unhandled_input(event):
	# $EventOut.text = event.as_text()
	# DevTools.println(event.as_text())
	
	var vname = 'dunno'
	if 'axis' in event:
		vname = event.axis
	if 'button_index' in event:
		vname = event.button_index
		
	var thin_name = "{0} Axis {1}".format([event.get_class(), vname])
	DevTools.out(thin_name, event.as_text())
#	if event is InputEventMouseMotion:
#		return
	if event is InputEventKey:
		var val = 0
		var direction = 'up'
		if event.scancode == KEY_UP:
			val = power_step	
		
		if event.scancode == KEY_DOWN:
			val = power_step * -1
			direction = 'down' 
		
		key_power += val 
		if key_power < 0:
			key_power = 0
		if key_power > 1:
			key_power = 1
		DevTools.out('keypower', str(direction, ' to: ', val, ' ', key_power))
		
		if event.scancode == KEY_R and event.pressed:
			reset_node(event)	
		
		if event.scancode == KEY_F and event.pressed:
			refuel_node(event)	
			
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
