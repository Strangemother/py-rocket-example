extends Spatial

onready var controller:Spatial = get_node('/root/World/Controller')
onready var DevTools = get_node('/root/World/DevTools')

func _ready():
	pass


func _process(delta):
	var r_stick_ud = controller.current_value(3)
	var l_stick_ud = controller.current_value(1)
	var l_stick_l = controller.current_value(0)
	DevTools.log_print('right', r_stick_ud)
	DevTools.log_print('left', l_stick_ud)
	
	$BlueJoint.set('angular_spring_x/equilibrium_point', -l_stick_l)
	DevTools.log_print('Blue Joint equilibrium_point X', $BlueJoint.get('angular_spring_x/equilibrium_point'))
	$Blue.add_power = l_stick_l * l_stick_l
	
	$BlackJoint.set('angular_spring_x/equilibrium_point', -l_stick_l)
	DevTools.log_print('Blue Joint equilibrium_point X', $BlackJoint.get('angular_spring_x/equilibrium_point'))
	$Black.add_power = l_stick_l * l_stick_l
	
	$FrontRightJoint.set('angular_spring_x/equilibrium_point', -l_stick_l)
	DevTools.log_print('Front Right Joint equilibrium_point X', $BlueJoint.get('angular_spring_x/equilibrium_point'))
	$FrontRight.add_power = -l_stick_l * -l_stick_l
	
	$BackRightJoint.set('angular_spring_x/equilibrium_point', -l_stick_l)
	DevTools.log_print('Back Right Joint equilibrium_point X', $BlackJoint.get('angular_spring_x/equilibrium_point'))
	$BackRight.add_power = -l_stick_l * -l_stick_l
	
