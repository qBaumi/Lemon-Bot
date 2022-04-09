import json
import math
import operator
import random
import time
from typing import Optional, List
from discord.app_commands import Choice
import cogs.essentialfunctions as es
import asyncio
import discord
from discord import Colour
from discord.ext import commands
import mysql.connector

from cogs.support import support_channel_id
from discord import app_commands
from config import guilds



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
notlisted = ["Candy", "Adventcalendar"]


class economy(commands.Cog):
    def __init__(self, client):
        self.client = client



    """---------------------------------------------------------------------------------------------"""
    """---------------------------------------COMMANDS----------------------------------------------"""
    """---------------------------------------------------------------------------------------------"""



    # Startup command to open account
    @app_commands.command(name="startup", description="Get a quick introduction")
    async def startup(self, interaction : discord.Interaction):
        # Use the open_account function and give a quick overview to the bot, help, some commands etc
        # GLOBALS
        STARTMONEY = 50
        user = interaction.user
        # Get the function into accountopened to check if already an account was made
        accountopened = await es.open_account(user=user)

        if accountopened == False:
            em = discord.Embed()
            em.add_field(name=f"Sorry, you already created an account!",
                         value=f"If you didn't read the message the first time you used this command, try: `/help` , to get more information")
            await interaction.response.send_message(f"{user.mention}\n", embed=em)
            return

        # Now if an account wasn't opened the code comes here and sends the embed
        em = discord.Embed(color=discord.Color.blurple(), title="Hello!",
                           description=f"Let me introduce you to our little friend Lemon right here.")
        em.add_field(name="Welcome you can find out more about me with `/about`",
                     value="Congrats! You already found the *startup command*. \n"
                           "Next is the `/balance` command. You can look up your balance there, \nbut don't forget to NEVER share your bank account data! \nUse `/help` for more information")
        await interaction.response.send_message(embed=em)
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

    class ShopButtons(discord.ui.View):

        def __init__(self, ecoclass, timeout):
            super().__init__(timeout=timeout)
            self.ecoclass = ecoclass
            self.shop = "normal"
            self.notlisted = ["Candy", "Adventcalendar"]
            self.switch_emoji = "<:GoldenLemon:882634893039923290>"
            self.switch_emoji_normal = "<:lemon2:881595266757713920>"
            self.itemsperpage = 5
            self.timeoutsec = 60
            self.switch = self.switch_emoji
            self.page = 1
        @discord.ui.button(label='◀', style=discord.ButtonStyle.blurple)
        async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
            if await self.ecoclass.getshopembed(self.page - 1, self.itemsperpage, self.switch, self.notlisted, self.shop):
                self.page -= 1
                em = await self.ecoclass.getshopembed(self.page, self.itemsperpage, self.switch, self.notlisted, self.shop)
            else:
                await interaction.response.send_message("This is the first page!", ephemeral=True)
                return
            await interaction.response.edit_message(view=self, embed=em)

        @discord.ui.button(label="▶", style=discord.ButtonStyle.blurple)
        async def right(self, interaction: discord.Interaction, button: discord.ui.Button):

            if await self.ecoclass.getshopembed(self.page + 1, self.itemsperpage, self.switch, self.notlisted, self.shop):
                self.page += 1
                em = await self.ecoclass.getshopembed(self.page, self.itemsperpage, self.switch, self.notlisted, self.shop)
            else:
                await interaction.response.send_message("This is the last page!", ephemeral=True)
                return
            await interaction.response.edit_message(view=self, embed=em)
        @discord.ui.button(label='Golden Lemons', style=discord.ButtonStyle.green)
        async def golden(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.shop == "normal":
                em = await self.ecoclass.getshopembed(1, self.itemsperpage, self.switch, self.notlisted, shop="special")
                self.shop = "special"
                button.label = "Lemons"
                self.page = 1
            elif self.shop == "special":
                em = await self.ecoclass.getshopembed(1, self.itemsperpage, self.switch, self.notlisted, shop="normal")
                self.shop = "normal"
                self.page = 1
                button.label = "Golden Lemons"
            await interaction.response.edit_message(view=self, embed=em)

        async def on_timeout(self):
            for child in self.children:  # We need to iterate over all the buttons/selects in the View (self.children returns a list of all the Items in the View)
                child.disabled = True  # And set disabled = True to disable them
            await self.message.edit(view=self)  # Now we just need to update our old message with the updated buttons

    @app_commands.command(name="shop", description="Have a look at the shop")
    async def shop(self, interaction : discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        page = 1
        shop = "normal"
        switch_emoji = "<:GoldenLemon:882634893039923290>"
        switch_emoji_normal = "<:lemon2:881595266757713920>"
        itemsperpage = 5
        timeoutsec = 60
        switch = switch_emoji
        user = interaction.user

        em = await self.getshopembed(page, itemsperpage, switch_emoji, notlisted, shop)
        view = self.ShopButtons(ecoclass=self, timeout=300)
        await interaction.response.send_message(f"{user.mention}", embed=em, view=view)
        view.message = await interaction.original_message()
        return



    with open("./json/spItems.json", "r", encoding="utf-8") as f:
        specialitems = json.load(f)
    specialitems = specialitems["MysterySkin"]

    itemlist = []
    for item in globalmainshop:
        if item["name"] not in notlisted:
            itemlist.append(Choice(name=item["name"], value=item["name"].lower()))
    for item in specialitems:
        itemlist.append(Choice(name=item["name"], value=item["name"].lower()))

    #print(itemlist)


    @app_commands.describe(item='The name of the item you want to buy')
    @app_commands.describe(amount='Amount of items you want to buy')
    @app_commands.choices(item=itemlist)
    @app_commands.command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction : discord.Interaction, item : str, amount : Optional[int]):

        # GLOBALS
        blacklist = ["safe", "adventcalendar"]
        user = interaction.user

        if amount is None:
            amount = 1
        if not await es.interaction_check_account(interaction):
            return
        if amount < 1:
            await interaction.response.send_message(":)")
            return

        """CHECK IF ITEM BOUGHT TWICE"""
        """First check if you want to /buy safe 2"""
        """Then check if item is in users bag and amount is bigger than 1"""
        if item.lower() in blacklist and amount > 1:
            await interaction.response.send_message(f"{user.mention}\nYou can only buy one {item}")
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
                await interaction.response.send_message(f"{user.mention}\nYou can only buy one {item}!")
                return


        """Get response from res and respond then if bought was successful"""
        res = await self.buy_this(user, item, amount)


        if not res[0]:
            if res[1] == 1:
                await interaction.response.send_message(f"{user.mention}\nThat Item isn't there!")
                return
            if res[1] == 2:
                await interaction.response.send_message(f"{user.mention}\nYou don't have enough money in your wallet to buy {amount} {item}")
                return
            if res[1] == 5:
                await interaction.response.send_message(f"{user.mention}\nThat item isnt in stock!")
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

                supportchannel = await self.client.fetch_channel(support_channel_id)
                await interaction.channel.send(f"{user.mention}\n**To redeem your prize please open a ticket in {supportchannel.mention}")
                channel = await self.client.fetch_channel(845281850230308864) # Send message to an admin channel or idk
                rocsie = await self.client.fetch_user(148086360425758720) # fetch rocsie
                await channel.send(f"{rocsie.mention}\n{user.mention} claimed {item}!")
                break
            index+=1

        await interaction.response.send_message(f"{user.mention}\nYou just bought {amount} {item}")
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

    @app_commands.describe(item='The name of the item you want to sell')
    @app_commands.describe(amount='Amount of items you want to sell')
    @app_commands.command(name="sell", description="Sell an item")
    async def sell(self, interaction : discord.Interaction, item : str, amount : Optional[int]):

        if amount is None:
            amount = 1

        if not await es.interaction_check_account(interaction):
            return
        if amount < 1:
            await interaction.response.send_message(":)")
            return
        user = interaction.user



        res = await self.sell_this(user, item, amount)

        if not res[0]:
            if res[1] == 1:
                await interaction.response.send_message(f"{user.mention}\nThat Object isn't there!")
                return
            if res[1] == 2:
                await interaction.response.send_message(f"{user.mention}\nYou don't have {amount} {item} in your bag.")
                return
            if res[1] == 3:
                await interaction.response.send_message(f"{user.mention}\nYou don't have {item} in your bag.")
                return

        await interaction.response.send_message(f"{user.mention}\nYou just sold {amount} {item}.")

    @sell.autocomplete('item')
    async def sell_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        items = await es.getChoices(interaction.user)
        return [
            app_commands.Choice(name=item, value=item.lower())
            for item in items if current.lower() in item.lower()
        ]



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
                    es.sql_exec(sql)


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
    @app_commands.command(name="daily", description="Get your daily 20 lemons")
    async def daily(self, interaction : discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        user = interaction.user

        isOnCooldown, sec = es.isOnCooldown(user, "daily")
        if isOnCooldown:
            await interaction.response.send_message(f"You are still on cooldown until <t:{math.floor(time.time() + sec)}>", ephemeral=True)
            return
        es.setCooldown(user, "daily")

        daily_lemons = 20

        await es.update_balance(user, daily_lemons, "pocket")
        # Send an embed to show him and get currency
        money = await es.currency(user)
        em = discord.Embed(colour=Colour.red(), title=f"You got your daily {daily_lemons} lemons! "
                                                      f"Dont eat them all at the same time!",
                           description=f"You have now `{int(money[0])}` lemons")
        await interaction.response.send_message(embed=em)




    """
    Steals 1 - 4 % money from a user
    60% chance
    both users need 100 lemons
    cooldown 369 seconds
    """
    @app_commands.command(name="steal", description="Steal from another person or get slapped")
    @app_commands.describe(victim="The person you want to steal from")
    async def steal(self, interaction : discord.Interaction, victim : discord.User):

        """Globals"""
        user = interaction.user
        users = await es.get_bank_data(user.id)
        usersvictim = await es.get_bank_data(victim.id)
        sentences = [f"You were captured when you tried to open {victim.name}'s bag",
                     f"When you touched {victim.name}'s pocket the police saw you and arrested you. Have fun in jail!",
                     f"Pretty unlucky...{victim.name} is currently attempting a self-defending course, you stand no chance",
                     f"{victim.name}'s big brother saw you...he is very big"
            , f"Robbing in front of a cop...you should try to type that in youtube!",
                     f"When you opened {victim.name}'s bag, her little chihuahua (Yeah I googled that name before) jumped into your face and bit you"]

        isOnCooldown, sec = es.isOnCooldown(user, "steal")
        if isOnCooldown:
            await interaction.response.send_message(
                f"You are still on cooldown until <t:{math.floor(time.time() + sec)}>", ephemeral=True)
            return

        """FALSE CHECKS"""
        if victim == user:
            await interaction.response.send_message(f"{user.mention}\nHwat? You wanna rob yourself?!?!? I am always a thought ahead of you...trust me")
            return
        if not await es.interaction_check_account(interaction):
            return
        if users[str(user.id)]['pocket'] < 100:
            await interaction.response.send_message(f"{user.mention}\nYou need atleast `100 lemons` in your pocket in order to steal from another person")
            return
        try:
            if usersvictim[str(victim.id)]['pocket'] < 100:
                await interaction.response.send_message(f"{user.mention}\n{victim.mention} is too `poor` to get robbed")
                return
        except:
            await interaction.response.send_message(f"{user.mention}\nYour victim hasn't opened an account yet")
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
            await interaction.response.send_message(embed=em)
            await es.update_balance(user, loss * -1)
            await es.update_balance(victim, loss)
            es.setCooldown(user, "steal")
            return

        await es.update_balance(victim, int(round(usersvictim[str(victim.id)]['pocket']*percent, 0)*-1))
        await es.update_balance(user, int(round(usersvictim[str(victim.id)]['pocket']*percent, 0)))
        em = discord.Embed(colour=discord.Color.red(), title=f"{user.name} stole {victim.name} {round(usersvictim[str(victim.id)]['pocket']*percent, 0):g} lemons", description=f"Less lemonade for {victim.name} I guess")
        await interaction.response.send_message(embed=em)
        es.setCooldown(user, "steal")



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
            await interaction.response.send_message(f"{author.mention}\nYou need to use `/startup` first")
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