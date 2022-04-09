import json
import math
import random
from typing import Optional

import cogs.essentialfunctions as es
import discord
from discord.ext import commands
from discord import app_commands
from config import guilds

# Add a person to the halloffame in the json file
async def addhalloffame(userid):
    with open("./json/halloffame.json", "r") as f:
        users = json.load(f)
    userid = int(userid)
    if not userid in users:
        users.append(userid)

    with open("./json/halloffame.json", "w") as f:
        json.dump(users, f)

# Calculate max pages of collectibles
def getMaxPages():

    collectibles = getCollectibles()

    all_collectibles = 0
    for collectible in collectibles:
        all_collectibles += 1
    pages = math.ceil(all_collectibles / 10)
    return pages

def getCollectibles():
    with open("./json/collectibles.json", "r", encoding="utf-8") as f:
        return json.load(f)

class collectibles(commands.Cog):
    def __init__(self, client):
        self.client = client



    #10 collectibles per page
    #shows all collectibles
    @app_commands.command(name="collectibles", description="Show all collectibles that exist")
    @app_commands.describe(page="Specify a page")
    async def collectibles(self, interaction : discord.Interaction, page : Optional[app_commands.Range[int, 1, getMaxPages()]]):

        if page==None:
            page = 1
        em = discord.Embed(title="All collectibles", colour=discord.Color.dark_teal())

        pages = getMaxPages()
        collectibles = getCollectibles()

        if page > pages or page < 1:
            await interaction.response.send_message(f"There are only {pages} pages")
            return

        for i in range(page * 10 - 10, page * 10):
            try:
                name = collectibles[i]["name"]
                emoji = collectibles[i]["emoji"]
                desc = collectibles[i]["desc"]
            except:
                break
            em.add_field(name=f"{name} {emoji}", value=f"{desc}", inline=False)

        em.set_footer(text=f"{page} / {pages}")
        await interaction.response.send_message(embed=em)

    """
    returns list with all collectibles
    [{"name": name, "amount": amount}, {"name": name, "amount": amount}, {"name": name, "amount": amount}] etc
    """
    async def getcollection(self, id):
        sql = f"SELECT * FROM collectibles WHERE id = {id}"
        data = es.sql_select(sql)
        bag = []
        for item in data:
            name = item[1]
            amount = item[2]
            dict = {"name": name, "amount": amount}
            bag.append(dict)
        return bag


    @app_commands.command(name="collection", description="take a look at your collection, you can get collectibles with /vendingmachine")
    async def collection(self, interaction : discord.Interaction):

        user = interaction.user
        if not await es.interaction_check_account(interaction):
            return

        try:
            collection = await self.getcollection(user.id)
        except:
            collection = []
        collectibles = getCollectibles()

        em = discord.Embed(title="Your Collection", colour=discord.Color.teal())
        collectibles_amount, all_collectibles = await self.getcollectiblesamout(user.id)
        for item in collection:
            name = item["name"]
            name_ = name.capitalize()
            amount = item["amount"]

            for collectible in collectibles:
                emoji = collectible["emoji"]
                if name == collectible["name"]:
                    break

            if amount > 0:
                em.add_field(name=f"{name_} {emoji}", value=f"amount: `{amount}`", inline=False)
        em.set_footer(text=f"{collectibles_amount} / {all_collectibles} collectibles")
        await interaction.response.send_message(embed=em)

        #ADD HALL OF FAME
        if collectibles_amount == all_collectibles:
            await addhalloffame(user.id)


    @app_commands.command(name="vendingmachine", description="Throw 150 Lemons into a vending machine to collect a useless toy")
    async def vendingmachine(self, interaction : discord.Interaction):

        user = interaction.user
        users = await es.get_bank_data(user.id)


        if not await es.interaction_check_account(interaction):
            return
        if users[str(user.id)]["pocket"] < 150:
            await interaction.response.send_message(f"{user.mention}\nYou dont have enough money!")
            return



        collectibles = getCollectibles()

        collectible = random.choice(collectibles)
        name = collectible["name"]
        emoji = collectible["emoji"]
        try:
            collection = await self.getcollection(user.id)
        except:
            collection = []
        try:
            index = 0
            t = None
            for thing in collection:
                n = thing["name"]
                if n == name:
                    old_amt = thing["amount"]
                    new_amt = old_amt + 1
                    es.sql_exec(f"UPDATE collectibles SET amount = {new_amt} WHERE id = {user.id} AND name = '{name}'")

                    t = 1
                    break
            if t == None:
                es.sql_exec(f"INSERT INTO collectibles (id, name, amount) VALUES ({user.id}, '{name}', 1)")

        except:
            es.sql_exec(f"INSERT INTO collectibles (id, name, amount) VALUES ({user.id}, '{name}', 1)")


        await es.update_balance(user, -150)
        em = discord.Embed(
            title=f"You threw your 150 <:lemon2:881595266757713920> lemons into a vending machine and got a {name} {emoji}",
            description="Dont ask me how you can throw 150 lemons in there", colour=discord.Color.dark_blue())
        await interaction.response.send_message(embed=em)


        """ADD HALL OF FAME"""
        collectibles_amount, all_collectibles = await self.getcollectiblesamout(user.id)
        if collectibles_amount == all_collectibles:
            await addhalloffame(user.id)

    async def getcollectiblesamout(self, userid):
        try:
            collection = await self.getcollection(userid)
        except:
            collection = []
        collectibles = getCollectibles()

        collectibles_amount = 0
        all_collectibles = 0
        for collectible in collectibles:
            all_collectibles += 1
        for item in collection:
            collectibles_amount += 1

        return collectibles_amount, all_collectibles

    # Hall of Fame for all people who collect all collectibles
    @app_commands.command(description="Have a look at legends", name="halloffame")
    async def halloffame(self, interaction: discord.Interaction):
        with open("./json/halloffame.json", "r") as f:
            users = json.load(f)
        em = discord.Embed(colour=discord.Color.dark_purple(), title="Hall of Fame",
                           description="only true and loyal legends get there...")
        # Fetch every user that is in the halloffame and add them to the embed
        for userid in users:
            user = await self.client.fetch_user(userid)
            em.add_field(name=user.name, value="\u200b", inline=False)
        await interaction.response.send_message(embed=em)


async def setup(client):
    await client.add_cog(collectibles(client), guilds=guilds)