from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
import queue
from helper_functions import starter_function_generator
from helper_functions import validate_mac

if platform == 'android':
    from jnius import autoclass
    from bt_client import Bluetooth_connection
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')


class start_interface(Popup):
    def __init__(self, **kwargs):
        super(start_interface, self).__init__(**kwargs)
        self.size_hint = 1, None
        self.height = "240dp"
        self.title = 'START INTERFACE'
        self.interface_list = BoxLayout(orientation='vertical')
        self.add_widget(self.interface_list)
        self.placeholder = Label(text='GETTING INTERFACES....')
        self.interface_list.add_widget(self.placeholder)
        app = App.get_running_app()
        conn = app.Bluetooth_connection
        self.dismiss_button = Button(text='CLOSE')
        self.dismiss_button.bind(on_release=self.dismiss)
        self.interface_list.add_widget(self.dismiss_button)

        command = {
            'ACTION': 'GET_DOT11_INTERFACES'
        }
        request_id = conn.send(msg=command)
        app.register_request(request_id, self.gen_starter_functions)

    def gen_starter_functions(self, *args, **kwargs):
        app = App.get_running_app()
        print(f"gen_starter_functions got args: {args}")
        interfaces = args[0]

        self.interface_list.remove_widget(self.placeholder)

        for i in interfaces:
            print(f"Generating starter function for {i}")
            running = False
            STATE = interfaces[i]['STATE']
            if STATE == 'RUNNING':
                running = True
                app.interfaces[i] = interfaces[i]['SETTINGS']
                print(f"[{__name__}]app.interfaces[{i}]: {app.interfaces[i]}")

            widget = Interface_list_entry(i, starter_function_generator(i, self), running)
            self.interface_list.add_widget(widget)


class Interface_list_entry(GridLayout):
    def __init__(self, name, starter_function, running, **kwargs):
        super(Interface_list_entry, self).__init__(**kwargs)
        self.rows = 1
        self.cols = 2

        self.name = Label(text=name)
        self.switch = Switch()
        self.switch.active = running
        self.switch.bind(active=starter_function)

        self.add_widget(self.name)
        self.add_widget(self.switch)


class MainInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(MainInterface, self).__init__(**kwargs)


class add_target(Popup):
    def __init__(self, *args, **kwargs):
        super(add_target, self).__init__(**kwargs)
        self.size_hint = 1, None
        self.title = 'Add target'
        self.height = "250dp"

        self.main_body = BoxLayout(orientation='vertical')
        self.name_entry = TextInput(hint_text='name', multiline=False)
        self.mac_entry = TextInput(hint_text='MAC Address', multiline=False)
        self.mac_entry.bind(on_text_validate=self.validate_mac)
        self.dismiss_button = Button(text='Close')

        self.buttons = GridLayout(rows=1, cols=2)
        self.dismiss_button.bind(on_release=self.dismiss)
        self.add_button = Button(text='Add target')
        self.add_button.bind(on_release=self.add)
        self.add_button.disabled = True
        self.error_message = Label(text='', color=(1, 0, 0, 0))

        self.buttons.add_widget(self.dismiss_button)
        self.buttons.add_widget(self.add_button)

        self.main_body.add_widget(self.name_entry)
        self.main_body.add_widget(self.mac_entry)
        self.main_body.add_widget(self.error_message)
        self.main_body.add_widget(self.buttons)

        self.add_widget(self.main_body)
        self.app = App.get_running_app()
        self.target_list = self.app.root.ids['middle_window'].ids['TARGET_LIST']


    def validate_mac(self, *args, **kwargs):
        print(f"[{__name__}]validate_mack called:")
        if not validate_mac(self.mac_entry.text):
            print(f"[{__name__}]{self.mac_entry.text} is not a valid mac")
            self.error_message.color = (1, 0, 0, 1)
            self.error_message.text = 'BAD MAC'
            #self.add_button.disabled = True
        else:
            print(f"[{__name__}]{self.mac_entry.text} is a valid mac")
            self.add_button.disabled = False
            self.error_message.color = (1, 0, 0, 0)
            self.error_message.text = ''

    def add(self, *args, **kwargs):
        app = App.get_running_app()
        conn = app.Bluetooth_connection

        if not app.interfaces:
            self.error_message.color = (1, 0, 0, 1)
            self.error_message.text = 'NO STARTED INTERFACES'
        else:
            for key in app.interfaces:
                interface = app.interfaces[key]
                interface['TARGETS'].append(self.mac_entry.text)
                self.target_list.add_target((self.mac_entry.text, self.name_entry.text))

                request = {
                    'ACTION': 'UPDATE_SETTINGS',
                    'ARGS': {'interface_name': key},
                    'SETTINGS': {'TARGETS': interface['TARGETS']}
                }
                request_id = conn.send(request)
                app.register_request(request_id, self.add_target_callback)

    def add_target_callback(self, *args, **kwargs):
        print(f"[add_target_callback]Got args {args} and kwargs {kwargs}")



class TargetView(ScrollView):
    def __init__(self, **kwargs):
        super(TargetView, self).__init__(**kwargs)
        pass


class Target(GridLayout, Widget):
    def __init__(self, name=None, MAC=None, **kwargs):
        super(Target, self).__init__(**kwargs)
        self.cols = 3
        self.rows = 1
        self.ids['name'].text = name
        self.ids['mac'].text = MAC
        self.spacing = 3
        self.name = name
        self.MAC = MAC
        self.info_rssi = self.ids['info_rssi']
        self.info_channel = self.ids['info_channel']
        self.info_bssid = self.ids['info_bssid']

        self.register_event_type('on_hit')

    def dispatch_on_hit(self, *args, **kwargs):
        self.dispatch('on_hit', *args, **kwargs)

    def on_hit(self, *args, **kwargs):
        hit = args[0]

        self.info_rssi.text = f"RSSI: {hit['rssi']}"
        self.info_channel.text = f"CHANNEL: {hit['channel']}"
        self.info_bssid.text = f"BSSID: {hit['bssid']}"

        return True


class TargetList(GridLayout):
    def __init__(self, targets=None, **kwargs):
        super(TargetList, self).__init__(**kwargs)
        #self.orientation = 'vertical'

        if targets:
            self.rows = len(targets)
        else:
            self.rows: 1
        self.cols = 1
        self.targets = dict()
        self.size_hint = (1, None)
        if targets:
            for t in targets:
                t_name = t[0]
                t_mac = t[1]
                self.targets[t_mac] = Target(name=t_name, MAC=t_mac)

        print("TARGET LIST: {}".format(self.targets))

    def add_target(self, target, *args):
        print(f"[TargetList][add_target]Got args: {args} and target {target}")
        t_mac = target[0].upper()
        t_name = target[1]
        if t_mac not in self.targets:
            self.targets[t_mac] = Target(name=t_name, MAC=t_mac)
            self.add_widget(self.targets[t_mac])


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
                b = Button(text=d, size_hint=(1, None), height="{}dp".format(self.button_height))
                b.bind(on_press=self.connect_to_device)
                self.paired_devices.append(b)

        self.height = "{}dp".format((len(self.paired_devices)*self.button_height))
        print("self.height: {}".format(self.height))
        if self.paired_devices:
            for d in self.paired_devices:
                self.add_widget(d)

    def connect_to_device(self, widget):
        device = self.app.paired_devices[widget.text]
        self.app.connect_bluetooth(device)
        self.parent_widget.dismiss()


class MyApp(App):
    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.bt_queue = queue.Queue()
        self.connected = False
        self.Bluetooth_connection = None
        self.paired_devices = dict()
        self.connect_status = f"Connected: {self.connected}"
        self.outstanding_requests = dict()
        self.starter_functions = dict()
        self.interfaces = dict()


        if platform == 'android':
            print("Running on android!")
            self.paired_devices = {d.getName(): d for d in
                                   BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()}

        print(self.paired_devices)
        for d in self.paired_devices:
            print("Paired Device: {}".format(d))

    def clock_callback(self, dt):
        app = App.get_running_app()
        target_list = app.root.ids['middle_window'].ids['TARGET_LIST']

        while not self.bt_queue.empty():
            msg = self.bt_queue.get(timeout=0.2)

            if msg.get('TYPE') == 'HIT':
                print(f"[clock_callback]Got type 'HIT' {msg}")
                body = msg['BODY']
                addrs = [m.upper() for m in body['mac']]

                for addr in addrs:
                    print(f"[clock_callback]Checking if {addr} is in targetlist")
                    if addr in target_list.targets:
                        target_list.targets[addr].dispatch_on_hit(body)
            elif msg.get('TYPE') == 'RESPONSE':
                req_id = msg['ACK']

                requester = self.outstanding_requests.get(req_id)
                if requester:
                    print(f"[clock_callback]Got a response for id {req_id}: {msg}")
                    requester(msg['BODY'])

        return True

    def build(self):
        return MainInterface()

    def connect_bluetooth(self, name):
        for i in self.root.ids:
            print("{} ::: {}".format(i, self.root.ids[i]))
        if platform == 'android':
            self.Bluetooth_connection = Bluetooth_connection(name, out_queue=self.bt_queue)

            if self.Bluetooth_connection.connect():
                self.connected = self.Bluetooth_connection.connected
                self.connect_status.format(self.connected)
                self.app.root.ids['status_connected'].text = f"Connected: {self.connected}"
                self.app.root.ids['ADD_TARGET'].disabled = False
                self.app.root.ids['INTERFACES'].disabled = False
                Clock.schedule_interval(self.clock_callback, 5.0)
            else:
                print("Couldn't connect to {}".format(name))

        else:
            print("Can't connect to BT when not on android.")
            print("Wold have connected to: {}".format(name))

            return False

    def register_request(self, request_id, callback):
        self.outstanding_requests[request_id] = callback


if __name__ == '__main__':
    MyApp().run()
