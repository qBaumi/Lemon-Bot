import mysql.connector, discord, json
from .economy import mycursor, mydb

with open("password.txt", "r") as f:
    password = f.read()
with open("IP.txt", "r") as f:
    ip = f.read()






"""
OPENS AN ACCOUNT AND PUTS USER IN DATABASE FOR THE FIRST TIME
"""
async def open_account(user):
    mycursor.execute("SELECT id FROM users")
    ids = mycursor.fetchall()
    for id in ids:
        ### SELECT RETURNS TUPLES WHICH HAVE AN INDEX
        if str(user.id) == id[0]:
            return False
    else:
        sql = "INSERT INTO users (id, pocket, safe, xp, lvl) VALUES (%s, %s, %s, %s, %s)"
        val = (user.id, 0, 0, 0, 1)
        mycursor.execute(sql, val)
    mydb.commit()
    return True

"""
RETURNS TRUE IF USER USED LEM STARTUP
OR RETURNS FALSE IF NOT AND GIVES MESSAGE
"""
async def check_account(ctx):
    mycursor.execute("SELECT id FROM users")

    ids = mycursor.fetchall()

    for id in ids:
        ### SELECT RETURNS TUPLES WHICH HAVE AN INDEX
        if str(ctx.author.id) == id[0]:
            return True
    await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
    return False

"""
GETS USER BANK DATA
returns dict with pocket and safe money
"""
async def get_bank_data(id):
    mycursor.execute(f"SELECT * FROM users WHERE id = {id}")
    data = mycursor.fetchall()

    users = {data[0][0] : {"pocket" : data[0][1], "safe" : data[0][2]}}
    return users

"""
return JSON file
"""
async def get_item_data():
    # open the json file in read mode to load users and return them
    with open("spItems.json", "r", encoding="utf-8") as f:
        specialitems = json.load(f)
    return specialitems

"""
returns list with all user items
"""
async def getbag(id):
    mycursor.execute(f"SELECT * FROM items WHERE id = {id}")
    data = mycursor.fetchall()
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
    mycursor.execute(sql)
    mydb.commit()
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
            mycursor.execute(sql)
            mydb.commit()
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
                mycursor.execute(sql)
                mydb.commit()
                t = 1
                break
            index += 1

        if t == None:
            sql = f"INSERT INTO items (id, name, amount) VALUES ({userid}, '{item_name}', {amount})"
            mycursor.execute(sql)
            mydb.commit()
    except:
        sql = f"INSERT INTO items (id, name, amount) VALUES ({userid}, '{item_name}', {amount})"
        mycursor.execute(sql)
        mydb.commit()