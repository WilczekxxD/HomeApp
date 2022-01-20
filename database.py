from selenium import webdriver
from selenium import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

Path = "C:\Program Files (x86)\chromedriver.exe"

frisco_data = {"file": "frisco", "addr": "https://www.frisco.pl/?gclid=CjwKCAjwkdL6BRAREiwA-kiczMFr7_62jsQxMnhzWM94KfpTi8HKUi3wTsjQATuJ-6p0aCsQ09Zd8RoC5ggQAvD_BwE"}
auchan_data = {"file": "auchan", "addr": "https://www.auchandirect.pl/auchan-warszawa/pl?gclid=EAIaIQobChMIq6GI09v_6wIViNeyCh36PwZ9EAAYASAAEgI-zvD_BwE"}
carrefour_data = {"file": "carefour.txt", "addr": "https://www.carrefour.pl/?gclsrc=aw.ds&ds_rl=1262234&gclid=EAIaIQobChMInPqyg-3_6wIVCrh3Ch0YKAu5EAAYASAAEgLu3vD_BwE&gclsrc=aw.ds"}
kaufland_data = {"file": "kaufland.txt", "addr": "https://www.kaufland.pl/?cid=pl:sea:google_11141601296_107576343565&campaign=11141601296&adgroupid=107576343565&matchtype=e&network=g&keyword=kaufland&placement=&target=kwd-69869287&adposition=&creative=465829837640&aceid=&device=c&gclid=EAIaIQobChMIg5uqsJ6B7AIViPuyCh2kNQMWEAAYASAAEgI07fD_BwE"}


class Database:
    def __init__(self):
        self.frisco = self.Frisco()
        self.auchan = self.Auchan()

    class Frisco:
        def __init__(self):
            self.addr = frisco_data["addr"]
            self.file = frisco_data["file"]

        def load_data(self, list):
            driver = webdriver.Chrome(Path)
            driver.get(self.addr)
            for product in list:
                #opening file
                file_name = self.file+"/" + product + ".txt"
                f = open(file_name, "a")
                clean_file(file_name)

                search_box_class = "input-text"
                search = driver.find_element_by_class_name(search_box_class)
                search.send_keys(product)
                product_box_class = "product-box_content"
                driver.maximize_window()
                time.sleep(10)
                pList = driver.find_elements_by_class_name(product_box_class)
                addrlist = []
                for element in pList:
                    if element.find_element_by_class_name("product-box_labels").text != "Produkt polecany":
                        addrlist.append(element.find_element_by_class_name("product-box_image").get_attribute("href"))
                for adres in addrlist:
                    product_driver = webdriver.Chrome(Path)
                    product_driver.get(adres)
                    time.sleep(3)
                    product_driver.maximize_window()
                    time.sleep(1)

                    name = product_driver.find_element_by_class_name("product-page_name-box").find_element_by_xpath("//h1").text
                    f.write("#P" + name +"\n")

                    price = product_driver.find_element_by_class_name("cart-box_price").find_element_by_class_name("main-price").text
                    f.write("#L" + "price" + ";"+"\n" + price + "\n")

                    mini_notification = product_driver.find_elements_by_class_name("mini-notifications-holder")
                    mini_notification_close = mini_notification[1].find_element_by_class_name("mini-notification_close")
                    mini_notification_close.click()

                    tabs_header = product_driver.find_element_by_class_name("ui-tabs_header-inner")
                    tabs = tabs_header.find_elements_by_class_name("ui-tabs_tab")
                    tabs[1].click()
                    for x, tab in enumerate(tabs):
                        tab.click()
                        label = tab.text
                        content = product_driver.find_element_by_class_name("ui-tabs_tab-content").text
                        # "#L" po to by łatwo było znależć w pliku opis produktu bo zajmuiją wiele linijek a w ten sposób
                        # jeżeli pierwszy znak == #L to wiadomo że to nowy opis, Label
                        f.write("#L" + label + "\n" + content + "\n")
                    f.write("\n")
                    product_driver.quit()
                f.close()
                driver.close()

        def get_data(self, list):
            elements = []
            for element in list:

                f = open(self.file + "/" + element + ".txt", "r")
                products = []
                product = ""
                for line in f:

                    if line[:2] == "#P":
                        if len(product) == 0:
                            product = {"name": line[2:]}
                        else:
                            products.append(product)
                            product = {"name": line[2:]}

                    elif line[:2] == "#L":
                        label = line[2:]
                        product[label] = ""

                    else:
                        product[label] += (line)

                elements.append(products)

            for products in elements:
                for product in products:
                    for x in product:
                        print(x)

    class Auchan:
        def __init__(self):
            self.file = auchan_data["file"]
            self.addr = auchan_data["addr"]

        def load_data(self, list):

            driver = webdriver.Chrome(Path)
            driver.get(self.addr)

            for produckt in list:
                # opening file
                file_name = self.file + "/" + produckt + ".txt"
                f = open(file_name, "w", encoding='utf-8')
                clean_file(file_name)
                driver.maximize_window()
                time.sleep(1.5)
                consent = driver.find_element_by_id("onetrust-reject-all-handler")
                consent.click()
                search = driver.find_element_by_class_name("_12bN")
                search.send_keys(produckt)
                search.send_keys(Keys.RETURN)
                time.sleep(5)

                displays = driver.find_elements_by_class_name("_33Dr")
                href_list = []
                print(displays)
                for display in displays:
                    href_list.append(display.get_attribute("href"))

                for addr in href_list:

                    produckt_driver = webdriver.Chrome(Path)
                    produckt_driver.get(addr)

                    time.sleep(1)
                    name = ""

                    name = name + produckt_driver.find_element_by_xpath("//*[@id='productDetails']/div/div[1]/div/div[1]/h1").text
                    f.write("#P" + name + "\n")

                    price = produckt_driver.find_element_by_class_name("_1zsk").text
                    f.write("#L" + "price" + "\n" + price + "\n")

                    section_box = produckt_driver.find_element_by_class_name("_1TPn")
                    sections = section_box.find_elements_by_xpath("//*[@id='container']/div[2]/div/div/div[2]/div[4]/div/div/div[2]/div[1]/div/div/div")
                    print(f"sections {sections}")
                    for x, section in enumerate(sections):
                        x = str(x +1)
                        label = section.find_element_by_class_name("_238Y").text
                        f.write("#L" + label + "\n")
                        description = section.find_element_by_xpath(f"//*[@id='container']/div[2]/div/div/div[2]/div[4]/div/div/div[2]/div[1]/div/div/div[{x}]/div[2]").text
                        f.write(description + "\n")

                    produckt_driver.quit()
                f.close()
            driver.quit()

        def get_data(self, list):
            elements = []
            for element in list:

                f = open(self.file + "/" + element + ".txt", "r")
                products = []
                product = ""
                for line in f:

                    if line[:2] == "#P":
                        if len(product) == 0:
                            product = {"name": line[2:]}
                        else:
                            products.append(product)
                            product = {"name": line[2:]}

                    elif line[:2] == "#L":
                        label = line[2:]
                        product[label] = ""

                    else:
                        product[label] += (line)

                elements.append(products)

            for products in elements:
                for product in products:
                    for x in product:
                        print(x)

        def get_descriptions(self):
            names = ""
            for root, dirs, files in os.walk(os.path.join(os.getcwd(), self.file)):
                 names = files

            descriptions = []
            for name in names:

                current = [""]
                f = open(os.path.join(self.file, name), "r", encoding='utf-8')
                description = False
                for line in f:
                    if line[:2] == "#L" or line[:2] == "#P":
                        label = line[2:-1]
                        if label == "OPIS PRODUKTU":
                            description = True
                        elif line[:2] == "#P":
                            # todo current can be used with or without a label, that is products name
                            descriptions.append(current[0])
                            current = ["", label]
                            description = False
                        else:
                            description = False
                    elif description:
                        current[0] = current[0] + str(line[:-1] + " ")
                f.close()
            return descriptions

        def get_product_descriptions(self, product):
            # returns description name array

            if product[-4:] == ".txt":
                product = product[:-4]
            names = ""
            for root, dirs, files in os.walk(os.path.join(os.getcwd(), self.file)):
                names = files

            descriptions = []
            for name in names:
                if name == product+".txt":
                    current = [""]

                    f = open(os.path.join(self.file, name), "r", encoding='utf-8')
                    description = False
                    for line in f:
                        if line[:2] == "#L" or line[:2] == "#P":
                            label = line[2:-1]
                            if label == "OPIS PRODUKTU":
                                description = True
                            elif line[:2] == "#P":
                                descriptions.append(current)
                                current = ["", label]
                                description = False
                            else:
                                description = False

                        elif description:
                            current[0] = current[0] + str(line[:-1]+" ")
                    f.close()
            return descriptions

        def get_product_description_price(self, product):
            # returns description, price, name array

            if product[-4:] == ".txt":
                product = product[:-4]
            names = []
            for root, dirs, files in os.walk(os.path.join(os.getcwd(), self.file)):
                names = files

            descriptions = []
            for name in names:
                if name == product + ".txt":
                    current = [""]
                    price = ""

                    f = open(os.path.join(self.file, name), "r", encoding='utf-8')
                    description = False
                    price = False
                    for line in f:
                        if line[:2] == "#L" or line[:2] == "#P":
                            label = line[2:-1]
                            if label == "OPIS PRODUKTU":
                                description = True
                                price = False
                            # todo change either opis from All caps or price into
                            elif label == "price":
                                price = True
                                description = False
                            elif line[:2] == "#P":
                                descriptions.append(current)
                                current = ["", label]
                                description = False
                                price = False
                            else:
                                description = False
                                price = False

                        elif description:
                            current[0] = current[0] + str(line[:-1] + " ")
                        elif price:
                            current.append(line[:-1])

                    f.close()
            return descriptions

        def get_product_info(self, kind, name):
            # retrieves all label of a single product

            # getting the info of the kind of product
            kind += ".txt"
            file = open(os.path.join(os.getcwd(), self.file, kind), "r", encoding='utf-8')
            lines = file.readlines()
            file.close()

            current = "not found"
            properties = []
            i = 0
            found = False
            while not found:
                if lines[i][2:-1] == name:
                    end = False
                    current = ""
                    while not end:
                        i += 1
                        line = lines[i]
                        print(line)
                        if line[:2] == "#P":
                            end = True
                            found = True
                            properties.append(current)
                        elif line[0] == '#':
                            properties.append(current)
                            current = f"{line[2:-1].lower()};"
                        else:
                            current += f"{line[:-1]} "
                i += 1
            return properties[1:]

    # todo all of it
    class Carrefour:

        def __init__(self):
            self.file = carrefour_data["file"]
            self.addr = carrefour_data["addr"]

        def load_data(self, list):

            clean_file(self.file)
            driver = webdriver.Chrome(Path)
            driver.get(self.addr)
            driver.maximize_window()
            time.sleep(2)

            consent = driver.find_element_by_class_name("jss299").find_elements_by_class_name("MuiButtonBase-root")[0]
            consent.click()
            search = driver.find_element_by_id("search-input")

            for produckt in list:

                search.send_keys(produckt)
                search.send_keys(Keys.RETURN)

                jss_list = driver.find_elements_by_class_name("jss442")
                print(jss_list)
                href_list = []
                for jss in jss_list:
                    href_list.append(jss.find_element_by_class_name("MuiButtonBase-root MuiButton-root MuiButton-text jss522 MuiButton-textPrimary"))

                print(href_list)

    class Kaufland:

        def __init__(self):
            self.file = kaufland_data["file"]
            self.addr = kaufland_data["addr"]

        def load_data(self, list):
            driver = webdriver.Chrome(Path)
            driver.get(self.addr)


def clean_file(file_name):
    f = open(file_name, "r+")
    f.truncate(0)
    f.close()


def save_text(file_name, text):
    f = open(os.path.join(os.getcwd(), file_name), "w", encoding="utf-8")
    f.write(text)
    f.close()


def add_load(product):
    # adds a product to the beginning of load file
    f = open(os.path.join(os.getcwd(), "load.txt"), "r")
    products = f.readlines()[0].split(";")
    f.close()
    products = [product] + products
    f = open(os.path.join(os.getcwd(), "load.txt"), "w")
    f.write(";".join(products))
    f.close()


def check_load(product):
    # checks if product in loading queue
    f = open(os.path.join(os.getcwd(), "load.txt"), "r", encoding="utf-8")
    products = f.readlines()[0].split(";")
    if product not in products:
        return "error"
    return "allGood"


if __name__ == "__main__":

    list = ["wołowina"]
    database = Database()
    dsc = database.auchan.load_data(list)
    print(dsc)

    print("ended")
    #driver.quit()
