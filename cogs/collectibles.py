import json
import math
import random
import cogs.essentialfunctions as es
import discord
from discord.ext import commands
from .economy import mycursor, mydb

async def addhalloffame(userid):
    with open("./json/halloffame.json", "r") as f:
        users = json.load(f)
    userid = int(userid)
    if not userid in users:
        users.append(userid)

    with open("./json/halloffame.json", "w") as f:
        json.dump(users, f)


class collectibles(commands.Cog):
    def __init__(self, client):
        self.client = client

    """
    10 collectibles per page
    shows all collectibles
    """
    @commands.command()
    async def collectibles(self, ctx, page=1):
        page = int(page)
        em = discord.Embed(title="All collectibles", colour=discord.Color.dark_teal())

        with open("./json/collectibles.json", "r", encoding="utf-8") as f:
            collectibles = json.load(f)

        """
        Calculate pages
        """
        all_collectibles = 0
        for collectible in collectibles:
            all_collectibles += 1
        pages = math.ceil(all_collectibles / 10)

        if page > pages or page < 1:
            await ctx.send(f"There are only {pages} pages")
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
        await ctx.send(embed=em)

    """
    returns list with all collectibles
    [{"name": name, "amount": amount}, {"name": name, "amount": amount}, {"name": name, "amount": amount}] etc
    """
    async def getcollection(self, id):
        mycursor.execute(f"SELECT * FROM collectibles WHERE id = {id}")
        data = mycursor.fetchall()
        bag = []
        for item in data:
            name = item[1]
            amount = item[2]
            dict = {"name": name, "amount": amount}
            bag.append(dict)
        return bag


    @commands.command()
    async def collection(self, ctx, page=1):

        if not await es.check_account(ctx):
            return

        try:
            collection = await self.getcollection(ctx.author.id)
        except:
            collection = []
        with open("./json/collectibles.json", "r", encoding="utf-8") as f:
            collectibles = json.load(f)

        em = discord.Embed(title="Your Collection", colour=discord.Color.teal())
        collectibles_amount, all_collectibles = await self.getcollectiblesamout(ctx.author.id)
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
        await ctx.send(embed=em)

        """ADD HALL OF FAME"""
        if collectibles_amount == all_collectibles:
            await addhalloffame(ctx.author.id)


    @commands.command()
    async def vendingmachine(self, ctx):

        users = await es.get_bank_data(ctx.author.id)
        user = ctx.author

        if not await es.check_account(ctx):
            return
        if users[str(user.id)]["pocket"] < 150:
            await ctx.send(f"{ctx.author.mention}\nYou dont have enough money!")
            return



        with open("./json/collectibles.json", "r", encoding="utf-8") as f:
            collectibles = json.load(f)

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
                    sql = f"UPDATE collectibles SET amount = {new_amt} WHERE id = {user.id} AND name = '{name}'"
                    mycursor.execute(sql)
                    mydb.commit()
                    t = 1
                    break
            if t == None:
                sql = f"INSERT INTO collectibles (id, name, amount) VALUES ({user.id}, '{name}', 1)"
                mycursor.execute(sql)
                mydb.commit()
        except:
            sql = f"INSERT INTO collectibles (id, name, amount) VALUES ({user.id}, '{name}', 1)"
            mycursor.execute(sql)
            mydb.commit()

        await es.update_balance(ctx.author, -150)
        em = discord.Embed(
            title=f"You threw your 150 <:lemon2:881595266757713920> lemons into a vending machine and got a {name} {emoji}",
            description="Dont ask me how you can throw 150 lemons in there", colour=discord.Color.dark_blue())
        await ctx.send(embed=em)


        """ADD HALL OF FAME"""
        collectibles_amount, all_collectibles = await self.getcollectiblesamout(ctx.author.id)
        if collectibles_amount == all_collectibles:
            await addhalloffame(ctx.author.id)

    async def getcollectiblesamout(self, userid):
        try:
            collection = await self.getcollection(userid)
        except:
            collection = []
        with open("./json/collectibles.json", "r", encoding="utf-8") as f:
            collectibles = json.load(f)

        collectibles_amount = 0
        all_collectibles = 0
        for collectible in collectibles:
            all_collectibles += 1
        for item in collection:
            collectibles_amount += 1

        return collectibles_amount, all_collectibles

async def setup(client):
    await client.add_cog(collectibles(client))