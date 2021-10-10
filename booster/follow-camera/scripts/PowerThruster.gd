extends "res://scripts/RayCastThruster.gd"

export var max_out:float = 100 # electric units? 
# Declare member variables here. Examples:
# var a = 2
# var b = "text"

# max value a emitter cell can ouput. This should be a little-more than its 
# expected power. 
export var max_cell_power:float = 1 # Megawatts max

# How much throughput of power on input.
# if max cell is 10 and capacity is 4, it'll take 2 and a bit (3) 
# delta processes to fill.
export var max_pipe_capacity:float = 5 # Megawatts

# power for 1 cell power of 1 area, for 1 mass.
# e.g. 9.8 == 1 cell (rocket) area 1 sqft ~ 1kg 
# Being (1) -Y gravity
export var cell_netwons = 11

var power_curve:float = 1 #-.2

## Called when the node enters the scene tree for the first time.
#func _ready():
#	pass # Replace with function body.
onready var controller:Spatial = get_node('/root/World/Controller')

# a cache for the input pipe calculation.
var current_feed_request = 0 # Mw

# Available Fuel.
var fuel:float = 10_000 #kw

	
var add_foot_pressure:float = 1
var tip_pad_height:float = 2
var foot_pad_pressure:float = 3
var max_pad_force:float = 10
var max_result_force:float = 20
export var add_power:float = 0

export var power_axis:int = 7

func get_input_power():
	"""Return the amount of input from the (fly by wire) requested controller
	input. 
	
	To quietly mimic a fuel system, the input power (trigger) mixes 
	input fuel (pipe capacity) with a feed in speed (receiver input max) -
	Then a _request_ is made to ramp to the value goverened by pipe capacity.
	
	+ requested power (input) opens fuel _sleuth_, % clamped by pipe capacity.
	+ Feed time (as charge rate or liquid fill) governs the target output 
	  ramping speed over delta time.
	+ max_power = strength, output_capacity per _cell_
	
	input (0.7) -> ease sleuth (.5) -> feed amount (60Mw/t)	
	"""
	var trigger_percent = controller.current_value(power_axis) * add_power # 0-1
	current_feed_request = max_pipe_capacity * trigger_percent # 0 to max_pipe
	log_print('get_input_power pipe output', current_feed_request)
	return current_feed_request


func get_power():
	"""Return the thruster strength given a input mix and mutliplier"""
	return thruster_strength
	
	
func _process(delta):
	"""Apply request fuel feed amount (if any) 
	"""
	# push some fuel into thrust, returning the literal reduction in fuel
	thruster_strength = request_fuel_amount(current_feed_request, delta) # 0-n


func request_fuel_amount(current_feed_request:float, delta:float=1) -> float: # 0-n
	"""Pull the value from the fuel supply - or max possible, applying delta.
	return a removed fuel
	"""
	# The cut of pipe over delta
	var delta_drain:float = current_feed_request * (delta*.5)
	# The value to delete.
	var step_drain:float = current_feed_request * delta_drain
	var feed = get_input_power() * step_drain
#
	var power_01 = ease(feed * step_drain, power_curve)
	var power = power_01 * cell_netwons
	log_print('current_feed_request', stepify(current_feed_request, 0.01))
	log_print('delta_draindrain: ', delta_drain)
	log_print("step_drain:", step_drain)
	log_print("feed:", feed)
	log_print("power %:", power_01)
	log_print("power:", power)
	log_print("cell_netwons:", cell_netwons)
	
	#add presure + (atmos(1) * power_01
	add_foot_pressure = power_01
	if fuel <= 0:
		log_print('Fuel','Empty.')
		return 0.0
		
	fuel -= step_drain
	log_print('Fuel',fuel)
	return power
	

func norm(val, _max, _min):
	return (val - _min) / (_max -_min)
	

func get_foot_pressure(force_direction, _delta):
	var result:Vector3 = force_direction * get_power()
	var pressure = envelope_pressure(force_direction) 
	result.y += (pressure * envelope_falloff)
	var pad_pressure:Vector3 = get_tip_pressure(force_direction)
	

	# minus atmosphere pressure height - here we cheat and use the _literal_ 
	# height of the thruster, later attaching instruments
	var y = self.global_transform.origin.y
	var atmos_pressure = 1.01 - y * .01
	var height_pressure_reduce_add_pressure:float = pressure * add_foot_pressure * atmos_pressure

	var hf = force_direction * height_pressure_reduce_add_pressure * pressure
	#hf += pad_pressure
	var mpu = pad_pressure * height_pressure_reduce_add_pressure #* hf
	result = (result * height_pressure_reduce_add_pressure) + (mpu.normalized() * 2 * pad_pressure)

	log_print('atmos_pressure', str(atmos_pressure))
	log_print('pad_pressure', str(pad_pressure))
	log_print('height_pressure_reduce_add_pressure', stepify(height_pressure_reduce_add_pressure, 0.01) )
	log_print('add_foot_pressure 1', str(add_foot_pressure, ' HF (Y):', stepify(hf.y, 0.01)))
	log_print('pad_pressure * height_pressure_reduce_add_pressure (Y)', stepify(mpu.y, 0.001))
	print_pressure(pressure, result)
	log_print('add_foot_pressure 3', str(add_foot_pressure, ' result:', result))
	return result


func get_tip_pressure(force_direction:Vector3) -> Vector3:
	"""Return the high factor _foot_ pressure closest to the ground
	"""
	var y = self.global_transform.origin.y
	
	var tip_pad_strength = clamp(foot_pad_pressure * current_feed_request, 0, max_pad_force)
	var height = 1.5 + tip_pad_height # - target offset from self (1.5)
	# Normalise the foot pad pressure from the _heighted_ size to 0-1
	var tip_pad = norm(max(0, height - y), tip_pad_height, 0)
	# Then gather a % of the total amount
	var pad_pressure = tip_pad * tip_pad_strength

	log_print('Height', str(stepify(height, 0.01), ' ', y))
	log_print("tip_padding %", tip_pad)
	log_print("tip_padding val", pad_pressure)
	pad_pressure *= force_direction.normalized()
	pad_pressure.x = 0
	pad_pressure.z = 0
	return pad_pressure
	
	
