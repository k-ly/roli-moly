import os
import asyncio
from dotenv import load_dotenv
from discord import Intents, Client, Message, Webhook, Embed
import requests 
import json
import aiohttp
from utils import inv, updateValues
# 1. Set Up Variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
HOOKURL = os.getenv('WEBHOOK_URL')
USERID = 261 # roblox user ID of inventory to check
cache = dict()

# 2. Set up bot
intents = Intents.default()
client = Client(intents=intents)

# 3. Check trade ads
async def getTradeAds(itemsToCheck: set):
    async with aiohttp.ClientSession() as session:
        # initial setup
        count = 0
        url = 'https://api.rolimons.com/tradeads/v1/getrecentads'
        updateValues(cache)
        itemsToCheck = inv(USERID)
        tradeAdsIDs = dict()
        while True:
            await asyncio.sleep(10)
            count += 10
            # refresh inv and values every hour
            try:
                if count==3600:
                    updateValues(cache)
                    itemsToCheck=inv(USERID)
                    count=0
                response = requests.get(url)
                ads = json.loads(response.text)['trade_ads']
                for ad in ads:
                    # only check for new ads with no tags and that contain items from itemsToCheck 
                    if ad[0] not in tradeAdsIDs and 'items' in ad[5] and any(x in itemsToCheck for x in ad[5]['items']):
                        # if tradeAds gets bigger than a certain amount, remove first item that was put in to save memory
                        if len(tradeAdsIDs)>50:
                            tradeAdsIDs.pop(next(iter(tradeAdsIDs)))
                        tradeAdsIDs[ad[0]]=None
                        #check if its a good deal
                        offer=sum(cache[item] for item in ad[4]['items']) + int(ad[4].get('robux',0) *.7)
                        request=sum(cache[item] for item in ad[5]['items'])
                        deal = (offer/request) * 100
                        # if deal is over a certain percent, send discord message
                        if deal>107:
                            # send message
                            webhook = Webhook.from_url(HOOKURL, session=session)
                            # set up the embed for the message
                            embed = Embed(title='Found a {:0.0f}%% deal!'.format(deal), description="{} for {} value!".format(offer,request))
                            embed.add_field(name='Trade Link', value = 'https://www.rolimons.com/tradead/{}'.format(ad[0]))
                            embed.add_field(name='Send Trade', value = 'https://www.roblox.com/users/{}/trade'.format(ad[2]))
                            await webhook.send(content= '@everyone', embed = embed, username = 'Roli Trade Deals')  
            except Exception as e:
                continue  
    return
# Start the discord bot
'''@client.event
async def on_ready() -> None:
    userItems = inv(9916273)
    updateValues(cache)
    client.run(TOKEN)
    getTradeAds(message, userItems)'''

if __name__ == "__main__":
    userItems = inv(USERID)
    updateValues(cache)
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(getTradeAds(userItems))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()
