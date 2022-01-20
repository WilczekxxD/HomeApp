import os
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score
from database import Database
from datetime import datetime
import pickle

ENCODING = "utf-8"


def load_classifier(homeIP):
    classifier = "classifier.pickle"
    f = open(os.path.join(os.getcwd(), "homes", homeIP, classifier), "rb")
    re = pickle.load(f)
    f.close()
    return re


def load_vectorizer(homeIP):
    # todo decide on local vs common vectorizers
    vectorizer = "vectorizer.pickle"
    f = open(os.path.join(os.getcwd(), "homes", homeIP, vectorizer), "rb")
    re = pickle.load(f)
    f.close()
    return re


def classify(homeIP, description):
    classifier = load_classifier(homeIP)
    vectorizer = load_vectorizer(homeIP)
    group = classifier.predict(vectorizer.transform([description]))

    return str(group[0])


def add_history(homeIP, description):
    group = classify(description)[0]
    path = os.path.join(os.getcwd(), "homes", homeIP, group + ".txt")
    f = open(path, "r")
    history = f.readline()[0].split(";")
    f.close()

    if len(history) >= 5:
        history = history[1:].append(description)
    else:
        history = history.append(description)

    f = open(path, "w")
    f.write(";".join(history))
    f.close()


def get_history(homeIP, group):
    path = os.path.join(os.getcwd(), "homes", homeIP, group + ".txt")
    f = open(path, "r")
    history = f.readline().split(";")
    f.close()
    return history


def suggest(homeIP, candidates, vectorizer):
    scores = []
    for description in candidates:
        # making clusters out of history and suggestion
        score = 0
        history = get_history(homeIP, classify(homeIP, description))

        for i in range(len(history)):
            data = [description, history[i], history[(i + 1) % (len(history))]]
            data = vectorizer.transform(data)
            clf = KMeans(n_clusters=2, init="k-means++", n_init=10)
            clf.fit(data)

            # scoring the candidate
            predictions = clf.predict(data)
            for prediction in predictions[1:]:
                if prediction == predictions[0]:
                    score += 1

        scores.append(score)

    return scores


# the complete scoring function, from descriptions to scores
def get_scores(homeIP, descriptions):
    vectorizer = load_vectorizer(homeIP)
    return suggest(homeIP, descriptions, vectorizer)


# loads products from homes shopping list
def load_products(homeIP):
    dtb = Database()
    f = open(os.path.join(os.getcwd(), "homes", homeIP, "shopping_list.txt"))
    lines = f.readlines()[0].split(";")[:-1]
    shopping_list = [product.split(":")[0] for product in lines]
    descriptions = []
    # if statement is used to check if the products in the list match those that are loaded form the website
    # maybe raising error would be better then returning,
    # probably not because there is no way to return the faulty index
    # TODO make it suggest the closest relative instead of returning the faulty item
    for x, item in enumerate(shopping_list):
        item_descriptions = dtb.auchan.get_product_description_price(item)[1:]
        if len(item_descriptions) != 0:
            for description in item_descriptions:
                description.append(str(x))
            descriptions.append(item_descriptions)
        else:
            return f"error;{item};{x}"
    return descriptions


def my_key(item):
    return item[-1]


# converts homes shoppping list into sorted lists of suggestions
def convert(homeIP):
    all_descriptions = load_products(homeIP)
    if all_descriptions[:5] == "error":
        # todo there is a faulty item in the list
        return all_descriptions

    suggestions = []
    for product in all_descriptions:
        names = [description[1] for description in product]
        # todo it looks odd to look for prices in description so it should be re factorised
        prices = [description[-2] for description in product]
        descriptions = [description[0] for description in product]
        indexes = [description[-1] for description in product]

        scores = get_scores(homeIP, descriptions)

        # combining scores and names of products
        combined = []
        for x in range(len(names)):
            combined.append([names[x], prices[x], indexes[x], str(scores[x])])
        combined.sort(key=my_key)
        suggestions.append(combined)

    # changing it from list into string form so it can be send
    converted = ""
    for product in suggestions:
        for x, suggestion in enumerate(product):
            product[x] = ":".join(suggestion)
        product = ";".join(product)
        converted += product + "\n"
    return converted


if __name__ == "__main__":
    # print(suggest(history, candidates, vectorizer), "out of", len(history))
    print(convert("0000000013"))
