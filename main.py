from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock
import queue
import threading
import time

# We need these to be able to refer to them in the .kv file
from widgets import AddTarget
from widgets import StartInterface
from widgets import TargetList, Target
from widgets import BTPickerPopup
from widgets import FocusTarget

if platform == 'android':
    from jnius import autoclass
    from bt_client import Bluetooth_connection
    from plyer import notification
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    autoclass('org.jnius.NativeInvocationHandler')


class MainInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(MainInterface, self).__init__(**kwargs)


class MyApp(App):
    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.thread_queue = queue.Queue()
        self.bt_queue = queue.Queue()
        self.connected = False
        self.Bluetooth_connection = None
        self.paired_devices = dict()
        self.connect_status = f"Connected: {self.connected}"
        self.outstanding_requests = dict()
        self.starter_functions = dict()
        self.interfaces = dict()
        self.connected_device = None
        self.focus_target = ''
        self.fetcher = None

        if platform == 'android':
            print("Running on android!")
            self.paired_devices = {d.getName(): d for d in
                                   BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()}

        print(self.paired_devices)
        for d in self.paired_devices:
            print("Paired Device: {}".format(d))

    def event_fetcher(self):
        while self.connected:
            app = App.get_running_app()
            target_list = app.root.ids['middle_window'].ids['TARGET_LIST']

            while not self.thread_queue.empty():
                msg = self.thread_queue.get(timeout=0.2)
                if msg.get('TYPE') == 'HIT':
                    body = msg['BODY']
                    addrs = [m.upper() for m in body['mac']]

                    for addr in addrs:
                        if addr in target_list.targets:
                            target = target_list.targets[addr]
                            last_notify = target.last_notify
                            msg['ADDR'] = addr

                            if time.time() - last_notify > 60:
                                message = f"{target.name_label.text} RSSI: {body['rssi']} CHANNEL {body['channel']}"
                                notification.notify(title=f'{target.name_label.text} UPDATED', message=message)
                                target.last_notify = time.time()

                self.bt_queue.put(msg)

            time.sleep(1.0)

    def clock_callback(self, dt):
        app = App.get_running_app()
        target_list = app.root.ids['middle_window'].ids['TARGET_LIST']
        focus_target = app.root.ids['middle_window'].ids['FOCUS_TARGET']

        while not self.bt_queue.empty():
            msg = self.bt_queue.get(timeout=0.2)

            if msg.get('TYPE') == 'HIT':
                body = msg['BODY']
                addr = msg['ADDR']

                target_list.targets[addr].dispatch_on_hit(body)

                if addr == self.focus_target:
                    focus_target.on_hit(body)

            elif msg.get('TYPE') == 'RESPONSE':
                req_id = msg['ACK']

                requester = self.outstanding_requests.get(req_id)
                if requester:
                    print(f"[clock_callback]Got a response for id {req_id}: {msg}")
                    requester(msg['BODY'])

            elif msg.get('TYPE') == 'STATUS':
                print(f"[clock_status]Got STATUS {msg}")

        return True

    def build(self):
        return MainInterface()

    def connect_bluetooth(self, name):
        for i in self.root.ids:
            print("{} ::: {}".format(i, self.root.ids[i]))
        if platform == 'android':
            self.Bluetooth_connection = Bluetooth_connection(name, out_queue=self.thread_queue)

            if self.Bluetooth_connection.connect():
                self.connected = self.Bluetooth_connection.connected
                self.connect_status.format(self.connected)
                self.app.root.ids['status_connected'].text = f"Connected: {self.connected}"
                self.app.root.ids['ADD_TARGET'].disabled = False
                self.app.root.ids['INTERFACES'].disabled = False
                Clock.schedule_interval(self.clock_callback, 1.0)
                self.fetcher = threading.Thread(target=self.event_fetcher)
                self.fetcher.start()
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
