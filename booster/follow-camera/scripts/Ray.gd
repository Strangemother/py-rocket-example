extends RayCast


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
export var distance_vector:Vector3
export var distance:float

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if is_colliding():
		var obj = get_collider()
		var orA:Vector3 = get_collision_point() # obj.get_global_transform().origin
		var orB:Vector3 = get_global_transform().origin
		distance_vector = orB - orA
		distance = orB.y - orA.y
		#print(distance)

