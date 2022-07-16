from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
import time
from helper_functions import remove_targets

from kivy.utils import platform

if platform == 'android':
    from plyer import notification


class Target(BoxLayout, Widget):
    def __init__(self, name=None, MAC=None, **kwargs):
        super(Target, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.orientation = 'vertical'
        self.tgt = GridLayout(cols=3, rows=1)
        self.cols = 3
        self.rows = 2

        self.name = name
        self.MAC = MAC
        self.seen_on_channels = set()

        self.last_notify = 0
        self.target_list = self.app.root.ids['middle_window'].ids['TARGET_LIST']
        self.focus_target = self.app.root.ids['middle_window'].ids['FOCUS_TARGET']
        self.remove_func = self.target_list.remove_target_from_list

        self.ident = GridLayout(cols=1, rows=2)
        self.name_label = Label(text=name)
        self.MAC_label = Label(text=MAC)
        self.ident.add_widget(self.name_label)
        self.ident.add_widget(self.MAC_label)
        self.tgt.add_widget(self.ident)

        self.info = GridLayout(cols=1, rows=3)
        self.rssi = Label(text='RSSI: -')
        self.channel = Label(text='Ch: -')
        self.BSSID = Label(text='BSSID: -')
        self.info.add_widget(self.rssi)
        self.info.add_widget(self.channel)
        self.info.add_widget(self.BSSID)
        self.tgt.add_widget(self.info)

        self.control_buttons = GridLayout(cols=1, rows=2)
        self.remove_btn = Button(text='X')
        self.remove_btn.id = self.MAC_label.text
        self.remove_btn.bind(on_release=self.remove_func)

        self.focus_btn = Button(text='FOCUS')
        self.control_buttons.add_widget(self.remove_btn)

        self.control_buttons.add_widget(self.focus_btn)
        self.tgt.add_widget(self.control_buttons)

        self.add_widget(self.tgt)
        self.register_event_type('on_hit')

        def set_focus(*args, **kwargs):
            self.focus_target.set_target(name=self.name, MAC=self.MAC)
            self.app.focus_target = self.MAC

        self.focus_btn.bind(on_release=set_focus)

    def dispatch_on_hit(self, *args, **kwargs):
        self.dispatch('on_hit', *args, **kwargs)

    def on_hit(self, *args, **kwargs):
        hit = args[0]

        self.rssi.text = f"RSSI: {hit['rssi']}"
        self.channel.text = f"CHANNEL: {hit['channel']}"
        self.BSSID.text = f"BSSID: {hit['bssid']}"
        self.seen_on_channels.add(int(hit['channel']))

        return True


class TargetList(ScrollView):
    def __init__(self, targets=None, **kwargs):
        super(TargetList, self).__init__(**kwargs)
        self.scroll_list = GridLayout(size_hint=(1, None))
        self.size_hint = 1, None
        if targets:
            self.scroll_list.rows = len(targets)
        else:
            self.scroll_list.rows = 1
        self.scroll_list.cols = 1
        self.targets = dict()
        self.size_hint = (1, None)
        if targets:
            for t in targets:
                t_name = t[0]
                t_mac = t[1]
                self.targets[t_mac] = Target(name=t_name, MAC=t_mac)

        #print("TARGET LIST: {}".format(self.targets))

        self.add_widget(self.scroll_list)

    def add_target_to_list(self, target, *args):
        t_mac = target[0].upper()
        t_name = target[1]
        if t_mac not in self.targets:
            self.targets[t_mac] = Target(name=t_name, MAC=t_mac)
            self.scroll_list.rows += 1
            self.scroll_list.height += self.targets[t_mac].height
            self.scroll_list.add_widget(self.targets[t_mac])

    def remove_target_from_list(self, *args):
        app = App.get_running_app()
        print(f"[remove_target_from_list]args {args}")
        caller = args[0]
        try:
            t = self.targets[caller.id]
        except KeyError:
            return False
        if t:
            t_mac = t.MAC
            t_name = t.name

            def callback(*args, **kwargs):
                self.scroll_list.height -= t.height
                self.scroll_list.rows -= 1
                self.scroll_list.remove_widget(t)
                self.targets.pop(t_mac)
            for i in app.interfaces:
                remove_targets([(t_mac, t_name)], i, callback_func=callback)