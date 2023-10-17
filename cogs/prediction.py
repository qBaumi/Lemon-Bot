import asyncio
import datetime
from functools import partial

import discord, json
from discord.ext import commands, tasks
from discord import app_commands
from discord import ui
from discord.ui import View

from config import guilds
from discord.app_commands import Choice
import cogs.essentialfunctions as es

"""
<:FNC:1162308600128086096>
<:GEN:1162308602250399744>
<:JDG:1162308603504508949>
<:KT:1162308604787957781>
<:LNG:1162308607409397770>
<:MAD:1162308610173452298>
<:NRG:1162308612291567686>
<:T1:1162308614413877308>
<:TL:1162308616657829958>
<:WBG:1162308617979048008>
<:BLG:1162308619203784784>
<:C9:1162308621657440267>
<:G2:1162308625763672154>
<:DK:1162308751433404516>
<:BDS:1163070288406265966>
<:GAM:1163070290205614170>
"""

teamchoices = [
    Choice(name='FNC', value="<:FNC:1162308600128086096>"),
    Choice(name='GEN', value="<:GEN:1162308602250399744>"),
    Choice(name='JDG', value="<:JDG:1162308603504508949>"),
    Choice(name='KT', value="<:KT:1162308604787957781>"),
    Choice(name='LNG', value="<:LNG:1162308607409397770>"),
    Choice(name='MAD', value="<:MAD:1162308610173452298>"),
    Choice(name='NRG', value="<:NRG:1162308612291567686>"),
    Choice(name='T1', value="<:T1:1162308614413877308>"),
    Choice(name='TL', value="<:TL:1162308616657829958>"),
    Choice(name='WBG', value="<:WBG:1162308617979048008>"),
    Choice(name='BLG', value="<:BLG:1162308619203784784>"),
    Choice(name='C9', value="<:C9:1162308621657440267>"),
    Choice(name='G2', value="<:G2:1162308625763672154>"),
    Choice(name='DK', value="<:DK:1162308751433404516>"),
    Choice(name='BDS', value="<:BDS:1163070288406265966>"),
    Choice(name='GAM', value="<:GAM:1163070290205614170>"),
    ]


def getChoiceByTeamname(teamname):
    for team in teamchoices:
        if team.name == teamname:
            return team
    return None

predictions_channel_id = 651364619402739713
leaderboard_message_id = 1163532547473559612
leaderboard_channel_id = 1162712965087244298

class prediction(commands.GroupCog):
    def __init__(self, client):
        self.client = client
        self.lock_prediction_timer.start()

    async def update_leaderboard(self):
        channel = await self.client.fetch_channel(leaderboard_channel_id)
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
        em = discord.Embed(title="Predictions Leaderboard", colour=discord.Color.dark_red())
        firstpoints = leaderboard[0][1]
        secondpoints = 0
        thirdpoints = 0
        for i, user in enumerate(leaderboard):
            if user[1] < firstpoints:
                secondpoints = user[1]
                break
        for i, user in enumerate(leaderboard):
            if user[1] < thirdpoints:
                thirdpoints = user[1]
                break
        def getUsercountWithPoints(points):
            usercount = 0
            for user in leaderboard:
                if user[1] == points:
                    usercount+=1

            return usercount
        ties_firstplace = getUsercountWithPoints(firstpoints)
        ties_secondplace = getUsercountWithPoints(secondpoints)
        ties_thirdplace = getUsercountWithPoints(thirdpoints)
        for i, user in enumerate(leaderboard):
            member = await self.client.fetch_user(user[0].decode('utf-8'))
            str = f""
            if i == 0:
                str += "🥇 "
            elif i == 1:
                str += "🥈 "
            elif i == 2:
                str += "🥉 "
            else:
                str += f"{i+1}. "
            str += f"{member.name} with {user[1]} points"
            em.add_field(name=str, value=int(user[1]), inline=False)
        if ties_firstplace >= 2:
            em.add_field(name="Ties for 🥇:", value=f"{ties_firstplace} users have tied for first place with {firstpoints} points", inline=False)
        if ties_secondplace >= 2:
            em.add_field(name="Ties for 🥈:", value=f"{ties_secondplace} users have tied for second place with {secondpoints} points", inline=False)
        if ties_thirdplace >= 2:
            em.add_field(name="Ties for 🥉:", value=f"{ties_thirdplace} users have tied for third place with {thirdpoints} points", inline=False)


        return em

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @app_commands.command(name="result", description="Put result into a Prediction")
    @app_commands.describe(matchid="The matchid is the last line / footer of the prediction")
    async def result(self, interaction: discord.Interaction, matchid: int, team1score: int, team2score: int):
        es.sql_exec(f"UPDATE matches SET team1={int(team1score)}, team2={int(team2score)} WHERE matchid={int(matchid)}")
        msgid = es.sql_select(f"SELECT messageid FROM matches WHERE matchid={matchid}")[0][0].decode('utf-8')
        channel = await self.client.fetch_channel(predictions_channel_id)
        msg = await channel.fetch_message(msgid)
        embed = msg.embeds[0]
        embed.title = f"{embed.title} | Prediction has ended {team1score} - {team2score}"
        winner = es.sql_select(f"""SELECT
    CASE
        WHEN team1 > team2 THEN team1name
        WHEN team2 > team1 THEN team2name
        ELSE 'Tie or Unknown'
    END AS team_with_higher_score
FROM matches
WHERE matchid = {matchid}
""")[0][0].decode("utf-8")
        embed.add_field(name=f"Winner", value=f"{getChoiceByTeamname(winner).value} {winner}", inline=False)
        await msg.edit(embed=embed)
        await interaction.response.send_message(f"Updated Prediction with matchid {matchid}", ephemeral=True)
        await self.update_leaderboard()

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @commands.command(name="lockprediction")
    async def lockprediction(self, ctx, matchid):
        await self.lock_prediction(matchid)
        await ctx.send("Locked prediction")



    async def lock_prediction(self, matchid):
        msgid = es.sql_select(f"SELECT messageid FROM matches WHERE matchid={matchid}")[0][0].decode('utf-8')
        channel = await self.client.fetch_channel(predictions_channel_id)
        msg = await channel.fetch_message(msgid)
        view = View.from_message(msg)
        view.children[0].disabled = True
        view.children[1].disabled = True
        await msg.edit(view=view)
        es.sql_exec(f"UPDATE matches SET locked = 1  WHERE matchid={matchid}")

    @tasks.loop(seconds=59)
    async def lock_prediction_timer(self):
        matchids = es.sql_select(f"SELECT matchid FROM matches WHERE timestamp < UNIX_TIMESTAMP(NOW()) AND locked = 0;")
        for matchid in matchids:
            matchid = matchid[0]
            await self.lock_prediction(matchid)
            channel = await self.client.fetch_channel(651364619402739713) # test channel id
            await channel.send("Prediction was succesfully locked!")
            await asyncio.sleep(1)

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @commands.command(name="predictionleaderboard")
    async def predictionleaderboard(self, ctx):
        em = discord.Embed(colour=discord.Color.dark_red())
        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/1163437922310168586/IMG_6763.webp?ex=653f9300&is=652d1e00&hm=88f67c863db9299db094a710e39819fbc390f3cd979bf7c8f3f92dcd638aa12c&=")
        await ctx.send(embed=em)
        em = discord.Embed(colour=discord.Color.dark_red(), title="Prediction Info", description=
        """
This new system will make it way easier for everyone to participate in predictions! Keep in mind it is still new and we might experience bugs along the way, so please be patient and let us know if something isn't working for you.

To participate in predictions all you have to do is:
* Go to <#1162712749407731792> 
* Click the button `Pick a winner` for the match you want to predict
* If the match is a Bo3 or Bo5 you will get a message under the prediction that makes you able to pick the result
* If you're unsure what you predicted later you can press `Show my prediction` under the same match and Lemon Bot will tell you what you predicted. 

The predictions will be locked on game start!

__**Prizes**__
🥇 20€ worth of RP
🥈 10€ worth of RP
🥉 Mystery skin
🏅 Rest of top 10 will get 100 Golden Lemons
        """)
        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
        await ctx.send(embed=em)

        em = await self.getLeaderboardEmbed()
        await ctx.send(embed=em, view=LeaderboardDropdownView(client=self.client))



    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods")
    @app_commands.choices(team1=teamchoices)
    @app_commands.choices(team2=teamchoices)
    @app_commands.choices(bestof=[
        Choice(name="Best of 1", value="1"),
        Choice(name="Best of 3", value="2"),
        Choice(name="Best of 5", value="3"),
    ])
    @app_commands.command(name="create", description="Create a prediction")
    @app_commands.describe(matchbegin_timestamp="Use `/timestamp` to get a timestamp for the date and time or a website")
    async def create(self, interaction, team1: Choice[str], team2: Choice[str], bestof: Choice[str], matchbegin_timestamp: str):
        em = discord.Embed(colour=discord.Color.brand_green(), title=f"{team1.name} vs {team2.name}", description=f"Predictions close when the match begins at <t:{matchbegin_timestamp}>")
        em.add_field(name=f"{team1.value} Votes for {team1.name}", value="0")
        em.add_field(name=f"{team2.value} Votes for {team2.name}", value="0")
        # Calculate the new matchid value separately
        new_matchid = es.sql_select("SELECT COALESCE(MAX(matchid), 0) + 1 FROM matches")[0][0]
        # Use the calculated new_matchid value in the INSERT statement
        es.sql_exec(f"INSERT INTO matches (matchid, messageid, team1, team2, timestamp, team1name, team2name, bestof) VALUES ({new_matchid}, '0', 0, 0, '{matchbegin_timestamp}', '{team1.name}', '{team2.name}', {int(bestof.value)});")
        matchid = es.sql_select(f"SELECT MAX(matchid) FROM matches")[0][0]
        view = PredictionDropdownViewBestofOne(self.client, [team1, team2], matchid, int(bestof.value))
        em.set_footer(text=f"MatchID: {str(new_matchid)}")
        msg = await interaction.channel.send(embed=em, view=view)
        es.sql_exec(f"UPDATE matches SET messageid='{msg.id}' WHERE matchid = {new_matchid}")
        await interaction.response.send_message("Successfully created prediction", ephemeral=True)


class LeaderboardDropdownView(discord.ui.View):
    def __init__(self, client):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)
        self.client = client
        showallmypredictionsbutton = discord.ui.Button(label="Show all my Predictions", style=discord.ButtonStyle.grey, custom_id=f"showallmypredictions")
        showallmypredictionsbutton.callback = self.showallmypredictions
        self.add_item(showallmypredictionsbutton)

    async def showallmypredictions(self, interaction):
        mypredictions = es.sql_select(f"""        
        SELECT p.team1, p.team2, m.team1name, m.team2name
        FROM predictions p
        JOIN matches m ON p.matchid = m.matchid
        WHERE userid = '{interaction.user.id}'
        """)
        str = f""
        for prediction in mypredictions:
            str += f"**{prediction[2].decode('utf-8')}** vs **{prediction[3].decode('utf-8')}** | **{prediction[0]}** - **{prediction[1]}**\n"
        em = discord.Embed(title="All your Predictions", colour=discord.Color.dark_red(), description=str)
        await interaction.response.send_message(embed=em, ephemeral=True)
        #await interaction.response.send_message(f"You have currently selected **{mypredictions[0]} - {mypredictions[1]}** for **{mypredictions[2].decode('utf-8')}** vs **{mypredictions[3].decode('utf-8')}**", ephemeral=True)

class PredictionDropdownViewBestofOne(discord.ui.View):
    def __init__(self, client, teams, matchid, bestof):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(PredictionSelectBestofOne(client, teams, matchid, bestof))

        showmypredictionsbutton = discord.ui.Button(label="Show my Prediction", style=discord.ButtonStyle.green, custom_id=f"showmyprediction")
        showmypredictionsbutton.callback = partial(self.showmyprediction, matchid=matchid)
        self.add_item(showmypredictionsbutton)

    async def showmyprediction(self, interaction, matchid):
        await interaction.response.defer()
        mypredictions = es.sql_select(f"""        
        SELECT p.team1, p.team2, m.team1name, m.team2name
        FROM predictions p
        JOIN matches m ON p.matchid = m.matchid
        WHERE p.matchid = {matchid} AND userid = '{interaction.user.id}'
        """)
        if mypredictions:
            mypredictions = mypredictions[0]
            await interaction.followup.send(f"You have currently selected **{mypredictions[0]} - {mypredictions[1]}** for **{mypredictions[2].decode('utf-8')}** vs **{mypredictions[3].decode('utf-8')}**", ephemeral=True)
        else:
            await interaction.followup.send(f"**You haven't selected a winner for this prediction yet!**", ephemeral=True)

class PredictionViewScoreButtons(discord.ui.View):
    def __init__(self, client, teams, matchid, bestof, winnerteam, votes_message_id):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)
        self.client = client
        self.teams = teams
        self.matchid = matchid
        self.bestof = bestof
        self.votes_message_id = votes_message_id

        if int(bestof) == 2:
            options = [(2, 0), (2, 1)]
        else:
            options = [(3, 0), (3, 1), (3, 2)]
        for option in options:
            button = discord.ui.Button(label=f"{option[0]} - {option[1]}", style=discord.ButtonStyle.green, custom_id=f"scoreoption_{option[0]}_{option[1]}")
            button.callback = partial(self.selectScore, matchid=matchid, option=option, winnerteam=winnerteam)
            self.add_item(button)

    async def selectScore(self, interaction, matchid, winnerteam,  option):
        await interaction.response.defer()
        await update_user_prediction(self.client, interaction, matchid, self.teams, winnerteam, option, self.votes_message_id)


class PredictionSelectBestofOne(discord.ui.Select):
    def __init__(self, client, teams, matchid, bestof):
        self.client = client
        self.teams = teams
        self.matchid = matchid
        self.bestof = bestof
        options = [
            discord.SelectOption(label=teams[0].name, emoji=teams[0].value, description=f"Pick {teams[0].name} as winner"),
            discord.SelectOption(label=teams[1].name, emoji=teams[1].value, description=f"Pick {teams[1].name} as winner"),
        ]
        super().__init__(placeholder='Pick a winner', min_values=1, max_values=1,
                         options=options, custom_id=f'predictionselectbestofone')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.bestof == 1:
            await update_user_prediction(self.client, interaction, self.matchid, self.teams, self.values[0], (1, 0), interaction.message.id)
        else:
            await interaction.followup.send(f"You've picked **{self.values[0]}** as **winner**. What score will they finish?", view=PredictionViewScoreButtons(self.client, self.teams, self.matchid, self.bestof, self.values[0], interaction.message.id), ephemeral=True)

async def update_user_prediction(client, interaction, matchid, teams, winnerteam, winningscore, votes_message_id):
    oldPrediction = es.sql_select(
        f"SELECT * FROM predictions WHERE userid = {interaction.user.id} AND matchid = {matchid}")

    if winnerteam == teams[0].name:
        team1score = winningscore[0]
        team2score = winningscore[1]
    else:
        team1score = winningscore[1]
        team2score = winningscore[0]

    # check if prediction is already in
    if oldPrediction:
        oldPrediction = oldPrediction[0]
        #print(f"{int(winningscore[0])} == {int(oldPrediction[2])} and {winnerteam} == {teams[0]} and {winningscore[1]} == {oldPrediction[3]}")
        if int(team1score) == int(oldPrediction[2]) and winnerteam == teams[0].name and int(team2score) == int(oldPrediction[3]) or int(team1score) == int(oldPrediction[2]) and winnerteam == teams[1].name and int(team2score) == int(oldPrediction[3]):
            await interaction.followup.send(
                f"You've already choosen {teams[0].name} vs {teams[1].name} | {team1score} - {team2score}\n**Try to click Show my Prediction!**", ephemeral=True)
            return

    if not oldPrediction:
        es.sql_exec(
            f"INSERT INTO predictions(userid, matchid, team1, team2) VALUES('{interaction.user.id}', {int(matchid)}, {team1score}, {team2score})")
    else:
        es.sql_exec(
            f"UPDATE predictions SET team1={team1score}, team2={team2score} WHERE userid = '{interaction.user.id}' AND matchid = {matchid}")
    await update_votes(client, matchid, votes_message_id)
    await interaction.followup.send(f"You predicted **{teams[0].name} vs {teams[1].name} | {team1score} - {team2score}**", ephemeral=True)

async def update_votes(client, matchid, msgid):
        votes = es.sql_select(f"""SELECT
  SUM(CASE WHEN m.team1 > m.team2 THEN 1 ELSE 0 END) AS team1_score,
  SUM(CASE WHEN m.team2 > m.team1 THEN 1 ELSE 0 END) AS team2_score
FROM predictions m WHERE matchid={matchid};""")[0]
        channel = await client.fetch_channel(predictions_channel_id)
        msg = await channel.fetch_message(msgid)
        embed = msg.embeds[0]
        field1name = embed.fields[0].name
        field2name = embed.fields[1].name
        embed.clear_fields()
        embed.add_field(name=field1name, value=int(votes[0]))
        embed.add_field(name=field2name, value=int(votes[1]))
        await msg.edit(embed=embed)


async def setup(client):
    await client.add_cog(prediction(client), guilds=guilds)