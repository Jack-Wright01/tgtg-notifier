from tgtg import TgtgClient
from forex_python.converter import CurrencyCodes
from math import floor
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage
from time import sleep
import winsound
from datetime import datetime

######################################
# E-Mail notifier for TooGoodToGo updates
######################################
# Heavily focused on using unofficial tgtg API from Anthony Hivert @ https://github.com/ahivert/tgtg-python
# Logs onto user's tgtg account and notifies user of any new update on their >favourite< venues
# Updates on all venues available through API documentation, but this system only uses the user's favourites as a filter
######################################

load_dotenv()

HOST_EMAIL = os.getenv('2G2G_EMAIL')
HOST_PW = os.getenv('2G2G_PASSWORD')
MAIL_PW = os.getenv('MAIL_PASSWORD')
MAIL_TO = os.getenv('MAIL_TO')

REFRESH_INTERVAL = 60 #Seconds

client = TgtgClient(email=HOST_EMAIL, password=HOST_PW)

def getItems(mail=False, alert=False, printToConsole=False):
    items = client.get_items(with_stock_only=True)
    for child in items:
        item = child['item']
        store = child['store']

        #Store
        store_name = store['store_name']
        store_location = store['store_location']['address']
        address = store_location['address_line']

        #Item
        item_id = item['item_id']
        price = item['price']
        currency = CurrencyCodes().get_symbol(price['code']) or "" #No symbol if failed to find symbol
        cost = "{:.2f}".format(price['minor_units'] / 100) #double decimal format
        description = item['description']

        data = { #To send to email
            "id": item_id,
            "name": store_name,
            "address": address,
            "description": description,
            "price": currency + str(cost),
        }

        if (mail):
            sendEmail(data)

        if (printToConsole):
            today = datetime.now()
            currDate = today.strftime("%b-%d-%Y %H:%M:%S").replace(" ", " @ ")
            print(f"{currDate} | New magic bag | {data['name']} | {data['price']}")

        if (alert):
            ping()

def sendEmail(data):
    #debug terminal server
    #with smtplib.SMTP('localhost', 1025) as smtp:
    #python -m smtpd -c DebuggingServer -n localhost:1025
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(HOST_EMAIL, MAIL_PW)
        msg = EmailMessage()

        msg['Subject'] = f"🍔 New Listing ({data['price']}): {data['name']} ({data['id']})"
        msg['From'] = HOST_EMAIL
        msg['To'] = MAIL_TO
        msg.set_content(f"{data['name']}\n{data['address']}\n\n{data['description']}")

        smtp.send_message(msg)

def ping(): #Optional default disabled
    winsound.PlaySound("*", winsound.SND_ALIAS)

print("""--------------------------------------------------
                 Too Good To Go
           Auto searcher & Email notifier 
--------------------------------------------------
Recieve email updates of your favourite tgtg venues
faster and beat the crowd at getting the best bargain

Developed by Jack Wright (@Jack_Wright10) with credit
to Anthony Hivert (@ahivert_) for the underlying API

            Last updated 01 Oct 2021
--------------------------------------------------
         New listings are displayed below
--------------------------------------------------""")

def main():
    while True:
        getItems(mail=True, alert=False, printToConsole=True)
        sleep(REFRESH_INTERVAL)

main()
    