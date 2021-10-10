extends VBoxContainer


# Declare member variables here. Examples:
# var a = 2
# var b = "text"

export var mapped:Dictionary = {}
var Sequence = preload("res://assets/Sequence.tscn")
var items = {}

func hit(key):
	"""Announce an assertion of a match
	"""
	var item = items.get(key) # Sequence
	item.hit()	
	
func create_string_chars(char_dict:Dictionary):
	for key in char_dict:
		var new_char = Sequence.instance()
		new_char.set_kv(key, char_dict[key])
		add_child(new_char)
		items[key] = new_char
	
		
func update_key(key, index):
	"""Update the key name with the selected position index int.
		
		update_key('fruit', 2)
	"""
	var item = items.get(key) # Sequence
	if item == null:
		print('Sequence of key does not exist: ', key)
		return 
	
	item.set_key_index(index)
	

func reset_chars():
	for char_instance in items:
		self.remove_child(char_instance)
	
	items = []
	
# Called when the node enters the scene tree for the first time.
func _ready():
	create_string_chars(mapped)


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
