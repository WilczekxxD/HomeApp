import os
import shutil
from random import *
from database import *
import time
import threading
import pickle
from datetime import datetime

# programs to handle client files
#   class user: login, registration,
#   class home: new home, joining existing home,

users = "users"
homes_dir = "homes"


def register(email, password1, password2):
    # sprawdzic czy użytkownik istnieje
    # zobaczyc czy hasła są identyczne
    # dodac plik z użytkownikiem do folderu user
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, users, str(email) + ".txt")):
        return "user already exisitng"
    elif password1 != password2:
        return "passwords doesn't match"
    else:
        f = open(os.path.join(cwd, users, str(email) + ".txt"), "w")
        f.write("password:" + password1 + "\n")
        f.write("homes:'\n'")
        if os.path.exists(os.path.join(cwd, users, str(email) + ".txt")):
            return "successfully registered"
        else:
            return "error"


def login(email, password):
    # sprawdzic czy istnieje
    # zobaczyc czy zgadza się hasło
    if os.path.exists(os.path.join(users, str(email) + ".txt")):
        f = open(os.path.join(users, str(email) + ".txt"))
        saved_pass = f.readline()[9:-1]
        f.close()
        if saved_pass == password:
            return "0"
        else:
            return "wrong password"
    else:
        return "user doesn't exist"


def load_classifier():
    classifier = "classifier.pickle"
    f = open(os.path.join(os.getcwd(), classifier), "rb")
    re = pickle.load(f)
    f.close()
    return re


def load_vectorizer():
    vectorizer = "vectorizer.pickle"
    f = open(os.path.join(os.getcwd(), vectorizer), "rb")
    re = pickle.load(f)
    f.close()
    return re


def build_home(email, name, gpass):
    # sprawdzic hasło
    # wziąć ostatni numer z log.txt
    # stworzyć folder dom a w nim pliki
    cwd = os.getcwd()
    user_f = open(os.path.join(cwd, users, email + ".txt"), "r")
    lines = user_f.readlines()
    home_count = len(lines[1][6:-1].split(";"))-1
    pas = lines[0][9:-1]
    user_f.close()
    if pas == gpass:
        if home_count <= 5:

            log_f = open(os.path.join(cwd, homes_dir, "log.txt"), "r")
            last = int(log_f.readline())
            log_f.close()
            str_new = ("0" * (10 - len(str(last + 1))) + str(last + 1))
            new_home_dir = os.path.join(cwd, homes_dir, str_new)
            log_f = open(os.path.join(cwd, homes_dir, "log.txt"), "w")
            log_f.write(str_new)
            os.mkdir(new_home_dir)
            # creating files inside the new home: inf, chat, invite_codes, shopping_list
            new_home_inf = open(os.path.join(new_home_dir, "inf.txt"), "w")
            new_home_inf.write("name:" + name + "\n")
            new_home_inf.write("users:" + email + ";")

            new_home_chat = open(os.path.join(new_home_dir, "chat.txt"), "w")
            new_invite_codes = open(os.path.join(new_home_dir, "invite_codes.txt"), "w")
            new_shopping_list = open(os.path.join(new_home_dir, "shopping_list.txt"), "w")
            categories = open(os.path.join(new_home_dir, "categories.txt"), "w")

            categories.close()
            new_shopping_list.close()
            new_invite_codes.close()
            new_home_inf.close()
            new_home_chat.close()
            log_f.close()

            # creating shopping history
            for i in range(5):
                new_history = open(os.path.join(new_home_dir, f"{i}.txt"), "w")
                new_history.close()

            classifier = load_classifier()
            with open(os.path.join(new_home_dir, "classifier.pickle"), "wb") as f:
                pickle.dump(classifier, f)

            vectorizer = load_vectorizer()
            with open(os.path.join(new_home_dir, "vectorizer.pickle"), "wb") as f:
                pickle.dump(vectorizer, f)

            user_f = open(os.path.join(cwd, users, email + ".txt"), "a")
            user_f.write(str_new + ";")
            user_f.close()

            return "success"
        else:
            return "home limit is full"
    else:
        return "wrong password"


def invite_home(homeIP):
    # crating the code and chacking if in the code list unless not
    # setting codes timer in another thread
    # dlete when accepted or when time runs out

    cwd = os.getcwd()
    end = False
    while not end:
        code = generate_code(homeIP)
        if code:
            code_dir = os.path.join(cwd, homes_dir, homeIP, "invite_codes.txt")
            code_f = open(code_dir, "a")
            code_f.write(code+";")
            code_f.close()
            end = True
            #return "success"
    return "success"


class Code:
    def __init__(self, homeIP, code):
        self.homeIP = homeIP
        self.code = code
        self.ob = threading.Thread(target=self.obliterate)
        self.ob.start()

    def obliterate(self):
        print("countdown started")

        time.sleep(60*3)

        cwd = os.getcwd()
        code_dir = os.path.join(cwd, homes_dir, self.homeIP, "invite_codes.txt")

        try:
            code_f = open(code_dir, "r")
            code_l = code_f.read().split(";")
            code_f.close()
            code_i = code_l.index(self.code)
            code_l.pop(code_i)

            code_f = open(code_dir, "w")
            code_f.write(";".join(code_l))
            code_f.close()
            print("deleated")
        except:
            print("not there")


def generate_code(homeIP):
    cwd = os.getcwd()
    code_dir = os.path.join(cwd, homes_dir, homeIP, "invite_codes.txt")
    code_f = open(code_dir, "r")
    code_l = code_f.read().split(";")
    code_f.close()
    code_str = str(randint(10000, 99999))
    ob = Code(homeIP, code_str)
    if code_str in code_l:
        return False
    else:
        return code_str


def accept_invitation(code, homeIP, email):
    cwd = os.getcwd()

    # checking if already in house or house doesn't exist
    home_p = os.path.join(cwd, homes_dir, homeIP)
    user_f = open(os.path.join(cwd, users, email + ".txt"), "r")
    homes_l = user_f.readlines()[1][6:].split(";")
    user_f.close()

    if os.path.exists(home_p) and homeIP not in homes_l:

        #if home exists checking the code
        code_dir = os.path.join(cwd, homes_dir, homeIP, "invite_codes.txt")
        code_f = open(code_dir, "r")
        code_l = code_f.read().split(";")
        code_f.close()
        if code in code_l:
            try:
                # removing the old invite code
                delete_code(code, homeIP)

                # adding new user to the house
                open(os.path.join(home_p, "inf.txt"), "a").write(email + ";")

                # adding new house to the user
                open(os.path.join(cwd, users, email + ".txt"), "a").write(homeIP + ";")
                return "1"
            except ValueError:
                return "invitation has already expired or has been used"
        else:
            return "invitation already expired or has been used"
    else:
        return "error"


def delete_code(code, homeIP):
    # tool to deleate the code
    cwd = os.getcwd()
    i = 0
    code_dir = os.path.join(cwd, homes_dir, homeIP, "invite_codes.txt")
    end = False
    while not end:
        code_f = open(code_dir, "r")
        code_l = code_f.read().split(";")
        code_f.close()
        try:
            code_f = open(os.path.join(code_dir), "w")
            code_i = code_l.index(code)
            code_l.pop(code_i)
            code_f.write(";".join(code_l))
            code_f.close()
            end = True
        except ValueError:
            end = True


def delete_home(email, homeIP, gpas):
    # user info
    cwd = os.getcwd()
    user_f = open(os.path.join(cwd, users, email + ".txt"), "r")
    lines = user_f.readlines()
    pas = lines[0]
    homes = lines[1][6:-1]
    homes_l = homes.split(";")
    print(homes)
    user_f.close()
    # house info
    home_f = open(os.path.join(cwd, homes_dir, homeIP, "inf.txt"), "r")
    home_lines = home_f.readlines()
    print(f"home_lines: {home_lines}")
    users_l = home_lines[1][6:].split(";")
    home_f.close()
    print(users_l)
    print(homeIP, homes_l, gpas, pas[9:-1])
    if homeIP in homes_l and gpas == pas[9:-1]:
        # usuwanie domu u użytkownika
        IP_index = homes_l.index(homeIP)
        homes_l.pop(IP_index)
        homes_j = ";".join(homes_l)
        user_f = open(os.path.join(cwd, users, email + ".txt"), "w")
        user_f.write(pas + "homes:" + homes_j)
        user_f.close()

        # usuwanie całego domu jeżeli ostatni lub tylko użytkownika
        print(len(users_l[:-1]))
        if len(users_l[:-1]) <= 1:
            shutil.rmtree(os.path.join(cwd, homes_dir, homeIP))
        else:
            user_index = users_l.index(email)
            users_l.pop(user_index)
            home_f = open(os.path.join(cwd, homes_dir, homeIP, "inf.txt"), "w")
            home_f.write(home_lines[0]+"users:" + ";".join(users_l))
            home_f.close()

        return "1"
    else:
        return "error"


def get_homes(email):
    out = []
    cwd = os.getcwd()
    user_f = open(os.path.join(cwd, users, email + ".txt"), "r")
    homes = user_f.readlines()[1][6:]
    print(homes)
    user_f.close()
    homes = homes.split(";")[:-1]
    for homeIP in homes:
        print(homeIP)
        print(os.path.join(cwd, homes_dir, str(homeIP), "inf.txt"))
        home_f = open(os.path.join(cwd, homes_dir, str(homeIP), "inf.txt"), "r")
        home_n = home_f.readlines()[0][5:-1]
        home_f.close()
        out.append([homeIP, home_n])
    return out


def get_codes(homeIP):
    cwd = os.getcwd()
    code_dir = os.path.join(cwd, homes_dir, homeIP, "invite_codes.txt")
    code_f = open(code_dir, "r")
    code_str = code_f.read()
    code_f.close()
    return code_str


def get_chat(homeIP):
    cwd = os.getcwd()
    chat_dir = os.path.join(cwd, homes_dir, homeIP, "chat.txt")
    chat_f = open(chat_dir, "r")
    chat_lines = chat_f.readlines()
    print(chat_lines)
    chat_f.close()

    if chat_lines != []:
        return chat_lines[0]
    else:
        return ""


def add_msg(msg, homeIP, email):
    cwd = os.getcwd()
    chat_dir = os.path.join(cwd, homes_dir, homeIP, "chat.txt")
    chat_f = open(chat_dir, "a")
    chat_f.write(email+":" + msg+";")
    chat_f.close()


def add_product(product, homeIP):
    cwd = os.getcwd()
    list_dir = os.path.join(cwd, homes_dir, homeIP, "shopping_list.txt")
    list_f = open(list_dir, "a")
    list_f.write(product+";")
    list_f.close()


def get_products(homeIP):
    cwd = os.getcwd()
    list_dir = os.path.join(cwd, homes_dir, homeIP, "shopping_list.txt")
    list_f = open(list_dir, "r")
    lines = list_f.readlines()
    list_f.close()
    return lines


def update_products(homeIP, products):
    cwd = os.getcwd()
    list_dir = os.path.join(cwd, homes_dir, homeIP, "shopping_list.txt")
    list_f = open(list_dir, "w")
    list_f.write(products)
    list_f.close()


def remove_product(product, homeIP):
    cwd = os.getcwd()
    list_dir = os.path.join(cwd, homes_dir, homeIP, "shopping_list.txt")
    list_f = open(list_dir, "r")
    lines = list_f.readlines()[0]
    product_list = lines.split(";")
    list_f.close()

    try:
        i = product_list.index(product)
        product_list.pop(i)
        new_list_f = open(list_dir, "w")
        new_list_f.write(";".join(product_list))
        new_list_f.close()
        return "1"
    except ValueError:
        return "0"


def get_product_info(homeIP, name, index):
    # todo think of a more efficiant way of getting the kind although i doubt it is possible
    # getting the kind of product based on index from shopping list
    shopping_dir = os.path.join(os.getcwd(), homes_dir, homeIP, "shopping_list.txt")
    shopping_f = open(shopping_dir, "r")
    lines = shopping_f.readlines()
    kind = lines[0].split(";")[int(index)].split(":")[0]
    shopping_f.close()

    # getting all info about the given product
    dtb = Database()
    info = dtb.auchan.get_product_info(kind, name)
    info = "^".join(info)
    return info

if __name__ == "__main__":
    # debugging space
    """"
    end = False
    while not end:
        cwd = os.getcwd()
        # email = input("email:")
        # pass1 = input("pass1:")
        print(get_homes("test"))
        if input("end?") == "y":
            end = True
    """""

