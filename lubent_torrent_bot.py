import telepot
import random
import time
import os

import netifaces
import re
from time import gmtime, strftime
from textwrap import dedent

from subprocess import PIPE, Popen

from json import load
from urllib2 import urlopen

import logging

try:
	### load config file
	config = load(open('config_torrent_bot.json'))

	### allowed chat IDs
	lubent_chatID = config["allowed_telegram_chat_id"]

	### Transmission credentials
	transmissionCredentials = config["transmission_credentials"]

	### SUDO password
	sudoPassword = config["sudo_password"]

	### log file
	logFile = config["log_file"]

	### create Telegram bot
	bot = telepot.Bot(config["telegram_bot_key"])

except Exception as e:
	print(e)

def risp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	sender_id = msg['from']['id']
	sender_username = msg['from']['username']
	sender_firstname = msg['from']['first_name']
	sender_lastname = msg['from']['last_name']
	cmd = msg['text']

	if sender['id'] != int(lubent_chatID):
		logging.warning('Unauthorized user tryed to access to TorrentBot. TelegramID=%s - %s %s (%s)', sender_username, sender_firstname, sender_lastname, sender_id)
		bot.sendMessage(chat_id, "You are not allowed to use this bot")
		bot.sendMessage(int(lubent_chatID), "Unauthorized user tryed to access to TorrentBot. TelegramID=%s - %s %s (%s)", sender_username, sender_firstname, sender_lastname, sender_id)
		Termination()

	if cmd == '/start':
		Start(msg)
	elif cmd == '/help':
		PrintHelp(msg)
	elif cmd == '/random':
		AskRandom(msg)
	elif cmd == '/showPrivateIP':
		ShowPrivateIp(msg)
	elif cmd == '/showPublicIP':
		ShowPublicIp(msg)
	elif cmd == '/torrents':
		TorrentList(msg)
	elif cmd == '/shutdown':
		ShutdownTorrentServer(msg)
	elif cmd == '/reboot':
		RebootTorrentServer(msg)
	elif cmd == '/torrentStart':
		StartTorrentService(msg)
	elif cmd == '/torrentStop':
		StopTorrentService(msg)
	elif cmd == '/statistics':
		TorrentServiceStatistics(msg)
	elif cmd == '/whoami':
		WhoAmI(msg)
	elif cmd == '/chat_id':
		ChatID(msg)
	elif cmd == '/tortoiseON':
		AlternativeSpeedON(msg)
	elif cmd == '/tortoiseOFF':
		AlternativeSpeedOFF(msg)
	elif cmd == '/tortoiseOFF':
		AlternativeSpeedOFF(msg)
	elif cmd == '/nightmodeToggle':
		NightModeON_OFF(msg)
	elif cmd == '/nightmodeRead':
		NightModeReadStatus(msg)
	elif cmd.startswith('/add magnet:'):
		AddTorrentFile(msg)
	else:
		UnknownCommand(msg)


def Start(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	logging.info('%s(%s) started a new chat with TorrentBot', sender['username'], sender['id'])
	bot.sendMessage(chat_id, "Welcome")
	bot.sendMessage(chat_id, "Use /help to print menu")

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

def PrintHelp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	h = dedent("""Menu for Lubent Torrent Bot:
	/help prints help menu
	/random for a random number
	/showPrivateIP LAN IP
	/showPublicIP public IP
	/whoami your username\n
	/chat_id Telegram chatID\n
	/torrents torrent list
	/statistics of the torrent service\n
	/nightmodeRead nightmode status
	/nightmodeToggle nightmode ON/OFF
	/tortoiseON alternative speed ON
	/tortoiseOFF alternative speed OFF\n
	/torrentStart torrent service
	/torrentStop torrent service\n
	/add <magnetURL>\n
	/reboot torrent server
	/shutdown torrent server""")
	bot.sendMessage(chat_id, h)
	logging.info('%s(%s) printed help menu', sender['username'], sender['id'])

def UnknownCommand(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	bot.sendMessage(chat_id, "I don't know this command")
	logging.error('%s(%s) typed unknown command: "%s"', sender['username'], sender['id'], msg['text'])

def AskRandom(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	number = random.randint(1,1000)
	bot.sendMessage(chat_id, number)
	logging.info('%s(%s) asked a new random number: %s', sender['username'], sender['id'], str(number))

def ShowPrivateIp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	netifaces.ifaddresses('enp0s4')
	ip = netifaces.ifaddresses('enp0s4')[2][0]['addr']
	bot.sendMessage(chat_id, "The torrent server is connected at " + ip)
	logging.info('%s(%s) read telegram server IP: %s', sender['username'], sender['id'], ip)

def ShowPublicIp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	ip = load(urlopen('http://httpbin.org/ip'))['origin']
	bot.sendMessage(chat_id, "The torrent server is connected at " + ip)
	logging.info('%s(%s) read telegram server PublicIP: %s', sender['username'], sender['id'], ip)

def WhoAmI(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	bot.sendMessage(chat_id, "You are " + sender['first_name'] + " (" + sender['username'] + ")")
	logging.info('%s(%s) asked his/her name: %s %s', sender['username'], sender['id'], sender['first_name'], sender['last_name'])

def ChatID(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	bot.sendMessage(chat_id, "Your chatID is " + str(chat_id))
	logging.info('%s(%s) asked his/her chatID: %s', sender['username'], sender['id'], str(chat_id))

def TorrentList(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	count = 0
	try:
		#cmdoutput = cmdline('t-ls')
		cmdoutput = cmdline('transmission-remote -n '+transmissionCredentials+' -l')
		t_list = cmdoutput.split('\n')
		for i in range(0, len(t_list)):
			if(i >= 1 and i < len(t_list)-2):
				t_attr = re.split(r'\s{2,}', t_list[i]) # split where there are 2 or more spaces
				### print t_attr
				output = str(t_attr[9] + "\n" + t_attr[2] + " completed\n" + t_attr[4] + " time to termination")
				bot.sendMessage(chat_id, output)
				count = count + 1
			if(i == len(t_list)-2):
				t_attr = re.split(r'\s{2,}', t_list[i]) # split where there are 2 or more spaces
				output = "Total DOWN rate: " + str(t_attr[3]).rstrip() + " kbps\nTotal UP rate: " + str(t_attr[2]).rstrip() +" kbps"
				bot.sendMessage(chat_id, output)
	except Exception as e:
		print ("Exception: " + str(e))
		bot.sendMessage(chat_id, "Operation failed")
		logging.error('%s(%s) asked torrent list but operation failed: %s', sender['username'], sender['id'], str(e))
	logging.info('%s(%s) asked torrent list: %s elements in list', sender['username'], sender['id'], str(count))

def ShutdownTorrentServer(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']

	try:
		bot.sendMessage(chat_id, "Shutting down...")
		os.system("echo " +sudoPassword+ " | sudo -S shutdown now")
		logging.info('%s(%s) shutdown torrent server', sender['username'], sender['id'])

	except Exception as e:
		print("Exception generated while shutting down: " + str(e))
		bot.sendMessage(chat_id, "Operation failed")
		logging.error('%s(%s) tried to shutdown torrent server but operation failed: %s', sender['username'], sender['id'], str(e))

def RebootTorrentServer(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']

	try:
		bot.sendMessage(chat_id, "Rebooting...")
		os.system("echo " +sudoPassword+ " | sudo -S reboot now")
		logging.info('%s(%s) reboot torrent server', sender['username'], sender['id'])

	except Exception as e:
		print ("Exception generated while rebooting: " + str(e))
		bot.sendMessage(chat_id, "Operation failed")
		logging.error('%s(%s) tried to reboot torrent server but operation failed: %s', sender['username'], sender['id'], str(e))

def StartTorrentService(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']

	try:
		os.system("echo " +sudoPassword+ " | sudo -S service transmission-daemon start")
		bot.sendMessage(chat_id, "Starting torrent service...")
		logging.info('%s(%s) started torrent service', sender['username'], sender['id'])

	except Exception as e:
		print ("Exception: " + str(e))
		bot.sendMessage(chat_id, "Operation failed. Service not started")
		logging.error('%s(%s) tried to start torrent service but operation failed: %s', sender['username'], sender['id'], str(e))

def StopTorrentService(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']

	try:
		os.system("echo " +sudoPassword+ " | sudo -S service transmission-daemon stop")
		bot.sendMessage(chat_id, "Stopping torrent service...")
		logging.info('%s(%s) stopped torrent service', sender['username'], sender['id'])

	except Exception as e:
		print ("Exception: " + str(e))
		bot.sendMessage(chat_id, "Operation failed. Service not stopped")
		logging.error('%s(%s) tried to stop torrent service but operation failed: %s', sender['username'], sender['id'], str(e))

def TorrentServiceStatistics(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']

	try:
		#cmdoutput = cmdline('t-basicstats')
		cmdoutput = cmdline('transmission-remote -n '+transmissionCredentials+' -st')
		t_list = cmdoutput.split('\n')
		msg1 = ''
		msg2 = ''
		for i in range(0, len(t_list)):
			if(i == 1):
				msg1 = t_list[i]
			if(i > 1 and i <= 5):
				msg1 = msg1 + '\n' + t_list[i]
			if(i == 7):
				msg2 = t_list[i]
			if(i > 7):
				msg2 = msg2 + '\n' + t_list[i]
		bot.sendMessage(chat_id, msg1)
		bot.sendMessage(chat_id, msg2)

	except  Exception as e:
		print ("Exception: " + str(e))
		bot.sendMessage(chat_id, "Operation failed")
		logging.error('%s(%s) asked torrent service statistics but operation failed: %s', sender['username'], sender['id'], str(e))

	logging.info('%s(%s) asked torrent service statistics', sender['username'], sender['id'])

def AlternativeSpeedON(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	os.system("transmission-remote -n "+transmissionCredentials+" --alt-speed")
	bot.sendMessage(chat_id, "Enabling alternative speed...")
	logging.info('%s(%s) enabled Transmission alternative speed', sender['username'], sender['id'])

def AlternativeSpeedOFF(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	os.system("transmission-remote -n "+transmissionCredentials+" --no-alt-speed")
	bot.sendMessage(chat_id, "Disabing alternative speed...")
	logging.info('%s(%s) disabled Transmission alternative speed', sender['username'], sender['id'])
	
def NightModeReadStatus(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	bot.sendMessage(chat_id, "NightMode is currently " + nightmode)

def NightModeON_OFF(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	global nightmode
	if nightmode == "OFF":
		nightmode = "ON"
		os.system("transmission-remote -n "+transmissionCredentials+" --alt-speed-time-begin 0800")
		os.system("transmission-remote -n "+transmissionCredentials+" --alt-speed-time-end 2345")
		os.system("transmission-remote -n "+transmissionCredentials+" --alt-speed-scheduler")
		bot.sendMessage(chat_id, "NightMode turned ON")
		bot.sendMessage(chat_id, "Alternative speed from 08:00 to 23:45\nFull speed from 23:45 to 08:00")
		logging.info('%s(%s) NightMode turned ON', sender['username'], sender['id'])
	elif nightmode == "ON":
		nightmode = "OFF"
		os.system("transmission-remote -n "+transmissionCredentials+" --no-alt-speed-scheduler")
		os.system("transmission-remote -n "+transmissionCredentials+" --no-alt-speed")
		bot.sendMessage(chat_id, "NightMode turned OFF")
		bot.sendMessage(chat_id, "Torrents download will proceed at full speed h24")
		logging.info('%s(%s) NightMode turned OFF', sender['username'], sender['id'])
	else:
		bot.sendMessage(chat_id, "Error on NightMode value")
		logging.info('%s(%s) Error on NightMode value: (%s)', sender['username'], sender['id'], nightmode)

def AddTorrentFile(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	text = msg['text']
	magnetURL = text[5:]
	cmdoutput = cmdline("transmission-remote -n "+transmissionCredentials+" --add " + magnetURL)
	if (cmdoutput.find('responded: "success"') > -1):
		bot.sendMessage(chat_id, "Torrent file successfully added to download list")
		logging.info('%s(%s) Torrent file added to download list: (%s)', sender['username'], sender['id'], magnetURL)
	else:
		bot.sendMessage(chat_id, "Error in the magnet URL. Torrent file not added to download list")
		logging.info('%s(%s) Tryed to add torrent file to download list without success: (%s)', sender['username'], sender['id'], magnetURL)

def Termination():
	quit()

def main():
	try:
		### create logger
		logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
		logging.info('Torrent server turned ON')

		bot.sendMessage(lubent_chatID, "Torrent server turned ON")
		bot.message_loop(risp)

		while 1:
			time.sleep(30)

	except KeyboardInterrupt:
		### to intercept CTRL+C interrupt
		logging.info('Torrent server turned OFF with keyboard interrupt')
		print("\nQuitting...")
	except Exception as e:
		logging.error('Runtime Exception: ' + str(e))

if __name__ == "__main__":
	main()
