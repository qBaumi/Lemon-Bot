import datetime

import discord, json
from discord.ext import commands
import cogs.essentialfunctions as es



"""
Other 
"""
class other(commands.Cog):
    def __init__(self, client):
        self.client = client

    """
    Hall of Fame for all people who collect all collectibles
    """
    @commands.command()
    async def halloffame(self, ctx):
        with open("./json/halloffame.json", "r") as f:
            users = json.load(f)
        em = discord.Embed(colour=discord.Color.dark_purple(), title="Hall of Fame", description="only true and loyal legends get there...")
        for userid in users:
            user = await self.client.fetch_user(userid)
            em.add_field(name=user.name, value="\u200b")
        await ctx.send(embed=em)

    """
    Present 100 golden lemons for christmas
    """
    @commands.command()
    async def present(self, ctx):
        with open("./json/present.json", "r") as f:
            users = json.load(f)
        if ctx.author.id in users:
            await ctx.send("You already claimed your present!")
            return
        date = datetime.date.today()
        date = str(date)
        print(date)
        if (date != "2021-12-25"):
            await ctx.send("No gift to claim <:Sadge:720250426892615745>\nSanta Veigar arrives at the **25. December** 2021 in the early morning!")
            return
        await es.update_balance(ctx.author, 100, "safe")
        users.append(ctx.author.id)
        with open("./json/present.json", "w") as f:
            json.dump(users, f)
        em = discord.Embed(title="Merry Christmas", description="You claimed your 100 golden lemons!")
        await ctx.send(f"{ctx.author.mention}\n", embed=em)

async def addhalloffame(userid):
    with open("./json/halloffame.json", "r") as f:
        users = json.load(f)
    userid = int(userid)
    if not userid in users:
        users.append(userid)

    with open("./json/halloffame.json", "w") as f:
        json.dump(users, f)




def setup(client):
    client.add_cog(other(client))