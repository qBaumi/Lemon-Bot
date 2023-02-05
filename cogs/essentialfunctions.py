import math
import random
import time
import mysql.connector, json
from config import allowedRoles, dbargs
import discord

# returns True if user has Perms
# returns False if not
# if not await es.checkPerms(interaction):
#    return
async def checkPerms(interaction):
    role_ids = [role.id for role in interaction.user.roles]
    for role in allowedRoles:
        if role in role_ids:
            print("You're allowed")
            return True
    await interaction.response.send_message("You need to be a Mod or Admin in order to use this command!")
    return False

# checkPerms with custom Role List
async def checkPerms(interaction, roleList):
    role_ids = [role.id for role in interaction.user.roles]
    for role in roleList:
        if role in role_ids:
            print("You're allowed")
            return True
    await interaction.response.send_message("You need to be a Mod or Admin in order to use this command!")
    return False

def sql_exec(sql):
    """
        W3SCHOOLS MYSQL CONNECTOR FOR MOR INFO
    """
    mydb = mysql.connector.connect(
        host=dbargs["host"],
        user=dbargs["user"],
        password=dbargs["password"],
        port=dbargs["port"],
        database=dbargs["database"],
        auth_plugin=dbargs["auth_plugin"]

    )
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    mydb.close()
def sql_select(sql):
    mydb = mysql.connector.connect(
        host=dbargs["host"],
        user=dbargs["user"],
        password=dbargs["password"],
        port=dbargs["port"],
        database=dbargs["database"],
        auth_plugin=dbargs["auth_plugin"]

    )
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    data = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return data
#OPENS AN ACCOUNT AND PUTS USER IN DATABASE FOR THE FIRST TIME
async def open_account(user):

    ids = sql_select("SELECT id FROM users")
    for id in ids:
        ### SELECT RETURNS TUPLES WHICH HAVE AN INDEX
        if str(user.id) == id[0]:
            return False
    else:
        sql_exec(f"INSERT INTO users (id, pocket, safe, xp, lvl) VALUES ({user.id}, 0, 0, 0, 1)")
    return True

"""
RETURNS TRUE IF USER USED /STARTUP
OR RETURNS FALSE IF NOT AND GIVES MESSAGE
"""
async def interaction_check_account(interaction : discord.Interaction):
    ids = sql_select("SELECT id FROM users")

    for id in ids:
        ### SELECT RETURNS TUPLES WHICH HAVE AN INDEX
        if str(interaction.user.id) == id[0]:
            return True
    await interaction.response.send_message(f"{interaction.user.mention}\nUse the `/startup` command first!")
    return False

"""
GETS USER BANK DATA
returns dict with pocket and safe money
"""
async def get_bank_data(id):
    data = sql_select(f"SELECT * FROM users WHERE id = {id}")
    users = {data[0][0] : {"pocket" : data[0][1], "safe" : data[0][2]}}
    return users

"""
return JSON file
"""
async def get_item_data():
    # open the json file in read mode to load users and return them
    with open("./json/spItems.json", "r", encoding="utf-8") as f:
        specialitems = json.load(f)
    return specialitems

"""
returns list with all user items
"""
async def getbag(id):
    data = sql_select(f"SELECT * FROM items WHERE id = {id}")
    bag = []
    for item in data:
        name = item[1]
        amount = item[2]
        dict = {"item" : name, "amount" : amount}
        bag.append(dict)
    return bag

"""
UPDATE MONEY
"""
async def update_balance(user, change=0, mode="pocket"):
    # Get the bank file data
    users = await get_bank_data(id=user.id)
    sql = f"UPDATE users SET {mode} = {users[str(user.id)][mode] + change} WHERE id = {user.id}"
    sql_exec(sql)
    bal = users[str(user.id)]["pocket"] + change
    return bal


"""Returns currency from users table"""
async def currency(user):
    # Get bank data
    users = await get_bank_data(id=user.id)
    # Third index with all money you have
    # Get both the pocket and galaxy money into the bal variable and return it
    bal = users[str(user.id)]["pocket"], users[str(user.id)]["safe"], users[str(user.id)]["pocket"] + \
          users[str(user.id)]["safe"]
    return bal

"""
deletes an item from a user inventory
id = user id
item = item name str
amount = delete how many
"""
async def del_item(id, item, amount=1):
    index = 0
    t = None
    userbag = await getbag(id)
    for thing in userbag:
        n = thing["item"]
        if n == item:
            old_amt = thing["amount"]
            new_amt = old_amt - amount
            if new_amt < 0:
                return [False, 2]
            sql = f"UPDATE items SET amount = {new_amt} WHERE id = {id} AND name = '{item}'"
            sql_exec(sql)
            t = 1
            break
        index += 1

"""
adds an item to a user inventory
id = user id
item_name = item name str
amount = add how many
"""
async def add_item(item_name, userid, amount):
    item_name = item_name.lower()
    index = 0
    t = None
    userbag = await getbag(userid)
    try:
        for thing in userbag:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                # SINGLE QUOTE MAFMEDLSAKFJÃ–S
                sql = f"UPDATE items SET amount = {new_amt} WHERE id = {userid} AND name = '{item_name}'"
                sql_exec(sql)
                t = 1
                break
            index += 1

        if t == None:
            sql = f"INSERT INTO items (id, name, amount) VALUES ({userid}, '{item_name}', {amount})"
            sql_exec(sql)
    except:
        sql = f"INSERT INTO items (id, name, amount) VALUES ({userid}, '{item_name}', {amount})"
        sql_exec(sql)

# get choice for each normal item you have in your bag
# returns a choice list
async def getChoices(user):
    # Get all special items from json
    specialitems = await get_item_data()
    specialitems = specialitems["MysterySkin"]

    # Make list and append name if they are in spItems [spItemName, spItemName, ...]
    # to search if item not in spItems
    spItemList = []
    for item in specialitems:
        spItemList.append(item["name"].lower())

    # Get user bag and make a list with every different item
    bag = sql_select(f"SELECT DISTINCT name, amount FROM items WHERE id = {user.id}")
    # Now make the list for the choices and return it
    itemlist = []
    for item in bag:
        if item[1] > 0 and item[0] not in spItemList:
            itemlist.append(item[0])
    return itemlist

# Check if user is on cooldown in database, returns True if is on cooldown, returns False if he can use the command again
# types
# daily
# work
# steal
"""
    isOnCooldown, sec = self.isOnCooldown(user, "daily")
    if isOnCooldown:
        await interaction.response.send_message(f"You are still on cooldown until <t:{math.floor(time.time() + sec)}>")
        return
    self.setCooldown(user, "daily")
"""
def isOnCooldown(user, cdtype):
    data = sql_select(f"SELECT time FROM cooldowns WHERE id = '{user.id}' AND type = '{cdtype}'")

    current_time = time.time()
    if not data:
        return False, 0
    data = data[0][0]
    print(f"Momentane Zeit: {current_time}")
    print(f"Cooldown geht bis: {data}")
    if data > current_time:
        return True, math.floor(data - current_time)
    sql_exec(f"DELETE FROM cooldowns WHERE id = '{user.id}' AND type = '{cdtype}'")
    return False, 0

def setCooldown(user, type):
    if type == "daily":
        sec = 86400
    elif type == "work":
        sec = 300
    elif type == "steal":
        sec = 369
    elif type == "stealuser":
        sec = 900
    else:
        sec = 0
    sql_exec(f"INSERT INTO cooldowns VALUES ('{user.id}', {time.time()+sec},'{type}')")

def getRandomUser():
    sql = "SELECT id FROM users"
    data = sql_select(sql)
    users = data
    userlist = []
    for user in users:
        userlist.append(user)
    user = random.choice(userlist)
    user = user[0]
    return user

async def getxp(id):
    data = sql_select(f"SELECT * FROM users WHERE id = {id}")
    xp = data[0][3]
    lvl = data[0][4]
    print(xp)
    return xp, lvl