extends Spatial


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

onready var DevTools = get_node('/root/World/DevTools')
onready var controller:Spatial = get_node('/root/World/Controller')
export var target:NodePath = NodePath('.')
onready var cached_target:Node = get_node(target)
# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# nose up down
# Right stick UD
export var pitch_input:int = 3
export var pitch_compute:float = 1

# rotate on z - spin on horizontal axis
# left stick LR
export var roll_input:int = 0
export var roll_compute:float = -1

# rotate on y - spin on vertical axis
export var yaw_input:int = 2
export var yaw_compute:float = 1

export var yaw_range:float = PI * .3

export var roll_range:float = PI * .5
export var pitch_range:float = PI * .3

export var yaw_trim:float = 0
export var roll_trim:float = 0
export var pitch_trim:float = 0

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	present_motion(delta)
	
	 
func present_motion(delta=1):
	# rotations on each
	# yaw: y
	# roll: z
	# pitch: x
	var v3 = get_pyr(delta)
	cached_target.rotation = v3
	DevTools.out('Gimbal', v3, {})
	
	
func get_pyr(_delta=1) -> Vector3:
	# All squished so no vars are created when producing this vector.
	return Vector3(
		deadzone_trim(get_input(pitch_input), pitch_trim, pitch_compute, pitch_range), #pitch
		deadzone_trim(get_input(yaw_input), yaw_trim, yaw_compute, yaw_range), #yaw
		deadzone_trim(get_input(roll_input), roll_trim, roll_compute, roll_range) #roll
		)

func deadzone_trim(value, trim, compute, compute_range) -> float:
	# Fix the trim enuring it's *1 when input == 1 (dead zone), 
	# and slowly remove as input heads to 1. This ensures the extreme 
	# of each roll is equal on both roll axis
	
	# var corrected_trim = roll_trim * (1 - abs(roll))
	# Roll plus the center factored trim, and then the given input
	# var vroll = (roll + corrected_trim) * roll_compute * roll_range 
	var corrected_trim:float = trim * (1 - abs(value))
	# Roll plus the center factored trim, and then the given input
	return (value + corrected_trim) * compute * compute_range
	
	
func get_input(input_index):
	return controller.current_value(input_index)
