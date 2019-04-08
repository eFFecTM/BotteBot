current_food_place = "Pizza Hut"
current_orders = []


def process_call(user, input_text, channel):

    if "overview" in input_text:
        output_text = get_overview()
    elif "order" in input_text:
        output_text = order_food(user, input_text)
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


def order_food(user, input_text):
    values = input_text.split(" ")
    values.pop(0)
    values.pop(0)
    current_orders.append((user, " ".join(values)))
    return "Order placed: " + " ".join(values)
