import requests
import json

# Arg: ROBLOXuserID: int, Returns: set of users limited items
def inv(user: int) -> set:
    response = requests.get('https://inventory.roblox.com/v1/users/{}/assets/collectibles?limit=100'.format(user))
    inventory = json.loads(response.text)['data']
    invIDs = set()
    for asset in inventory:
        if not asset['isOnHold']:
            invIDs.add(asset['assetId'])
    return invIDs
# Arg: cache: dict of item values, Returns: None, just updates the values in the dictionary
def updateValues(itemDict: dict) -> None:
    url= 'https://www.rolimons.com/itemapi/itemdetails'
    response = requests.get(url)
    allItems = json.loads(response.text)['items']
    for id, data in allItems.items():
        itemDict[int(id)] = data[4]
    return