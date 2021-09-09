extends HBoxContainer


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

var chars:Array = []
var key_index = -1 

var index_char
var Char = preload("res://assets/Char.tscn")
var label = 'no label'

func hit():
	print('HIT')
	for _char in chars:
		_char.hit()
	
func fail_all():
	# print('Fail')
	for _char in chars:
		_char.fail()
	

func set_kv(key:String, value):
	$Label.text = key 
	label = key 
	reset_chars()
	create_chars(value)


func set_key_index(index:int):
	key_index = index
	#print(label, ' Set index: ', index)
	index_char.text = str(key_index)
	if index == 0:
		return fail_all()
	if index >= 1:
		#print('   set_key_index highlight on ', key_index-1)
		if key_index-1 < len(chars):
			chars[key_index-1].highlight()
		else:
			print('Cannot highlight index ', key_index-1, ' for ', label)
#		chars[key_index-1].get_node('AnimationPlayer').play('TextColor')
		
		
func create_chars(items_or_str):
	if items_or_str is String:
		return create_string_chars(items_or_str)
	print('Urm ', items_or_str)
	
	
func create_string_chars(items_or_str:String):
	for letter in items_or_str:
		var new_char = Char.instance()
		new_char.text = letter
		add_child(new_char)
		chars.append(new_char)
		
func reset_chars():
	for char_instance in chars:
		self.remove_child(char_instance)
	
	chars = []
	
# Called when the node enters the scene tree for the first time.
func _ready():
	index_char = Char.instance()
	index_char.text = str(key_index)
	# set_kv('fruit', 'banana')
	add_child(index_char)
	 


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
