from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.popup import Popup

import queue
from helper_functions import remove_targets

# We need these to be able to refer to them in the .kv file
from widgets import AddTarget
from widgets import StartInterface
from widgets import TargetList, Target
from widgets import BTPickerPopup

if platform == 'android':
    from jnius import autoclass
    from plyer import notification
    from bt_client import Bluetooth_connection
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    autoclass('org.jnius.NativeInvocationHandler')



class MainInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(MainInterface, self).__init__(**kwargs)



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
        self.connected_device = None


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
                #print(f"[clock_callback]Got type 'HIT' {msg}")
                body = msg['BODY']
                addrs = [m.upper() for m in body['mac']]

                for addr in addrs:
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
                Clock.schedule_interval(self.clock_callback, 1.0)
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
