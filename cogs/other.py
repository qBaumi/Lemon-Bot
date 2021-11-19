import discord, json
from discord.ext import commands



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