from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class StatusBar(GridLayout):
	def __init__(self, **kwargs):
		super(StatusBar, self).__init__(**kwargs)
		self.rows = 1
		self.cols = 2
		self.size_hint = 1, None
		self.height = "60dp"

		self.metrics_container = BoxLayout(orientation='vertical')
		self.metric_pps = Label(text='- pps', font_size="12sp")
		self.metric_hps = Label(text='- hps', font_size="12sp")
		self.metric_temp = Label(text='temp - °C', font_size="12sp")

		self.metrics_container.add_widget(self.metric_pps)
		self.metrics_container.add_widget(self.metric_hps)
		self.metrics_container.add_widget(self.metric_temp)
		self.add_widget(self.metrics_container)

		self.interface_container = BoxLayout(orientation='vertical')
		self.interfaces = dict()
		self.add_widget(self.interface_container)

	def update_interface(self, *args, name=None, status=None, **kwargs):
		print(f"[StatusBar]Got name: {name} :: Got Status {status}")

		if name in self.interfaces:
			self.interfaces[name].text = f'{name}: {status}'
		else:
			self.interfaces[name] = Label(text=f'{name}: {status}', font_size='12sp')
			self.interface_container.add_widget(self.interfaces[name])

	def update_metrics(self, metrics, *args, **kwargs):
		# {'pps': 18.7, 'hps': 0.0, 'temp': '35.0', 'iface': 'wlan1'}

		self.metric_pps.text = f"{metrics['pps']}  pps"
		self.metric_hps.text = f"{metrics['hps']}  hps"
		self.metric_temp.text = f"{metrics['temp']}  °C"

