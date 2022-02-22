import operator

import cogs.essentialfunctions as es
from discord.ext import commands
import discord, asyncio


class loyalty(commands.Cog):
    def __init__(self, client):
        self.client = client

    def check_loyalty(self, user):
        es.mycursor.execute(f"SELECT id FROM loyalty WHERE id = '{user.id}'")

        id = es.mycursor.fetchall()
        print(id)
        if id:
            return True

        print("here")
        return False

    @commands.command(name="reward", description="Rewards a player with loyalty points")
    @commands.has_any_role("Admins", "HM", "Developer", "Mods")
    async def reward(self, ctx, user: discord.User, points):
        points = int(points)
        if points>10:
            await ctx.send("You can't give more than 10 points! <:Madge:786069469020815391>")
            return
        if not self.check_loyalty(user):
            sql = f"INSERT INTO loyalty (id, points) VALUES ('{user.id}', {points})"
            es.mycursor.execute(sql)
            es.mydb.commit()
            await ctx.send(f"{user.mention} got {points} loyalty points, they now have {points} loyalty points in total!")

            """Now check if user already startupped"""
            es.mycursor.execute("SELECT id FROM users")
            ids = es.mycursor.fetchall()
            for id in ids:
                ### SELECT RETURNS TUPLES WHICH HAVE AN INDEX
                if str(ctx.author.id) == id[0]:
                    return
            # If he didnt startup then this comes
            em = discord.Embed(color=discord.Color.blurple(), title="Hello!",
                               description=f"Let me introduce you to our little friend Lemon right here.")
            em.add_field(name="Welcome you can find out more about me with <lem about>",
                         value="Congrats! You already found the *startup command*. \n"
                               "Next is the `lem lemons` or `lem balance` command. You can look up your balance there, \nbut don't forget to NEVER share your bank account data! \nUse `lem help` for more information")
            await ctx.send(f"{user.mention}", embed=em)
            await es.update_balance(user, 50)

            return
        es.mycursor.execute(f"SELECT points FROM loyalty WHERE id = '{user.id}'")
        data = es.mycursor.fetchall()
        prevpoints = int(data[0][0])
        print(prevpoints)
        sql = f"UPDATE loyalty SET points = {points+prevpoints} WHERE id = '{user.id}'"
        es.mycursor.execute(sql)
        es.mydb.commit()
        await ctx.send(f"{user.mention} got {points} loyalty points, they now have {prevpoints+points} loyalty points in total!")

    @commands.command(name="profile", description="Check your Loyalty points and your balance")
    async def profile(self, ctx):
        user = ctx.author
        es.mycursor.execute(f"SELECT points FROM loyalty WHERE id = '{user.id}'")
        points = es.mycursor.fetchall()
        try:
            points = points[0][0]
        except:
            points = 0
        try:
            bal = await es.currency(user)
            lemons = bal[0]
            glemons = bal[1]
        except:
            lemons = 0
            glemons = 0
            await ctx.send("If you haven't already use `lem startup` first!")

        print(lemons)
        print(glemons)
        print(points)
        em = discord.Embed(colour=discord.Color.teal(), title=f"Profile of {user.name}")
        em.add_field(name="You have ",
                     value=f"`{int(round(lemons, 0)):g}` <:lemon2:881595266757713920> lemons in your pocket",
                     inline=False)
        em.add_field(name="You have ",
                     value=f"`{int(round(glemons, 0)):g}` <:GoldenLemon:882634893039923290> golden lemons",
                     inline=False)
        em.add_field(name="You have ",
                     value=f"`{points}` Loyalty points",
                     inline=False)
        await ctx.send(embed=em)

    @commands.command(name="loyalty", description="Leaderboard for loyalty points")
    async def loyalty(self, ctx, x=10):
        # Get all loyal points with user id in a list
        """
        list of tuples
        user = (user.id, points)
        loyaltylist = [(user.id, points), (user.id, points), (user.id, points)...]
        """
        es.mycursor.execute(f"SELECT * FROM loyalty")
        data = es.mycursor.fetchall()
        print(data)
        print(data[0])
        loyaltylist = sorted(data, key=operator.itemgetter(1), reverse=True)[:x]
        print(loyaltylist)
        em = discord.Embed(colour=discord.Color.teal(), title="Loyalty Leaderboard", description="You can obtain loyalty points from participating at events")
        for user in loyaltylist:
            member = await self.client.fetch_user(user[0])
            em.add_field(name=str(member), value=f"{user[1]} Points", inline=False)
        await ctx.send(embed=em)



def setup(client):
    client.add_cog(loyalty(client))