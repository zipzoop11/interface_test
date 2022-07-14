from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton


class BTPickerPopup(Popup):
    def __init__(self, **kwargs):
        super(BTPickerPopup, self).__init__(**kwargs)
        self.auto_dismiss = False
        self.size_hint = 1, None
        self.title = "Connect to Bluetooth"

        self.device_picker = Bluetooth_device_picker(self)
        self.add_widget(self.device_picker)


class Bluetooth_device_picker(GridLayout):
    def __init__(self, parent, **kwargs):
        super(Bluetooth_device_picker, self).__init__(**kwargs)
        self.cols = 1
        self.parent_widget = parent
        self.size_hint = 1, None
        self.app = App.get_running_app()
        self.paired_devices = []
        self.button_height = 65

        if self.app.paired_devices:
            for d in self.app.paired_devices:
                b = ToggleButton(text=d, size_hint=(1, None), height="{}dp".format(self.button_height))
                if d == self.app.connected_device:
                    b.state = 'down'
                b.bind(on_press=self.connect_to_device)
                self.paired_devices.append(b)

        self.height = "{}dp".format((len(self.paired_devices)*self.button_height))

        if self.paired_devices:
            for d in self.paired_devices:
                self.add_widget(d)

    def connect_to_device(self, widget):
        app = App.get_running_app()
        if widget.state == 'normal':
            app.Bluetooth_connection.disconnect()
            app.connected_device = ''
            app.connected = False
            app.root.ids['status_connected'].text = f"Connected: {app.connected}"
        else:
            device = self.app.paired_devices[widget.text]
            self.app.connect_bluetooth(device)
            app.connected_device = widget.text
        self.parent_widget.dismiss()
