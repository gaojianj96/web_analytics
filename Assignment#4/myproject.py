import requests
from flask import Flask, request, Response
import HTMLParser
import stack_search_API
import weather_coord as weather
import time,random
import logging
from logging.handlers import RotatingFileHandler

application = Flask(__name__)

# FILL THESE IN WITH YOUR INFO
my_bot_name = 'jjg_bot' #e.g. zac_bot
my_slack_username = 'jerry_jianjiegao' #e.g. zac.wentzell
my_IP='54.213.133.175'
color_hex_list=["#ff0000","#ffa600","#ffff00","#00ff00","#006600","#0000ff","#cc00cc"]

slack_inbound_url = 'https://hooks.slack.com/services/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'#zac
# slack_inbound_url = 'https://hooks.slack.com/services/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'#own

# this handles POST requests sent to your server at SERVERIP:41953/slack
@application.route('/slack', methods=['POST'])
def inbound():
    delay = random.uniform(0, 10)
    time.sleep(delay)
    application.logger.debug( '========POST REQUEST @ /slack=========')
    response = {'username': my_bot_name, 'icon_emoji': ':snowman:', 'text': '','attachments':[]}
    application.logger.debug( 'FORM DATA RECEIVED IS:')
    application.logger.debug( request.form)

    channel = request.form.get('channel_name') #this is the channel name where the message was sent from
    username = request.form.get('user_name') #this is the username of the person who sent the message
    text = request.form.get('text') #this is the text of the message that was sent
    inbound_message = username + " in " + channel + " says: " + text
    application.logger.info( '\n\nMessage:\n' + inbound_message)

    if username in [my_slack_username, 'zac.wentzell']:
        # Your code for the assignment must stay within this if statement
        text=HTMLParser.HTMLParser().unescape(text)
        # A sample response:
        if text == "What's your favorite color?":
        # you can use print statments to debug your code
            application.logger.info( 'Bot is responding to favorite color question')
            response['text'] = 'Blue!'
            application.logger.info( 'Response text set correctly')
        # Task 1
        elif text.strip() == "<BOTS_RESPOND>":
            response['text'] = 'Hello, my name is {}. I belong to {}. I live at {}'.format(my_bot_name, my_slack_username,
                                                                                           my_IP)
        # Task 2,3
        elif text.startswith('<I_NEED_HELP_WITH_CODING>'):
            application.logger.debug( 'Success Repond <I_NEED_HELP_WITH CODING>')
            texts = text.split(':')
            question_text = ''
            for index in range(1, len(texts)):
                question_text += texts[index]
            application.logger.info( 'Question is' + question_text)
            search_result = stack_search_API.stack_search(question_text)
            response_text = []
            print "searchResult_LEN:"+str(len(search_result))
            if len(search_result)>0:
                for index,row in enumerate(search_result):
                    attach={"color":color_hex_list[index],
                            "title": row[0],
                            "title_link":row[1],
                            "fields": [{
                        "value": "{} responses, {}".format(row[2], row[3]),
                        "short": False}]}
                    response['attachments'].append(attach)
                    response['text'] = 'Here are '+str(len(search_result))+' results:'
            else:
                response['text'] = '*No answered result is suitable for your question!*'
                application.logger.info( response_text)
        #Task4
        elif text.startswith("<WHAT'S_THE_WEATHER_LIKE_AT>"):
            location=text.strip().split(':')[1].strip()
            rep_msg,fields=weather.get_wether(location)
            response["attachments"]=fields
            if rep_msg!=None and rep_msg!="":
                response['text']=rep_msg+"\n"
            response['text']+="Basic weather info:"
        elif text in ['hello', 'help', 'hi']:
            response['text'] = 'Hello! I\'m jgao_bot. What you want?'
        else:
            return Response(), 200

        if slack_inbound_url and response['text']:
            application.logger.debug("ChatBot's response is:\n" + str(response))
            r = requests.post(slack_inbound_url, json=response)

        application.logger.debug( '========REQUEST HANDLING COMPLETE========\n\n')

    return Response(), 200


# this handles GET requests sent to your server at SERVERIP:41953/
@application.route('/', methods=['GET'])
def test():
    return Response('Your flask app is running!')

if __name__ == "__main__":
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler_log = RotatingFileHandler("log_chatbot.log", maxBytes=10000000, backupCount=5)
    handler_console=logging.StreamHandler()

    handler_log.setLevel(logging.DEBUG)
    handler_console.setLevel(logging.INFO)

    handler_log.setFormatter(formatter)
    application.logger.addHandler(handler_log)
    application.logger.addHandler(handler_console)

    application.run(host='0.0.0.0', port=41953)