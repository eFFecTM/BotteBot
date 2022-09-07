import asyncio
import hashlib
import json
import logging
import threading
import urllib.parse

import tzlocal
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from slack_sdk.rtm_v2 import RTMClient

import admin_bot
import food_bot
import query
import random_bot
import services_helper
from constants import slack_bot_token, weekday, where_time, what_time, template_modal, template_modal_flattext

logger = logging.getLogger()
rtm_client = RTMClient(token=slack_bot_token)


async def start_scheduler():
    try:
        scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
        scheduler.add_job(services_helper.print_where_food_notification,
                          CronTrigger(day_of_week=weekday, hour=where_time.split(":")[0],
                                      minute=where_time.split(":")[1]))
        scheduler.add_job(services_helper.print_what_food_notification,
                          CronTrigger(day_of_week=weekday, hour=what_time.split(":")[0],
                                      minute=what_time.split(":")[1]))
        scheduler.add_job(services_helper.get_users_and_channels_info,
                          CronTrigger(day_of_week=weekday, hour="03", minute="00"))
        # scheduler.add_job(food_bot.update_restaurant_database, CronTrigger(day_of_week="wed", hour="09")) # Not needed as Takeaway scraping is broken
        food_bot.get_restaurants_from_takeaway()
        scheduler.add_job(admin_bot.reset_orders, CronTrigger(day_of_week="wed", hour="23", minute="59"))
        scheduler.start()
        logger.info('Started APScheduler!')
    except Exception as e:
        logger.exception(e)


async def start_slack_client():
    thread = threading.Thread(target=start_slack_thread, daemon=True)
    thread.start()
    try:
        services_helper.init(rtm_client.web_client)
        random_bot.init()  # initialize runtime variables
    except Exception as e:
        logger.exception(e)
    while True:
        await asyncio.sleep(60)


def start_slack_thread():
    global rtm_client
    try:
        logger.info('Connected to Slack!')
        rtm_client.start()
    except Exception as e:
        logger.exception(e)


@rtm_client.on("message")
def handle(client: RTMClient, event: dict):
    if 'text' in event:
        try:
            if 'user' in event:
                services_helper.receive_message(event['user'], event['text'], event['channel'], event['ts'])
        except Exception as e:
            logger.exception(e)


async def start_web_server():
    try:
        app = web.Application()
        app.add_routes([web.post('/slack/interactive-endpoint', interactive_message)])
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, '*', 3000)
        await site.start()
        logger.info('Started AIOHTTP Server!')
    except Exception as e:
        logger.exception(e)


async def interactive_message(request):
    try:
        logger.debug("Receiving request from Slack: {}".format(str(request)))
        if request.body_exists:
            body = await request.text()
            body = urllib.parse.unquote_plus(body)
            if body.startswith("payload="):
                data = json.loads(body[8:])
                user = services_helper.get_user_info(data["user"]["id"])["user"]["real_name"]
                if data["type"] == "block_actions":
                    if len(data["actions"]) == 1:
                        action_text = data["actions"][0]["text"]["text"]
                        services_helper.last_channel_id = data["channel"]["id"]
                        services_helper.last_block_message_ts = data["message"]["ts"]
                        if action_text == "Manage Your Options":  # user is adding a new option / managing existing ones
                            logger.debug("Manage Your Options")
                            blocks = {"blocks": []}
                            food_bot.add_modal_question(blocks, "Add a new option")
                            dropdown = food_bot.create_modal_dropdown("Pick from existing options")
                            orders = query.get_food_order_items()
                            my_orders = query.get_food_order_by_user(user)

                            if orders:
                                dropdown["element"]["options"] = []
                                for [item] in orders:
                                    food_bot.add_dropdown_option(dropdown, False, item)
                                if my_orders:
                                    dropdown["element"]["initial_options"] = []
                                    for [_, item] in my_orders:
                                        food_bot.add_dropdown_option(dropdown, True, item)
                                blocks["blocks"].append(dropdown)
                            template_modal["blocks"] = blocks["blocks"]
                            services_helper.open_view(data["trigger_id"], template_modal)
                            logger.debug("Opening modal for user {}".format(user))
                        elif action_text == "View All Orders as Text":
                            logger.debug("View as Text")
                            template_modal_flattext["blocks"][0]["text"]["text"] = food_bot.get_order_overview(True)
                            logger.debug("Got order overview")
                            services_helper.open_view(data["trigger_id"], template_modal_flattext)
                            logger.debug("Opening modal for user {}".format(user))
                        else:
                            logger.error("Unknown action {}", action_text)
                elif data["type"] == "view_submission":  # user is submitting the order through the modal
                    new_order = orders = None
                    try:
                        block_id_0 = data["view"]["blocks"][0]["block_id"]
                        action_id_0 = data["view"]["blocks"][0]["element"]["action_id"]
                        new_order = data["view"]["state"]["values"][block_id_0][action_id_0]["value"]
                    except (KeyError, IndexError):
                        pass
                    try:
                        block_id_1 = data["view"]["blocks"][1]["block_id"]
                        action_id_1 = data["view"]["blocks"][1]["element"]["action_id"]
                        orders = data["view"]["state"]["values"][block_id_1][action_id_1]["selected_options"]
                    except (KeyError, IndexError):
                        pass
                    # remove all orders from the user and add the ones selected
                    items = query.get_food_order_items()
                    query.remove_food_orders_by_user(user)
                    if orders:
                        for order in orders:
                            output = None
                            for [item] in items:
                                if order["value"] == hashlib.sha256(item.encode('utf-8')).hexdigest():
                                    output, success = food_bot.order_food(user, item)
                                    break
                            if not output:
                                logger.warning("Cannot find item with name {} and checksum {}. Adding as new order.".format(order["text"]["text"], order["value"]))
                                food_bot.order_food(user, order["text"]["text"])
                    # add a new order if it was filled in
                    if new_order:
                        food_bot.order_food(user, new_order)
                    blocks = food_bot.get_order_overview(False)
                    services_helper.update_message(blocks=json.dumps(blocks["blocks"]))
                    logger.debug("Order from modal accepted, updating message for user {}".format(user))
        return web.Response()
    except Exception as e:
        logger.exception(e)
