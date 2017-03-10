#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A simple Telegram bot

"""

import urllib
import time
import ConfigParser
import json
import logging
import sys
import socket
from database import Database
import onionGpio


reload(sys)
sys.setdefaultencoding('utf-8')
socket.setdefaulttimeout(2)

logging.basicConfig(filename='/root/botti.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')
logging.debug('Starting')

CFG = ConfigParser.RawConfigParser()
# Use absolute path to your script when using init.d
CFG.read('/root/default.ini')

DEBUG = int(CFG.get("cfg", "DEBUG"))

def init():
    """ Initialize the bot by creating or connecting to a database """
    database = Database("bot.db", int(CFG.get("cfg", "dbtype")))
    return database

def loop(database):
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
    # Get the refresh interval from Config
    refresh_interval = float(CFG.get("cfg", "refresh_interval"))

    while status == 0:
        lights = int(sensor.getValue())
        # TODO: Implement projector current sensing
        projector = 0
        timestamp = time.time()
        database.addData(timestamp, lights, projector)
        # Get a new messages from server
        new_msg = recieve(msg_id)

        if len(new_msg) > 0:
            # Handle the messages and get return parameters
            param = handle(new_msg, last_public, lights, database)
            # Update the ID of the next wanted message
            if param[0] >= 0:
                msg_id = param[0]
            # Update the timestamp of last group message
            last_public = param[1]

        time.sleep(refresh_interval)

def send(text, reciever):
    """ Send a Telegram message """
    # Set destination URL here
    url = 'https://api.telegram.org/' + CFG.get("botapi", "api_key") + '/sendMessage'
    # Set POST fields here
    post_fields = urllib.urlencode({'text': text, 'chat_id' : reciever})
    if DEBUG:
        print reciever
    # Try to send the message
    try:
        result = json.load(urllib.urlopen(url, post_fields))
    except IOError as ex:
        print "Check your internet connection and bot API-key: ", ex
        return 1
    if result['ok'] is True:
        return True
    else:
        print ("Message send failed:"), result
        return False

def recieve(offset):
    """ Check for incoming messages """
    url = 'https://api.telegram.org/'+ CFG.get("botapi", "api_key") + '/getUpdates'
    post_fields = urllib.urlencode({'offset': int(offset), 'allowed_updates': ["message"]})
    jsoni = urllib.urlopen(url, post_fields)
    info = json.load(jsoni)
    if DEBUG:
        print "offset is", offset
        print info
    return info['result']


def handle(messages, last_group_post, light_status, database):
    """ Handles an array of messages """
    result = [-1, last_group_post]
    # Iterate through recieved messages
    for i in range(0, len(messages)):
        # Double check that there is messages
        if i >= len(messages):
            if DEBUG:
                print "No object"
            if i > 0:
                result[0] = messages[i-1]['message']['update_id']+1
            break
        obj = messages[i]

        # Update the ID to remember which messages have been processed
        result[0] = obj["update_id"]+1
        if DEBUG:
            print obj

        # If the message is not text, skip
        if not "text" in obj['message'].keys():
            if DEBUG:
                print "Not a text message"
            continue

        # Check if the message contained a command for us
        command = obj['message']['text'].lower()

        # Command to tell light status
        msg = ""
        if command == '/valot' or command == '/valot@pkvalobot':

            if int(light_status):
                msg = "Valot ovat päällä"
            else:
                last = database.lastLights()
                msg = "".join("Valot olivat edellisen kerran päällä " + str(last))
        # Command to tell coffee status
        elif command == '/kahvi' or command == '/kahvi@pkvalobot':
            keitto, levy = getcoffee()
            msg = "".join("Keitetty: " + keitto + "\nLevy viimeksi päällä: " + levy)

        # Not a command, skip
        else:
            continue
        # Check if we want to respond to the poster or to a channel
        if (int(CFG.get("cfg", 'post_on_channels'))) and \
            ((obj['message']['chat']['type'] == 'group') or \
            (obj['message']['chat']['type'] == 'supergroup')) and \
            (time.time() - last_group_post > int(CFG.get("cfg", 'channel_post_interval'))):
            # To a chat
            addr = obj['message']['chat']['id']
            last_group_post = time.time()
        else:
            # To the poster
            addr = obj['message']['from']['id']
        # If we got a message and a destination, try to send
        if addr and msg:
            try:
                send(msg, addr)
            except IOError as ex:
                logging.debug("Message send failed!")
                logging.debug(ex)
                # Message respond failed, mark message as unhandled
                result[0] = result[0]-1
                break
    result[1] = (last_group_post)
    return result

def getcoffee():
    """ Get coffee status """
    url = CFG.get("cfg", 'coffee_bot_url')
    try:
        result = json.load(urllib.urlopen(url))
        result = result[0]
        return result['keitto'], result['levy']
    except IOError:
        logging.debug("No result from coffee sensor")
        return "kahvisensori ei vastannut", "kahvisensori ei vastannut"

logging.debug("Starting the bot")

def main(db):
    try:
        loop(db)
    except Exception as ex:
        logging.debug(ex)
        main(db)
        

main(init())
logging.debug("Bot exited")
