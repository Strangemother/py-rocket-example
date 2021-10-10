extends RigidBody


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
export(NodePath) var node
var engine = preload("res://assets/engine.tscn")
export var reset_button = 3

func _input(event):
#
#	if Input.is_action_pressed("A_Button"):
#		var new_one = engine.instance()
#		new_one.key_thrust = 'Trigger_Right'
#		var rpath = get_path()
#		new_one.rocket_node = NodePath(rpath)
#		add_child(new_one)
		
	if event is InputEventJoypadButton:
		if event.button_index == reset_button and event.pressed:
			reset_node(event)
			
# Called every frame. 'delta' is the elapsed time since the previous frame.
func reset_node(_event=null):
	var target = get_node_or_null(node)
	if target:
		target.translation = Vector3(111,69,105)
		target.rotation.z = 0
		target.rotation.y = 0
		target.linear_velocity = Vector3(0,0,0)
