import os
import socket
import threading
from database import *
from user_handler import *
from product_converter import *

HEADER = 64
PORT = 5051
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

chat_history = "chat_history.txt"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

connections = []

codes = {"h"}


def rcv(conn):

    end = False
    while not end:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        print("waiting")
        if msg_length:
            print(msg_length)
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            return(msg)


def snd(msg, conn):
    print("sending")
    send_msg = msg.encode(FORMAT)
    msg_length = len(send_msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(send_msg)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.\n")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            print(f"[{addr}] {msg}")

            if msg == DISCONNECT_MESSAGE:
                conn.send("Disconected".encode(FORMAT))
                connected = False

            elif msg == "d01":
                print("adding a product to the loading que")
                product = rcv(conn)
                add_load(product)

            elif msg == "u01":
                print("logging user in")
                email = rcv(conn)
                pas = rcv(conn)
                ans = login(email, pas)
                snd(ans, conn)

            elif msg == "u02":
                print("registering user")
                email = rcv(conn)
                pas1 = rcv(conn)
                pas2 = rcv(conn)
                ans = register(email, pas1, pas2)
                snd(ans, conn)

            elif msg == "h01":
                print("building home")
                email = rcv(conn)
                name = rcv(conn)
                pas = rcv(conn)
                ans = str(build_home(email, name, pas))
                snd(ans, conn)

            elif msg == "h02":
                print("fetching homes")
                email = rcv(conn)
                ans = get_homes(email)
                nans = ""
                for x, home in enumerate(ans):
                    if x == 0:
                        nhome = ""
                    else:
                        nhome = ":"
                    nhome += str(home[0]) + ";" + str(home[1])
                    nans += nhome
                print(nans)
                snd(nans, conn)

            elif msg == "h03":
                print("deleting home")
                homeIP = rcv(conn)
                email = rcv(conn)
                pas = rcv(conn)
                snd(delete_home(email, homeIP, pas), conn)

            elif msg == "i01":
                print("creating code")
                homeIP = rcv(conn)
                ans = invite_home(homeIP)
                snd(ans, conn)

            elif msg == "i02":
                print("fetching codes")
                homeIP = rcv(conn)
                codes = get_codes(homeIP)
                print(codes)
                snd(codes, conn)

            elif msg == "i03":
                print("accepting invitation")
                homeIP = rcv(conn)
                code = rcv(conn)
                email = rcv(conn)
                ans = accept_invitation(code, homeIP, email)
                snd(ans, conn)

            elif msg == "c01":
                print("sending users msg")
                msg = rcv(conn)
                homeIP = rcv(conn)
                email = rcv(conn)
                add_msg(msg, homeIP, email)

            elif msg == "c02":
                print("fetching chat")
                homeIP = rcv(conn)
                ans = get_chat(homeIP)
                snd(ans, conn)

            elif msg == "s01":
                print("adding product")
                product = rcv(conn)
                print(product)
                homeIP = rcv(conn)
                add_product(product, homeIP)

            elif msg == "s02":
                print("fetching products")
                homeIP = rcv(conn)
                products = get_products(homeIP)
                if len(products) > 0:
                    snd(products[0], conn)
                else:
                    snd("", conn)

            elif msg == 's03':
                print("deleting product")
                homeIP = rcv(conn)
                product = rcv(conn)
                print(remove_product(product, homeIP))

            elif msg == 's04':
                print("updating list")
                homeIP = rcv(conn)
                product_list = rcv(conn)
                product_list = product_list + ";"
                update_products(homeIP, product_list)

            elif msg == 's05':
                print("checking for wrong product")
                homeIP = rcv(conn)
                product = rcv(conn)

                check = check_load(product)
                if check == "error":
                    snd(check, conn)
                else:
                    snd("allGood", conn)

            elif msg == 'l01':
                print("converting the list")
                homeIP = rcv(conn)
                converted_string = convert(homeIP)
                print(converted_string)
                snd(converted_string, conn)

            elif msg == 'l02':
                print("sending full product info")
                homeIP = rcv(conn)
                name = rcv(conn)
                index = rcv(conn)
                info = get_product_info(homeIP, name, index)
                snd(info, conn)


    conn.close()


def load_server():
    # contiously loading products and rearenging the loading list
    end = False
    while not end:
        dtb = Database()
        f = open(os.path.join(os.getcwd(), "load.txt"), "r", encoding='utf-8')
        line = f.readlines()[0]
        f.close()
        products = line.split(";")
        print(products)
        dtb.auchan.load_data([products[0]])
        f = open(os.path.join(os.getcwd(), "load.txt"), "w", encoding='utf-8')
        products = products[1:] + [products[0]]
        f.write(";".join(products))
        f.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    ls = threading.Thread(target=load_server(), args=())
    ls.start()
    while True:
        conn, addr = server.accept()
        connections.append(conn)
        hc = threading.Thread(target=handle_client, args=(conn, addr))
        hc.start()

        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()