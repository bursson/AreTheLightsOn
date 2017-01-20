# -*- coding: utf-8 -*-
"""
A simple Telegram bot

"""

import urllib
import time
import ConfigParser
import json
import onionGpio

CFG = ConfigParser.RawConfigParser()
# Use absolute path to your script when using init.d
CFG.read('/root/default.ini')

DEBUG = int(CFG.get("cfg", "DEBUG"))

def loop():
    """ Main loop running the bot """
    # Initialize the light sensor. Note that the Gpio library
    # returns strings...
    sensorpin = CFG.get("cfg", "light_sensor_pin")
    sensor = onionGpio.OnionGpio(int(sensorpin))
    status = int(sensor.setInputDirection())
    # Check sensor status
    if status == 0:
        print "Sensor ok"
    if status == -1:
        print "Error"
        return 1

    # The id of the next message wanted
    msg_id = 0
    # Timestamp of the last message to a group
    last_public = 0

    while status == 0:
        # Get a new messages from server
        new_msg = recieve(msg_id)

        if len(new_msg) > 0:
            # Handle the messages and get return parameters
            param = handle(new_msg, last_public, int(sensor.getValue()))
            # Update the ID of the next wanted message
            if param[0] >= 0:
                msg_id = param[0]
            # Update the timestamp of last group message
            last_public = param[1]

        time.sleep(float(CFG.get("cfg", "refresh_interval")))

def send(text, reciever):
    """ Send a Telegram message """
    # Set destination URL here
    url = 'https://api.telegram.org/' + CFG.get("botapi", "api_key") + '/sendMessage'
    # Set POST fields here
    post_fields = urllib.urlencode({'text': text, 'chat_id' : reciever})
    if DEBUG:
        print reciever
    # TODO implement check of send was OK
    urllib.urlopen(url, post_fields)

def recieve(offset):
    """ Check for incoming messages """
    url = 'https://api.telegram.org/'+ CFG.get("botapi", "api_key") + '/getUpdates'
    post_fields = urllib.urlencode({'offset': int(offset), 'allowed_updates': ["message"]})
    if DEBUG:
        print "offset is", offset
    jsoni = urllib.urlopen(url, post_fields)
    info = json.load(jsoni)
    return info['result']

def handle(messages, last_group_post, light_status):
    """ Handles an array of messages """
    result = [-1, last_group_post]
    # Iterate through recieved messages
    for i in range(0, len(messages)):
        if i >= len(messages):
            if DEBUG:
                print "No object"
            if i > 0:
                result[0] = messages[i-1]['message']['update_id']+1
            break
        obj = messages[i]
        if DEBUG:
            print obj
        if not "text" in obj['message'].keys():
            if DEBUG:
                print "Not a text message"
            result[0] = obj["update_id"]+1
            continue
            # Check if the message contained a command for us
        if (obj['message']['text'].lower() == '/valot') or \
         (obj['message']['text'].lower() == '/valot@pkvalobot'):
            # Check if the message was on a channel and if the bot is allowed to respond
            if (int(CFG.get("cfg", 'post_on_channels'))) and \
            ((obj['message']['chat']['type'] == 'group') or \
            (obj['message']['chat']['type'] == 'supergroup')) and \
            (time.time() - last_group_post > int(CFG.get("cfg", 'channel_post_interval'))):
                if DEBUG:
                    print "Posting to group", obj['message']['chat']['id']
                last_group_post = time.time()
                if light_status:
                    send("Valot ovat päällä", obj['message']['chat']['id'])
                else:
                    send("Valot eivät ole päällä", obj['message']['chat']['id'])
            # Respond in private chat
            elif int(light_status):
                send("Valot ovat päällä", obj['message']['from']['id'])
            else:
                send("Valot eivät ole päällä", obj['message']['from']['id'])
        result[0] = obj["update_id"]+1
    result[1] = (last_group_post)
    return result

print "Starting the bot"
loop()
print "Bot exited"
