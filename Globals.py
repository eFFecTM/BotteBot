def init():
    global web_client
    global bot_id
    global user_ids
    global public_channel_ids
    global last_message_ts
    global last_channel_id
    global counter_joke
    global logger
    global notification_channel, where_time, what_time
    global ignored_words
    global delivery, delivery_channel
    global counter_threshold
    global translator
    global stop
    global SLACK_BOT_TOKEN
    global API_KEY
    global previous_joke
    global oxford
    global current_food_place
    global is_imaginelab
    global database
    global weather_triggers, insult_triggers, lmgtfy_triggers, def_triggers, food_triggers, repeat_triggers, \
        image_triggers, help_triggers, joke_triggers, resto_triggers, menu_triggers, set_triggers, overview_triggers,\
        order_triggers, schedule_triggers, add_triggers, remove_triggers, rating_triggers, no_imaginelab_triggers, \
        bugreport_triggers

    web_client = None
    bot_id = None
    user_ids = None
    public_channel_ids = None
    last_message_ts = None
    last_channel_id = None
    counter_joke = 0
    logger = None
    notification_channel = where_time = what_time = None
    ignored_words = None
    delivery = None
    delivery_channel = None
    counter_threshold = None
    translator = None
    stop = None
    SLACK_BOT_TOKEN = None
    API_KEY = None
    previous_joke = None
    oxford = None
    current_food_place = "..."
    is_imaginelab = None
    database = None

    weather_triggers = None
    insult_triggers = None
    lmgtfy_triggers = None
    def_triggers = None
    food_triggers = None
    repeat_triggers = None
    image_triggers = None
    help_triggers = None
    joke_triggers = None
    resto_triggers = None
    menu_triggers = None
    set_triggers = None
    overview_triggers = None
    order_triggers = None
    schedule_triggers = None
    add_triggers = None
    remove_triggers = None
    rating_triggers = None
    no_imaginelab_triggers = None
    bugreport_triggers = None
