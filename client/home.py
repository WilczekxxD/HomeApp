from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from Server.user_handler import *
import socket
import threading

# socket info

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.35"
ADDR = (SERVER, PORT)
    # connecting socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# file info

users = "users.txt"
shopping = "shopping.txt"
chat_history = "chat_history.txt"


class UsersWindow(Screen):
    pass


class CreateHomeWindow(Screen):
    pass


class ShoppingWindow(Screen):

    def on_enter(self):
        self.shopping = shopping
        txt = ""
        self.file = open(self.shopping)
        for line in self.file:
            txt += line
            txt += "\n"
        self.shoppingl.text = txt


class ChatWindow(Screen):

    def send(self):
        message = self.msg.text.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
        self.msg.text = ""

    def refresh(self):
            self.chat_history = chat_history
            txt = ""
            self.file = open(self.chat_history)
            for line in self.file:
                txt += line
                txt += "\n"
            self.chat_h.text = txt
            self.file.close()
            # TODO: figure out how to make it refresh without getting out of chat window

    def on_enter(self):
        ChatWindow.refresh(self)
        refreshing = threading.Thread(target=ChatWindow.refresh)
        refreshing.start()


class LogInWindow(Screen):

    def user_login(self):
        ans = login(self.email.text, self.pas.text)
        if ans == 0:
            wm.current = "home"
        else:
            print("error")

    def on_pre_enter(self, *args):

        if self.remember.active:
            self.pas.text = ""
        else:
            self.pas.text = ""
            self.email.text = ""


class HomesWindow(Screen):
    pass


class HomeWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("home.kv")

wm = WindowManager()

screens = [LogInWindow(name="login"), HomeWindow(name="home"), UsersWindow(name="users"), ShoppingWindow(name="shopping"),
           ChatWindow(name="chat"), HomesWindow(name="homes"), CreateHomeWindow(name="chome")]
for screen in screens:
    wm.add_widget(screen)

wm.current = "homes"


class HomeApp(App):
    def build(self):
        return wm


if __name__ == "__main__":
    HomeApp().run()