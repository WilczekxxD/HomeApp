from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import PopupException
from kivy.factory import Factory
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.dropdown import DropDown
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.uix.textinput import TextInput

import kivy
from user_handler import *
import socket
import threading
import os
import socket

# TODO center chat and popup if not centered in a new version after merger

# socket info

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.43.105"
ADDR = (SERVER, PORT)
# connecting socket
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDR)

# file info
local_dir = os.path.join(os.getcwd(), "local.txt")
shopping = os.path.join(os.getcwd(), "shopping_list.txt")

class CreateHomeWindow(Screen):

    def create(self):
        self.success.text = "pending"
        local_f = open(local_dir, "r")
        email = local_f.readlines()[0][6:-1]
        local_f.close()
        pas = self.pas.text
        name = self.hname.text
        print(email, pas, name)
        if len(pas) != 0 and len(name) != 0 and len(pas) != 0:
            ans = "success"
            if ans == "success":
                self.success.text = "success"
            else:
                self.success.text = ans
        else:
            self.success.text = "do not leave blank spaces"

    def on_enter(self, *args):
        self.success.text = ""
        self.pas.text = ""
        self.hname.text = ""


class ShoppingWindow(Screen):
    class DeleteProductButton(Button):
        Pname = StringProperty(defaultvalue="")

    class QuantityButton(Button):
        quantity = NumericProperty(defaultvalue=0)
        index = NumericProperty(defaultvalue=0)
        shopping_list = StringProperty(defaultvalue="")

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        # local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        current = lines[3][8:-1]

        # making layout for the scroller, 4 columns for name, quantity,measure, deleating
        self.list_viewer.clear_widgets()
        self.width = Window.size[0]
        # print(self.list_viewer.__getattribute__("size_hint_x"), self.width)
        scroll_layout = GridLayout(cols=3, spacing=40, size_hint_y=None, padding=[0, 5, 0, 5],
                                   size_hint_x=self.list_viewer.__getattribute__("size_hint_x"))
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        if current != "0":
            local_f = open(shopping, "r")
            lines = local_f.readlines()[0]
            shopping_list = lines.split(";")
            if len(shopping_list) == 1:
                shopping_list = 1
            else:
                shopping_list = shopping_list[:-1]
        else:
            shopping_list = 0

        if shopping_list != 0 and shopping_list != 1:
            for index, product in enumerate(shopping_list):
                WholeProduct = product
                product = product.split(":")
                name = product[0]
                quantity = product[1]
                measure = product[2]


                # product name label
                # col 1

                label = Label(text=f'{name}',
                              text_size=(self.width / 3, None),
                              halign="center")
                scroll_layout.add_widget(label)
                # quantity inside a separate float layout becouse thats the way to put more than one widget in one box
                # col2

                quantity_layout = FloatLayout()
                label = Label(text=f'[ref=quantity]{quantity}[/ref] {measure}',
                              markup=True,
                              pos_hint={'x': 0.05, 'y': 0.025},
                              size_hint=(0.5, 0.95)
                              )

                up_button = self.QuantityButton(text='+',
                                                pos_hint={'x': 0.575, 'y': 0.05},
                                                size_hint=(0.25, 0.9),
                                                quantity=quantity,
                                                index=index,
                                                shopping_list=";".join(shopping_list))

                down_button = self.QuantityButton(text='-',
                                                  pos_hint={'x': 0.825, 'y': 0.05},
                                                  size_hint=(0.25, 0.9),
                                                  quantity=quantity,
                                                  index=index,
                                                  shopping_list=";".join(shopping_list))

                quantity_layout.add_widget(label)
                quantity_layout.add_widget(up_button)
                quantity_layout.add_widget(down_button)

                scroll_layout.add_widget(quantity_layout)

                # delete item from the list
                # col 4

                button = self.DeleteProductButton(text="X", size_hint=(None, None))
                button.__setattr__("Pname", WholeProduct)
                scroll_layout.add_widget(button)

        self.list_viewer.add_widget(scroll_layout)

    # def edit_quantity(self, instance):

class FinalListWindow(Screen):
    class DeleteProductButton(Button):
        Pindex = NumericProperty(defaultvalue=0)

    class QuantityButton(Button):
        quantity = NumericProperty(defaultvalue=0)
        index = NumericProperty(defaultvalue=0)

    class InfoButton(Button):
        Pindex = NumericProperty(defaultvalue=0)

    def on_enter(self, *args):
        self.refresh()

    def refresh(self):
        # only name price and measure!!!
        # The whole converted list is managed locally no to convert it multiple times

        # local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]

        # making layout for the scroller, one column and inside 1 column for name
        # and below 4 for price, measure, deleting, info
        self.list_viewer.clear_widgets()
        self.width = Window.size[0]

        # print(self.list_viewer.__getattribute__("size_hint_x"), self.width)
        scroll_layout = GridLayout(cols=1, spacing=40, size_hint_y=None, padding=[0, 10, 0, 5],
                                   size_hint_x=self.list_viewer.__getattribute__("size_hint_x"))
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # getting the converted list from local file
        if current != "0":
            converted_list_path = os.path.join(os.getcwd(), "final_list.txt")
            converted_list_file = open(converted_list_path, "r")
            converted_list = converted_list_file.readlines()
            converted_list_file.close()

            if len(converted_list) == 0:
                converted_list = 0
            else:
                converted_list = converted_list
        else:
            converted_list = 0

        if converted_list != 0 and converted_list != 1:
            for index, suggestions in enumerate(converted_list):
                suggestions = suggestions.split(";")
                best = suggestions[0].split(":")
                print(best)

                # product name label
                # col 0
                label = Label(text=f'{best[0]}',
                              text_size=(None, None),
                              halign="center",
                              )
                scroll_layout.add_widget(label)

                # under the name new layout for price, buttons and info
                feature_box = GridLayout(cols=4, spacing=40, size_hint_y=None, padding=[0, 5, 0, 5],
                                         size_hint_x=self.list_viewer.__getattribute__("size_hint_x"))
                # price

                # col 2
                label = Label(text=f'{best[1]}',
                              text_size=(self.width / 3, None),
                              halign="center")
                feature_box.add_widget(label)

                # quantity inside a separate float layout becouse thats the way to put more than one widget in one box
                # col3
                quantity_layout = FloatLayout()
                quantity = best[2]
                label = Label(text=f'[ref=quantity]{quantity}[/ref] szt.',
                              markup=True,
                              pos_hint={'x': 0.05, 'y': 0.025},
                              size_hint=(0.5, 0.95)
                              )

                up_button = self.QuantityButton(text='+',
                                                pos_hint={'x': 0.575, 'y': 0.05},
                                                size_hint=(0.25, 0.9),
                                                quantity=quantity,
                                                index=index)
                up_button.bind(on_release=self.increase_quantity)

                down_button = self.QuantityButton(text='-',
                                                  pos_hint={'x': 0.825, 'y': 0.05},
                                                  size_hint=(0.25, 0.9),
                                                  quantity=quantity,
                                                  index=index)
                down_button.bind(on_release=self.decrease_quantity)

                quantity_layout.add_widget(label)
                quantity_layout.add_widget(up_button)
                quantity_layout.add_widget(down_button)

                feature_box.add_widget(quantity_layout)

                # delete item from the list, locally
                # col 4

                button = self.DeleteProductButton(text="X", size_hint=(0.3, 0.2))
                button.__setattr__("Pindex", index)
                feature_box.add_widget(button)

                # info button
                # col 5
                button = self.InfoButton(text="i", size_hint=(0.3, 0.2))
                button.__setattr__("Pindex", index)
                feature_box.add_widget(button)

                # adding the feature space to the scroll layout
                scroll_layout.add_widget(feature_box)

        self.list_viewer.add_widget(scroll_layout)

    def delete_product(self, instance):
        # instead of deleting whole product class deletes only single suggestions
        index = instance.__getattribute__("Pindex")

        converted_list_path = os.path.join(os.getcwd(), "client", "final_list.txt")
        converted_list_file = open(converted_list_path, "r")
        converted_list = converted_list_file.readlines()

        suggestions = converted_list[index]
        suggestions = ";".join(suggestions.split(";")[1:])
        converted_list[index] = suggestions
        converted_list_file.close()

        # writing it down
        final_list_path = os.path.join(os.getcwd(), "client", "final_list.txt")
        final_list_file = open(final_list_path, "w")
        for product in converted_list:
            final_list_file.write(product)
        final_list_file.close()

        self.refresh()

    def increase_quantity(self, instance):
        # local final list
        converted_list_path = os.path.join(os.getcwd(), "final_list.txt")
        converted_list_file = open(converted_list_path, "r")
        converted_list = converted_list_file.readlines()
        converted_list_file.close()

        suggestions = converted_list[instance.index].split(";")
        product = suggestions[0]
        product = product.split(":")
        quantity = int(instance.quantity + 1)
        product[2] = str(quantity)
        product = ":".join(product)
        suggestions[0] = product
        suggestions = ";".join(suggestions)
        converted_list[instance.index] = suggestions

        # updating converted list locally
        final_list_path = os.path.join(os.getcwd(), "final_list.txt")
        print(final_list_path)
        final_list_file = open(final_list_path, "w")
        for product in converted_list:
            final_list_file.write(product)
        final_list_file.close()

        self.refresh()

    def decrease_quantity(self, instance):
        # local info
        if instance.quantity > 0:
            # local final list
            converted_list_path = os.path.join(os.getcwd(), "final_list.txt")
            converted_list_file = open(converted_list_path, "r")
            converted_list = converted_list_file.readlines()
            converted_list_file.close()

            suggestions = converted_list[instance.index].split(";")
            product = suggestions[0]
            product = product.split(":")
            quantity = int(instance.quantity - 1)
            product[2] = str(quantity)
            product = ":".join(product)
            suggestions[0] = product
            suggestions = ";".join(suggestions)
            converted_list[instance.index] = suggestions

            # updating converted list locally
            final_list_path = os.path.join(os.getcwd(), "final_list.txt")
            final_list_file = open(final_list_path, "w")
            for suggestions in converted_list:
                final_list_file.write(suggestions)
            final_list_file.close()
        self.refresh()


class ChatWindow(Screen):

    def on_enter(self):
        self.refresh()

    def send(self):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]
        email = lines[0][6:-1]
        local_f.close()

        self.msg.text = ""

        self.refresh()

    def refresh(self):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]
        email = lines[0][6:-1]
        local_f.close()

        self.chat_h.clear_widgets()

        if current != "0":
            local_f = open(local_dir, "r")
            lines = local_f.readlines()[0]
            local_f.close()
            chat = lines
            chat = chat.split(";")[:-1]
            view = FloatLayout(size_hint=(1, 1))
            print(chat)
            offsets = [0]
            padding = 10
            msg_list = []
            # always start in the new row
            if chat:
                for line in chat:
                    line = line.split(":")
                    author = line[0]
                    msg = line[1]
                    if author == email:

                        label = Label(text=(msg + "\n" + author),
                                      text_size=(self.chat_h.width / 2, None),
                                      halign="right", )
                        label.texture_update()
                        label.size = label.texture_size
                        noffset = offsets[-1] + label.height + padding
                        offsets.append(noffset)
                        msg_list.append([label, author])

                    else:

                        label = Label(text=(msg + "\n" + author),
                                      text_size=(self.chat_h.width / 2, None),
                                      halign="left", )
                        label.texture_update()
                        label.size = label.texture_size
                        noffset = offsets[-1] + label.height + padding
                        offsets.append(noffset)
                        msg_list.append([label, author])

                view.size = (self.chat_h.width, offsets[-1])
                view.size_hint = (None, None)
                view.pos = (0, 0)
                test = Button(pos=(0, 0), size_hint=(0.1, 0.1))
                test2 = Button(pos=(155, view.height), size_hint=(0.1, 0.1))
                for i, msg in enumerate(msg_list):
                    label = msg[0]
                    author = msg[1]
                    if author == email:
                        label.pos = (label.get_center_x(),
                                     view.height / 2 - offsets[i] - label.height / 2)
                    else:
                        label.pos = (0,
                                     view.height / 2 - offsets[i] - label.height / 2)
                    print(label.pos)
                    label.pos_hint = {}
                    view.add_widget(label)
                view.add_widget(test2)
                view.add_widget(test)
                self.chat_h.add_widget(view)
            else:
                self.chat_h.add_widget(Label(text="there are no messages"))
        else:
            self.chat_h.add_widget(Label(text="you are not in any home"))


class LogInWindow(Screen):

    def user_login(self):
        wm.current = "home"

    def on_pre_enter(self, *args):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        email, pas = "", ""
        for line in lines:
            if line[:6] == "email:":
                email = line[6:-1]
            if line[:5] == "pass:":
                pas = line[5:-1]

            if pas != "0" and email != "0":
                self.pas.text = pas
                self.email.text = email
                self.remember.active = True

        local_f.close()

    def on_leave(self, *args):
        local_f = open(local_dir, "r")
        lines = []
        past_email, past_pas = "", ""
        for line in local_f:
            if line[:6] == "email:":
                past_email = line[6:-1]
                line = "email:" + self.email.text + "\n"
            if line[:5] == "pass:":
                past_pas = line[5:-1]
                line = "pass:" + self.pas.text + "\n"
            if line[:9] == "remember:":
                if self.remember.active:
                    line = "remember:1\n"
                else:
                    line = "remember:0\n"
            if line[:8] == "current:":
                if past_email != self.email.text and past_pas != self.pas.text:
                    line = "current:0\n"
            lines.append(line)
        local_f.close()

        local_f = open(local_dir, "w")
        for line in lines:
            local_f.write(line)
        local_f.close()


class RegisterWindow(Screen):

    def register(self):
        self.success.text = "pending"
        if self.email.text != "" and self.pas1.text != "" and self.pas2.text != "":
            ans = "successfully registered"
            if ans == "successfully registered":
                self.success.text = "successfuly registered"
            else:
                self.success.text = "error"
        else:
            self.success.text = "fill blank spaces"


class InviteWindow(Screen):

    def on_enter(self):
        self.refresh()

    def refresh(self):
        # local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]

        # setting scroll view preview
        self.code_viewer.clear_widgets()
        scroll_layout = GridLayout(cols=1, spacing=40, size_hint_y=None, padding=[0, 5, 0, 5])
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # fetching code list to add to scroll view
        if current != "0":
            codes_l = ["you have no pending invitations for the home you are currently in"]
        else:
            codes_l = ["you currently are not in any home"]

        for code in codes_l:
            label = Label(text=code, size_hint_y=None, height=5)
            scroll_layout.add_widget(label)
        self.code_viewer.add_widget(scroll_layout)

    def redeem_code(self):
        self.feedback.text = "pending"
        if self.gcode.text != "" and self.ghomeIP.text != "":
            local_f = open(local_dir, "r")
            lines = local_f.readlines()
            email = lines[0][6:-1]
            ans = "1"
            if ans == "1":
                self.feedback.text = "success"
            else:
                self.feedback.text = ans
        else:
            self.feedback.text = "give homeIP and code"

    def generate_code(self):
        self.feedback.text = "pending"
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]
        local_f.close()
        if current != "0":
            pass
        else:
            self.feedback.text = "no house chosen"


class HomesWindow(Screen):
    pass


class ChooseHomeWindow(Screen):

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        email = lines[0][6:-1]
        current = lines[3][8:-1]
        local_f.close()
        if current != "0":
            self.current.text = f"your current home is {current}"
        else:
            self.current.text = "You currently aren't in any house"
        for child in self.children:
            for c in child.children:
                print(c.text)

        homes = ""
        # fix for situation when no homes are in the list, .split creates lists from empty strings
        if homes != "":
            homes = homes.split(":")
            print(homes)
            temp_homes = []
            for home in homes:
                l = home.split(";")
                temp_homes.append(l)
            homes = temp_homes
        else:
            homes = []

        y = 0.80
        self.IPlist = []
        home_list_layout = FloatLayout()
        for home in homes:
            homeIP = str(home[0])
            self.IPlist.append(homeIP)
            homeN = str(home[1])
            if homeIP == current:
                label = Label(pos_hint={'x': 0.55, 'y': y}, size_hint=(0.15, 0.1), text="this is your current home")
                home_list_layout.add_widget(label)
                button = Button(pos_hint={'x': 0.75, 'y': y}, size_hint=(0.15, 0.1), text="step out")
                home_list_layout.add_widget(button)
            else:
                button = Button(pos_hint={'x': 0.55, 'y': y}, size_hint=(0.15, 0.1), text="come in")
                home_list_layout.add_widget(button)
                button = Button(pos_hint={'x': 0.75, 'y': y}, size_hint=(0.15, 0.1), text="move out")
                home_list_layout.add_widget(button)
            label = Label(pos_hint={'x': 0.1, 'y': y}, size_hint=(0.4, 0.1),
                          text=f"home name: {homeN}    homeIP: {homeIP}")
            home_list_layout.add_widget(label)
            y -= 0.15
        for _ in range(5 - len(homes)):
            label = Label(pos_hint={'x': 0.45, 'y': y}, text="empty plot", size_hint=(0.15, 0.1))
            home_list_layout.add_widget(label)
            y -= 0.15

        self.home_list_layout = home_list_layout
        # removing previous list layout
        children_len = len(self.children)
        for x, child in enumerate(self.children):
            if x != (children_len - 1):
                self.remove_widget(child)
        self.add_widget(self.home_list_layout)

    def choose(self, instance):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        y = float(str(instance.__getattribute__("pos_hint"))[-4:-1])
        y = int(y * 100)
        index = int(abs(((y - 5) / 15) - 5))
        line = f"current:{self.IPlist[index]}\n"
        lines = lines[:-1]
        lines += [line]
        local_f = open(local_dir, "w")
        for line in lines:
            local_f.write(line)
        local_f.close()
        self.refresh()

    def step_out(self, instance):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        line = "current:0\n"
        lines = lines[:-1]
        lines += [line]
        local_f = open(local_dir, "w")
        for line in lines:
            local_f.write(line)
        local_f.close()
        self.refresh()

    def confirm(self, instance):
        y = float(str(instance.__getattribute__("pos_hint"))[-4:-1])
        y = int(y * 100)
        self.index = int(abs(((y - 5) / 15) - 5))
        popup = Factory.ConfirmDelete()
        popup.title = "delete confirmation"
        popup.title_align = "center"
        layout = FloatLayout()
        layout.add_widget(Label(text="are you sure you want to delete this home?", pos_hint={'x': 0.01, 'y': 0.4}))
        button = Button(text="yes", pos_hint={'x': 0.15, 'y': 0.1}, size_hint=(0.3, 0.2))
        layout.add_widget(button)
        button = Button(text="no", pos_hint={'x': 0.55, 'y': 0.1}, size_hint=(0.3, 0.2))
        layout.add_widget(button)
        popup.content = layout
        popup.open()

    def move_out(self, instance):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        email = lines[0][6:-1]
        pas = lines[1][5:-1]
        homeIP = self.IPlist[self.index]
        ans = "1"
        if ans == "1":
            self.refresh()
        else:
            print("Error")


class AboutWindow(Screen):
    pass


class HomeWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("home.kv")

wm = WindowManager()

screens = [LogInWindow(name="login"), HomeWindow(name="home"),
           ShoppingWindow(name="shopping"),
           InviteWindow(name="invite"), ChatWindow(name="chat"), HomesWindow(name="homes"),
           CreateHomeWindow(name="create_home"), RegisterWindow(name="register"), ChooseHomeWindow(name="choose"),
           FinalListWindow(name="final_list"), AboutWindow(name="about")]
for screen in screens:
    wm.add_widget(screen)

wm.current = "login"


class HomeApp(App):
    def build(self):
        return wm


if __name__ == "__main__":
    HomeApp().run()