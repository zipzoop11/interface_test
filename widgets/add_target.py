from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from helper_functions import validate_mac, add_targets


class AddTarget(Popup):
    def __init__(self, *args, **kwargs):
        super(AddTarget, self).__init__(**kwargs)
        self.size_hint = 1, None
        self.title = 'Add target'
        self.height = "250dp"

        self.main_body = BoxLayout(orientation='vertical')
        self.name_entry = TextInput(hint_text='name', multiline=False)
        self.mac_entry = TextInput(hint_text='MAC Address', multiline=False)
        self.dismiss_button = Button(text='Close')

        self.buttons = GridLayout(rows=1, cols=2)
        self.dismiss_button.bind(on_release=self.dismiss)
        self.add_button = Button(text='Add target')
        self.add_button.bind(on_release=self.add)
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

    def add(self, *args, **kwargs):
        print("ADD CALLED!")
        app = App.get_running_app()
        conn = app.Bluetooth_connection

        if not app.interfaces:
            print("GOT NO INTERFACES")
            self.error_message.color = (1, 0, 0, 1)
            self.error_message.text = 'NO STARTED INTERFACES'
        else:
            if validate_mac(self.mac_entry.text):
                print("VALID MAC!")
                self.error_message.color = (1, 0, 0, 0)
                self.error_message.text = ''
                for key in app.interfaces:
                    entry = (self.mac_entry.text, self.name_entry.text)
                    add_targets([entry], key, callback_func=self.add_target_callback)
            else:
                print("INVALID MAC")
                self.error_message.color = (1, 0, 0, 1)
                self.error_message.text = 'BAD MAC'

    def add_target_callback(self, *args, **kwargs):
        self.error_message.color = (0, 1, 0, 1)
        self.error_message.text = 'ADDED!'
        self.target_list.add_target_to_list((self.mac_entry.text, self.name_entry.text))