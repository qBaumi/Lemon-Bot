import json
import math
import operator
import random
from typing import Optional

import cogs.essentialfunctions as es
import asyncio
import discord
from discord import Colour
from discord.ext import commands
import mysql.connector
from config import dbargs
from discord import app_commands
from config import guilds


"""
    W3SCHOOLS MYSQL CONNECTOR FOR MOR INFO
"""

mydb = mysql.connector.connect(
  host=dbargs["host"],
  user=dbargs["user"],
  password=dbargs["password"],
  port=dbargs["port"],
  database = dbargs["database"],
  auth_plugin=dbargs["auth_plugin"]

)
mycursor = mydb.cursor()

globalmainshop = [{"name": "Lemonade", "price": 5, "desc": "Everyone likes lemonade", "money": "lemons", "emoji" : "<:lemonade:882239415601213480>"},
                {"name": "Treat", "price": 5, "desc": "Give your sweet pet at treat <:Gladge:792430592636616714>", "money": "lemons", "emoji" : "🍖"},
                {"name": "Cheesecake", "price": 10, "desc": "You can either eat it, or throw it at another person :)", "money": "lemons", "emoji" : "🍰"},
                {"name": "Flowers", "price": 15, "desc": "Flowers are always a great birthday gift!", "money": "lemons","emoji": "💐"},
                {"name": "Present", "price": 70, "desc": "Now you can gift every item", "money": "lemons", "emoji": "🎁"},
                {"name": "Pinata", "price": 150, "desc": "Piñata is great, but be careful with the baseball bat!", "money": "lemons","emoji": "<:pinata:882600329517096971>"},
                {"name": "ConchShell", "price": 200, "desc": "LONG LIVE THE MAGIC CONCH SHELL", "money": "lemons","emoji": "<:magicconchshell:882556087843307520>"},
                {"name": "Mobile", "price": 500, "desc": "Phone, I hope you know what a phone is", "money": "lemons", "emoji" : "☎"},
                {"name": "Laptop", "price": 1000, "desc": "Browse for cute animals, make memes or play minecraft", "money": "lemons", "emoji": "💻"},
                {"name": "Safe", "price": 1500, "desc": "Store 5000 precious lemons in it!", "money": "lemons", "emoji": "<:safe:885811224418332692>"},
                {"name": "Candy", "price": 10, "desc": "f", "money": "lemons","emoji": "🍬"}]
                #{"name": "Adventcalendar", "price": 10000, "desc": "Open a door and get a price everyday", "money": "lemons", "emoji": "🎅"}

class economy(commands.Cog):
    def __init__(self, client):
        self.client = client
    petcursor = mycursor



    """---------------------------------------------------------------------------------------------"""
    """---------------------------------------COMMANDS----------------------------------------------"""
    """---------------------------------------------------------------------------------------------"""



    # Startup command to open account
    @commands.command(aliases=["start"])
    async def startup(self, ctx):
        # Use the open_account function and give a quick overview to the bot, help, some commands etc
        # GLOBALS
        STARTMONEY = 50
        user = ctx.author
        # Get the function into accountopened to check if already an account was made
        accountopened = await es.open_account(user=user)

        if accountopened == False:
            em = discord.Embed()
            em.add_field(name=f"Sorry, you already created an account!",
                         value=f"If you didn't read the message the first time you used this command, try: `lem help` , to get more information")
            await ctx.send(f"{ctx.author.mention}\n", embed=em)
            return

        # Now if an account wasn't opened the code comes here and sends the embed
        em = discord.Embed(color=discord.Color.blurple(), title="Hello!",
                           description=f"Let me introduce you to our little friend Lemon right here.")
        em.add_field(name="Welcome you can find out more about me with `lem about`",
                     value="Congrats! You already found the *startup command*. \n"
                           "Next is the `lem lemons` or `lem balance` command. You can look up your balance there, \nbut don't forget to NEVER share your bank account data! \nUse `lem help` for more information")
        await ctx.send(embed=em)
        await es.update_balance(user, STARTMONEY)


    # Get your balance
    @app_commands.command(name="balance", description="Your bank account details")
    async def balance(self, interaction : discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        # Get currency with helper function and send it in an embed
        # If you returned several things in one variable you can get one specific with
        # f. E. money[0]      *the first index*
        # START WITH ZERO
        money = await es.currency(interaction.user)

        # Make a nice looking embed
        em = discord.Embed(title="Your currency", colour=Colour.gold())
        # Set the footer text
        if money[2] < 100:
            em.set_footer(text="Pff, what a poor commoner")
        elif money[2] > 1000:
            em.set_footer(text="Welcome to the rich people gang")
        # Set the Fields for pocket and safe
        em.add_field(name="You have ", value=f"`{int(round(money[0], 0)):g}` <:lemon2:881595266757713920> lemons in your pocket", inline=False)
        em.add_field(name="You have ", value=f"`{int(round(money[1], 0)):g}` <:GoldenLemon:882634893039923290> golden lemons", inline=False)

        await interaction.response.send_message(embed=em)

    # Shop
    mainshop = globalmainshop

    def getmoneyemoji(self, moneyform):
        if moneyform == "lemons":
            moneyemoji = "<:lemon2:881595266757713920>"
        else:
            moneyemoji = "<:GoldenLemon:882634893039923290>"
        return moneyemoji

    async def getshopembed(self, page, itemsperpage, switch_emoji, notlisted, shop="normal"):

        em = discord.Embed(title='Shop', description="<:GoldenLemon:882634893039923290> switch to golden lemon shop!")

        specialitems = await es.get_item_data()
        specialitems = specialitems["MysterySkin"]

        if shop=="special":
            """
                    Calculate pages
            """
            shopitems = 0
            for item in specialitems:
                if item["name"] not in notlisted:
                    shopitems += 1
            pages = math.ceil(shopitems / itemsperpage)

            if page > pages or page < 1:
                return False

            """
                Get the page indexes in the for loop and add every item to the embed
            """

            print(pages)
            print(f"start index: {page * itemsperpage - itemsperpage}")
            print(f"end index: {page * itemsperpage}")

            for i in range(page * itemsperpage - itemsperpage, page * itemsperpage):
                try:
                    name = specialitems[i]["name"]
                    emoji = specialitems[i]["emoji"]
                    desc = specialitems[i]["desc"]
                    stock = specialitems[i]["stock"]
                    moneyemoji = self.getmoneyemoji(specialitems[i]["money"])
                    price = specialitems[i]["price"]

                except:
                    break
                if name not in notlisted:
                    em.add_field(name=f"{name} {emoji}      -      {price} {moneyemoji}", value=f'Only `{stock}` items left!!! {desc}', inline=False)

        elif shop=="normal":
            """
                            Calculate pages
                    """
            shopitems = 0
            for item in self.mainshop:
                if item["name"] not in notlisted:
                    shopitems += 1
            pages = math.ceil(shopitems / itemsperpage)

            if page > pages or page < 1:
                return False

            """
                Get the page indexes in the for loop and add every item to the embed
            """

            print(pages)
            print(f"start index: {page * itemsperpage - itemsperpage}")
            print(f"end index: {page * itemsperpage}")

            for i in range(page * itemsperpage - itemsperpage, page * itemsperpage):
                try:
                    name = self.mainshop[i]["name"]
                    emoji = self.mainshop[i]["emoji"]
                    desc = self.mainshop[i]["desc"]
                    moneyemoji = self.getmoneyemoji(self.mainshop[i]["money"])
                    price = self.mainshop[i]["price"]
                    print(i)
                    print(name)
                except:
                    break
                if name not in notlisted:
                    em.add_field(name=f"{name} {emoji}      -      {price} {moneyemoji}", value=f"{desc}", inline=False)
        em.set_footer(text=f"{page} / {pages}")

        return em

    @commands.command()
    async def Shop(self, ctx, page=1, shop="normal"):
        if not await es.check_account(ctx):
            return


        notlisted = ["Candy", "Adventcalendar"]
        switch_emoji = "<:GoldenLemon:882634893039923290>"
        switch_emoji_normal = "<:lemon2:881595266757713920>"
        itemsperpage = 5
        timeoutsec = 60
        switch = switch_emoji

        em = await self.getshopembed(page, itemsperpage, switch_emoji, notlisted, shop)
        msg = await ctx.send(f"{ctx.author.mention}", embed=em)
        if shop=="special":
            switch = switch_emoji_normal

        """
            Here comes the switch pages part after the embed was sent the first time
        """
        await msg.add_reaction("◀️")
        await msg.add_reaction("▶️")
        await msg.add_reaction(switch_emoji)

        def check(reaction, user):
            return reaction.message.id == msg.id and user == ctx.author
        while True:
            try:
                reaction, useremoji = await self.client.wait_for('reaction_add', timeout=timeoutsec, check=check)
            except asyncio.TimeoutError:

                """
                    IT ONLY WORKS LIKE THIS REMOVE OWN REACTION BLYAT EDKLFSÖJLKJSDFL
                """
                await msg.remove_reaction("◀️", self.client.user)
                await msg.remove_reaction("▶️", self.client.user)
                await msg.remove_reaction(switch, self.client.user)
                return

            if reaction.emoji == "◀️":

                if await self.getshopembed(page-1, itemsperpage, switch, notlisted, shop):
                    page -= 1
                    em = await self.getshopembed(page, itemsperpage, switch, notlisted, shop)
                await msg.remove_reaction("◀️", ctx.author)
            elif str(reaction.emoji) == "▶️":

                if await self.getshopembed(page+1, itemsperpage, switch, notlisted, shop):
                    page += 1
                    em = await self.getshopembed(page, itemsperpage, switch, notlisted, shop)
                await msg.remove_reaction("▶️", ctx.author)
            elif str(reaction.emoji) == str(switch_emoji):
                print("yas")
                em = await self.getshopembed(1, itemsperpage, switch, notlisted, shop="special")
                await msg.remove_reaction(switch, self.client.user)
                switch = switch_emoji_normal
                shop = "special"
                await msg.remove_reaction(switch_emoji, ctx.author)
            elif str(reaction.emoji) == str(switch_emoji_normal):
                em = await self.getshopembed(1, itemsperpage, switch, notlisted, shop="normal")
                await msg.remove_reaction(switch, self.client.user)
                switch = switch_emoji
                shop = "normal"
                await msg.remove_reaction(switch_emoji_normal, ctx.author)


            await msg.edit(embed=em)
            #msg = await ctx.send(f"{ctx.author.mention}\n", embed=em)
            await msg.add_reaction(switch) #here it is









    # Buy Sell etc
    @commands.command()
    async def buy(self, ctx, item, amount=1):

        # GLOBALS
        blacklist = ["safe", "adventcalendar"]
        user = ctx.author

        """FALSE CHECKS"""
        if not await es.check_account(ctx):
            return
        if amount < 1:
            await ctx.send(":)")
            return

        """CHECK IF ITEM BOUGHT TWICE"""
        """First check if you want to lem buy safe 2"""
        """Then check if item is in users bag and amount is bigger than 1"""
        if item.lower() in blacklist and amount > 1:
            await ctx.send(f"{ctx.author.mention}\nYou can only buy one {item}")
            print("that")
            return
        try:
            bag = await es.getbag(user.id)
        except:
            bag = []

        """
            get the index of the item in the blacklist for the check if the user has already that item once
        """
        index = -1
        for i in range(0, len(blacklist)):
            if blacklist[i].lower() == item.lower():
                print(i)
                index = i
                break


        for useritem in bag:
            if useritem["item"] == blacklist[index] and useritem["amount"] > 0 and item.lower() == blacklist[index]:
                print("this")
                await ctx.send(f"{ctx.author.mention}\nYou can only buy one {item}!")
                return


        """Get response from res and respond then if bought was successful"""
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

        """Loop through items to get index and get stock minus amount"""
        """If item arg equals one name in specialitems JSON file then the stock amount gets reduced and the file is saved"""
        specialitems = await es.get_item_data()
        index = 0
        for spitem in specialitems["MysterySkin"]:
            name = spitem["name"]
            if item.lower() == name.lower():
                specialitems["MysterySkin"][index]["stock"] = specialitems["MysterySkin"][index]["stock"] - amount
                with open("./json/spItems.json", "w") as f:
                    json.dump(specialitems, f, indent=4)

                await ctx.send(f"{user.mention}\n**To redeem your prize please make sure to message Rocsie!**")
                channel = await self.client.fetch_channel(845281850230308864) # Send message to an admin channel or idk
                rocsie = await self.client.fetch_user(148086360425758720) # fetch rocsie
                await channel.send(f"{rocsie.mention}\n{user.mention} claimed {item}!")
                break
            index+=1

        await ctx.send(f"{ctx.author.mention}\nYou just bought {amount} {item}")




    """
    FUNCTION FOR BUY
    :returns
    boolean, int
    ERROR CODES
    1 : item doesnt exist
    2 : not enough money
    5 : item isnt in stock
    """
    async def buy_this(self, user, item_name, amount=1):
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
            specialitems = await es.get_item_data()
            for thing in specialitems:
                for specialitem in specialitems[thing]:
                    print(specialitem)
                    name = specialitem['name'].lower()
                    price = specialitem['price']
                    moneyform = specialitem['money']
                    stock = specialitem['stock']
                    if name == item_name:
                        if stock <= 0:
                            # Item not in stock
                            return [False, 5]
                        name_ = name
                        price = specialitem["price"]
                        moneyform = specialitem['money']
                        break


        # Item doesnt exist
        if name_ == None:
            return [False, 1]

        if moneyform == "lemons":
            depot = "pocket"
            depotindex = 0
        if moneyform == "golden lemons":
            depot = "safe"
            depotindex = 1

        cost = price * amount


        bal = await es.currency(user)
        # Not enough money
        if bal[depotindex] < cost:
            return [False, 2]






        await es.add_item(item_name, user.id, amount)
        await es.update_balance(user, cost * -1, depot)

        return [True, "Worked"]



    @commands.command()
    async def sell(self, ctx, item, amount=1):

        """FALSY CHECKS"""
        if not await es.check_account(ctx):
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


    """
    FUNCTION FOR SELL
    :returns
    boolean : int
    ERROR CODES
    1 : item not in shop
    2 : You dont have item with amount to sell
    3 : You dont have item (once) in your bag
    """
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

        depot = self.getdepot(moneyform)

        cost = price * amount


        try:
            index = 0
            t = None
            userbag = await es.getbag(user.id)
            for thing in userbag:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt - amount
                    if new_amt < 0:
                        return [False, 2]

                    sql = f"UPDATE items SET amount = {new_amt} WHERE id = {user.id} AND name = '{item_name}'"
                    mycursor.execute(sql)
                    mydb.commit()

                    t = 1
                    break
                index += 1
            if t == None:
                return [False, 3]
        except:
            return [False, 3]


        await es.update_balance(user, cost, depot)

        return [True, "Worked"]

    """
    FUNCTION TO GET DEPOT FOR BUY SELL etc
    """
    def getdepot(self, moneyform):
        if moneyform == "lemons":
            depot = "pocket"
        if moneyform == "golden lemons":
            depot = "safe"
        return depot


    # daily lemons and cooldown 86400 is one day in seconds
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command()
    async def daily(self, ctx):
        """FALSY CHECKS"""
        if not await es.check_account(ctx):
            return

        daily_lemons = 20

        await es.update_balance(ctx.author, daily_lemons, "pocket")
        # Send an embed to show him and get currency
        money = await es.currency(ctx.author)
        em = discord.Embed(colour=Colour.red(), title=f"You got your daily {daily_lemons} lemons! "
                                                      f"Dont eat them all at the same time!",
                           description=f"You have now `{int(money[0])}` lemons")
        await ctx.send(embed=em)

    # Send the error in an embed and add the exact number of seconds in the footer
    @daily.error
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(colour=Colour.dark_red(), title='You can only use this command once a day')
        embed.set_footer(text=error)

        await ctx.send(embed=embed)




    """
    Steals 1 - 4 % money from a user
    60% chance
    both users need 100 lemons
    cooldown 369 seconds
    """
    @commands.cooldown(1, 369, commands.BucketType.user)
    @commands.command(aliases=["rob"])
    async def steal(self, ctx, victim : discord.User):

        """Globals"""
        user = ctx.author
        users = await es.get_bank_data(user.id)
        usersvictim = await es.get_bank_data(victim.id)
        sentences = [f"You were captured when you tried to open {victim.name}'s bag",
                     f"When you touched {victim.name}'s pocket the police saw you and arrested you. Have fun in jail!",
                     f"Pretty unlucky...{victim.name} is currently attempting a self-defending course, you stand no chance",
                     f"{victim.name}'s big brother saw you...he is very big"
            , f"Robbing in front of a cop...you should try to type that in youtube!",
                     f"When you opened {victim.name}'s bag, her little chihuahua (Yeah I googled that name before) jumped into your face and bit you"]

        """FALSE CHECKS"""
        if victim == user:
            await ctx.send(f"{ctx.author.mention}\nHwat? You wanna rob yourself?!?!? I am always a thought ahead of you...trust me")
            self.steal.reset_cooldown(ctx)
            return
        if not await es.check_account(ctx):
            self.steal.reset_cooldown(ctx)
            return
        if users[str(user.id)]['pocket'] < 100:
            await ctx.send(f"{ctx.author.mention}\nYou need atleast `100 lemons` in your pocket in order to steal from another person")
            self.steal.reset_cooldown(ctx)
            return
        try:
            if usersvictim[str(victim.id)]['pocket'] < 100:
                await ctx.send(f"{ctx.author.mention}\n{victim.mention} is too `poor` to get robbed")
                self.steal.reset_cooldown(ctx)
                return
        except:
            await ctx.send(f"{ctx.author.mention}\nYour victim hasn't opened an account yet")
            self.steal.reset_cooldown(ctx)
            return



        chance = random.randrange(0, 100)
        percent = round(random.uniform(0.01, 0.041), 2)
        if chance < 40:

            funnysentence = random.choice(sentences)
            if usersvictim[str(victim.id)]['pocket'] < users[str(user.id)]['pocket']:
                loss = round(users[str(user.id)]['pocket'] * percent * (usersvictim[str(victim.id)]['pocket']/users[str(user.id)]['pocket']), 0)
            else:
                loss = round(users[str(user.id)]['pocket'] * percent, 0)
                loss = int(loss)
            em = discord.Embed(colour=discord.Color.red(),
                               title=f"{user.name} lost {loss:g} lemons when trying to steal from {victim.name}",
                               description=funnysentence)
            await ctx.send(embed=em)
            await es.update_balance(user, loss * -1)
            await es.update_balance(victim, loss)
            return

        await es.update_balance(victim, int(round(usersvictim[str(victim.id)]['pocket']*percent, 0)*-1))
        await es.update_balance(user, int(round(usersvictim[str(victim.id)]['pocket']*percent, 0)))
        em = discord.Embed(colour=discord.Color.red(), title=f"{user.name} stole {victim.name} {round(usersvictim[str(victim.id)]['pocket']*percent, 0):g} lemons", description=f"Less lemonade for {victim.name} I guess")
        await ctx.send(embed=em)

    @steal.error
    async def on_command_error(self, ctx, error):
        em = discord.Embed(colour=discord.Color.red(), title=error, description="If your user wasnt found, you need to tag them with an @ `lem steal @name` for example")
        await ctx.send(embed=em)

    """
    Leaderboard of all lemons inclusive safe
    gets list with join from tables users and safe
    """
    @app_commands.command(name="leaderboard", description="Who has the most lemons")
    @app_commands.describe(limit="Limit for how many users will be shown")
    async def leaderboard(self, interaction : discord.Interaction, limit : Optional[app_commands.Range[int, 1, 25]]):
        await interaction.response.defer()
        if limit is None:
            limit = 10
        def users_list():
            data = es.sql_select(f"SELECT users.id, pocket, safe.money, (pocket + IFNULL(safe.money, 0)) as total FROM `users` LEFT JOIN `safe` ON safe.id = users.id ORDER BY `total` DESC LIMIT {limit}")
            userlist = []
            for guy in data:
                dict = {"id" : guy[0], "total" : guy[3]}
                userlist.append(dict)
            return userlist

        em = discord.Embed(title=f"Top {limit} richest people", color=discord.Color.dark_gold())
        index = 1
        for user in users_list():
            member = await self.client.fetch_user(user["id"])
            em.add_field(name=f"{index}. {member.name}", value=f"`{int(user['total'])}` lemons <:lemon2:881595266757713920>", inline=False)
            index+=1
        await interaction.followup.send(embed=em)

    @app_commands.command(name="pay", description="Pay another user")
    @app_commands.describe(user="Person you pay")
    @app_commands.describe(amount="How much you pay them")
    async def pay(self, interaction : discord.Interaction, user: discord.User, amount : int):
        userid = user
        author = interaction.user
        """False checks"""
        if not await es.interaction_check_account(interaction):
            await interaction.response.send_message(f"{author.mention}\nYou need to use `lem startup` first")
            return
        if userid == author:
            await interaction.response.send_message(f"{author.mention}\nYou cant pay yourself money...well technically, but not anymore!")
            return
        if amount > 0:
            user = author
            users = await es.get_bank_data(author.id)
            await self.Pay_helper(interaction=interaction, userid=userid, pay_amount=amount)
            wallet_amt = users[str(user.id)]['pocket']
            if True and amount <= wallet_amt:
                await interaction.response.send_message(
                    f"{author.mention}\nYou paid {userid.name} {amount} lemons. If you have an emberassing image, dont forget to TAX THE HELL OUT OF THEM")
        else:
            await interaction.response.send_message(f"{author.mention}\nNo")

    """Helper for Pay"""
    async def Pay_helper(self, interaction, userid: discord.User, pay_amount):
        user = interaction.user
        users = await es.get_bank_data(user.id)

        pay_amount = int(pay_amount)
        wallet_amt = users[str(user.id)]['pocket']
        if pay_amount <= wallet_amt:
            await es.update_balance(user=user, change=pay_amount * -1, mode='pocket')
            await es.update_balance(user=userid, change=pay_amount, mode='pocket')

        else:
            await interaction.response.send_message(
                f"{user.mention}\nYou dont have enough money!")
        return [True]



async def setup(client):
    await client.add_cog(economy(client), guilds=guilds)