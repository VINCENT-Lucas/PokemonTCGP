import os

with open("owned.txt", "r") as file:
    content = file.read()
    cards_list = eval(content)

print(cards_list)


cards = range(239)