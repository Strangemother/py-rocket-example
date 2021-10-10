extends Spatial

# Define the thruster strength.
# Default value 9.8 to match the global gravity
export(float) var thruster_strength:float = 9.8

# Flag true when the parente node is ready. 
# This may switch false when if the parent is lost.
export(bool) var attached:bool = false

# Rigidbody to manipulate. If unchanged, _self_ is used. Map to the body of 
# entity (vehicle) to move.
export(NodePath) var target:NodePath = NodePath('.')

# Captured after "_ready" to store a reference of rocket_node for repeat calls.
# By default this is populated by the target.
var cached_node:RigidBody 
var cached_force_vector = Vector3.ZERO


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	cached_force_vector = force_vector(get_global_transform().basis.y, delta)


func _ready():
	set_target(target)
	
	
func set_target(_target:NodePath):
	"""
	Given a nodepath, store the found node as the internal cached_node.
	Return the resolved Node
	"""
	var new_cached_node:Node = get_node_or_null(_target) 
	
	if new_cached_node == null:
		
		if get_parent() is  RigidBody:
			new_cached_node = get_parent()
			print(get_name(), 
				" - target reference was lost or was left empty. ",
				"Using parent - ", 
				new_cached_node)
		else:
			new_cached_node = get_node('.')
			print('Selecting _self_ as cached node')
	
	if new_cached_node.has_method('add_force') == false:
		print('Cannot add_force to given node', new_cached_node)
		attached = false
		return cached_node
	
	# Apply all references
	cached_node = new_cached_node
	attached = cached_node != null
	
	return cached_node
	
	
func _physics_process(delta):
	"""Apply the thrust to _self_ using the internal cached_node and other
	ready values. If 'attached' is false this funcion does nothing."""
	if attached == false:
		return 
		
	apply_thrust_force(get_global_transform().basis.y, delta)


func apply_thrust_force(force_direction:Vector3, delta:int=-1):
	"""Apply the force to the cached_node using internal geometry. Override the
	force given a direction_vector with a mandatory `Vector(y)` value
	"""
	
	cached_node.add_force(
		cached_force_vector,
		at_force_position()
		)	
		
		
func force_vector(force_direction:Vector3, _delta:int=-1):
	"""Given the current force direction vector apply additional forces 
	and return a Vector3 applied to add_force(*)
	"""
	return force_direction * get_power()
	
	
func get_power():
	"""Return the thruster strength
	"""
	return thruster_strength
	
	
func at_force_position():
	"""Return a Vector3 for the positon of the applied force vector on the 
	internal cached_node. By default this computes the position global_transform
	for _self_ origin and and cached_node origin.
	"""
	return get_global_transform().origin - cached_node.get_global_transform().origin

