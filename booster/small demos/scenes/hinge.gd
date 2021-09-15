extends Spatial


# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	add_child(timer) #to process
	timer.set_wait_time(2)
	timer.one_shot = true
	timer.connect("timeout",self,"_on_timer_timeout")

var reset_point = Vector3(0,15,0)
onready var bob = get_node("RigidBody/Top")
#onready var lega = get_node("RigidBody/Foot")
#onready var legb = get_node("Spatial/RigidBody2")

var loc_transform = Transform(Basis(Vector3(0,0,0)), reset_point)
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _physics_process(delta):
	if reset_node:
		#bob.transform = bob.transform.interpolate_with(loc_transform, delta*2)

		var distance = bob.translation.distance_to(reset_point)
		print(delta, ' ', distance)
		reset_node = false

		interp(bob)
		#interp(lega, Vector3(-3, -4, 0))
		#interp(legb, Vector3(-2, 0, 0))
		start_restopper()
#		lega.translation = reset_point + Vector3(2, 0, 0)
#		legb.translation = reset_point + Vector3(-2, 0, 0)

func temp_off(entity):
	#entity.gravity_scale = 1.0
	#entity.sleeping = true
	pass

func temp_on(entity):
	#entity.gravity_scale = 0.0
	#entity.sleeping = false
	pass

func interp(entity, offset=null):
	if not offset:
		offset = Vector3(0,0,0)
	var tween = get_node("Tween")
	temp_off(entity)
	tween.interpolate_property(entity, "translation",
		entity.translation, reset_point + offset, .6,
			Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
	tween.start()

onready var timer = Timer.new()

func start_restopper():
	#timeout is what says in docs, in signals
	#self is who respond to the callback
	#_on_timer_timeout is the callback, can have any name
	if not timer.is_stopped():
		timer.stop()
	timer.start() #to start

func _on_timer_timeout():
	temp_off(bob)
	print('Off')
	# bob.linear_velocity += Vector3(0, 10, 1)
	timer.stop()

func _unhandled_key_input(event):
	if event is InputEventKey and event.pressed:
		if event.scancode == KEY_SPACE:
			print('Space bar')
			reset_node = true

var reset_node = false


