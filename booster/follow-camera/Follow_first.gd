extends Spatial


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

export(NodePath) var target
export(NodePath) var pet

onready var target_node:Spatial = get_node(target)
onready var pet_node:Spatial = get_node(pet)

# Called when the node enters the scene tree for the first time.
func _ready():
	get_node('../Thing/AnimationPlayer').play('f')
	
var angle = null
var distance = 0
var ticker = 0
var init_scale = null
var look_value= 0


const CONSTANT_INTERPOLATION = 1

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
	
	# Point in one direction, relative to the target. (always left for example)
	# Remove to change; point in one world direction, regardless of target (always east)
#	ptrans.basis = vtrans.basis
#	ptrans.basis.z *= Vector3(1,1,1)
#	ptrans.basis.y *= Vector3(1,abs(ptrans.basis.y.y),1)
	
	ptrans.origin = vtrans.origin + vtrans.basis.z * 3
	ptrans.origin.y =  vtrans.origin.y + 2
	ptrans.origin.z =  follow_pos.z
	ptrans.origin.x =  follow_pos.x

#	ptrans.origin.x =  0
#	ptrans.origin.x =  0#vtrans.origin.y +4 #* 4
#	var v = ptrans.rotated(Vector3.UP, .5)

	# mount the pet on an Y rail:
#	ptrans.origin.x =  0#vtrans.origin.y +4 #* 4
#	ptrans.origin.y =  0#vtrans.origin.y +4 #* 4
#	ptrans.origin.z =  0#vtrans.origin.y +4 #* 4
	
	pet_node.transform = ptrans
	
#	ptrans.basis.x = Basis(vtrans)
#	ptrans.origin = vtrans.origin #+ vtrans.basis.z * 5
#	ptrans.origin = ptrans.origin + vtrans.basis.z * 3
#	ptrans.origin.y = 4
#	ptrans.origin.x = vtrans.origin.x
#	ptrans.origin.z = vtrans.origin.z
#	ptrans.origin.z = 0
#	pet_node.transform.origin = ptrans.origin
#	pet_node.transform = ptrans
	
	pet_node.look_at(vtrans.origin, Vector3.UP)
	
#	var v = look_follow(null, ptrans, target_position)
#	print(v)
#	if not pet_node.transform.is_equal_approx(target_node.transform):
#		pet_node.transform = pet_node.transform.interpolate_with(ptrans, .7)

const FOLLOW_SPEED = 1

var follow_pos:Vector3 = Vector3(1,1,0)

func _physics_process(delta):
	var pos = target_node.transform.origin

	follow_pos = follow_pos.linear_interpolate(pos, delta * FOLLOW_SPEED)
#	print(t)

func look_follow(state, current_transform, target_position):
	var up_dir = Vector3(0, 1, 0)
	var cur_dir = current_transform.basis.xform(Vector3(0, 0, 1))
	var target_dir = (target_position - current_transform.origin).normalized()
	var rotation_angle = acos(cur_dir.x) - acos(target_dir.x)
	return rotation_angle
#    state.set_angular_velocity(up_dir * (rotation_angle / state.get_step()))

	
	
func birdseye():
	var vtrans = target_node.transform
	var ptrans = Transform()
	ptrans.origin.y = 4
	ptrans.origin.x = vtrans.origin.x
	ptrans.origin.z = vtrans.origin.z
	pet_node.transform.origin = ptrans.origin

var t = 0

func x_process(delta):
	t += delta

	#pet_node.transform = pet_node.transform.interpolate_with(target_node.transform, .5)
