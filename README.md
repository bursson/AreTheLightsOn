# AreTheLightsOn
A simple python based Telegram Bot. Runs on [Onion Omega2](https://onion.io/) and checks if the lights are on, or when they were last on.

## Get started

Due the technical limitations of the Omega I have used a python 2.7.13-based lightweight packet called python-light.

#### Install

* Set up your Omega with https://wiki.onion.io/get-started. Make sure to upgrade to the latest firmware with `oupgrade`.
* Update your opkg and install python and some required modules with:
```
opkg update
opkg install python-light pyOnionGpio python-sqlite3 python-logging python-openssl python-codecs
```
* Clone or download this repository

* Wire your light sensor to your Omega. I used a simple Grove Light Sensor (v. 1.1) which is analog. Hooking it up to a digital pin is not a problem as we don't care about the exact reading. We just want the information if the lights are on or off. Feel free to pick any free GPIO pin as we can define it later in the configuration file.

* Create your Bot with https://core.telegram.org/bots#creating-a-new-bot.

* Rename the "default.example.ini" to "default.ini" and fill in the bot API key (token) which you acquired in phase 4. You can also specify the following things:
```
post_on_channels = 1          # 1 if the Bot is allowed to post to groups and supergroups
channel_post_interval = 60    # How often it may post to groups and supergroups if allowed
light_sensor_pin = 0          # Omega GPIO pin, where the light sensor is connected to
DEBUG = 1                     # 1 if debug is enabled
refresh_interval = 3          # How many seconds the Omega sleeps between queries
coffee_bot_url = ""           # Url for coffee monitor. Source code coming soon.
dbtype = 1                    # 1 for minimalistic solutin, 0 for a real db
```
* If your files are not located in `/root` (as they probably are not), edit the `botti.py` and replace `/root/default.ini` with the absolute path to your own `default.ini`.

* Now you can run your Bot with `python /$INSTALLDIR/botti.py`. If you message it on Telegram it should reply "Valot ovat päällä" or "Valot olivat edellisen kerran päällä *timestamp*".

* For permanent use I suggest using init scripts for launching the Bot. More info can be found at https://wiki.openwrt.org/doc/techref/initscripts. I suggest using a low START priority and a small (around 10-15 seconds) sleep before running the script. This ensures a Wifi connection is established at the time of the Bot's startup.

