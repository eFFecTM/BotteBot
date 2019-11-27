import json
import urllib.parse

import slack
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import FoodBot
import Globals
import Helper


async def start_scheduler():
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(Helper.print_where_food_notification,
                          CronTrigger(day_of_week="wed", hour=Globals.where_time.split(":")[0],
                                      minute=Globals.where_time.split(":")[1]))
        scheduler.add_job(Helper.print_what_food_notification,
                          CronTrigger(day_of_week="wed", hour=Globals.what_time.split(":")[0],
                                      minute=Globals.what_time.split(":")[1]))
        scheduler.add_job(FoodBot.update_restaurant_database, CronTrigger(day_of_week="wed", hour="09"))
        scheduler.add_job(FoodBot.remove_orders, CronTrigger(day_of_week="wed", hour="23", minute="59"))
        scheduler.start()
        Globals.logger.info('Started APScheduler!')
    except Exception as e:
        Globals.logger.exception(e)


async def start_slack_client():
    rtm_client = slack.RTMClient(token=Globals.SLACK_BOT_TOKEN, run_async=True)
    await rtm_client.start()
    Globals.logger.info('Connected to Slack!')


@slack.RTMClient.run_on(event='hello')
def on_message(**payload):
    try:
        Globals.web_client = payload['web_client']
        # Get all user IDs and channel IDs
        Globals.bot_id = Globals.web_client.auth_test()["user_id"]
        Globals.user_ids = [element["id"] for element in Globals.web_client.users_list()["members"]]
        Globals.public_channel_ids = [element["id"] for element in Globals.web_client.channels_list()["channels"]]
    except Exception as e:
        Globals.logger.exception(e)


@slack.RTMClient.run_on(event='message')
def on_message(**payload):
    try:
        data = payload['data']
        message = attachments = blocks = None
        if "user" in data:
            user_id, text_received, channel_read = data['user'], data['text'], data['channel']
            if user_id != Globals.bot_id:
                user_name = Globals.web_client.users_info(user=user_id)["user"]["name"]
                words_received = text_received.lower().split()
                if Globals.delivery:
                    message = Globals.delivery
                    channel = Globals.delivery_channel
                    Globals.delivery = None
                    Globals.delivery_channel = None
                else:
                    [channel, words_received] = Helper.check_channel(words_received, channel_read)
                    [words_received, mention] = Helper.filter_ignore_words(words_received, Globals.ignored_words)
                    if not message and (mention or (channel not in Globals.public_channel_ids)):
                        message, attachments, blocks = Helper.mention_question(user_name, words_received, channel, message)
                    if not message:
                        message, channel = Helper.check_random_keywords(user_name, words_received, channel, message)
                if message or attachments or blocks:
                    if blocks is not None:
                        blocks = json.dumps(blocks["blocks"])
                    Helper.send_message(channel, message, attachments, blocks)
    except Exception as e:
        Globals.logger.exception(e)


async def start_web_server():
    try:
        app = web.Application()
        app.add_routes([web.post('/slack/interactive-endpoint', interactive_message)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '*', 3000)
        await site.start()
        Globals.logger.info('Started AIOHTTP Server!')
    except Exception as e:
        Globals.logger.exception(e)


async def interactive_message(request):
    try:
        Globals.logger.debug("Receiving request from Slack: {}".format(str(request)))
        update = None
        if request.body_exists:
            body = await request.text()
            body = urllib.parse.unquote_plus(body)
            if body.startswith("payload="):
                data = json.loads(body[8:])
                user = data["user"]["name"]
                if data["type"] == "block_actions":
                    if len(data["actions"]) == 1:
                        action_text = data["actions"][0]["text"]["text"]
                        if action_text == "Add Option":  # user is adding a new option
                            template_modal = json.load(open("data/template_modal.json"))
                            blocks = {"blocks": []}
                            FoodBot.add_modal_question(blocks, "What do you want to order? (single item)")
                            template_modal["blocks"] = blocks["blocks"]
                            Globals.web_client.views_open(trigger_id=data["trigger_id"], view=template_modal)
                            Globals.logger.debug("Opening modal for user {}".format(user))
                        elif action_text == "View as Text":
                            template_modal_flattext = json.load(open("data/template_modal_flattext.json"))
                            template_modal_flattext["blocks"][0]["text"]["text"] = FoodBot.get_order_overview(True)
                            Globals.web_client.views_open(trigger_id=data["trigger_id"], view=template_modal_flattext)
                            Globals.logger.debug("Opening modal for user {}".format(user))
                        else:  # user is voting on an existing option
                            block_id = data["actions"][0]["block_id"]
                            block_list = data["message"]["blocks"]
                            for block in block_list:
                                if block["type"] == "section" and block["block_id"] == block_id:
                                    food = block["accessory"]["text"]["text"]
                                    update = FoodBot.vote_order_food(user, food)
                                    break
                            if update:
                                blocks = FoodBot.get_order_overview(False)
                                Helper.update_message(data["message"]["ts"], data["channel"]["id"], None,
                                                      json.dumps(blocks["blocks"]))
                                Globals.logger.debug("Updating message for user {}".format(user))
                elif data["type"] == "view_submission":  # user is submitting the order through the modal
                    block_id = data["view"]["blocks"][0]["block_id"]
                    action_id = data["view"]["blocks"][0]["element"]["action_id"]
                    order = data["view"]["state"]["values"][block_id][action_id]["value"]
                    output, success = FoodBot.order_food(user, order)
                    if success:
                        blocks = FoodBot.get_order_overview(False)
                        Helper.update_message(Globals.last_message_ts, Globals.last_channel_id, None,
                                              json.dumps(blocks["blocks"]))
                        Globals.logger.debug("Order from modal accepted, updating message for user {}".format(user))
                    else:
                        Helper.send_message(Globals.last_channel_id, output, None, None)
        return web.Response()
    except Exception as e:
        Globals.logger.exception(e)
