import asyncio
import glob
import json
import random
import time

import PIL
import discord
from discord import Colour
from discord.ext import commands
from array import *
import math
from PIL import Image, ImageDraw


class economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    # First time opening bank account for the startup command
    async def open_account(self, user):
        # Open the file with the getbankdata function
        users = await self.get_bank_data()
        # If they are already in there return False to check later on the startup command
        if str(user.id) in users:
            return False
        # If they aren't registered set the money on wallet and bank to 0
        else:
            # Make a new pocket and galaxy and set it to 0€ also make new DICTS to store the pets, these are dicts because they should have stats
            users[str(user.id)] = {}
            users[str(user.id)]['pocket'] = 0
            users[str(user.id)]['safe'] = 0
            users[str(user.id)]['pets'] = {}
            users[str(user.id)]['equippedpet'] = {}
            users[str(user.id)]['petslot1'] = {}
            users[str(user.id)]['petslot2'] = {}
            users[str(user.id)]['petslot3'] = {}
        # Open the json again but in write mode to dump the users
        with open('lemonbank.json', 'w') as f:
            json.dump(users, f, indent=4)
        # Return True to check in startup command
        return True

    # Check if you have an account opened
    async def check_account(self, user):
        # Open the file with the getbankdata function
        users = await self.get_bank_data()
        # If they are already in there return False to check later on the startup command
        if str(user.id) in users:
            return True
        return False

    # Get the Bank, user data stored in the json file
    async def get_bank_data(self):
        # open the json file in read mode to load users and return them
        with open("lemonbank.json", "r") as f:
            users = json.load(f)
        return users

    # Give or withdraw money from your account
    async def update_balance(self, user, change=0, mode="pocket"):
        # Get the bank file data
        users = await self.get_bank_data()
        # Update the value in the mode you want
        users[str(user.id)][mode] += change
        with open('lemonbank.json', 'w') as f:
            json.dump(users, f, indent=4)
        # Return a currency value for text purposes
        bal = users[str(user.id)]["pocket"], users[str(user.id)]["safe"]
        return bal


    # Currency helper function to get currency faster
    async def currency(self, user):
        # Get bank data
        users = await self.get_bank_data()
        # Third index with all money you have
        allmoney = users[str(user.id)]["pocket"] + users[str(user.id)]["safe"]
        # Get both the pocket and galaxy money into the bal variable and return it
        bal = users[str(user.id)]["pocket"], users[str(user.id)]["safe"], users[str(user.id)]["pocket"] + \
              users[str(user.id)]["safe"]
        return bal

    # Startup command to open account
    @commands.command(aliases=["start"])
    async def startup(self, ctx):
        # Use the open_account function and give a quick overview to the bot, help, some commands etc

        # Get the user
        user = ctx.author
        # Get the function into accountopened to check if already an account was made
        accountopened = await self.open_account(user=user)
        if accountopened == False:
            em = discord.Embed()
            em.add_field(name=f"Sorry, you already created an account!",
                         value=f"If you didn't read the message the first time you used this command, try: `lem help` , to get more information")
            await ctx.send(f"{ctx.author.mention}\n", embed=em)
            # Exit
            return

        # Now if an account wasn't opened the code comes here and sends the embed
        em = discord.Embed(color=discord.Color.blurple(), title="Hello!",
                           description=f"Let me introduce you to our little friend Lemon right here.")
        em.add_field(name="Welcome you can find out more about me with <lem about>",
                     value="Congrats! You already found the *startup command*. \n"
                           "Next is the `lem lemons` or `lem balance` command. You can look up your balance there, \nbut don't forget to NEVER share your bank account data! \nUse `lem help` for more information")
        await ctx.send(embed=em)

    # Get your balance/poop
    @commands.command(aliases=["curr", "bal", "currency", "lemons", "glemons", "bank"])
    async def balance(self, ctx):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        # Get currency with helper function and send it in an embed
        # If you returned several things in one variable you can get one specific with
        # f. E. money[0]      *the first index*
        # START WITH ZERO
        money = await self.currency(ctx.author)

        # Make a nice looking embed
        em = discord.Embed(title="Your currency", colour=Colour.gold())
        # Set the footer text
        if money[2] < 100:
            em.set_footer(text="Pff, what a poor commoner")
        elif money[2] > 1000:
            em.set_footer(text="Welcome to the rich people gang")
        # Set the Fields for pocket and galaxy
        em.add_field(name="You have ", value=f"`{int(round(money[0], 0)):g}` <:lemon2:881595266757713920> lemons in your pocket", inline=False)
        em.add_field(name="You have ", value=f"`{int(round(money[1], 0)):g}` golden lemons", inline=False)

        await ctx.send(embed=em)

    # Shop
    mainshop = [{"name": "Lemonade", "price": 5, "desc": "Everyone likes lemonade", "money": "lemons", "emoji" : "<:lemonade:882239415601213480>"},
                {"name": "Cheesecake", "price": 10, "desc": "You can either eat it, or throw it at another person :)", "money": "lemons", "emoji" : "🍰"},
                {"name": "Flowers", "price": 15, "desc": "Flowers are always a great birthday gift!", "money": "lemons","emoji": "💐"},
                {"name": "Present", "price": 70, "desc": "Now you can gift every item", "money": "lemons", "emoji": "🎁"},
                {"name": "Pinata", "price": 150, "desc": "Piñata is great, but be careful with the baseball bat!", "money": "lemons","emoji": "<:pinata:882600329517096971>"},
                {"name": "ConchShell", "price": 200, "desc": "LONG LIVE THE MAGIC CONCH SHELL", "money": "lemons","emoji": "<:magicconchshell:882556087843307520>"},
                {"name": "Candy", "price": 10, "desc": "f", "money": "lemons","emoji": "🍬"},
                {"name": "Mobile", "price": 500, "desc": "Phone, I hope you know what a phone is", "money": "lemons", "emoji" : "☎"},
                {"name": "Laptop", "price": 1000, "desc": "Yes, a thousand", "money": "lemons", "emoji": "💻"},
                {"name": "Safe", "price": 1500, "desc": "Store 5000 precious lemons in it!", "money": "lemons", "emoji": "<:safe:885811224418332692>"}]
    petshop = [{"name": "Lootbox-Common", "price" : 1500, "desc": "Get a random ★☆☆ pet", "money" : "lemons"},
                {"name": "Lootbox-Rare", "price": 3000, "desc": "Get a random ★★☆ pet", "money": "lemons"},
                {"name": "Lootbox-EA", "price": 5000, "desc": "Get a random ★★★ pet, personally from EA-man himself", "money": "lemons"}]

    async def get_item_data(self):
        # open the json file in read mode to load users and return them
        with open("spItems.json", "r", encoding="utf-8") as f:
            specialitems = json.load(f)
        return specialitems

    @commands.command()
    async def Shop(self, ctx):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        # make a nice embed
        embed = discord.Embed(title='Shop')
        # For every item make a string variable that will add a field per item
        specialitems = await self.get_item_data()
        print(specialitems)
        for thing in specialitems:
            print(thing)
            for item in specialitems[thing]:
                print(item)
                name = item['name']
                price = item['price']
                desc = item['desc']
                emoji = item["emoji"]
                moneyform = item['money']
                stock = item['stock']
                if stock > 0:

                    if moneyform == "lemons":
                        money = "lemons"
                        moneyemoji = "<:lemon2:881595266757713920>"
                    else:
                        money = "golden lemons"
                        moneyemoji = "<:GoldenLemon:882634893039923290>"
                    str = f"{name}  "
                    index = 0
                    for space in range(100-len(str)):
                        if index == 0:
                            str = str + f"{emoji}"
                        str = str + " "
                        index = index + 1
                    str2 = f"{price} {moneyemoji}"
                    str = str + str2
                    embed.add_field(name=str, value=f'Only `{stock}` items left!!! {desc}`', inline=False)
        for item in self.mainshop:
            name = item['name']
            price = item['price']
            desc = item['desc']
            emoji = item["emoji"]
            moneyform = item['money']
            if name != "Candy":
                if moneyform == "lemons":
                    money = "lemons"
                    moneyemoji = "<:lemon2:881595266757713920>"
                else:
                    money = "golden lemons"
                    moneyemoji = "<:lemon2:881595266757713920>"
                str = f"{name}  "
                index = 0
                for space in range(100-len(str)):
                    if index == 0:
                        str = str + f"{emoji}"
                    str = str + " "
                    index = index + 1
                str2 = f"{price} {moneyemoji}"
                str = str + str2
                embed.add_field(name=str, value=f'{desc}', inline=False)
        await ctx.send(embed=embed)

    # Buy Sell etc
    @commands.command()
    async def buy(self, ctx, item, amount=1):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        if amount < 1:
            await ctx.send(":)")
            return

        if item.lower() == "safe" and amount > 1:
            await ctx.send(f"{ctx.author.mention}\nYou can only buy one safe!")
            print("that")
            return
        users = await self.get_bank_data()
        user = ctx.author
        for useritem in users[str(user.id)]["bag"]:
            if useritem["item"] == "safe" and useritem["amount"] > 0:
                print("this")
                await ctx.send(f"{ctx.author.mention}\nYou can only buy one safe!")
                return



        res = await self.buy_this(ctx.author, item, amount)


        if not res[0]:
            if res[1] == 1:
                await ctx.send(f"{ctx.author.mention}\nThat Item isn't there!")
                return
            if res[1] == 2:
                await ctx.send(f"{ctx.author.mention}\nYou don't have enough money in your wallet to buy {amount} {item}")
                return
            if res[1] == 5:
                await ctx.send(f"{ctx.author.mention}\nThat item isnt in stock!")
                return
        if item.lower() == "mysteryskin":
            specialitems = await self.get_item_data()
            print(specialitems["MysterySkin"][0]["stock"])
            specialitems["MysterySkin"][0]["stock"] = specialitems["MysterySkin"][0]["stock"] - amount
            with open("spItems.json", "w") as f:
                json.dump(specialitems, f, indent=4)

        await ctx.send(f"{ctx.author.mention}\nYou just bought {amount} {item}")

    @commands.command(aliases = ["items"])
    async def bag(self, ctx):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        await self.open_account(ctx.author)
        user = ctx.author
        users = await self.get_bank_data()

        try:
            bag = users[str(user.id)]["bag"]
        except:
            bag = []

        em = discord.Embed(title="Bag")
        for item in bag:
            name = item["item"]
            name_ = name.capitalize()
            amount = item["amount"]

            if amount > 0:
                em.add_field(name=name_, value=amount, inline=False)


        await ctx.send(embed=em)

    async def buy_this(self, user, item_name, amount):
        item_name = item_name.lower()
        name_ = None
        stock = 100
        isnormal = False
        for item in self.mainshop:
            name = item["name"].lower()
            if name == item_name:
                if stock == 100:
                    name_ = name
                    price = item["price"]
                    moneyform = item['money']
                    isnormal = True
                    break


        if isnormal == False:
            specialitems = await self.get_item_data()
            for thing in specialitems:
                for specialitem in specialitems[thing]:
                    print(specialitem)
                    name = specialitem['name'].lower()
                    price = specialitem['price']
                    desc = specialitem['desc']
                    emoji = specialitem["emoji"]
                    moneyform = specialitem['money']
                    stock = specialitem['stock']
                    if name == item_name:
                        if stock <= 0:
                            return [False, 5]
                        name_ = name
                        price = specialitem["price"]
                        moneyform = specialitem['money']
                        break



        if name_ == None:
            return [False, 1]
        if moneyform == "lemons":
            depot = "pocket"
            depotindex = 0
        if moneyform == "golden lemons":
            depot = "safe"
            depotindex = 1

        cost = price * amount

        users = await self.get_bank_data()

        bal = await self.update_balance(user)

        if bal[depotindex] < cost:
            return [False, 2]

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt + amount
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index += 1

            if t == None:
                obj = {"item": item_name, "amount": amount}
                users[str(user.id)]["bag"].append(obj)
        except:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["bag"] = [obj]

        with open("lemonbank.json", "w") as f:
            json.dump(users, f, indent=4)

        await self.update_balance(user, cost * -1, depot)

        return [True, "Worked"]

    @commands.command()
    async def sell(self, ctx, item, amount=1):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        if amount < 1:
            await ctx.send(":)")
            return
        res = await self.sell_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send(f"{ctx.author.mention}\nThat Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(f"{ctx.author.mention}\nYou don't have {amount} {item} in your bag.")
                return
            if res[1] == 3:
                await ctx.send(f"{ctx.author.mention}\nYou don't have {item} in your bag.")
                return

        await ctx.send(f"{ctx.author.mention}\nYou just sold {amount} {item}.")

    async def sell_this(self, user, item_name, amount, price=None):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower()
            moneyform = item["money"]
            if name == item_name:
                name_ = name
                if price == None:
                    price = 0.5 * item["price"]
                break

        if name_ == None:
            return [False, 1]
        if moneyform == "lemons":
            depot = "pocket"
            depotindex = 0
        if moneyform == "golden lemons":
            depot = "safe"
            depotindex = 1

        cost = price * amount

        users = await self.get_bank_data()

        bal = await self.update_balance(user)

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt - amount
                    if new_amt < 0:
                        return [False, 2]
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index += 1
            if t == None:
                return [False, 3]
        except:
            return [False, 3]

        with open("lemonbank.json", "w") as f:
            json.dump(users, f, indent=4)

        await self.update_balance(user, cost, depot)

        return [True, "Worked"]

    # daily poop and cooldown 21600 is one day in seconds
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command()
    async def daily(self, ctx):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        # Give the user 10 daily poop
        await self.update_balance(ctx.author, 10, "pocket")
        # Send an embed to show him and get currency
        money = await self.currency(ctx.author)
        em = discord.Embed(colour=Colour.red(), title=f"You got your daily 10 lemons! Dont eat them all at the same time!",
                           description=f"You have now `{int(money[0])}` lemons")
        await ctx.send(embed=em)

    # Send the error in an embed and add the exact number of seconds in the footer
    @daily.error
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(colour=Colour.dark_red(), title='You can only use this command once a day')
        embed.set_footer(text=error)

        await ctx.send(embed=embed)







    @commands.command()
    @commands.has_role("Admins")
    async def gift(self, ctx, winner : discord.User, money, *, moneyform="lemons"):
        user = ctx.author
        role = discord.utils.get(user.guild.roles, id=598307015181467650)
        print(role)
        print(user.roles)
        role2 = discord.utils.get(user.guild.roles, id=825532026462797835)


        users = await self.get_bank_data()
        if moneyform == "lemons":
            mode = "pocket"
        else:
            mode = "safe"
        print(f"{user.name} gifted {winner} {money} {moneyform}")
        await self.update_balance(winner, int(money), mode=mode)
        await ctx.send(f"{winner} received {money} {moneyform}")

    @commands.has_role("Admins")
    @commands.command()
    async def refill(self, ctx, item, amount=0):
        if amount == 0:
            await ctx.send("You didnt specify the amount `lem refill Mysteryskin 10` for example")
            return
        user = ctx.author
        specialitems = await self.get_item_data()
        index = -1
        exists = 0
        item = item.lower()
        for thing in specialitems:
            for specialitem in specialitems[thing]:
                print(specialitem)
                name = specialitem['name'].lower()
                stock = specialitem['stock']
                index = index + 1
                if name == item:
                    exists = 1
                    break
        if exists == 0:
            await ctx.send("That item cannot be refilled!")
            return
        specialitems["MysterySkin"][index]["stock"] = specialitems["MysterySkin"][index]["stock"] + int(amount)
        instock = specialitems["MysterySkin"][index]["stock"]
        with open("spItems.json", "w") as f:
            json.dump(specialitems, f, indent=4)
        await ctx.send(f"There are now {instock} {name}'s in stock")

    @commands.command()
    @commands.has_role("Mods")
    async def modgift(self, ctx, winner: discord.User, money, *, moneyform="lemons"):
        user = ctx.author


        users = await self.get_bank_data()
        if moneyform == "lemons":
            mode = "pocket"
        else:
            mode = "safe"
        print(f"{user.name} gifted {winner} {money} {moneyform}")
        await self.update_balance(winner, int(money), mode=mode)
        await ctx.send(f"{winner} received {money} {moneyform}")



    @gift.error
    async def on_command_error(self, ctx, error):
        await ctx.send(f"{ctx.author.mention}\nYou need to be an Admin or Mod, in order to use this command")

    @modgift.error
    async def on_command_error(self, ctx, error):
        await ctx.send(f"{ctx.author.mention}\nYou need to be an Admin or Mod, in order to use this command")

    @refill.error
    async def on_command_error(self, ctx, error):
        await ctx.send(f"{ctx.author.mention}\nYou need to be an Admin to use this command")

    @commands.cooldown(1, 180, commands.BucketType.user)
    @commands.command(aliases=["rob"])
    async def steal(self, ctx, victim : discord.User):
        user = ctx.author
        if victim == user:
            await ctx.send(f"{ctx.author.mention}\nHwat? You wanna rob yourself?!?!? I am always a thought ahead of you...trust me")
            self.steal.reset_cooldown(ctx)
            return
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nYou need to use `lem startup` first")
            self.steal.reset_cooldown(ctx)
            return
        users = await self.get_bank_data()
        if users[str(user.id)]['pocket'] < 100:
            await ctx.send(f"{ctx.author.mention}\nYou need atleast `100 lemons` in your pocket in order to steal from another person")
            self.steal.reset_cooldown(ctx)
            return
        try:
            if users[str(victim.id)]['pocket'] < 100:
                await ctx.send(f"{ctx.author.mention}\nIs too `poor` to get robbed")
                self.steal.reset_cooldown(ctx)
                return
        except:
            await ctx.send(f"{ctx.author.mention}\nYour victim hasn't opened an account yet")
            self.steal.reset_cooldown(ctx)
            return
        chance = random.randrange(0, 100)
        percent = round(random.uniform(0.01, 0.041), 2)
        print(percent)
        if chance < 40:
            sentences = [f"You were captured when you tried to open {victim.name}'s bag", f"When you touched {victim.name}'s pocket the police saw you and arrested you. Have fun in jail!", f"Pretty unlucky...{victim.name} is currently attempting a self-defending course, you stand no chance", f"{victim.name}'s big brother saw you...he is very big"
                         ,f"Robbing in front of a cop...you should try to type that in youtube!", f"When you opened {victim.name}'s bag, her little chihuahua (Yeah I gooled that name before) jumped into your face and bit you"]
            funnysentence = random.choice(sentences)
            if users[str(victim.id)]['pocket'] < users[str(user.id)]['pocket']:
                loss = round(users[str(user.id)]['pocket'] * percent * (users[str(victim.id)]['pocket']/users[str(user.id)]['pocket']), 0)
            else:
                loss = round(users[str(user.id)]['pocket'] * percent, 0)
                loss = int(loss)
            em = discord.Embed(colour=discord.Color.red(),
                               title=f"{user.name} lost {loss:g} lemons when trying to steal from {victim.name}",
                               description=funnysentence)
            await ctx.send(embed=em)
            await self.update_balance(user, loss * -1)
            await self.update_balance(victim, loss)
            return

        await self.update_balance(victim, int(round(users[str(victim.id)]['pocket']*percent, 0)*-1))
        await self.update_balance(user, int(round(users[str(victim.id)]['pocket']*percent, 0)))
        em = discord.Embed(colour=discord.Color.red(), title=f"{user.name} stole {victim.name} {round(users[str(victim.id)]['pocket']*percent, 0):g} lemons", description=f"Less lemonade for {victim.name} I guess")
        await ctx.send(embed=em)

    @steal.error
    async def on_command_error(self, ctx, error):
        em = discord.Embed(colour=discord.Color.red(), title=error, description="If your user wasnt found, you need to tag them with an @ `lem steal @name` for example")
        await ctx.send(embed=em)


    @commands.command()
    async def leaderboard(self, ctx, x=10):
        users = await self.get_bank_data()
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            if name == 783380754238406686 or name == 442913791215140875:
                None
            else:

                total_amount = users[user]["pocket"]
                leader_board[total_amount] = name
                total.append(total_amount)

        total = sorted(total, reverse=True)

        em = discord.Embed(title=f"Top {x} richest people", color=discord.Color.dark_gold())
        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = await self.client.fetch_user(id_)

            name = member.name
            em.add_field(name=f"{index}. {name}", value=f"`{int(amt)}` lemons <:lemon2:881595266757713920>", inline=False)
            if index == x:
                break
            else:
                index += 1

        await ctx.send(embed=em)

    @commands.command(aliases=['give', 'send'])
    async def Pay(self, ctx, userid: discord.User, pay_amount):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nYou need to use `lem startup` first")
            return
        if await self.check_account(userid) == False:
            await ctx.send(f"{ctx.author.mention}\n{userid} has not opened an account yet!")
            return
        if userid == ctx.author:
            await ctx.send(f"{ctx.author.mention}\nYou cant pay yourself money...well technically, but not anymore!")
            return
        pay_amount = int(pay_amount)
        if pay_amount > 0:
            await  self.get_bank_data()
            user = ctx.author
            users = await self.get_bank_data()
            await self.Pay_helper(ctx=ctx, userid=userid, pay_amount=pay_amount)
            wallet_amt = users[str(user.id)]['pocket']
            if True and pay_amount <= wallet_amt:
                await ctx.send(
                    f"{ctx.author.mention}\nYou paid {userid.name} {pay_amount} lemons. If you have an emberassing image, dont forget to TAX THE HELL OUT OF THEM")
        else:
            await ctx.send(f"{ctx.author.mention}\nNo")

    async def Pay_helper(self, ctx, userid: discord.User, pay_amount):
        await  self.get_bank_data()
        user = ctx.author
        users = await self.get_bank_data()

        pay_amount = int(pay_amount)
        wallet_amt = users[str(user.id)]['pocket']
        if pay_amount <= wallet_amt:
            await self.update_balance(user=user, change=pay_amount * -1, mode='pocket')
            await self.update_balance(user=userid, change=pay_amount, mode='pocket')

        else:
            await ctx.send(
                f"{ctx.author.mention}\nYou dont have enough money!")
        return [True]

    @commands.command()
    async def lottery(self, ctx, bet=0):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nYou need to use `lem startup` first")
            return
        if bet==0:
            await ctx.send(f"{ctx.author.mention}\nYou didn't set a bet, try again `lem lottery 10` for example")
            return
        if bet<0:
            await ctx.send(f"{ctx.author.mention}\nYou think I wouldnt see that coming? :)")
            return
        users = await self.get_bank_data()
        user = ctx.author
        if users[str(user.id)]['pocket'] < bet:
            await ctx.send(f"{ctx.author.mention}\nYou don't have enough money")
            return
        await self.update_balance(ctx.author, bet*-1)
        fruits = ['<:pineapple:881594630888620052>', '<:grapes:881594630888620052>', '<:cherries:881594630888620052>', '<:green_apple:881594630888620052>', '<:lemon:881594630888620052>']
        em =discord.Embed(title="Lottery", description="Your bet gets multiplied for each lemon", colour=discord.Color.from_rgb(254, 254, 51))
        fruit1 = random.choice(fruits)
        fruit2 = random.choice(fruits)
        fruit3 = random.choice(fruits)
        fruit4 = random.choice(fruits)
        win = 0
        if fruit1 == "<:lemon:881594630888620052>":
            win += bet
        if fruit2 == "<:lemon:881594630888620052>":
            win += bet
        if fruit3 == "<:lemon:881594630888620052>":
            win += bet
        if fruit4 == "<:lemon:881594630888620052>":
            win += bet

        multiplier = 0
        if win == bet:
            multiplier = 1
        if bet*2 == win:
            multiplier = 2
        if bet*3 == win:
            multiplier = 3
        if bet * 4 == win:
            multiplier = 4
        realwin = win-bet
        em.add_field(name=f"\u200b", value=f"<:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052>\n"
                                                      f"<:red_square:881594630888620052>{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}<:red_square:881594630888620052> \u200b **BET: {bet} lemons**\n"
                                                      f"<:arrow:881594485023314040>{fruit1}{fruit2}{fruit3}{fruit4}<:arrow_back:881594471521878047> \u200b **MULT: {multiplier}x**\n"
                                                      f"<:red_square:881594630888620052>{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}<:red_square:881594630888620052> \u200b **WIN: {realwin} lemons\n**"
                                                      f"<:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052>\n")
        if multiplier==0:
            em.set_footer(text="No luck today? :(")
        if multiplier==4:
            em.set_footer(text="JACKPOOOOOOOOOOOT")
        await ctx.send(embed=em)
        await self.update_balance(ctx.author, win)

    @commands.command()
    async def roulette(self, ctx, bet=0):
        if bet==0:
            await ctx.send(f"{ctx.author.mention}\nYou didn't set a bet, try again `lem roulette 10` for example")
            return
        if bet<0:
            await ctx.send(f"{ctx.author.mention}\nYou think I wouldnt see that coming? :)")
            return
        users = await self.get_bank_data()
        user = ctx.author
        if users[str(user.id)]['pocket'] < bet:
            await ctx.send(f"{ctx.author.mention}\nYou don't have enough money in their pocket!")
            return
        def check(message):
            return message.channel == ctx.channel and message.author == ctx.author

        await ctx.send("Where do you set your bet on?\n`red`🟥\n`black`⬛\n`odd` 1️⃣\n`even` ⃣\nnumber between `0` and `36`")

        try:
            # I can get both of the parameters of checkreaction like this
            msg = await self.client.wait_for('message', timeout=60, check=check)
            bid = "None"
            if msg.content.lower() == "red" or msg.content.lower() == "black" or msg.content.lower() == "odd" or msg.content.lower() == "even" or int(msg.content) >= 0 and int(msg.content) <= 36:
                await ctx.send(f"{ctx.author.mention}\nYou set your bet on {msg.content}")
                try:
                    bid = int(msg.content)
                except:
                    bid = msg.content.lower()

            else:
                await ctx.send(f"{ctx.author.mention}\nYou cant set your bet on that!")
                return
            number = random.randrange(0, 37)
            print(number)
            red = [9, 18, 7, 12, 3, 32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14]
            black = [31, 22, 29, 28, 35, 26, 15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20]
            iswon = False
            if bid == "red":
                if number in red:
                    iswon = True
            if bid == "black":
                if number in black:
                    iswon = True
            if bid == "odd":
                if number%2==1:
                    iswon = True
            if bid == "even":
                if number%2==0:
                    iswon = True
            if bid == number:
                iswon = True

            if iswon==False:
                line = "lost"
            if iswon==True:
                line= "won"
            img = Image.open("roulette2.png")
            img = img.rotate(45, PIL.Image.NEAREST, expand = 1)
            img.resize((500, 500))


            #draw = ImageDraw.Draw(img)
            #draw.ellipse((430, 215, 460, 245), fill=(255, 255, 255))

            img.save("roulettesaved.png")
            file = discord.File("roulettesaved.png")
            em = discord.Embed(colour=discord.Color.gold(), title=f"{user.name} {line} {bet} lemons!", description=f"The ball landed on the {number}!")
            em.set_image(url="attachment://roulettesaved.png")
            await ctx.send(f"{user.mention}\n", embed=em, file = file)


        except asyncio.TimeoutError:
            await ctx.send(f"{user.name} did not accept in time")
            return
    @commands.command()
    async def tictactoe(self, ctx, enemy: discord.User, bet=0):
        if bet==0:
            await ctx.send(f"{ctx.author.mention}\nYou didn't set a bet, try again `lem tictactoe `{enemy.name}` 10` for example")
            return
        if bet<0:
            await ctx.send(f"{ctx.author.mention}\nYou think I wouldnt see that coming? :)")
            return
        users = await self.get_bank_data()
        user = ctx.author
        if users[str(user.id)]['pocket'] < bet or users[str(enemy.id)]['pocket'] < bet:
            await ctx.send(f"{ctx.author.mention}\nYou or your enemy doesn't have enough money in their pocket!")
            return

        def checkreaction(reaction, user):
            return reaction.message.id == msg.id and user == enemy and reaction.emoji == "✅" or reaction.message.id == msg.id and user == enemy and reaction.emoji == "❌"


        msg = await ctx.send(f"{enemy.name} has 60 seconds to accept!")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        try:
            # I can get both of the parameters of checkreaction like this
            reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=checkreaction)

            if reaction.emoji == "❌":
                await ctx.send(f"{ctx.author.mention}\n{enemy.name} dosent wanna play tictactoe with you right now <:Sadge:720250426892615745>")
                return


        except asyncio.TimeoutError:
            await ctx.send(f"{enemy.name} did not accept in time")
            return

        await ctx.send(f"{enemy.name} accepted, let the battle begin!")



        gameboard = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        player1 = ctx.author
        player2 = enemy
        players = [player1, player2]
        starter = random.choice(players)

        await ctx.send(f"{starter.name} starts\nNow type `top left` , `top mid` , `top right` , `mid left`, `mid mid` , `mid right` , `bot left`, `bot mid` or `bot right`")
        topleft1 = "<:rect843:881875152630059019>"
        topleft2 = "<:rect843:881875152630059019>"
        topleft3 = "<:rect843:881875152630059019>"
        topleft4 = "<:rect843:881875152630059019>"
        topmid1 = "<:rect843:881875152630059019>"
        topmid2 = "<:rect843:881875152630059019>"
        topmid3 = "<:rect843:881875152630059019>"
        topmid4 = "<:rect843:881875152630059019>"
        topright1 = "<:rect843:881875152630059019>"
        topright2 = "<:rect843:881875152630059019>"
        topright3 = "<:rect843:881875152630059019>"
        topright4 = "<:rect843:881875152630059019>"
        midleft1 = "<:rect843:881875152630059019>"
        midleft2 = "<:rect843:881875152630059019>"
        midleft3 = "<:rect843:881875152630059019>"
        midleft4 = "<:rect843:881875152630059019>"
        midmid1 = "<:rect843:881875152630059019>"
        midmid2 = "<:rect843:881875152630059019>"
        midmid3 = "<:rect843:881875152630059019>"
        midmid4 = "<:rect843:881875152630059019>"
        midright1 = "<:rect843:881875152630059019>"
        midright2 = "<:rect843:881875152630059019>"
        midright3 = "<:rect843:881875152630059019>"
        midright4 = "<:rect843:881875152630059019>"
        botleft1 = "<:rect843:881875152630059019>"
        botleft2 = "<:rect843:881875152630059019>"
        botleft3 = "<:rect843:881875152630059019>"
        botleft4 = "<:rect843:881875152630059019>"
        botmid1 = "<:rect843:881875152630059019>"
        botmid2 = "<:rect843:881875152630059019>"
        botmid3 = "<:rect843:881875152630059019>"
        botmid4 = "<:rect843:881875152630059019>"
        botright1 = "<:rect843:881875152630059019>"
        botright2 = "<:rect843:881875152630059019>"
        botright3 = "<:rect843:881875152630059019>"
        botright4 = "<:rect843:881875152630059019>"

        isWon = False

        turn = 0
        #turn
        while True:
            if turn != 0:

                if str(starter) == str(player1):
                    starter = player2
                else:
                    starter = player1







            if gameboard[0][0] == 1:
                topleft1 = "<:x1:881870717451391006>"
                topleft2 = "<:x2:881870728339808286>"
                topleft3 = "<:x3:881870748925440030>"
                topleft4 = "<:x4:881870748707336292>"
            if gameboard[0][1] == 1:
                topmid1 = "<:x1:881870717451391006>"
                topmid2 = "<:x2:881870728339808286>"
                topmid3 = "<:x3:881870748925440030>"
                topmid4 = "<:x4:881870748707336292>"
            if gameboard[0][2] == 1:
                topright1 = "<:x1:881870717451391006>"
                topright2 = "<:x2:881870728339808286>"
                topright3 = "<:x3:881870748925440030>"
                topright4 = "<:x4:881870748707336292>"
            if gameboard[1][0] == 1:
                midleft1 = "<:x1:881870717451391006>"
                midleft2 = "<:x2:881870728339808286>"
                midleft3 = "<:x3:881870748925440030>"
                midleft4 = "<:x4:881870748707336292>"
            if gameboard[1][1] == 1:
                midmid1 = "<:x1:881870717451391006>"
                midmid2 = "<:x2:881870728339808286>"
                midmid3 = "<:x3:881870748925440030>"
                midmid4 = "<:x4:881870748707336292>"
            if gameboard[1][2] == 1:
                midright1 = "<:x1:881870717451391006>"
                midright2 = "<:x2:881870728339808286>"
                midright3 = "<:x3:881870748925440030>"
                midright4 = "<:x4:881870748707336292>"
            if gameboard[2][0] == 1:
                botleft1 = "<:x1:881870717451391006>"
                botleft2 = "<:x2:881870728339808286>"
                botleft3 = "<:x3:881870748925440030>"
                botleft4 = "<:x4:881870748707336292>"
            if gameboard[2][1] == 1:
                botmid1 = "<:x1:881870717451391006>"
                botmid2 = "<:x2:881870728339808286>"
                botmid3 = "<:x3:881870748925440030>"
                botmid4 = "<:x4:881870748707336292>"
            if gameboard[2][2] == 1:
                botright1 = "<:x1:881870717451391006>"
                botright2 = "<:x2:881870728339808286>"
                botright3 = "<:x3:881870748925440030>"
                botright4 = "<:x4:881870748707336292>"

            ##player2
            if gameboard[0][0] == 2:
                topleft1 = "<:o1:881935408378822676>"
                topleft2 = "<:o2:881935419313389569>"
                topleft3 = "<:o4:881935448501547018>"
                topleft4 = "<:o4:881935426330431548>"
            if gameboard[0][1] == 2:
                topmid1 = "<:o1:881935408378822676>"
                topmid2 = "<:o2:881935419313389569>"
                topmid3 = "<:o4:881935448501547018>"
                topmid4 = "<:o4:881935426330431548>"
            if gameboard[0][2] == 2:
                topright1 = "<:o1:881935408378822676>"
                topright2 = "<:o2:881935419313389569>"
                topright3 = "<:o4:881935448501547018>"
                topright4 = "<:o4:881935426330431548>"
            if gameboard[1][0] == 2:
                midleft1 = "<:o1:881935408378822676>"
                midleft2 = "<:o2:881935419313389569>"
                midleft3 = "<:o4:881935448501547018>"
                midleft4 = "<:o4:881935426330431548>"
            if gameboard[1][1] == 2:
                midmid1 = "<:o1:881935408378822676>"
                midmid2 = "<:o2:881935419313389569>"
                midmid3 = "<:o4:881935448501547018>"
                midmid4 = "<:o4:881935426330431548>"
            if gameboard[1][2] == 2:
                midright1 = "<:o1:881935408378822676>"
                midright2 = "<:o2:881935419313389569>"
                midright3 = "<:o4:881935448501547018>"
                midright4 = "<:o4:881935426330431548>"
            if gameboard[2][0] == 2:
                botleft1 = "<:o1:881935408378822676>"
                botleft2 = "<:o2:881935419313389569>"
                botleft3 = "<:o4:881935448501547018>"
                botleft4 = "<:o4:881935426330431548>"
            if gameboard[2][1] == 2:
                botmid1 = "<:o1:881935408378822676>"
                botmid2 = "<:o2:881935419313389569>"
                botmid3 = "<:o4:881935448501547018>"
                botmid4 = "<:o4:881935426330431548>"
            if gameboard[2][2] == 2:
                botright1 = "<:o1:881935408378822676>"
                botright2 = "<:o2:881935419313389569>"
                botright3 = "<:o4:881935448501547018>"
                botright4 = "<:o4:881935426330431548>"

            await ctx.send(
                f"{topleft1}{topleft2}:white_large_square:{topmid1}{topmid2}:white_large_square:{topright1}{topright2}\n"
                f"{topleft3}{topleft4}:white_large_square:{topmid3}{topmid4}:white_large_square:{topright3}{topright4}\n"
                f":white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n"
                f"{midleft1}{midleft2}:white_large_square:{midmid1}{midmid2}:white_large_square:{midright1}{midright2}\n"
                f"{midleft3}{midleft4}:white_large_square:{midmid3}{midmid4}:white_large_square:{midright3}{midright4}\n"
                f":white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n"
                f"{botleft1}{botleft2}:white_large_square:{botmid1}{botmid2}:white_large_square:{botright1}{botright2}\n"
                f"{botleft3}{botleft4}:white_large_square:{botmid3}{botmid4}:white_large_square:{botright3}{botright4}\n")


            def checkturn(m):
                if m.author != starter or m.channel != ctx.channel:
                    return False
                return m.content == f"top left" or m.content == f"top mid" or m.content == f"top right" or m.content == f"mid left" or m.content == f"mid mid" or m.content == f"mid right" or m.content == f"bot left" or m.content == f"bot mid" or m.content == f"bot right"
            if turn != 0:
                await ctx.send(f"Now it's {starter.mention}'s turn.\nType `top left` , `top mid` , `top right` , `mid left`, `mid mid` , `mid right` , `bot left`, `bot mid` or `bot right`")
            turn = turn+1
            while True:
                try:
                    msg = await self.client.wait_for('message', timeout=30, check=checkturn)
                    msg.content = msg.content.lower()
                    if msg.content == "top left" and starter == player1:
                        if gameboard[0][0] == 0:
                            gameboard[0][0] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "top mid" and starter == player1:
                        if gameboard[0][1] == 0:
                            gameboard[0][1] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "top right" and starter == player1:
                        if gameboard[0][2] == 0:
                            gameboard[0][2] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "mid left" and starter == player1:
                        if gameboard[1][0] == 0:
                            gameboard[1][0] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "mid mid" and starter == player1:
                        if gameboard[1][1] == 0:
                            gameboard[1][1] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "mid right" and starter == player1:
                        if gameboard[1][2] == 0:
                            gameboard[1][2] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "bot left" and starter == player1:
                        if gameboard[2][0] == 0:
                            gameboard[2][0] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "bot mid" and starter == player1:
                        if gameboard[2][1] == 0:
                            gameboard[2][1] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "bot right" and starter == player1:
                        if gameboard[2][2] == 0:
                            gameboard[2][2] = 1
                            break
                        else:
                            await ctx.send("You can't mark this field")


                    #player2
                    if msg.content == "top left" and starter == player2:
                        if gameboard[0][0] == 0:
                            gameboard[0][0] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "top mid" and starter == player2:
                        if gameboard[0][1] == 0:
                            gameboard[0][1] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "top right" and starter == player2:
                        if gameboard[0][2] == 0:
                            gameboard[0][2] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "mid left" and starter == player2:
                        if gameboard[1][0] == 0:
                            gameboard[1][0] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "mid mid" and starter == player2:
                        if gameboard[1][1] == 0:
                            gameboard[1][1] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "mid right" and starter == player2:
                        if gameboard[1][2] == 0:
                            gameboard[1][2] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "bot left" and starter == player2:
                        if gameboard[2][0] == 0:
                            gameboard[2][0] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "bot mid" and starter == player2:
                        if gameboard[2][1] == 0:
                            gameboard[2][1] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")
                    if msg.content == "bot right" and starter == player2:
                        if gameboard[2][2] == 0:
                            gameboard[2][2] = 2
                            break
                        else:
                            await ctx.send("You can't mark this field")

                except:
                    await ctx.send(f"{enemy.name} did not answer in time")
                    return

            if gameboard[0][0] == 1 and gameboard[0][1] == 1 and gameboard[0][2] == 1:
                isWon = True
                winner = player1
            if gameboard[1][0] == 1 and gameboard[1][1] == 1 and gameboard[1][2] == 1:
                isWon = True
                winner = player1
            if gameboard[2][0] == 1 and gameboard[2][1] == 1 and gameboard[2][2] == 1:
                isWon = True
                winner = player1

            if gameboard[0][0] == 1 and gameboard[1][0] == 1 and gameboard[2][0] == 1:
                isWon = True
                winner = player1
            if gameboard[0][1] == 1 and gameboard[1][1] == 1 and gameboard[2][1] == 1:
                isWon = True
                winner = player1
            if gameboard[0][2] == 1 and gameboard[1][2] == 1 and gameboard[2][2] == 1:
                isWon = True
                winner = player1

            if gameboard[0][0] == 1 and gameboard[1][1] == 1 and gameboard[2][2] == 1:
                isWon = True
                winner = player1
            if gameboard[0][2] == 1 and gameboard[1][1] == 1 and gameboard[2][0] == 1:
                isWon = True
                winner = player1

            if gameboard[0][0] == 2 and gameboard[0][1] == 2 and gameboard[0][2] == 2:
                isWon = True
                winner = player2
            if gameboard[1][0] == 2 and gameboard[1][1] == 2 and gameboard[1][2] == 2:
                isWon = True
                winner = player2
            if gameboard[2][0] == 2 and gameboard[2][1] == 2 and gameboard[2][2] == 2:
                isWon = True
                winner = player2

            if gameboard[0][0] == 2 and gameboard[1][0] == 2 and gameboard[2][0] == 2:
                isWon = True
                winner = player2
            if gameboard[0][1] == 2 and gameboard[1][1] == 2 and gameboard[2][1] == 2:
                isWon = True
                winner = player2
            if gameboard[0][2] == 2 and gameboard[1][2] == 2 and gameboard[2][2] == 2:
                isWon = True
                winner = player2

            if gameboard[0][0] == 2 and gameboard[1][1] == 2 and gameboard[2][2] == 2:
                isWon = True
                winner = player2
            if gameboard[0][2] == 2 and gameboard[1][1] == 2 and gameboard[2][0] == 2:
                isWon = True
                winner = player2

            if isWon == True:

                em = discord.Embed(colour=discord.Color.gold(),
                                   title=f"Congratulations, {winner.name} won the bet of {bet} lemons!")
                if winner == player2:
                    looser = player1
                else:
                    looser = player2
                await self.update_balance(winner, bet)
                await self.update_balance(looser, -1 * bet)
                await ctx.send(embed=em)
                return

            if gameboard[0][0] != 0 and gameboard[0][1] != 0 and gameboard[0][2] != 0 and gameboard[1][0] != 0 and \
                    gameboard[1][1] != 0 and gameboard[1][2] != 0 and gameboard[2][0] != 0 and gameboard[2][1] != 0 and \
                    gameboard[2][2] != 0:
                await ctx.send("It's a draw, nobody won. What a pitty!")
                return

    @commands.command(aliases=["wouldyourather", "would you rather"])
    async def wyr(self, ctx):
        users = await self.get_bank_data()
        user = ctx.author
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        if users[str(user.id)]["pocket"] < 25:
            await ctx.send(f"{ctx.author.mention}\nYou dont have enough money!")
            return
        await self.update_balance(user, -25)
        await ctx.send(f"{ctx.author.mention}\nYou succesfully paid your 25 lemons for this question!")
        with open("wyr.json", "r") as f:
            wyr = json.load(f)
        while True:
            scenedict = random.choice(wyr)
            scenedict2 = random.choice(wyr)
            if scenedict["category"] == scenedict2["category"]:
                break
        scene = scenedict["scene"]
        scene2 = scenedict2["scene"]
        await ctx.send(f"{ctx.author.mention}\nWould you rather {scene} or {scene2}")

    @commands.command()
    async def collectibles(self, ctx, page=1):
        page = int(page)
        em = discord.Embed(title="All collectibles", colour=discord.Color.dark_teal())
        with open("collectibles.json", "r", encoding="utf-8") as f:
            collectibles = json.load(f)
        all_collectibles = 0

        for collectible in collectibles:
            all_collectibles += 1
        pages = math.ceil(all_collectibles / 10)
        if page > pages or pages < 1:
            await ctx.send(f"There are only {pages} pages")
            return
        if page == 1:
            for i in range(10):
                try:
                    name = collectibles[i]["name"]
                    emoji = collectibles[i]["emoji"]
                    desc = collectibles[i]["desc"]
                except:
                    break
                em.add_field(name=f"{name} {emoji}", value=f"{desc}", inline=False)
        else:
            for i in range(page*10-10, page*10+10):
                try:
                    name = collectibles[i]["name"]
                    emoji = collectibles[i]["emoji"]
                    desc = collectibles[i]["desc"]
                except:
                    break
                em.add_field(name=f"{name} {emoji}", value=f"{desc}", inline=False)

        em.set_footer(text=f"{page} / {pages}")
        await ctx.send(embed=em)



    @commands.command()
    async def collection(self, ctx, page=1):
        user = ctx.author
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        users = await self.get_bank_data()

        try:
            collection = users[str(user.id)]["collectibles"]
        except:
            collection = []
        with open("collectibles.json", "r", encoding="utf-8") as f:
            collectibles = json.load(f)

        em = discord.Embed(title="Your Collection", colour=discord.Color.teal())
        collectibles_amount = 0
        all_collectibles = 0
        for collectible in collectibles:
            all_collectibles += 1
        for item in collection:
            name = item["name"]
            name_ = name.capitalize()
            amount = item["amount"]
            collectibles_amount += 1
            for collectible in collectibles:
                emoji = collectible["emoji"]
                if name == collectible["name"]:
                    break

            if amount > 0:
                em.add_field(name=f"{name_} {emoji}", value=f"amount: `{amount}`", inline=False)
        pages = math.ceil(collectibles_amount/10)
        em.set_footer(text=f"{collectibles_amount} / {all_collectibles} collectibles")
        await ctx.send(embed=em)


    @commands.command()
    async def vendingmachine(self, ctx):
        users = await self.get_bank_data()
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        user = ctx.author
        if users[str(user.id)]["pocket"] < 150:
            await ctx.send(f"{ctx.author.mention}\nYou dont have enough money!")
            return
        with open("collectibles.json", "r", encoding="utf-8") as f:
            collectibles = json.load(f)

        collectible = random.choice(collectibles)
        name = collectible["name"]
        emoji = collectible["emoji"]
        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["collectibles"]:
                n = thing["name"]
                if n == name:
                    old_amt = thing["amount"]
                    new_amt = old_amt + 1
                    users[str(user.id)]["collectibles"][index]["amount"] = new_amt
                    t = 1
                    break
                index += 1
            if t == None:
                obj = {"name": name, "amount": 1}
                users[str(user.id)]["collectibles"].append(obj)
        except:
            obj = {"name": name, "amount": 1}
            users[str(user.id)]["collectibles"] = [obj]
        with open('lemonbank.json', 'w') as f:
            json.dump(users, f, indent=4)
        await self.update_balance(ctx.author, -150)
        em = discord.Embed(title=f"You threw your 150 <:lemon2:881595266757713920> lemons into a vending machine and got a {name} {emoji}", description="Dont ask me how you can throw 150 lemons in there", colour=discord.Color.dark_blue())
        await ctx.send(embed=em)

    @commands.command()
    async def use(self, ctx, item="None"):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nYou need to use `lem startup` first")
            return
        if item == "None":
            await ctx.send(f"{ctx.author.mention}\nYou cant use nothing")
            return
        user = ctx.author
        users = await self.get_bank_data()
        checkifitem = 0
        index = -1
        for item_ in users[str(user.id)]["bag"]:
            item_name = item_["item"]
            item_amount = item_["amount"]
            index = index +1
            if item.lower() == item_name.lower():
                if item_amount <= 0:
                    await ctx.send(f"{ctx.author.mention}\nYou dont have {item_name.capitalize()}")
                    return
                else:
                    checkifitem = 1
                break
        if checkifitem == 0:
            print(users[str(user.id)]["bag"][index]["item"])
            if users[str(user.id)]["bag"][index]["item"] != item.lower():
                await ctx.send(f"{ctx.author.mention}\nYou dont have {item.capitalize()}")
                return
        item = item.lower()
        if item == "lemonade":
            await ctx.send(f"{ctx.author.mention}\nYou just drank lemonade that was made by lemons, that you bought with the lemons, that you get paid as a lemon farmer for harvesting lemons")
            await ctx.send("But atleast you got refreshed, so who cares")
            await ctx.send("<:FeelsDankMan:810802803739983903>")
            print(index)
            users[str(user.id)]["bag"][index]["amount"] = item_amount-1
            with open('lemonbank.json', 'w') as f:
                json.dump(users, f, indent=4)
            return
        if item == "candy":
            lines = ["You like the candy, because it tasted like lemon!", "You didnt like this candy", "You spit the candy out, because it was so gross", "Mmmmm lime also tastes good", "You threw the ananas candy in the trash, because you were eating pizza at the same time"]
            line = random.choice(lines)
            await ctx.send(line)
            print(index)
            users[str(user.id)]["bag"][index]["amount"] = item_amount-1
            with open('lemonbank.json', 'w') as f:
                json.dump(users, f, indent=4)
            return

        if item == "flowers":
            await ctx.send(f"{ctx.author.mention}\nWho will be the happy one that gets your beautiful flowers?")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send("You didnt answer in time")
                return
            lines = ["cried of happiness", "said thank you", "thanked you for them", "put them in a vase", "was confused", "is allergic to flowers", "was angry because they are bad ones", "doesnt like the colour of the flowers"]
            line = random.choice(lines)

            try:
                class id:
                    id = msg.content[3:len(msg.content) - 1]
                    id = int(id)

                print(msg.content)

                print(id)

                users[str(user.id)]["bag"][index]["amount"] = item_amount - 1
                await ctx.send(f"You gifted your flowers to {msg.content}, they " + line)
                with open('lemonbank.json', 'w') as f:
                    json.dump(users, f, indent=4)
                try:
                    await self.update_balance(id, 15)
                    await self.buy_this(id, "flowers", 1)
                    return
                except:
                    await ctx.send(f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                    return

            except:
                await ctx.send(f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                return

        if item == "safe":

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "dep" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "depot" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "with" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "withdraw" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "witd" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "deposit"

            users = await self.get_bank_data()
            try:
                safe = users[str(user.id)]["bag"][index]
                money = safe["money"]
            except:
                users[str(user.id)]["bag"][index]["money"] = 0
                money = users[str(user.id)]["bag"][index]["money"]
            em = discord.Embed(colour=discord.Color.dark_gray(), title="Your safe <:safe:885811224418332692>", description=f"`{money}` lemons")
            await ctx.send(f"{user.mention}\nDo you want to `deposit` or `withdraw` money from your safe?", embed=em)
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{user.mention}\nYou didnt answer in time")
                return

            if msg.content.lower() == "dep" or msg.content.lower() == "depot" or msg.content.lower() == "deposit":
                userbal = users[str(user.id)]["pocket"]

                def checkmoney(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                await ctx.send(f"{user.mention}\nHow much lemons do you want to deposit?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkmoney)
                except:
                    await ctx.send(f"{user.mention}\nYou didnt answer in time")
                    return
                try:

                    amountmoney = int(msg.content)
                except:
                    await ctx.send(f"{user.mention}\nNo")
                    return
                if amountmoney < 0:
                    await ctx.send(f"{user.mention}\nYou know, you can also `withdraw` money")
                    return
                if userbal < amountmoney:
                    await ctx.send(f"{user.mention}\nYou dont have enough money!")
                    return
                maxamount = 5000
                if money+amountmoney > 5000:
                    await ctx.send(f"{user.mention}\nYou can only store `5000` lemons in your safe!")
                    return

                newamt = money + amountmoney
                users[str(user.id)]["bag"][index]["money"] += amountmoney

                with open('lemonbank.json', 'w') as f:
                    json.dump(users, f, indent=4)
                await self.update_balance(user, -1 * amountmoney)
                await ctx.send(f"{user.mention}\nYou now have `{newamt}` lemons stored in your safe")
                return
            if msg.content.lower() == "withdraw" or msg.content.lower() == "witd" or msg.content.lower() == "with":
                userbal = users[str(user.id)]["pocket"]

                def checkmoney(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                await ctx.send(f"{user.mention}\nHow much lemons do you want to withdraw?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkmoney)
                except:
                    await ctx.send(f"{user.mention}\nYou didnt answer in time")
                    return
                try:
                    amountmoney = int(msg.content)
                except:
                    await ctx.send(f"{user.mention}\nNo")
                    return
                if amountmoney < 0:
                    await ctx.send(f"{user.mention}\nYou know, you can also `deposit` money")
                    return

                if amountmoney > money:
                    await ctx.send(f"{user.mention}\nYou dont have enough lemons in your safe!")
                    return

                newamt = money - amountmoney
                users[str(user.id)]["bag"][index]["money"] -= amountmoney
                with open('lemonbank.json', 'w') as f:
                    json.dump(users, f, indent=4)
                await self.update_balance(user, amountmoney)
                await ctx.send(f"{user.mention}\nYou now have `{newamt}` lemons stored in your safe")
                return
            return



        if item == "present":
            await ctx.send(f"{ctx.author.mention}\nWhat item do you want to gift?")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return

            present_item_index = -1
            itemreal = 0
            for present_item in users[str(user.id)]["bag"]:
                present_item_name = present_item["item"]
                present_item_amount = present_item["amount"]
                present_item_index = index + 1
                present_item_name = present_item_name.lower()
                if msg.content.lower() == present_item_name.lower():
                    if present_item_amount <= 0:
                        await ctx.send(f"{ctx.author.mention}\nYou dont have {present_item_name.capitalize()}")
                        return
                    itemreal = 1
                    break
            if itemreal == 0:
                await ctx.send(f"{ctx.author.mention}\nThat item doesnt exist or you dont have it!")
                return

            ###now user
            lines = ["cried of happiness", "said thank you", "thanked you for it",
                     "was confused"]
            line = random.choice(lines)

            await ctx.send(f"{ctx.author.mention}\nWho will be the happy one? (@ them)")

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return

            try:
                class id:
                    id = msg.content[3:len(msg.content) - 1]
                    id = int(id)

                print(msg.content)

                print(id)
                if user.id == id.id:
                    await ctx.send(f"{ctx.author.mention}\nYou cant just give yourself a present!")
                    return

                users[str(user.id)]["bag"][index]["amount"] = item_amount - 1

                await ctx.send(f"{ctx.author.mention}\nYou gifted {present_item_name} to {msg.content}, they " + line)
                with open('lemonbank.json', 'w') as f:
                    json.dump(users, f, indent=4)

                for shopitem in self.mainshop:
                    price = shopitem["price"]
                    if shopitem["name"].lower() == present_item_name.lower():
                        break
                try:
                    await self.update_balance(user, int((-1)*(price/2)))
                    await self.sell_this(user, present_item_name, 1)
                    await self.update_balance(id, price)
                    await self.buy_this(id, present_item_name, 1)
                    return
                except:
                    await ctx.send(f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                    return

            except:
                await ctx.send(f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                return

            return






        if item == "conchshell":
            await ctx.send(f"{ctx.author.mention}\nAhhh I see, you need Trustpilot 10⭐ advice...what lies on your heart my friendo?")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            message = await ctx.send("*Ziiip*")
            time.sleep(4)
            lines = ["Yes", "No", "Why", "I dont know", "Ask again", "Of course", "No you are not", "Take the RTX 3060", "No dont buy Intel CPUs", "I know the answer", "The answer is:", "Why always ask me? You dont have a brain?", "No Squidward, you cant have anything to eat", "Long live the Conch Shell"]
            advice = random.choice(lines)
            await message.edit(content=advice)
            return


        if item == "mobile":
            em = discord.Embed(title="Who do you want to call?", colour=discord.Color.dark_blue(), description="`krusty crab`\n`telephone joker`\n`911`")
            em.set_footer(text="Just type the name")
            await ctx.send(embed = em)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "krusty crab" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "telephone joker" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "911"

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send("You didnt answer in time")
                return
            message = await ctx.send("Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
            time.sleep(2.5)
            await message.edit(content="Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
            time.sleep(3)
            if msg.content.lower() == "krusty crab":
                await message.edit(content="You: Hello, is this the Krusty Crab?")
                time.sleep(4)
                await message.edit(content="Krusty Crab: No, this is Patrick")
                time.sleep(4.2)
                await message.edit(content="You: Are you sure this isn't the Krusty Crab?")
                time.sleep(4.5)
                await message.edit(content="Krusty Crab: NO, THIS IS PATRICK")
                time.sleep(4)
                await message.edit(content="Patrick hung up on you...but you are calling again")
                time.sleep(4.5)
                await message.edit(content="Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
                time.sleep(4.5)
                await message.edit(content="Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
                time.sleep(4.5)
                await message.edit(content="You are talking in a slightly higher voice: Hello, is this the Krusty Crab?")
                time.sleep(4)
                await message.edit(content="KrUsTy CrAb: NoOoOoOoOoOoOoOo ThIs Is PaTrIcK")
                time.sleep(4)
                await message.edit(content="`deeeeepieeebieeep`")
                return
            if msg.content == "911":
                await message.edit(content="You: HELP ME HELP ME PLEASE IM GETTING ROBBED")
                time.sleep(7)
                await message.edit(content="Someone: You're POOR so it doesn't matter anyway")
                time.sleep(7.5)
                await message.edit(content="`deeeeepieeebieeep`")
                return
            if msg.content == "telephone joker":
                jokes = ['Singing in the shower is fun until you get soap in your mouth. Then its a soap opera.', 'What do you call a fish wearing a bowtie? Sofishticated.', 'Dear Math, grow up and solve your own problems.', 'Can a kangaroo jump higher than the empire state building? Of course! Buildings can’t jump', 'Why was the robot so tired after his road trip? He had a hard drive.', 'I was wondering why this frisbee kept looking bigger and bigger. Then it hit me.', 'A man rushed into a Doctors surgery, shouting "help me please, Im shrinking" The Doctor calmly said "now settle down a bit… youll just have to learn to be a little patient".', 'When I moved into my new igloo my friends threw me a surprise house-warming party. Now Im homeless.', 'I met my wife on Tinder. That was awkward.', 'My friend is fed up with my constant stream of dad jokes, so I asked her, "How can I stop my addiction?!" She shot back, "Whatever means necessary!!" I replied, "No, it doesnt!”', 'What’s the difference between a literalist and a kleptomaniac? A literalist takes things literally. A kleptomaniac takes things, literally.', 'ts been months since I bought the book, "How to scam people online." It still hasnt arrived yet.', "why did syndra run away from the fight? Because she had no balls <:OmegaLUL:598583138758950932>", "Why did the scarecrow win an award? Because he was outstanding in his field."]
                joke = random.choice(jokes)
                await message.edit(content=joke)
                return

        if item == "laptop":
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            def checkreaction(reaction, user):
                return reaction.message.id == message.id and user == ctx.author

            message = await ctx.send("What do you want to do on your computer?\n`Browse`\n`Minecraft`\n`League of Legends`")
            await message.add_reaction('<:GoogleChrome:883281638270844958>')
            await message.add_reaction('<:minecra:883287114270261268>')
            # YOU NEED TO AWAIT LMAO
            try:
                reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
            except asyncio.TimeoutError:
                await ctx.send('You didnt answer fast enough!')
                return
            print(reaction.emoji)
            if str(reaction.emoji) == "<:GoogleChrome:883281638270844958>":
                msg = await ctx.send(f"{ctx.author.mention}\nWhat do you want to browse on the web?\n`animals`\n`memes`\n`random facts`")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=check)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                if msg.content.lower() == "animals":
                    embed = discord.Embed(title="*Cute?*")

                    file_path_type = ["./animals/*.png", "./animals/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await ctx.send(file=file, embed=embed)
                    return
                elif msg.content.lower() == "memes":

                    embed = discord.Embed(title="*Funney?*")

                    file_path_type = ["./memes/*.png", "./memes/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await ctx.send(file=file, embed=embed)

                    return
                elif msg.content.lower() == "random facts":

                    embed = discord.Embed(title="*Interestestestesting*")

                    file_path_type = ["./randomfacts/*.png", "./randomfacts/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await ctx.send(file=file, embed=embed)

                    return
                else:
                    await ctx.send("You cant browse that!")
                    return
                return
            if str(reaction.emoji) == "<:minecra:883287114270261268>":
                users = await self.get_bank_data()
                userlist = []
                for user in users:
                    userlist.append(user)
                print(userlist)
                user = random.choice(userlist)
                print(user)
                lines = [f"You and <@!{user}> built a wooden house!", f"You and <@!{user}> played Minecraft for 5 hours", f"<@!{user}> set you a redstone trap and you fell for it", f"<@!{user}> and you built a lemon tree", f"<@!{user}> and you built a big mansion", f"<@!{user}> and you built a giant mob farm"]
                line = random.choice(lines)
                await ctx.send(line)
                return


        if item == "cheesecake":
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "eat" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "throw" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "share"
            def checkperson(m):
                return m.author == ctx.author and m.channel == ctx.channel
            await ctx.send(f"{ctx.author.mention}\nDo you want to `eat`, `throw` or `share` the cake? (Answer with `eat`, `throw` or `share`)")

            #YOU NEED TO AWAIT LMAO
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            if msg.content.lower() == "eat":
                await ctx.send(f"{ctx.author.mention}\nYou ate your cheesecake, it was very delicious")
                users[str(user.id)]["bag"][index]["amount"] = item_amount - 1
            elif msg.content.lower() == "share":
                await ctx.send(f"{ctx.author.mention}\nWith whom you want to share your cheesecake?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                person = msg.content
                await ctx.send(f"{ctx.author.mention}\nYou shared your cake with {person}!")
                users[str(user.id)]["bag"][index]["amount"] = item_amount - 1
            else:
                await ctx.send(f"{ctx.author.mention}\nWho will be your victim?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                person = msg.content
                await ctx.send(f"{ctx.author.mention}\nYou throw your cake at {person}")
                users[str(user.id)]["bag"][index]["amount"] = item_amount - 1
            with open('lemonbank.json', 'w') as f:
                json.dump(users, f, indent=4)
            return

        if item == "pinata":

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "use" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "gift"

            def checkperson(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send(f"{ctx.author.mention}\nDo you want to `use` or `gift` the pinata? (Answer with `use` or `gift`)")

            # YOU NEED TO AWAIT LMAO
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            if msg.content.lower() == "use":
                times = random.randrange(2, 10)
                candy = random.randrange(3, 7)
                print(candy)
                await ctx.send(f"{ctx.author.mention}\nAfter you hit 🏏 the pinata `{times}` times you got {candy} candy!")
                users[str(user.id)]["bag"][index]["amount"] = item_amount - 1
                with open('lemonbank.json', 'w') as f:
                    json.dump(users, f, indent=4)

                # IMPORTANT THE WITH OPEN BEFORE THE UPDATE OR IT WILL OVERWRITE THIS STUPID BAL AND BUYTHIS

                await self.update_balance(user, 10*candy)
                await self.buy_this(user, "candy", candy)



            else:
                await ctx.send(f"{ctx.author.mention}\nWho gets the pinata?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                try:
                    class id:
                        id = msg.content[3:len(msg.content) - 1]
                        id = int(id)

                    print(msg.content)
                    print(id)
                    users[str(user.id)]["bag"][index]["amount"] = item_amount - 1
                    await ctx.send(f"{ctx.author.mention}\nYou gifted your pinata to {msg.content}, muchas gracias they said")
                    with open('lemonbank.json', 'w') as f:
                        json.dump(users, f, indent=4)
                    try:
                        await self.update_balance(id, 150)
                        await self.buy_this(id, "pinata", 1)
                        return
                    except:
                        await ctx.send(
                            f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                        return
                except:
                    await ctx.send(
                        f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                    return




        else:
            await ctx.send(f"{ctx.author.mention}\nThat item does not exist or has no usage yet")







#####################################
##############JOBS##################
################################

    joblist = [{'Name': 'Lemon Farmer', 'Verdienst': 10, 'Beschreibung': ' Start little as a lemon farmer', 'lvl': 1},
               {'Name': 'Reddit Analyst', 'Verdienst': 20, 'Beschreibung': ' Carefully analyse r/woooosh posts', 'lvl': 3},
               {'Name': 'Lemonade salesman', 'Verdienst': 25, 'Beschreibung': ' sell overpriced lemonade to strangers', 'lvl': 4},
               {'Name': 'Discord Mod', 'Verdienst': 30, 'Beschreibung': ' Be a good Mod! Or Rocsie will get you!', 'lvl': 5},
               {'Name': 'Cat Enjoyer', 'Verdienst': 35, 'Beschreibung': ' <a:catJAM:810785548678987776><a:catJAM:810785548678987776><a:catJAM:810785548678987776>', 'lvl': 6},
               {'Name': 'Lemon Researcher', 'Verdienst': 40, 'Beschreibung': ' research 🔎 lemons 🍋', 'lvl': 7},
               {'Name': 'Pizza guy', 'Verdienst': 45, 'Beschreibung': ' make some pizza 🍕', 'lvl': 8}]

    async def job_helper(self, ctx):
        embed = discord.Embed(title='Help for the job command:', description="First use `lem job list` to take a look which jobs you can appeal for, then you can select them with `lem job select lemon farmer` for example. After that you can work with `lem work` and complete several tasks")
        embed.add_field(name='Job info', value='Look up your current job!', inline=False)
        embed.add_field(name='Job list', value='List every job!', inline=False)
        embed.add_field(name='Job select', value='Select a job that is in the list!',
                        inline=False)
        embed.add_field(name='lem work', value='Work, work, work, work...', inline=False)
        embed.set_footer(text='Send job ideas to @qBaumi#1247!')
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['jobs'])
    async def job(self, ctx, arg1='None', *, arg2='None'):
        users = await self.get_bank_data()
        user = ctx.author
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            return
        try:
            xp = users[str(user.id)]["xp"]
            lvl = users[str(user.id)]["lvl"]
        except:
            xp = users[str(user.id)]["xp"] = 0
            lvl = users[str(user.id)]["lvl"] = 1

        users[str(user.id)]["xp"] += 5
        lvl_start = users[str(user.id)]["lvl"]
        lvl_end = int(xp ** (1 / 4))
        print(lvl_end)

        if lvl_start < lvl_end:
            users[str(user.id)]["lvl"] = lvl_end
            if lvl != 1:
                embed = discord.Embed(title=f'{user.name} leveled up and can now access better job',
                                      description=f'You are now level {lvl}')
                await ctx.send(embed=embed)

        with open("lemonbank.json", "w") as f:
            json.dump(users, f, indent=4)

        if arg2 == 'None':
            if arg1 == 'list' or arg1 == 'List':
                embed = discord.Embed(title='Open Jobs:')
                for job in self.joblist:
                    name = job['Name']
                    desc = job['Beschreibung']
                    lvl = job['lvl']
                    verdienst = job['Verdienst']
                    verdienst = str(verdienst)
                    lvl = str(lvl)
                    embed.add_field(name=name + '  Salary: ' + verdienst, value=desc + ' | Level ' + lvl + ' needed',
                                    inline=False)
                embed.set_footer(text='Every Coorparation mentioned here is owned 51% by Lemon Inc.')
                await ctx.send(embed=embed)

            elif arg1 == 'info' or arg1 == 'Info':
                try:
                    userjob = users[str(user.id)]["userjob"]
                except:
                    userjob = []
                if not userjob:
                    embed = discord.Embed(title='You dont have a job!',
                                          description='Try: *lem job list*, then *lem job select <Job>*')
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title='Your Job:')

                    for job in userjob:
                        name = job['Name']
                        verdienst = job['Verdienst']
                        embed.add_field(name=name, value=f'Salary: {verdienst}')

                        lvl = str(lvl)
                        embed.set_footer(text=f'You are level {lvl}')

                    await ctx.send(embed=embed)

            else:
                await self.job_helper(ctx)
                return
        else:
            arg2 = arg2.lower()
            for job in self.joblist:
                name = job['Name']
                name = name.lower()
                neededlvl = job['lvl']
                verdienst = job['Verdienst']

                if arg1 == 'select' and arg2 == name or arg1 == 'Select' and arg2 == name or arg1 == 'sel' and arg2 == name or arg1 == 'Sel' and arg2 == name:

                    try:
                        userjob = users[str(user.id)]["userjob"]
                    except:
                        userjob = []



                    tf = 0
                    if bool(userjob) == True:

                        if userjob[0]["Name"] == name:
                            ausgabe = f'You already work as {name}!'
                            tf = 1
                            break

                    if lvl < neededlvl:
                        ausgabe = f'You dont have enough experience to work as {name}!'
                        embed2 = discord.Embed(title=ausgabe)
                        await ctx.send(embed=embed2)
                        tf = 1
                        return

                    obj = {"Name": name, "Verdienst": verdienst}
                    users[str(user.id)]["userjob"] = [obj]
                    with open("lemonbank.json", "w") as f:
                        json.dump(users, f, indent=4)
                    ausgabe = 'You wrote an application for the job and not even 2 hours later you received a phone call and got the job'
                    tf = 1
                    break


                elif arg1 == 'select' and arg2 != name or arg1 == 'Select' and arg2 != name or arg1 == 'sel' and arg2 != name or arg1 == 'Sel' and arg2 != name:
                    ausgabe = 'This job doesnt exist!'
                    tf = 1
                else:
                    await self.job_helper(ctx)
                    return
                    tf = 0
            if tf != 0:
                embed = discord.Embed(title=ausgabe)
                await ctx.send(f"{ctx.author.mention}", embed=embed)

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def work(self, ctx):
        user = ctx.author
        users = await self.get_bank_data()
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nUse the `lem startup` command first!")
            self.work.reset_cooldown(ctx)
            return
        try:
            userjob = users[str(user.id)]["userjob"]
        except:
            userjob = []
            embed = discord.Embed(title='You cant work without a job!')
            self.work.reset_cooldown(ctx)
            await ctx.send(embed=embed)
            time.sleep(3)
            await self.job_helper(ctx)
            return
        try:
            xp = users[str(user.id)]["xp"]
            lvl = users[str(user.id)]["lvl"]
        except:
            xp = users[str(user.id)]["xp"] = 0
            lvl = users[str(user.id)]["lvl"] = 1

        users[str(user.id)]["xp"] += 10
        lvl_start = users[str(user.id)]["lvl"]
        lvl_end = int(xp ** (1 / 4))
        print(lvl_end)
        if lvl_start < lvl_end:
            users[str(user.id)]["lvl"] = lvl_end
            if lvl != 1:
                embed = discord.Embed(title=f'{user.name} leveled up and can now access better job',
                                      description=f'You are now level {lvl}')
                await ctx.send(embed=embed)

        with open("lemonbank.json", "w") as f:
            json.dump(users, f, indent=4)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        def checkreaction(reaction, user):
            return reaction.message.id == message.id and user == ctx.author

        for job in userjob:
            name = job['Name']
            lohn = job['Verdienst']
            if name == 'tiktokhater':
                phrases = ['TikTok ist eine schreckliche Platform!', 'Ich hasse TikTok!', 'TikToker sind Weirdos',
                           'TikToker gehören in die Tonne']
                rndmphrase = random.choice(phrases)
                await ctx.send(f'Wenn du Tik Tok so hatest spam: "{rndmphrase}" 5 - Mal ')
                try:
                    msg = await self.client.wait_for('message', timeout=15, check=check)
                    msg1 = await self.client.wait_for('message', timeout=15, check=check)
                    msg2 = await self.client.wait_for('message', timeout=15, check=check)
                    msg3 = await self.client.wait_for('message', timeout=15, check=check)
                    msg4 = await self.client.wait_for('message', timeout=15, check=check)
                except asyncio.TimeoutError:
                    await ctx.send('Du hast nicht schnell genug geantwortet')

                    return

                if msg.content == rndmphrase and msg.content == rndmphrase and msg1.content == rndmphrase and msg2.content == rndmphrase and msg3.content == rndmphrase and msg4.content == rndmphrase:
                    await self.update_balance(user, lohn, 'pocket')
                    embed = discord.Embed(title='Richtig!', description=f'Du hast damit {lohn}€ verdient')
                    await ctx.send(embed=embed)
                    return
                else:
                    await ctx.send('Leider Falsch')


            elif name == 'dealer':
                anzahlM = random.randrange(3, 10)
                hmm = 'h'
                for i in range(anzahlM):
                    hmm = hmm + 'm'
                await ctx.send('Psssssst hast du meine Lieferung?\nJa Klar, was ist das Codewort')
                await ctx.send(hmm)
                time.sleep(4)
                await ctx.channel.purge(limit=1)
                await ctx.send('Wie viele ms hatte dieses Hmm? (z.B. mit 7 antworten)')
                try:
                    msg = await self.client.wait_for('message', timeout=7, check=check)
                except asyncio.TimeoutError:
                    await ctx.send('Du hast nicht schnell genug geantwortet')

                    return
                anzahlM = str(anzahlM)
                if msg.content == anzahlM:
                    await self.update_balance(user, lohn, 'Geldbörse')
                    embed = discord.Embed(title='KorReKt!', description=f'Du hast damit {lohn}€ verdient')
                    embed.set_footer(text='Den Rest bekommst du morgen...')
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('Leider Falsch')

            elif name == 'reddit analyst':
                ausgabe = f"Big PP or small PP?"

                embed = discord.Embed(title=ausgabe)

                file_path_type = ["./memes/*.png", "./memes/*.jpg", "./memes/*.gif"]
                images = glob.glob(random.choice(file_path_type))
                random_image = random.choice(images)
                file = discord.File(random_image)
                print(random_image)
                embed.set_image(url="attachment://"+random_image)
                message = await ctx.send(f"{ctx.author.mention}\n", file=file, embed=embed)
                await message.add_reaction('⬆')
                await message.add_reaction('⬇')

                try:
                    useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return
                await self.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'cat enjoyer':
                ausgabe = '<a:catJAM:810785548678987776>'

                embed = discord.Embed(title=ausgabe)

                file_path_type = ["./cats/*.png", "./cats/*.jpg"]
                images = glob.glob(random.choice(file_path_type))
                random_image = random.choice(images)
                file = discord.File(random_image)
                print(random_image)
                embed.set_image(url="attachment://"+random_image)
                message = await ctx.send(f"{ctx.author.mention}\n", file=file, embed=embed)
                await message.add_reaction('<:catJAM:810785548678987776>')

                try:
                    useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return
                await self.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'lemonade salesman':
                ausgabe = 'A stranger arrives and asks for some lemonade...he is strange'
                embed = discord.Embed(title=ausgabe)
                message = await ctx.send(f"{ctx.author.mention}\n", embed=embed)
                await message.add_reaction('<:lemonade:882239415601213480>')



                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send('You didnt answer fast enough!')
                    return

                em = discord.Embed(title="You gave him some lemonade, when you told him the price he gave you a *strange* look. But he paid anyways so you **didnt care**")
                await ctx.send(embed=em)
                await self.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'discord mod':
                ausgabe = 'Mute, Kick or Ban?'
                jokes = ['Singing in the shower is fun until you get soap in your mouth. Then its a soap opera.', 'What do you call a fish wearing a bowtie? Sofishticated.', 'Dear Math, grow up and solve your own problems.', 'Can a kangaroo jump higher than the empire state building? Of course! Buildings can’t jump', 'Why was the robot so tired after his road trip? He had a hard drive.', 'I was wondering why this frisbee kept looking bigger and bigger. Then it hit me.', 'A man rushed into a Doctors surgery, shouting "help me please, Im shrinking" The Doctor calmly said "now settle down a bit… youll just have to learn to be a little patient".', 'When I moved into my new igloo my friends threw me a surprise house-warming party. Now Im homeless.', 'I met my wife on Tinder. That was awkward.', 'My friend is fed up with my constant stream of dad jokes, so I asked her, "How can I stop my addiction?!" She shot back, "Whatever means necessary!!" I replied, "No, it doesnt!”', 'What’s the difference between a literalist and a kleptomaniac? A literalist takes things literally. A kleptomaniac takes things, literally.', 'ts been months since I bought the book, "How to scam people online." It still hasnt arrived yet.', "why did syndra run away from the fight? Because she had no balls <:OmegaLUL:598583138758950932>", "Why did the scarecrow win an award? Because he was outstanding in his field."]
                joke = random.choice(jokes)
                embed = discord.Embed(title=ausgabe, description=joke)
                message = await ctx.send(embed=embed)
                await message.add_reaction('🔇')
                await message.add_reaction('⛔')
                await message.add_reaction('🚫')


                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return
                print(reaction.emoji)
                if reaction.emoji == '🔇':
                    line = f"You muted him for 24h"
                elif reaction.emoji == '⛔':
                    line = f"You kicked him from the server"
                elif reaction.emoji == '🚫':
                    line = f"You banned him from the server"
                else:
                    line = f"Idk"

                em = discord.Embed(title=line)
                await ctx.send(f"{ctx.author.mention}\n", embed=em)
                await self.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f"You received {lohn} lemons!")
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'lemon researcher':
                ausgabe = '*Hmmm* intresting '
                facts = ["Lemons are native to Asia.", "Lemons are a hybrid between a sour orange and a citron.", "Lemons are rich in vitamin C.", "Lemons trees can produce up to 600lbs of lemons every year.", "Lemon trees produce fruit all year round.", "Lemon zest, grated rinds, is often used in baking.", "Lemon tree leaves can be used to make tea.", "The high acidity of lemons make them good cleaning aids.", "California and Arizona produces most of the United States’ lemon crop.", "The most common types of lemons are the Meyer, Eureka, and Lisbon lemons.", ]
                fact = random.choice(facts)
                embed = discord.Embed(title=ausgabe, description=fact + " <:Nerdge:814443289386156033>")
                message = await ctx.send(embed=embed)
                await message.add_reaction('<:Nerdge:814443289386156033>')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return



                em = discord.Embed(title="Well, interesting <:Nerdge:814443289386156033>")
                await ctx.send(embed=em)
                await self.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n",embed=embed)

            elif name == 'pizza guy':
                file = discord.File("./jobs/pizza.png")
                embed = discord.Embed(title="Mamma Mia! What topping this beautiful pizza shall get?", colour=discord.Color.green())
                embed.set_image(url="attachment://pizza.png")
                message= await ctx.send(embed=embed, file=file)
                await message.add_reaction('🍄')
                await message.add_reaction('🍍')
                await message.add_reaction('🌶️')
                await message.add_reaction('🥬')
                await message.add_reaction('🧅')
                await message.add_reaction('🍗')
                await message.add_reaction('🐟')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return

                if reaction.emoji == '🍄':
                    await ctx.send("I hope you didnt murder Moooooshroom for that!")
                elif reaction.emoji == '🍍':
                    await ctx.send("WHY DO YOU PUT PINEAPPLE ON PIZZA?!?!?")
                elif reaction.emoji == '🌶️':
                    await ctx.send("Hooooooooooooooooooooooooot")
                elif reaction.emoji == '🥬':
                    await ctx.send("Green stuff, really?")
                elif reaction.emoji == '🧅':
                    await ctx.send("Onions are good in salads, but not on pizza")
                elif reaction.emoji == '🍗':
                    await ctx.send("Chicken, always a great decision")
                elif reaction.emoji == '🐟':
                    await ctx.send("I like fish")
                else:
                    await ctx.send("I have no idea why you put that on your pizza!")
                await self.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f"You received {lohn} lemons!")
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'lemon farmer':
                rndmaufgabe = random.randrange(1, 4)

                if rndmaufgabe == 1:
                    ausgabe = 'Time to plant some grass! uuuhhhfkjdaslf I mean lemons of course... Dont do drugs kids'
                    embed = discord.Embed(title=ausgabe)
                    message = await ctx.send(f"{ctx.author.mention}\n",embed=embed)
                    await message.add_reaction('🌱')

                    try:
                        useremoji = await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time and the lemons were eaten by some birds")
                        return

                    await self.update_balance(user, lohn, 'pocket')
                    embed = discord.Embed(title=f"You received {lohn} lemons!")
                    await ctx.send(f"{ctx.author.mention}\n",embed=embed)
                elif rndmaufgabe == 2:
                    ausgabe = 'Time to water your precious lemons!'
                    embed = discord.Embed(title=ausgabe)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('🍋')

                    try:
                        useremoji = await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time and your lemon trees sadly died :(")
                        return

                    await self.update_balance(user, lohn, 'pocket')
                    embed = discord.Embed(title=f"You received {lohn} lemons!")
                    await ctx.send(f"{ctx.author.mention}\n",embed=embed)

                elif rndmaufgabe == 3:
                    ausgabe = 'Time to harvest your perfectly riped lemons'
                    embed = discord.Embed(title=ausgabe)
                    message = await ctx.send(f"{ctx.author.mention}\n", embed=embed)
                    await message.add_reaction('⛏')

                    try:
                        useremoji = await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time :(")
                        return

                    await self.update_balance(user, lohn, 'pocket')
                    embed = discord.Embed(title=f'You received {lohn} lemons!')
                    await ctx.send(f"{ctx.author.mention}\n",embed=embed)
                else:
                    await ctx.send('System Error *lmao*')

            else:
                await ctx.send(f"{ctx.author.mention}\nI think the creator didnt finish this job yet...")
                self.work.reset_cooldown(ctx)

    @work.error
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name='Sorry, in terms of health, we have no health', value=error)
        await ctx.send(embed=embed)

    @job.error
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name='Sorry, in terms of health, we have no health', value=error)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(economy(client))