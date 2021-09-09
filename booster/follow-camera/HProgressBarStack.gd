extends "res://scripts/HLabel.gd"


# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

export var max_value:int = 1

func configure(setup):
	"""Given a setup dictionary, apply the configuration and return nothing
	"""
	max_value = setup.get('max_value', 10)
	$Value.max_value = max_value
	

func set_value(value) -> void:
	$Value.value = int(float(value) * 10)
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
