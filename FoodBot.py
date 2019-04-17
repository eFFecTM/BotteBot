from _datetime import datetime

current_food_place = "Pizza Hut"
current_orders = []


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
    current_orders.append((user, " ".join(values)))
    return "Order placed: " + " ".join(values)


def save_data():
    today = datetime.now().strftime("%Y%m%d")
    file_polls = open("data/polls/" + today + "_polls", "w")
    file_polls.write("template")
    file_polls.close()

    file_orders = open("data/orders/" + today + "_orders", "w")
    for (user, order) in current_orders:
        file_orders.write(user + ";" + order + "\n")
    file_polls.close()