from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch

from helper_functions import starter_function_generator


class StartInterface(Popup):
    def __init__(self, **kwargs):
        super(StartInterface, self).__init__(**kwargs)
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
        target_list = app.root.ids['middle_window'].ids['TARGET_LIST']
        add_target_to_list = target_list.add_target_to_list

        for i in interfaces:
            print(f"Generating starter function for {i}")
            running = False
            STATE = interfaces[i]['STATE']
            if STATE == 'RUNNING':
                running = True
                app.interfaces[i] = interfaces[i]['SETTINGS']
                targets = interfaces[i]['SETTINGS']['TARGETS']

                if targets:
                    for t in targets:
                        add_target_to_list((t[0], t[1]))

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
