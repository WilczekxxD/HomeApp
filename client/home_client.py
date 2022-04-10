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

# socket info

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.72"
ADDR = (SERVER, PORT)
# connecting socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# file info
users = "users.txt"
shopping = "shopping.txt"
chat_history = "chat_history.txt"
local_dir = os.path.join(os.getcwd(), "local.txt")


def snd(msg):
    send_msg = msg.encode(FORMAT)
    msg_length = len(send_msg)
    print(msg + " length: " + str(msg_length))
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(send_msg)


def rcv():
    end = False
    while not end:
        msg_length = client.recv(HEADER).decode(FORMAT)
        print("waiting")
        if msg_length:
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            return msg


class CreateHomeWindow(Screen):

    def create(self):
        self.success.text = "pending"
        local_f = open(local_dir, "r")
        email = local_f.readlines()[0][6:-1]
        local_f.close()
        pas = self.pas.text
        name = self.hname.text
        print(email, pas, name)
        if len(pas) != 0 and len(name)!= 0 and len(pas)!= 0:
            snd("h01")
            snd(email)
            snd(name)
            snd(pas)
            ans = rcv()
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

        # making layout for the scroller, 3 columns for name, quantity/measure, deleating
        self.list_viewer.clear_widgets()
        self.width = Window.size[0]
        # print(self.list_viewer.__getattribute__("size_hint_x"), self.width)
        scroll_layout = GridLayout(cols=3, spacing=40, size_hint_y=None, padding=[0, 5, 0, 5],
                                   size_hint_x=self.list_viewer.__getattribute__("size_hint_x"))
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        if current != "0":
            snd("s02")
            snd(current)
            shopping_list = rcv().split(";")
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

                # checking if the product is correct
                snd("s05")
                snd(current)
                snd(name)
                check = rcv()
                if check == "error":
                    self.wrong_product_popup(WholeProduct)
                    break
                # product name label
                # col 1

                label = Label(text=f'{name}',
                              text_size=(self.width/3, None),
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
                up_button.bind(on_release=self.increase_quantity)

                down_button = self.QuantityButton(text='-',
                                                  pos_hint={'x': 0.825, 'y': 0.05},
                                                  size_hint=(0.25, 0.9),
                                                  quantity=quantity,
                                                  index=index,
                                                  shopping_list=";".join(shopping_list))
                down_button.bind(on_release=self.decrease_quantity)

                quantity_layout.add_widget(label)
                quantity_layout.add_widget(up_button)
                quantity_layout.add_widget(down_button)

                scroll_layout.add_widget(quantity_layout)

                # delete item from the list
                # col 4

                button = self.DeleteProductButton(text="X", size_hint=(None, None))
                button.__setattr__("Pname", WholeProduct)
                button.bind(on_release=self.delete_product)
                scroll_layout.add_widget(button)

        self.list_viewer.add_widget(scroll_layout)

    # def edit_quantity(self, instance):
    def increase_quantity(self, instance):
        # local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]
        shopping_list = instance.shopping_list.split(";")
        product = shopping_list[instance.index].split(":")

        quantity = int(instance.quantity + 1)
        product[1] = str(quantity)
        product = ":".join(product)
        shopping_list[instance.index] = product
        shopping_list = ";".join(shopping_list)
        # updating shopping list on the server
        snd("s04")
        snd(current)
        snd(shopping_list)
        self.refresh()

    def decrease_quantity(self, instance):
        # local info
        if instance.quantity > 0:
            local_f = open(local_dir, "r")
            lines = local_f.readlines()
            current = lines[3][8:-1]
            shopping_list = instance.shopping_list.split(";")
            product = shopping_list[instance.index].split(":")

            quantity = int(instance.quantity - 1)
            product[1] = str(quantity)
            product = ":".join(product)
            shopping_list[instance.index] = product
            shopping_list = ";".join(shopping_list)
            # updating shopping list on the server
            snd("s04")
            snd(current)
            snd(shopping_list)
            self.refresh()

    def add_product_popup(self):
        # this function makes a popup apear, instead of Factory the class it could be done separatly and than
        # popup functions would be inside a popup class, but for now it is okay # todo think about it eventually

        # popup
        self.popup = Factory.AddProduct()
        self.popup.title = "add product"
        self.popup.title_align = "center"
        popup_layout = FloatLayout()

        # new product name

        new_name_label = Label(size_hint=(0.6725, 0.15),
                               pos_hint={"x": 0.025, "y": 0.825},
                               halign="left",
                               text="product name")
        popup_layout.add_widget(new_name_label)

        self.new_name_input = TextInput(size_hint=(0.95, 0.15),
                                        pos_hint={"x": 0.025, "y": 0.65})
        popup_layout.add_widget(self.new_name_input)

        # quantity

        quantity_label = Label(size_hint=(0.675, 0.15),
                               pos_hint={"x": 0.025, "y": 0.45},
                               halign="left",
                               text="quantity")
        popup_layout.add_widget(quantity_label)

        # dropdown with measures

        measures = DropDown()
        possible_measures = ["szt.", "g."]
        for measure in possible_measures:
            btn = Button(text=f"{measure}", size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: measures.select(btn.text))
            measures.add_widget(btn)

        self.opener = Button(text='measure',
                        size_hint=(0.225, 0.15),
                        pos_hint={"x": 0.7, "y": 0.45})

        self.opener.bind(on_release=measures.open)

        measures.bind(on_select=lambda instance, x: setattr(self.opener, 'text', x))
        popup_layout.add_widget(self.opener)

        # quantity
        self.quantity_input = TextInput(size_hint=(0.95, 0.15),
                                        pos_hint={"x": 0.025, "y": 0.275})
        popup_layout.add_widget(self.quantity_input)

        # dissmiss & confirm
        back = Button(size_hint=(0.4625, 0.2),
                      pos_hint={"x": 0.025, "y": 0.025},
                      text="x")
        back.bind(on_release=self.popup.dismiss)

        confirm = Button(size_hint=(0.4625, 0.2),
                         pos_hint={"x": 0.5125, "y": 0.025},
                         text="confirm")
        confirm.bind(on_press=self.add_product_server)

        popup_layout.add_widget(back)
        popup_layout.add_widget(confirm)

        # initializing self.popup
        self.popup.content = popup_layout
        self.popup.open()

    def add_product_server(self, instance):

        # sends new product data to the servers home file
        # local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]
        if current != "0":
            if self.opener.text != 'measure':
                try:
                    # checking if quantity is a number
                    float(self.quantity_input.text)
                    # checking other possible errors
                    error = False
                    if len(self.new_name_input.text) < 200:
                        for letter in self.new_name_input.text:
                            if letter in "1234567890][{};:.,<>?/`~!@#$%^&*()_+\=|'":
                                self.new_name_input.text = "nazwa produktu może składać się z liter i '-'"
                                error = True
                                break
                    elif len(self.new_name_input.text)>200:
                        self.new_name_input.text = "za długa nazwa"
                    if not error:
                        # adding it on the server
                        snd("s01")
                        snd(self.new_name_input.text + ":" + self.quantity_input.text + ":" + self.opener.text)
                        snd(current)
                        self.popup.dismiss()
                        self.refresh()

                except ValueError:
                    self.quantity_input.text = "ilość prosze wyrazić w liczbach"
            else:
                self.opener.background_color = (0.6, 0, 0, 1)

    def wrong_product_popup(self, WholeProduct):
        self.popup = Factory.WrongProduct()
        self.popup.title = f"Wrong product in your list"
        self.popup.title_align = "center"
        self.popup.auto_dismiss = False
        name = WholeProduct.split(":")[0]
        popup_layout = FloatLayout()
        description = Label(text=f"{name} is not in our database, check your spelling and try again or add it to our database, it may take some time so wait before adding it again",
                            halign="center",
                            text_size=(Window.width * 0.4, Window.height * 0.6),
                            pos_hint={"x": 0.005, "y": 0.5})


        # dissmiss & confirm
        back = self.DeleteProductButton(size_hint=(0.4625, 0.2),
                                        pos_hint={"x": 0.025, "y": 0.025},
                                        text="x",
                                        Pname=WholeProduct)
        back.bind(on_release=self.delete_product_popup)

        # using already existing Button type instead of making new because it has the Pname attribute
        confirm = self.DeleteProductButton(size_hint=(0.4625, 0.2),
                                           pos_hint={"x": 0.5125, "y": 0.025},
                                           text="add",
                                           Pname=WholeProduct)
        confirm.bind(on_press=self.add_product_database)

        popup_layout.add_widget(description)
        popup_layout.add_widget(back)
        popup_layout.add_widget(confirm)

        # initializing self.popup
        self.popup.content = popup_layout
        self.popup.open()

    def add_product_database(self, instance):
        product = instance.__getattribute__("Pname")
        name = product.split(":")[0]
        # adding
        snd("d01")
        snd(name)
        # deleting
        snd("s03")
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        current = lines[3][8:-1]
        snd(current)
        snd(instance.__getattribute__("Pname"))
        self.popup.dismiss()
        self.refresh()

    def delete_product(self, instance):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        current = lines[3][8:-1]
        product = instance.__getattribute__("Pname")
        snd("s03")
        snd(current)
        snd(product)
        self.refresh()

    def delete_product_popup(self, instance):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        current = lines[3][8:-1]
        product = instance.__getattribute__("Pname")
        snd("s03")
        snd(current)
        snd(product)
        self.popup.dismiss()
        self.refresh()


class FinalListWindow(Screen):

    class DeleteProductButton(Button):
        Pindex = NumericProperty(defaultvalue=0)

    class QuantityButton(Button):
        quantity = NumericProperty(defaultvalue=0)
        index = NumericProperty(defaultvalue=0)

    class InfoButton(Button):
        Pindex = NumericProperty(defaultvalue=0)

    def on_pre_enter(self, *args):
        # local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]

        # getting the converted list form the server
        snd("l01")
        snd(current)
        converted = rcv()

        # writing it down
        final_list_path = os.path.join(os.getcwd(),  "final_list.txt")
        final_list_file = open(final_list_path, "w")
        final_list_file.write(converted)
        final_list_file.close()

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
                              text_size=(self.width/3, None),
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
                button.bind(on_release=self.delete_product)
                feature_box.add_widget(button)

                # info button
                # col 5
                button = self.InfoButton(text="i", size_hint=(0.3, 0.2))
                button.__setattr__("Pindex", index)
                button.bind(on_release=self.show_info)
                feature_box.add_widget(button)

                # adding the feature space to the scroll layout
                scroll_layout.add_widget(feature_box)

        self.list_viewer.add_widget(scroll_layout)

    def delete_product(self, instance):
        # instead of deleting whole product class deletes only single suggestions
        index = instance.__getattribute__("Pindex")

        converted_list_path = os.path.join(os.getcwd(), "final_list.txt")
        converted_list_file = open(converted_list_path, "r")
        converted_list = converted_list_file.readlines()

        suggestions = converted_list[index]
        suggestions = ";".join(suggestions.split(";")[1:])
        converted_list[index] = suggestions
        converted_list_file.close()

        # writing it down
        final_list_path = os.path.join(os.getcwd(), "final_list.txt")
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

    def show_info(self, instance):
        index = instance.Pindex

        converted_list_path = os.path.join(os.getcwd(), "final_list.txt")
        converted_list_file = open(converted_list_path, "r")
        converted_list = converted_list_file.readlines()
        converted_list_file.close()

        # extracting product name
        suggestions = converted_list[index]
        suggestions = suggestions.split(";")
        product = suggestions[0].split(":")
        name = product[0]
        index = product[-2]

        # homeIp extraction
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]
        local_f.close()

        snd("l02")
        snd(current)
        snd(name)
        snd(index)
        properties = rcv()
        properties = properties.split("^")

        # properties should be as name of the property, text of the property list
        # ex [price;540 , name;XXX]
        # popup with scroll layout for properties

        self.popup = Factory.Properties()
        self.popup.title = f"Info-{name}"
        self.popup.title_align = "center"
        self.popup.auto_dismiss = False
        popup_layout = FloatLayout()

        scroll_layout = GridLayout(cols=1, spacing=40, padding=[0, 0, 0, 40],
                                   size_hint=(0.9, None))
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # feature instead of property because property is a built in function
        for feature in properties:
            feature = feature.split(";")
            feature_name = feature[0]
            feature_description = feature[1]
            name = Label(text=feature_name, halign="center", text_size=(None, None))
            description = Label(text=feature_description, halign="left",
                                text_size=(Window.width - 0.3 * Window.width, None))
            description.texture_update()
            print(scroll_layout.spacing)
            if description.texture_size[1] > scroll_layout.spacing[1]:
                scroll_layout.spacing[1] = description.texture_size[1]
            scroll_layout.add_widget(name)
            scroll_layout.add_widget(description)

        back = Button(size_hint=(0.95, 0.2),
                      pos_hint={"x": 0.025, "y": 0.025},
                      text="x")
        back.bind(on_release=self.popup.dismiss)

        root = ScrollView(size_hint=(0.9, 0.75), pos_hint={"x": 0.1, "y": 0.25})
        root.add_widget(scroll_layout)
        popup_layout.add_widget(back)
        popup_layout.add_widget(root)

        # initializing self.popup
        self.popup.content = popup_layout
        self.popup.open()


class ChatWindow(Screen):

    def on_enter(self):
        self.refresh()

    def send(self):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]
        email = lines[0][6:-1]
        local_f.close()

        if current != "0":
            snd("c01")
            snd(self.msg.text)
            snd(current)
            snd(email)
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
            snd("c02")
            snd(current)
            chat = rcv()
            chat = chat.split(";")[:-1]
            view = FloatLayout(size_hint=(1, 1))
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

                        label = Label(text=(msg+"\n"+author),
                                      text_size=(self.chat_h.width/2, None),
                                      halign="right",)
                        label.texture_update()
                        label.size = label.texture_size
                        noffset = offsets[-1]+label.height + padding
                        offsets.append(noffset)
                        msg_list.append([label, author])

                    else:

                        label = Label(text=(msg+"\n"+author),
                                      text_size=(self.chat_h.width/2, None),
                                      halign="left",)
                        label.texture_update()
                        label.size = label.texture_size
                        noffset = offsets[-1]+label.height + padding
                        offsets.append(noffset)
                        msg_list.append([label, author])

                view.size = (self.chat_h.width, offsets[-1])
                view.size_hint = (None, None)
                view.pos = (0, 0)

                for i, msg in enumerate(msg_list):
                    label = msg[0]
                    author = msg[1]
                    if author == email:
                        label.pos = (label.get_center_x(),
                                     view.height/2 - offsets[i] - label.height/2)
                    else:
                        label.pos = (0,
                                     view.height / 2 - offsets[i] - label.height / 2)
                    print(label.pos)
                    label.pos_hint = {}
                    view.add_widget(label)
                self.chat_h.add_widget(view)
            else:
                self.chat_h.add_widget(Label(text="there are no messages"))
        else:
            self.chat_h.add_widget(Label(text="you are not in any home"))


class LogInWindow(Screen):

    def user_login(self):
        snd("u01")
        snd(self.email.text)
        snd(self.pas.text)
        ans = str(rcv())
        if ans == "0":
            wm.current = "home"
        else:
            print(ans)

    def on_pre_enter(self, *args):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        for line in lines:
            if line[:6] == "email:":
                email = line[6:-1]
            if line[:5] == "pass:":
                pas = line[5:-1]
            if line[:9] == "remember:":
                if line[9:-1] == "0":
                    self.pas.text = ""
                    self.email.text = ""
                else:
                    if pas != "0" and email != "0":
                        self.pas.text = pas
                        self.email.text = email
                        self.remember.active = True
                    else:
                        self.pas.text = ""
                        self.email.text = ""

        local_f.close()

    def on_leave(self, *args):
        print("left")
        local_f = open(local_dir, "r")
        lines = []
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
            snd("u02")
            snd(self.email.text)
            snd(self.pas1.text)
            snd(self.pas2.text)
            ans = rcv()
            if ans == "successfully registered":
                self.success.text = "successfuly registered"
            else:
                self.success.text = "error"
        else:
            self.success.text = "fill blank spaces"


class InviteWindow(Screen):

    def on_enter(self):
        self.refresh()
        rf = threading.Thread(target=self.refresh_continuously)
        rf.start()

    def on_leave(self, *args):
        self.gcode.text = ""
        self.ghomeIP.text = ""

    def refresh(self):
        #local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]

        # setting scroll view preview
        self.code_viewer.clear_widgets()
        scroll_layout = GridLayout(cols=1, spacing=40, size_hint_y=None, padding=[0, 5, 0, 5])
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # fetching code list to add to scroll view
        if current != "0":
            snd("i02")
            snd(current)
            codes_l = rcv().split(";")
            if len(codes_l) == 1:
                codes_l = ["you have no pending invitations for the home you are currently in"]
        else:
            codes_l = ["you currently are not in any home"]

        for code in codes_l:
            label = Label(text=code, size_hint_y=None, height=5)
            scroll_layout.add_widget(label)
        self.code_viewer.add_widget(scroll_layout)

    def refresh_continuously(self):
        # local info
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        current = lines[3][8:-1]

        # setting scroll view preview
        self.code_viewer.clear_widgets()
        scroll_layout = GridLayout(cols=1, spacing=40, size_hint_y=None, padding=[0, 5, 0, 5])
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # fetching code list to add to scroll view
        while wm.current == "invite":
            time.sleep(1)
            scroll_layout.clear_widgets()
            self.code_viewer.clear_widgets()
            print("lol")
            if current != "0":
                snd("i02")
                snd(current)
                codes_l = rcv().split(";")
                if len(codes_l) == 1:
                    codes_l = ["you have no pending invitations for the home you are currently in"]
            else:
                codes_l = ["you currently are not in any home"]

            for code in codes_l:
                label = Label(text=code, size_hint_y=None, height=5)
                scroll_layout.add_widget(label)

            self.code_viewer.add_widget(scroll_layout)

    def redeem_code(self):
        # TODO adding a popup window announcing that one has been added would hel visualy
        # TODO the success is just not visible enough
        self.feedback.text = "pending"
        if self.gcode.text != "" and self.ghomeIP.text != "":
            local_f = open(local_dir, "r")
            lines = local_f.readlines()
            email = lines[0][6:-1]
            snd("i03")
            snd(self.ghomeIP.text)
            snd(self.gcode.text)
            snd(email)
            ans = rcv()
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
            snd("i01")
            snd(current)
            ans = rcv()
            self.feedback.text = ans
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
        snd("h02")
        snd(email)
        homes = rcv()

        #fix for situation when no homes are in the list, .split creates lists from empty strings
        print(f"it printed:{homes}")
        if homes != "":
            homes = homes.split(":")
            print(homes)
            temp_homes = []
            for home in homes:
                l = home.split(";")
                temp_homes.append(l)
            homes = temp_homes
            print(homes)
            print(len(homes))
        else:
            homes = []

        y = 0.80
        self.IPlist = []
        home_list_layout = FloatLayout()
        for home in homes:
            homeIP = str(home[0])
            self.IPlist.append(homeIP)
            homeN= str(home[1])
            if homeIP == current:
                label = Label(pos_hint={'x': 0.55, 'y': y}, size_hint=(0.15, 0.1), text="this is your current home")
                home_list_layout.add_widget(label)
                button = Button(pos_hint={'x': 0.75, 'y': y}, size_hint=(0.15, 0.1), text="step out")
                button.bind(on_press=self.step_out)
                home_list_layout.add_widget(button)
            else:
                button = Button(pos_hint={'x': 0.55, 'y': y}, size_hint=(0.15, 0.1), text="come in")
                button.bind(on_press=self.choose)
                print(type(button.__getattribute__("pos_hint")))
                home_list_layout.add_widget(button)
                button = Button(pos_hint={'x': 0.75, 'y': y}, size_hint=(0.15, 0.1), text="move out")
                button.bind(on_press=self.confirm)
                home_list_layout.add_widget(button)
            label = Label(pos_hint={'x': 0.1, 'y': y}, size_hint=(0.4, 0.1), text=f"home name: {homeN}    homeIP: {homeIP}")
            home_list_layout.add_widget(label)
            y -= 0.15
        for _ in range(5-len(homes)):
            label = Label(pos_hint={'x': 0.45, 'y': y}, text="empty plot", size_hint=(0.15, 0.1) )
            home_list_layout.add_widget(label)
            y-=0.15

        self.home_list_layout = home_list_layout
        # removing previous list layout
        children_len = len(self.children)
        for x, child in enumerate(self.children):
            if x != (children_len-1):
                self.remove_widget(child)
        self.add_widget(self.home_list_layout)

    def choose(self, instance):
        local_f = open(local_dir, "r")
        lines = local_f.readlines()
        local_f.close()
        y = float(str(instance.__getattribute__("pos_hint"))[-4:-1])
        y = int(y*100)
        index = int(abs(((y-5)/15)-5))
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
        button.bind(on_press=self.move_out, on_release=popup.dismiss)
        layout.add_widget(button)
        button = Button(text="no", pos_hint={'x': 0.55, 'y': 0.1}, size_hint=(0.3, 0.2))
        button.bind(on_release=popup.dismiss)
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
        snd("h03")
        snd(homeIP)
        snd(email)
        snd(pas)
        ans = rcv()
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

screens = [LogInWindow(name="login"), HomeWindow(name="home"), ShoppingWindow(name="shopping"),
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
