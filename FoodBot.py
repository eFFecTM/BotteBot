from pathlib import Path

from _datetime import datetime

current_food_place = "Pizza Hut"
current_orders = []
polls_path = "data/polls/"
orders_path = "data/orders/"


def process_call(user, input_text, channel):
    input_array = input_text.split(" ")
    if len(input_array) >= 2 and input_array[1].lower() == "overview":
        output_text = get_overview()
    elif len(input_array) >= 3 and input_array[1].lower() == "order":
        input_array.pop(0)
        input_array.pop(0)
        output_text = order_food(user, input_array)
    else:
        output_text = "??????????????"

    return output_text


def get_overview():
    output_text = ""
    output_text += "From where do you want some food? " + current_food_place
    output_text += "\n\n\n"
    for (user, order) in current_orders:
        output_text += user + " orders the following: " + order + "\n"

    return output_text


def get_menu():
    pass


def order_food(user, values):
    food = " ".join(values)
    current_orders.append((user, food))
    save_orders(user, food)
    return "Order placed: " + food


def read_current_day_data():
    if len(current_orders) == 0:
        today = datetime.now().strftime("%Y%m%d")
        order_path = Path(orders_path + today + "_orders.txt")
        if order_path.is_file():
            order_file = open(order_path, "r")
            lines = order_file.readlines()
            for line in lines:
                elements = line.strip().split(";")
                current_orders.append((elements[0], elements[1]))
                print(elements)
    # expand when polls are used


def save_orders(user, food):
    today = datetime.now().strftime("%Y%m%d")
    file_orders = open(orders_path + today + "_orders.txt", "a+")
    file_orders.write(user + ";" + food + "\n")
    file_orders.close()


def save_polls():
    today = datetime.now().strftime("%Y%m%d")
    file_polls = open(polls_path + today + "_polls.txt", "a+")
    file_polls.write("template")
    file_polls.close()

