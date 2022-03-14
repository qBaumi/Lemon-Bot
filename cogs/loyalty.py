import operator
import cogs.essentialfunctions as es
from discord.ext import commands
import discord, asyncio
from discord import app_commands
from discord import ui
from config import guilds, allowedRoles
from discord.app_commands import Choice


class loyalty(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Check if the user exists in the loyalty table
    def check_loyalty(self, user):
        es.mycursor.execute(f"SELECT id FROM loyalty WHERE id = '{user.id}'")

        id = es.mycursor.fetchall()
        print(id)
        if id:
            return True

        print("here")
        return False

    @app_commands.command(name="reward", description="Rewards a player with loyalty points")
    # @app_commands.has_any_role("Admins", "HM", "Developer", "Mods")
    @app_commands.describe(user="User that gets Loyalty Points")
    @app_commands.describe(points="10 Points for winner, 5 for second, 3 for third and 1 for participation")
    async def reward(self, interaction: discord.Interaction, user: discord.User, points: app_commands.Range[int, 0, 10]):

        # Check if user is allowed
        role_ids = [role.id for role in interaction.user.roles]

        isAllowed = False

        for role in allowedRoles:
            if role in role_ids:
                print("You're allowed")
                isAllowed = True
        if not isAllowed:
            await interaction.response.send_message("You need to be a Mod or Admin in order to use this command!")
            return

        # If the user has no loyalty points he gets inserted into the loyalty table
        if not self.check_loyalty(user):
            sql = f"INSERT INTO loyalty (id, points) VALUES ('{user.id}', {points})"
            es.mycursor.execute(sql)
            es.mydb.commit()
            await interaction.response.send_message(
                f"{user.mention} got {points} loyalty points, they now have {points} loyalty points in total!")

            # Now check if user already startupped
            es.mycursor.execute("SELECT id FROM users")
            ids = es.mycursor.fetchall()
            for id in ids:
                if str(interaction.user.id) == id[0]:
                    return
            # If he didnt startup then this comes
            em = discord.Embed(color=discord.Color.blurple(), title="Hello!",
                               description=f"Let me introduce you to our little friend Lemon right here.")
            em.add_field(name="Welcome you can find out more about me with <lem about>",
                         value="Congrats! You already found the *startup command*. \n"
                               "Next is the `lem lemons` or `lem balance` command. You can look up your balance there, \nbut don't forget to NEVER share your bank account data! \nUse `lem help` for more information")
            await interaction.response.send_message(f"{user.mention}", embed=em)
            # Also give them the startup money
            await es.update_balance(user, 50)
            return
        # If the user already received loyalty points they get fetched and added
        es.mycursor.execute(f"SELECT points FROM loyalty WHERE id = '{user.id}'")
        data = es.mycursor.fetchall()
        prevpoints = int(data[0][0])
        print(prevpoints)
        sql = f"UPDATE loyalty SET points = {points + prevpoints} WHERE id = '{user.id}'"
        es.mycursor.execute(sql)
        es.mydb.commit()
        await interaction.response.send_message(
            f"{user.mention} got {points} loyalty points, they now have {prevpoints + points} loyalty points in total!")

    @app_commands.command(name="profile", description="Check your Loyalty points and your balance")
    async def profile(self, interaction: discord.Interaction):
        user = interaction.user

        # Get the loyalty points
        es.mycursor.execute(f"SELECT points FROM loyalty WHERE id = '{user.id}'")
        points = es.mycursor.fetchall()

        # try to fetch them if an error throws they are just 0
        try:
            points = points[0][0]
        except:
            points = 0
        # get the balance else it is 0
        try:
            bal = await es.currency(user)
            lemons = bal[0]
            glemons = bal[1]
        except:
            lemons = 0
            glemons = 0
            await interaction.response.send_message("If you haven't already use `lem startup` first!")

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
        await interaction.response.send_message(embed=em)

    @app_commands.command(name="loyalty", description="Leaderboard for loyalty points")
    async def loyalty(self, interaction: discord.Interaction):
        # Get all loyal points with user id in a list
        """
        list of tuples
        user = (user.id, points)
        loyaltylist = [(user.id, points), (user.id, points), (user.id, points)...]
        """
        es.mycursor.execute(f"SELECT * FROM loyalty ORDER BY points DESC LIMIT 10")
        data = es.mycursor.fetchall()

        em = discord.Embed(colour=discord.Color.teal(), title="Loyalty Leaderboard",
                           description="You can obtain loyalty points from participating at events")
        # loop through each user, fetch them and add to embed
        for user in data:
            member = await self.client.fetch_user(user[0])
            em.add_field(name=str(member), value=f"{user[1]} Points", inline=False)
        await interaction.response.send_message(embed=em)


async def setup(client):
    await client.add_cog(loyalty(client), guilds=guilds)