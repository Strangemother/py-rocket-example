extends Spatial


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

export(NodePath) var target
export(NodePath) var pet
export var offset:Vector3 = Vector3(0,0,8)
export var drag:float = 4
export var FOLLOW_SPEED:float = 1.0

onready var target_node:Spatial = get_node(target)
onready var pet_node:Spatial = get_node(pet)

# Called when the node enters the scene tree for the first time.
func _ready():
#	get_node('../Thing/AnimationPlayer').play('f')
	pass 
	
var angle = null
var distance = 0
var ticker = 0
var init_scale = null

var follow_pos:Vector3 = Vector3(1,1,0)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	ticker += 1

	distance = (target_node.translation.distance_to(pet_node.global_transform.origin))
	# if the distance is greater than the node allowed, move the pet towards the 
	# target
	#pet_node.look_at(target_node.translation, Vector3(0,0,1))
	#pet_node.transform = target_node.transform * Transform(Vector3(0,0,1), Vector3(0,-1,1), Vector3(0,0,1), Vector3(0,0,0))
	#pet_node.transform.basis
	var vtrans = target_node.transform
	var ptrans = Transform()
	
	ptrans.origin = vtrans.origin + vtrans.basis.z * offset.z
#	ptrans.origin.y =  vtrans.origin.y + offset.y
	ptrans.origin.y =  follow_pos.y + offset.y 
#	ptrans.origin.z +=  follow_pos.z + offset.z
	ptrans.origin.x =  follow_pos.x + offset.x
	
	pet_node.transform = ptrans
#	var v = look_follow(null, ptrans, follow_pos)
	pet_node.look_at(follow_pos, Vector3.UP)


func _physics_process(delta):
	var pos = target_node.transform.origin

#	follow_pos = follow_pos.linear_interpolate(pos, delta * FOLLOW_SPEED)

func look_follow(state, current_transform, target_position):
	var up_dir = Vector3(0, 1, 0)
	var cur_dir = current_transform.basis.xform(Vector3(0, 0, 1))
	var target_dir = (target_position - current_transform.origin).normalized()
	var rotation_angle = acos(cur_dir.x) - acos(target_dir.x)
	return rotation_angle
#    state.set_angular_velocity(up_dir * (rotation_angle / state.get_step()))

	
