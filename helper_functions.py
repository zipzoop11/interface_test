from kivy.app import App
import re


def starter_function_generator(*args, **kwargs):
	print(f"[starter_function_generator]{args} :: {kwargs}")
	interface_name = args[0]
	popup = args[1]

	def starter_function(*args):
		print(f"STARTER FUNCTION GOT ARGS {args}")
		switch_state = args[1]
		print(f"STARTER FUNCTION GOT SWITCH_STATE {switch_state}")
		if switch_state:
			ACTION = 'START'
		else:
			ACTION = 'STOP'
		app = App.get_running_app()
		bt_conn = app.Bluetooth_connection
		register_callback = app.register_request

		msg = {'ACTION': ACTION,
			   'ARGS': {'interface_name': interface_name},
			   'SETTINGS': {}}

		request_id = bt_conn.send(msg=msg)
		if ACTION == 'START':
			register_callback(request_id, add_interface)
		elif ACTION == 'STOP':
			register_callback(request_id, remove_interface)

	return starter_function


def add_interface(*args, **kwargs):
	app = App.get_running_app()
	interfaces = app.interfaces
	callback = args[0]
	name = callback['INTERFACE_NAME']

	interfaces[name] = callback['SETTINGS']
	print(f"[{__name__}]app.interfaces[{name}]: {app.interfaces[name]}")


def remove_interface(*args, **kwargs):
	app = App.get_running_app()
	interfaces = app.interfaces
	callback = args[0]
	name = callback['INTERFACE_NAME']

	try:
		interfaces.pop(name)
	except KeyError:
		pass


# Shamelessly stolen from: https://gist.github.com/EONRaider/c34f6799b9cf2259e90fce54a39d693c
def validate_mac(mac_address):
	is_valid_mac = re.match(r'([0-9A-F]{2}[:]){5}[0-9A-F]{2}|'
                            r'([0-9A-F]{2}[-]){5}[0-9A-F]{2}',
                            string=mac_address,
                            flags=re.IGNORECASE)
	try:
		return bool(is_valid_mac.group())  # True if match
	except AttributeError:
		return False
