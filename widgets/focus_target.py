import kivy.uix.gridlayout
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
import random
from channel_lookup_table import channel_lookup_table



class FocusTarget(BoxLayout):
	def __init__(self, **kwargs):
		super(FocusTarget, self).__init__(**kwargs)
		self.orientation = 'vertical'
		self.info_container = BoxLayout(orientation='vertical', size_hint=(1, .20))
		self.name_label = Label(text='---', font_size="18sp")
		self.mac_label = Label(text='de:ad:be:ef:13:37', font_size="18sp")
		self.info_container.add_widget(self.name_label)
		self.info_container.add_widget(self.mac_label)
		self.add_widget(self.info_container)

		self.RSSI_display = BoxLayout(orientation='horizontal', size_hint=(1, .40))
		self.RSSI_number = Label(text='--', font_size='75sp')
		self.RSSI_direction_indicator = Image(source='images/dash.png')

		self.RSSI_display.add_widget(self.RSSI_number)
		self.RSSI_display.add_widget(self.RSSI_direction_indicator)

		self.add_widget(self.RSSI_display)
		self.locked = 'UNLOCKED'
		self.channel_list_container = BoxLayout(orientation='vertical', size_hint=(1, .30), pos_hint={'center_x': .5})
		self.channel_header = Label(text=f'CHANNELS :: {self.locked}', font_size="18sp")
		self.channel_list_container.add_widget(self.channel_header)
		self.channel_list = GridLayout(orientation='tb-lr', spacing="5dp", cols=2, rows=5)
		self.channel_list_container.add_widget(self.channel_list)

		self.seen_channels = dict()
		self.channel_entries = dict()

		self.add_widget(self.channel_list_container)

		self.channel_control_buttons = BoxLayout(orientation='horizontal', size_hint=(1, .10))
		self.lock_button = Button(text='LOCK')
		self.lock_button.bind(on_release=self.lock_channels)
		self.unlock_button = Button(text='UNLOCK')
		self.unlock_button.bind(on_release=self.unlock_channels)

		self.channel_control_buttons.add_widget(self.lock_button)
		self.channel_control_buttons.add_widget(self.unlock_button)
		self.add_widget(self.channel_control_buttons)

		self.old_channels = None

	def set_target(self, name=None, MAC=None):
		self.name_label.text = name
		self.mac_label.text = MAC

		for ch in self.channel_entries:
			widget = self.channel_entries[ch]
			self.channel_list.remove_widget(widget)

		self.seen_channels = dict()
		self.channel_entries = dict()

		self.RSSI_direction_indicator.source = 'images/dash.png'
		self.RSSI_number.text = '--'


	def on_hit(self, hit, *args, **kwargs):
		# {'channel': 2452, 'rssi': -22, 'bssid': 'b0xnet', 'mac': ['30:23:03:dc:16:e1'], 'fcs': 3774233433}
		try:
			curr_rssi = int(self.RSSI_number.text)
		except ValueError:
			curr_rssi = 0

		new_rssi = hit['rssi']

		self.RSSI_number.text = str(new_rssi)
		if new_rssi - curr_rssi > 0:
			self.RSSI_direction_indicator.source = 'images/arrow_up.png'
		elif new_rssi - curr_rssi < 0:
			self.RSSI_direction_indicator.source = 'images/arrow_down.png'
		else:
			pass


		try:
			ch = channel_lookup_table[hit['channel']]
		except KeyError as e:
			print(f"[FocusTarget]Unknown channel: {e}")
			ch = None

		if ch in self.seen_channels:
			self.seen_channels[ch] += 1
			self.channel_entries[ch].text = f"{ch}    :::    {self.seen_channels[ch]}"
		else:
			self.seen_channels[ch] = 1
			self.channel_entries[ch] = Label(text=f"{ch}    :::    {self.seen_channels[ch]}")
			if len(self.channel_entries) > 5 and self.channel_list.cols <= 3:
				self.channel_list.cols += 1

			try:
				self.channel_list.add_widget(self.channel_entries[ch])
			except kivy.uix.gridlayout.GridLayoutException as e:
				print(f"[focus_target][on_hit]Hit exception {e}")

	def lock_channels(self, *args, **kwargs):
		app = App.get_running_app()
		interfaces = app.interfaces
		conn = app.Bluetooth_connection

		lock_channels = list(self.seen_channels.keys())
		for interface_name in interfaces:
			self.old_channels = interfaces[interface_name]['CHANNELS']
			request = {
				'ACTION': 'UPDATE_SETTINGS',
				'ARGS': {'interface_name': interface_name},
				'SETTINGS': {'CHANNELS': lock_channels}
			}

			def callback(*args, **kwargs):
				self.locked = 'LOCKED'
				self.channel_header.text = f'CHANNELS :: {self.locked}'

			req_id = conn.send(request)
			app.register_request(req_id, callback)


	def unlock_channels(self, *args, **kwargs):
		app = App.get_running_app()
		interfaces = app.interfaces
		conn = app.Bluetooth_connection

		for interface_name in interfaces:
			request = {
				'ACTION': 'UPDATE_SETTINGS',
				'ARGS': {'interface_name': interface_name},
				'SETTINGS': {'CHANNELS': self.old_channels}
			}

			def callback(*args, **kwargs):
				self.locked = 'UNLOCKED'
				self.channel_header.text = f'CHANNELS :: {self.locked}'

			req_id = conn.send(request)
			app.register_request(req_id, callback)











