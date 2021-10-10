"""A RayCast Thruster applies additional localised position variations given 
objects nearby, notably a _ground_  and its ground-effect. Considering a 
standard thruster (vtol focused), other variables may add alterations to the
translated position; such as suckdown, fountain lift and hot gas ingestion (HGI)
"""
extends "res://scripts/Thuster.gd"

# The element to check when calulating _down_ -y 
onready var internal_ray:Node = get_node('./RayCast')


export var washplate_path:NodePath = NodePath('./Washplate')
# Washplate for area and pressure size.
onready var washplate:Node = get_node(washplate_path)#get_node('./MeshInstance')

# fixed wing (a single thruster with one facing plate) generally feels 
# ground effect ~50% of the wingspan. 
# Therefore we have 1 wing and a static fountain effect, so the pressure 
# envelope is slightly larger.
export var washplate_reduction:float = .66

# For nested washplates, or "hard to compute" shapes, apply  base multiplier
# to correct an evaluated shape _washplate size_ before reduction.
# For example, if the washplate is within a collision shape, it may equate 1* its 
# scale, when we prefer 4*
export var washplate_scalar:float = 1.0

# The area of a sphere is ~.66% of a cube. If true, this factors for 
# the washplate size, so not to overestimaste a washplate of the same Y area
# to a similar sized rectangle.
export var eclipse_washplate:bool = true

# pressure amount given the % of envelope _squash_ and current thrust_strength
export var envelope_falloff:float = .6

# The current % foot pressure applied in the envelope. 0 for no ground-effect
# .9 for 90% pressure against a raycast collider.
export var pressure:float

# easeOutBack
# easeInBack
# easeInOutQuad
# easeOutExpo
export var envelope_ease:String = 'easeOutExpo'
export var print_report = false

# An internal cache of the washplate Y face area for ground effect calculation
var washplate_size:Vector3

onready var DevTools = get_node('/root/World/DevTools')

func log_print(name, strings):
	if print_report:
		DevTools.out(name, strings)


# Called when the node enters the scene tree for the first time.
func _ready():
	washplate_size = get_washplate_area()
	var size = get_washplate_size()
	internal_ray.cast_to.y = size * -10
	#DevTools.println(str('Ready washplate', internal_ray.cast_to, ' == ', size))
	
	
func get_washplate_area():
	if washplate:
		var my_scale:Vector3 = washplate.get_aabb().size *  washplate.scale * washplate_scalar
		if eclipse_washplate:
			my_scale *= washplate_reduction
		return my_scale
	return Vector3(1,1,1)
	


func get_washplate_size():
	return washplate_size.x * washplate_size.z 

var last

func force_vector(force_direction:Vector3, delta:int=-1):
	"""Apply a ground effect _cushion_ to the force.
	"""
	#var result:Vector3 = force_direction * get_power()
	var result = get_foot_pressure(force_direction, delta) 
	#result *= (pressure * envelope_falloff)
	#get_foot_pressure(pressure)
	
	var cv = clamp(abs(result.y), 1, 10)
	log_print('Particle Life', str(stepify(cv, 0.01)))
	$CPUParticles.lifetime = cv
	return result

func get_foot_pressure(force_direction, _delta):
	var result:Vector3 = force_direction * get_power()
	var pressure = envelope_pressure(force_direction) 
	result *= (pressure * envelope_falloff)
	
	print_pressure(pressure, result)
	
	return result

func print_pressure(pressure, result):
	var _last = stepify(pressure, 0.0001)
	if _last != last:
		log_print('pressure', str(_last, ' power force: ', result.y))
	last = _last
	
func envelope_pressure(force_direction):
	"""Return the pressure 0-1 under the thruster foot, accounting for distance
	to raycast and current thrust.
	"""
	# get area of washplate XY.
	var height = get_washplate_size() * washplate_reduction
	var distance = internal_ray.distance 
	
	# Assume a column, with the distance to the ground as a pressure 
	# addition for the force vector Y, adding more pressure when progressing to 
	# 0 distance. (P=F/m)
	log_print("force", str("Force Direction  Y: ", force_direction.y))
#	get_node('/root/World/Label').text = str("Force Direction  Y", force_direction.y)
	var pressure_y = clamp(-(distance-height) / height,0, 4)	
	var v:float = self.call(envelope_ease, pressure_y)
	# 1 for _global pressure_
	return 1 + v


func easeOutBack(x:float):
	var c1 = 1.70158
	var c3 = c1 + 1
	return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)
	
	
func easeInOutQuad(x:float):
	if (x < 0.5):
		return 2 * x * x 
	return 1 - pow(-2 * x + 2, 2) / 2


func easeInBack(x:float):
	var c1 = 1.70158
	var c3 = c1 + 1
	return c3 * x * x * x - c1 * x * x


func easeOutExpo(x:float):
	if x == 1:
		return 1
	return 1 - pow(2, -10 * x)

"""
Notes
Heat: 
	Work done by the thrust produces heat through the thruster out-port and
	internal components. Overworking the thruster will reduce performance and
	longevity
Washplate:
	The washplate defined the _effect area_ of the ground effect pressure area.
	Without a washplate, the internal calculation applies the area of XZ
Inlet:
	The _air_ inlet gathers from the external evironment and is affected by heat,
	due to hot gas ingestion. In the case of an ION thruster, this is _hot ions_.
Exhaust:
	The expulsion of work pipes through one out-port, ejecting _hot gasses_.
	promimity of the outlet and inlet will affect thruster performance,
"""
