from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
import random


class FocusTarget(BoxLayout):
	def __init__(self, **kwargs):
		super(FocusTarget, self).__init__(**kwargs)
		self.orientation = 'vertical'

		self.name_label = Label(text='NAME', size_hint=(1, .10), font_size="25sp")
		self.add_widget(self.name_label)

		self.RSSI_display = BoxLayout(orientation='horizontal', size_hint=(1, .60))
		self.RSSI_number = Label(text='-25', font_size='75sp')
		self.RSSI_direction_indicator = Label(text='UP')

		self.RSSI_display.add_widget(self.RSSI_number)
		self.RSSI_display.add_widget(self.RSSI_direction_indicator)
		self.add_widget(self.RSSI_display)

		self.channel_list = StackLayout(orientation='tb-lr', size_hint=(.5, .20), spacing="5dp", pos_hint={'center_x': .5})
		i = 0
		for x in range(2450, 2455):
			print(x)
			lbl = Button(text=str(x), size_hint=(None, None), width="45dp", height="45dp")
			self.channel_list.add_widget(lbl)
			i += 1

		self.add_widget(self.channel_list)

		self.channel_control_buttons = BoxLayout(orientation='horizontal', size_hint=(1, .10))
		self.lock_button = Button(text='LOCK')
		self.unlock_button = Button(text='UNLOCK')

		self.channel_control_buttons.add_widget(self.lock_button)
		self.channel_control_buttons.add_widget(self.unlock_button)
		self.add_widget(self.channel_control_buttons)