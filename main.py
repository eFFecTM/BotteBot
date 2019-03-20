export SLACK_BOT_TOKEN="xoxb-175230034435-584636481942-VvmeNSsBMlqUDtQ3HDnFXmol"

self.slackbot = SlackClient(str(self.config.get('slackbot', 'api_key')))

self.slackbot.send_message(self.slack_channel, message)

