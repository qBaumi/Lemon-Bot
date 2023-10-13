from functools import partial

import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice
import cogs.essentialfunctions as es

teams = [
    Choice(name='FNC', value="<:FNC:1162308600128086096>"),
    Choice(name='G2', value="<:G2:1162308625763672154>")
    ]

class prediction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @app_commands.command(name="predictionresult", description="Put result into a Prediction")
    async def predictionresult(self, interaction: discord.Interaction, matchid, team1score, team2score):
        es.sql_exec(f"UPDATE matches SET team1={int(team1score)}, team2={int(team2score)} WHERE matchid={int(matchid)}")
        await interaction.response.send_message(f"Updated Prediction with matchid {matchid}", ephemeral=True)

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @commands.command(name="lockprediction")
    async def lockprediction(self, ctx, matchid):

        await ctx.send("asdf")



    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @app_commands.choices(team1=teams)
    @app_commands.choices(team2=teams)
    @app_commands.choices(bestof=[
        Choice(name="Best of one", value="1"),
        Choice(name="Best of two", value="2"),
        Choice(name="Best of three", value="3"),
    ])
    @app_commands.command(name="prediction", description="Create a prediction")
    async def prediction(self, interaction, team1: Choice[str], team2: Choice[str], bestof: Choice[str], matchbegin_timestamp: str):
        em = discord.Embed(colour=discord.Color.brand_green(), title="FNC vs G2", description=f"Predictions close when the match begins at <t:{matchbegin_timestamp}>")
        em.add_field(name=f"Votes for {team1.name}", value="0")
        em.add_field(name=f"Votes for {team2.name}", value="0")
        # Calculate the new matchid value separately
        new_matchid = es.sql_select("SELECT COALESCE(MAX(matchid), 0) + 1 FROM matches")[0][0]
        print(new_matchid)
        # Use the calculated new_matchid value in the INSERT statement
        es.sql_exec(f"INSERT INTO matches (matchid, team1, team2, timestamp, team1name, team2name) VALUES ({new_matchid}, 0, 0, '{matchbegin_timestamp}', '{team1.name}', '{team2.name}');")
        matchid = es.sql_select(f"SELECT MAX(matchid) FROM matches")[0][0]
        print(matchid)
        if bestof.value == "1":
            view = PredictionDropdownViewBestofOne(self.client, [team1, team2], matchid)
        else:
            view = PredictionDropdownViewBestofOne(self.client, [team1, team2], matchid)

        em.set_footer(text=str(new_matchid))
        msg = await interaction.channel.send(embed=em, view=view)
        print(msg)
        
        await interaction.response.send_message("Successfully created prediction", ephemeral=True)



class PredictionDropdownViewBestofOne(discord.ui.View):
    def __init__(self, client, teams, matchid):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(PredictionSelectBestofOne(client, teams, matchid))
class PredictionSelectBestofOne(discord.ui.Select):
    def __init__(self, client, teams, matchid):
        self.client = client
        self.teams = teams
        self.matchid = matchid
        options = [
            discord.SelectOption(label=teams[0].name, emoji=teams[0].value, description=f"Pick {teams[0].name} as winner"),
            discord.SelectOption(label=teams[1].name, emoji=teams[1].value, description=f"Pick {teams[1].name} as winner"),
        ]
        super().__init__(placeholder='Pick a winner', min_values=1, max_values=1,
                         options=options, custom_id=f'persistent_view:match_id_{matchid}')



    async def callback(self, interaction: discord.Interaction):
        oldPrediction = es.sql_select(f"SELECT * FROM predictions WHERE userid = {interaction.user.id} AND matchid = {self.matchid}")
        print(oldPrediction)
        if self.values[0] == self.teams[0].name:
            team1score = 1
            team2score = 0
        else:
            team1score = 0
            team2score = 1
        if not oldPrediction:
            es.sql_exec(f"INSERT INTO predictions(userid, matchid, team1, team2) VALUES('{interaction.user.id}', {int(self.matchid)}, {team1score}, {team2score})")
            print("inserted")
        else:
            es.sql_exec(f"UPDATE predictions SET team1={team1score}, team2={team2score} WHERE userid = '{interaction.user.id}' AND matchid = {self.matchid}")
        await interaction.response.send_message(f"You predicted a **win for {self.values[0]}**", ephemeral=True)




async def setup(client):
    await client.add_cog(prediction(client), guilds=guilds)