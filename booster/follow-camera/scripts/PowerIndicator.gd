extends Spatial


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

export var target:NodePath = NodePath('./Indicator')
onready var cache_target:Node = get_node(target)

export var input_axis:int = 0
export var input_scale:float = -1.1
export var min_value:float = .1
onready var controller:Spatial = get_node('/root/World/Controller')

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	cache_target.scale.y = min_value + controller.current_value(input_axis) * input_scale
