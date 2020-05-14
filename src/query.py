from sql_query import database

"""Food Orders"""


def get_food_orders():
    return database.sql_get('SELECT name, item FROM food_orders ORDER BY item ASC')


def get_food_order(user, item):
    return database.sql_get('SELECT name, item FROM food_orders WHERE name=? AND item=?', (user, item))


def add_food_order(user, item, restaurant, date):
    database.sql_set(
        'INSERT OR IGNORE INTO food_orders (name, item, restaurant, "date") VALUES (?, ?, ?, ?)',
        (user, item, restaurant, date))


def remove_food_order(user, item):
    database.sql_set('DELETE FROM food_orders WHERE name=? AND item=?', (user, item))


def remove_food_orders():
    database.sql_set('DELETE FROM food_orders')


def get_food_order_items():
    return database.sql_get('SELECT item FROM food_orders GROUP BY item ORDER BY item ASC')


def get_food_order_by_user(user):
    return database.sql_get('SELECT name, item FROM food_orders WHERE name =? ORDER BY item ASC', (user,))


def remove_food_orders_by_user(user):
    database.sql_set('DELETE FROM food_orders WHERE name=?', (user,))


""""Restaurants"""


def add_restaurant(restaurant, rating, url):
    database.sql_set('INSERT OR IGNORE INTO restaurant_database (restaurant, rating, url) VALUES (?,?,?)',
                     (restaurant, rating, url))


def get_restaurants():
    return database.sql_get('SELECT restaurant, rating, url FROM restaurant_database ORDER BY rating DESC')


def get_restaurant_rating(restaurant):
    database.sql_get('SELECT rating FROM restaurant_database where ? LIKE restaurant LIMIT 1', (restaurant,))


def set_restaurant_rating(restaurant, rating):
    database.sql_set('UPDATE restaurant_database SET rating=? WHERE ? LIKE restaurant', (rating, restaurant))


"""Bug Reports"""


def add_bug_report(report, user):
    database.sql_set('INSERT OR IGNORE INTO bug_report (date, report, user_name) VALUES (CURRENT_TIMESTAMP, ?, ?)',
                     (report, user))
