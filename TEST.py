import os

wszystko = ""
end = False
while not end:
    a = input("podaj liczby: ")
    if a == "":
        end = True
    else:
        wszystko +=  a
print(wszystko)

