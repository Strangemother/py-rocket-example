
class Base:
	var _context := ""
	
	func _init(p_context):
		_context = p_context
	
	func debug(msg: String):
		pass

	func warn(msg: String):
		push_warning("{0}: {1}".format([_context, msg]))
	
	func error(msg: String):
		push_error("{0}: {1}".format([_context, msg]))


class Verbose extends Base:
	func _init(p_context: String).(p_context):
		pass
		
	func debug(msg: String):
		print(_context, ": ", msg)


static func get_for(owner: Object) -> Base:
	# Note: don't store the owner. If it's a Reference, it could create a cycle
	var context = owner.get_script().resource_path.get_file()
	if OS.is_stdout_verbose():
		return Verbose.new(context)
	return Base.new(context)

