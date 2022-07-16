from kivy.app import App
import re
import random


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
	status_bar = app.root.ids['status_bar']

	status_bar.update_interface(name=name, status='Started')

	interfaces[name] = callback['SETTINGS']
	print(f"[{__name__}]app.interfaces[{name}]: {app.interfaces[name]}")


def remove_interface(*args, **kwargs):
	app = App.get_running_app()
	interfaces = app.interfaces
	callback = args[0]
	name = callback['INTERFACE_NAME']

	status_bar = app.root.ids['status_bar']

	status_bar.update_interface(name=name, status='Stopped')

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


def add_targets(new_targets, interface_name, callback_func=None):
	app = App.get_running_app()
	conn = app.Bluetooth_connection

	register_callback = app.register_request
	interface = app.interfaces[interface_name]

	if not interface:
		return False
	else:
		target_list = interface['TARGETS']
		target_list += new_targets

		request = {
			'ACTION': 'UPDATE_SETTINGS',
			'ARGS': {'interface_name': interface_name},
			'SETTINGS': {'TARGETS': target_list}
		}
		request_id = conn.send(request)

		if callback_func:
			register_callback(request_id, callback_func)
			return True
		else:
			return True


def remove_targets(targets, interface_name, callback_func=None):
	app = App.get_running_app()
	conn = app.Bluetooth_connection
	print(f"[remove_targets]Removing: {targets} for interface {interface_name}")

	register_callback = app.register_request
	try:
		interface = app.interfaces[interface_name]
	except KeyError:
		return False
	intermediate_list = []
	for t in targets:
		intermediate_list.append(list(t))
		intermediate_list.append([t[0].lower(), t[1]])

	target_list = interface['TARGETS']
	print(f"got target_list: {target_list}")
	for t in intermediate_list:
		print(f"[remove_targets]Looking for {t} in {target_list}")
		if t in target_list:
			print(f"Found {t} in target list!")
			target_list.remove(t)

		print(f"target_list is now: {target_list}")

	request = {
		'ACTION': 'UPDATE_SETTINGS',
		'ARGS': {'interface_name': interface_name},
		'SETTINGS': {'TARGETS': target_list}
	}
	request_id = conn.send(request)

	if callback_func:
		register_callback(request_id, callback_func)
		return True
	else:
		return True





def random_macs(num):
	i = 0
	l = []
	while i <= num:
		m = "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
		n = str(random.randint(1, 65536))
		l.append((m, n))
		i += 1

	return l

