from functools import partial

import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord.ui import View

from config import guilds
from discord.app_commands import Choice
import cogs.essentialfunctions as es

teams = [
    Choice(name='FNC', value="<:FNC:1162308600128086096>"),
    Choice(name='G2', value="<:G2:1162308625763672154>")
    ]
predictions_channel_id = 651364619402739713
leaderboard_message_id = 1162372921692524684

class prediction(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def update_leaderboard(self):
        channel = await self.client.fetch_channel(predictions_channel_id)
        msg = await channel.fetch_message(leaderboard_message_id)
        await msg.edit(embed=await self.getLeaderboardEmbed())


    async def getLeaderboardEmbed(self):
        leaderboard = es.sql_select(f"""SELECT p.userid,
               SUM(CASE 
               WHEN p.team1 = m.team1 AND p.team2 = m.team2 THEN 2 
               WHEN p.team1 = m.team1 AND p.team2 != m.team2 THEN 1
               WHEN p.team2 = m.team2 AND p.team1 != m.team1 THEN 1
               ELSE 0 END) AS score
          FROM predictions p
               JOIN matches m ON p.matchid = m.matchid
        GROUP BY p.userid
        ORDER BY score DESC
        LIMIT 10;""")
        em = discord.Embed(title="Predictions Leaderboard")
        for user in leaderboard:
            member = await self.client.fetch_user(user[0].decode('utf-8'))
            em.add_field(name=member.name, value=int(user[1]), inline=False)
        return em

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @app_commands.command(name="predictionresult", description="Put result into a Prediction")
    async def predictionresult(self, interaction: discord.Interaction, matchid: int, team1score: int, team2score: int):
        es.sql_exec(f"UPDATE matches SET team1={int(team1score)}, team2={int(team2score)} WHERE matchid={int(matchid)}")
        msgid = es.sql_select(f"SELECT messageid FROM matches WHERE matchid={matchid}")[0][0].decode('utf-8')
        channel = await self.client.fetch_channel(predictions_channel_id)
        msg = await channel.fetch_message(msgid)
        embed = msg.embeds[0]
        embed.title = f"Prediction has ended {team1score} - {team2score} | {embed.title}"
        await msg.edit(embed=embed)
        await self.update_leaderboard()
        await interaction.response.send_message(f"Updated Prediction with matchid {matchid}", ephemeral=True)

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @commands.command(name="lockprediction")
    async def lockprediction(self, ctx, matchid):
        msgid = es.sql_select(f"SELECT messageid FROM matches WHERE matchid={matchid}")[0][0].decode('utf-8')
        channel = await self.client.fetch_channel(predictions_channel_id)
        msg = await channel.fetch_message(msgid)
        view = View.from_message(msg)
        view.children[0].disabled = True
        view.children[1].disabled = True
        await msg.edit(view=view)
        await ctx.send("Locked prediction")


    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @commands.command(name="predictionleaderboard")
    async def predictionleaderboard(self, ctx):
        em = await self.getLeaderboardEmbed()
        await ctx.send(embed=em)



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
        # Use the calculated new_matchid value in the INSERT statement
        es.sql_exec(f"INSERT INTO matches (matchid, messageid, team1, team2, timestamp, team1name, team2name) VALUES ({new_matchid}, 'none', 0, 0, '{matchbegin_timestamp}', '{team1.name}', '{team2.name}');")
        matchid = es.sql_select(f"SELECT MAX(matchid) FROM matches")[0][0]
        if bestof.value == "1":
            view = PredictionDropdownViewBestofOne(self.client, [team1, team2], matchid)
        else:
            view = PredictionDropdownViewBestofOne(self.client, [team1, team2], matchid)

        em.set_footer(text=str(new_matchid))
        msg = await interaction.channel.send(embed=em, view=view)
        es.sql_exec(f"UPDATE matches SET messageid='{msg.id}' WHERE matchid = {new_matchid}")
        await interaction.response.send_message("Successfully created prediction", ephemeral=True)



class PredictionDropdownViewBestofOne(discord.ui.View):
    def __init__(self, client, teams, matchid):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(PredictionSelectBestofOne(client, teams, matchid))

        showmypredictionsbutton = discord.ui.Button(label="Show my Prediction", style=discord.ButtonStyle.green, custom_id=f"showmyprediction_{matchid}")
        showmypredictionsbutton.callback = partial(self.showmyprediction, matchid=matchid)
        self.add_item(showmypredictionsbutton)

    async def showmyprediction(self, interaction, matchid):
        mypredictions = es.sql_select(f"""        
        SELECT p.team1, p.team2, m.team1name, m.team2name
        FROM predictions p
        JOIN matches m ON p.matchid = m.matchid
        WHERE p.matchid = {matchid} AND userid = '{interaction.user.id}'
        """)[0]
        print(mypredictions)
        await interaction.response.send_message(f"You have currently selected **{mypredictions[0]} - {mypredictions[1]}** for **{mypredictions[2].decode('utf-8')}** vs **{mypredictions[3].decode('utf-8')}**", ephemeral=True)

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


    async def update_votes(self, matchid, msgid):
            votes = es.sql_select(f"""SELECT
      SUM(CASE WHEN m.team1 > m.team2 THEN 1 ELSE 0 END) AS team1_score,
      SUM(CASE WHEN m.team2 > m.team1 THEN 1 ELSE 0 END) AS team2_score
    FROM predictions m WHERE matchid={matchid};""")[0]
            channel = await self.client.fetch_channel(predictions_channel_id)
            msg = await channel.fetch_message(msgid)
            embed = msg.embeds[0]
            field1name = embed.fields[0].name
            field2name = embed.fields[1].name
            embed.clear_fields()
            embed.add_field(name=field1name, value=int(votes[0]))
            embed.add_field(name=field2name, value=int(votes[1]))
            await msg.edit(embed=embed)


    async def callback(self, interaction: discord.Interaction):
        oldPrediction = es.sql_select(f"SELECT * FROM predictions WHERE userid = {interaction.user.id} AND matchid = {self.matchid}")
        #check if prediction is already in
        if oldPrediction:
            if self.values[0] == self.teams[0].name and oldPrediction[0][2] == 1 or self.values[0] == self.teams[1].name and oldPrediction[0][3] == 1:
                await interaction.response.send_message(f"You've already choosen {self.values[0]}\n**Try to click Show my Prediction!**", ephemeral=True)
                return

        if self.values[0] == self.teams[0].name:
            team1score = 1
            team2score = 0
        else:
            team1score = 0
            team2score = 1
        if not oldPrediction:
            es.sql_exec(f"INSERT INTO predictions(userid, matchid, team1, team2) VALUES('{interaction.user.id}', {int(self.matchid)}, {team1score}, {team2score})")
        else:
            es.sql_exec(f"UPDATE predictions SET team1={team1score}, team2={team2score} WHERE userid = '{interaction.user.id}' AND matchid = {self.matchid}")
        await self.update_votes(self.matchid, interaction.message.id)
        await interaction.response.send_message(f"You predicted a **win for {self.values[0]}**", ephemeral=True)




async def setup(client):
    await client.add_cog(prediction(client), guilds=guilds)