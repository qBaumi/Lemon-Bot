import asyncio
import datetime
import os
import random
from pathlib import Path
from typing import Optional

import discord, json
import pytz
from PIL import Image
from discord.ext import commands
from discord import app_commands
from discord import ui

from config import guilds, allowedRoles
from discord.app_commands import Choice
import cogs.essentialfunctions as es

staffqueuecheck_channel_id = 1158016066543427724
queuecontent_message_id = 0 # message in #stream-submissions

class other(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logchannel = None



    @commands.Cog.listener()
    async def on_ready(self):
        self.logchannel = await self.client.fetch_channel(967113937634078771)
        print("on_ready")


    @app_commands.command(name="suggest", description="Suggest an emote or something else!")
    async def suggest(self, interaction: discord.Interaction):
        modal = Suggestion(client=self.client)
        await interaction.response.send_modal(modal)

    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @commands.command(name="permqueuecontent", description="Permanent message for stream-submissions channel, admincommand")
    async def permqueuecontent(self, ctx):
        em = discord.Embed(colour=discord.Color.from_rgb(229, 196, 89))
        em.set_image(
            url="https://media.discordapp.net/attachments/651364619402739713/1158021337617531060/streamcontentsmile.png?ex=651abae9&is=65196969&hm=28a33f154353470d8249a3f9f159d897e72bec4845a0c71bc142ae28504c78d8&=&width=1440&height=458")
        await ctx.send(embed=em)

        em = discord.Embed(title="Nemesis Twitch Stream Submissions!", colour=discord.Color.from_rgb(229, 196, 89))
        em.add_field(name="\u200b", value="""Do you want Nemesis to look at your setup or rate your food? This is the channel to submit it in! The contributions from this channel will be sent in \<#1158007237894213672> for Nemesis to go through in between his games on stream.

*How to submit*
To submit queue content, you have to:
1. Click on the submit button under this message
2. Choose the category for the content you want to submit
3. Paste the link for the picture or video you want to submit in the textbox 

*Info*
- All server rules still apply!
- Please dont send very long clips, we will not approve that.
- Mods will go through every submission, so if you don't see your submission right away its not approved yet. Sit tight, it will appear in \<#1158007237894213672> once its cleared. 
- We do not choose when Nemesis decides to go through it and we do not take responsibility if you miss out on his review of your submission.""")
        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
        await ctx.send(embed=em, view=QueueContentDropdownView(self.client))

    @app_commands.choices(tag=[
        Choice(name='Food', value="food"),
        Choice(name='Setups', value="setups"),
    ])
    @app_commands.describe(link='A link to the image/gif')
    @app_commands.command(name="submit", description="Submit an image for Nemesis to view on stream!")
    async def submit(self, interaction: discord.Interaction, tag: Choice[str], link: str):

        if tag.value == "food":
            color = discord.Color.red()
            #thread = await self.client.fetch_channel(1158007582854746112)
        else:
            color = discord.Color.blue()
            #thread = await self.client.fetch_channel(1158007765646716988)
        em = discord.Embed(title=f"{interaction.user}", color=color)
        em.add_field(name=tag.name, value=link)
        em.set_footer(text=f"{interaction.user.id}")
        em.set_image(url=link)
        channel = await self.client.fetch_channel(staffqueuecheck_channel_id)
        msg = await channel.send(embed=em)
        await msg.add_reaction("✅")
        await interaction.response.send_message("Thanks for submitting!", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if(reaction.channel_id != staffqueuecheck_channel_id or reaction.user_id == 881476780765093939):
            return
        if(reaction.emoji.name == "✅"):
            print("worked reaction")
            channel = await self.client.fetch_channel(staffqueuecheck_channel_id)
            msg = await channel.fetch_message(reaction.message_id)
            embed = msg.embeds[0]
            if embed.fields[0].name == "Food":
                color = discord.Color.red()
                thread = await self.client.fetch_channel(1158007582854746112)
            else:
                color = discord.Color.blue()
                thread = await self.client.fetch_channel(1158007765646716988)
            embed.set_image(url=None)
            await thread.send(embed=embed)

    @app_commands.command(name="val", description="Sign up for the valorant tournament")
    async def val(self, interaction: discord.Interaction):
        modal = Val(client=self.client)
        await interaction.response.send_modal(modal)


    @app_commands.describe(game='The activity you want to start')
    @app_commands.choices(game=[
        Choice(name='Watch Together', value="880218394199220334"),
        Choice(name='Poker Night', value="755827207812677713"),
        Choice(name='Betrayal.io', value="773336526917861400"),
        Choice(name='Fishington.io', value="814288819477020702"),
        Choice(name='Chess In The Park', value="832012774040141894"),
        Choice(name='Sketchy Artist', value="879864070101172255"),
        Choice(name='Awkword', value="879863881349087252"),
        Choice(name='Doodle Crew', value="878067389634314250"),
        Choice(name='Sketch Heads', value="902271654783242291"),
        Choice(name='Letter League', value="879863686565621790"),
        Choice(name='Word Snacks', value="879863976006127627"),
        Choice(name='SpellCast', value="852509694341283871"),
        Choice(name='Checkers In The Park', value="832013003968348200"),
        Choice(name='Blazing 8s', value="832025144389533716"),
        Choice(name='Putt Party', value="945737671223947305"),
        Choice(name='Land-io', value="903769130790969345")
    ])
    @app_commands.command(name="game", description="Start a discord voice channel activity!")
    async def game(self, interaction: discord.Interaction, game: Choice[str]):
        # User needs to be in a voice channel
        if interaction.user.voice == None:
            await interaction.response.send_message(
                "You need to be in a voice channel to start an activity, that's why they're called voice channel activities")
            return

        # Create an invite with the application id
        invite = await interaction.user.voice.channel.create_invite(
            target_application_id=int(game.value),
            target_type=discord.InviteTarget.embedded_application
        )
        print(invite)
        em = discord.Embed(title="Click the link to start the game in your voice channel", description=invite)
        await interaction.response.send_message(embed=em)

    @app_commands.command(name="about", description="Start a discord voice channel activity!")
    async def about(self, interaction : discord.Interaction):
        em = discord.Embed(title="About me", description="Thanks to all the people that helped me making this bot!")
        em.add_field(name="Creator / Developer", value="qBaumi#1247", inline=False)
        em.add_field(name="Artist", value="https://twitter.com/lilRoundabout/", inline=False)
        em.add_field(name="Description",
                     value=f"Hello, I am the Lemon Bot. \n Let me introduce real quick.\nI am an economy bot for the Nemesis discord server. I can get you precious lemons, if you get some work done for me...of course\nYou can find out more about me when you type **/help** for example. But only in bot-commands, otherwise my boss will get angry...\nIf you have ANY ideas for items or commands, please share them with my Boss, you will find him at the beginning of this message.\n Thank you to all who helped creating me!",
                     inline=False)
        await interaction.response.send_message(embed=em)

    @app_commands.command(name="debug", description="Show the string of an emoji")
    async def debug(self, interaction: discord.Interaction, emoji: str):
        print(emoji)
        embed = discord.Embed(description=f"{emoji[1:len(emoji)-1]}", title=f"emoji: {emoji}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Start a discord voice channel activity!")
    async def hug(self, interaction : discord.Interaction, user : discord.User):
        hugs = ["<:nemeHug:834605591846584391>", "<:nemeHugBack:834971356873490462>",
                "<:nemeportalhug1:835504785285316648>", "<:nemeportalhug2:835504785586257939>",
                "<:wideHug1:834605591393206323><:widehug2:835116553812967444><:wideHug3:834605592022220860>",
                "<:dankHug:832245187614212106>"]
        hug = random.choice(hugs)
        await interaction.response.send_message(f"{interaction.user.mention} gave {user.mention} a hug")
        await interaction.channel.send(hug)


    @app_commands.command(name="badge", description="Get the PNG file of a role badge")
    async def badge(self, interaction, role : discord.Role):
        #guild = await self.client.fetch_guild(598303095352459305)
        #role = discord.utils.get(guild.roles, id=598307062086107156)
        print(role.icon)
        await interaction.response.send_message(role.icon)

    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(name="addteam", description="Adds a team to the tournament")
    async def addteam(self, interaction, name: str, role: discord.Role, captainrole: discord.Role):
        await interaction.response.defer()
        captain = captainrole.members[0]
        members = []
        sixthmember = False
        for member in role.members:
            if member != captain:
                members.append(member)
        members.insert(0, captain)
        try:
            print(members[5])
            sixthmember = True
        except:
            sixthmember = False

        """
        {
            "name": "Team 1",
            "logo": "https://cdn.discordapp.com/attachments/1073219367459880971/1073947900503142480/IMG_3710.png",
            "role": 992135667805081600,
            "members": [
              442913791215140875,
              198218633955115008
            ],
            "msgId": 8,
            "wins": 2,
            "losses": 3
          }
        """
        with open("./json/teams.json", "r", encoding="utf-8") as f:
            teams = json.load(f)
        channel = await self.client.fetch_channel(1073985397614444635)
        em = discord.Embed(title=name, description=role.mention)
        em.set_thumbnail(url=role.icon.url)
        em.add_field(name="Wins / Losses", value=f"0 / 0", inline=False)
        if sixthmember:
            em.add_field(name="Members", value=f"{captain.mention} - Team Captain\n{members[1].mention}\n{members[2].mention}\n{members[3].mention}\n{members[4].mention}\n{members[5].mention}", inline=False)
        else:
            em.add_field(name="Members", value=f"{captain.mention} - Team Captain\n{members[1].mention}\n{members[2].mention}\n{members[3].mention}\n{members[4].mention}", inline=False)
        em.set_footer(text="----------------------------------------------------------------------------")
        msg = await channel.send(embed=em)
        print(sixthmember)
        if sixthmember:
            teams.append({
                "name": name,
                "logo": role.icon.url,
                "role": role.id,
                "members": [
                    members[0].id,
                    members[1].id,
                    members[2].id,
                    members[3].id,
                    members[4].id,
                    members[5].id
                ],
                "msgId":msg.id,
                "wins":0,
                "losses":0
            })
        else:
            teams.append({
                "name": name,
                "logo": role.icon.url,
                "role": role.id,
                "members": [
                    members[0].id,
                    members[1].id,
                    members[2].id,
                    members[3].id,
                    members[4].id
                ],
                "msgId": msg.id,
                "wins": 0,
                "losses": 0
            })

        with open("./json/teams.json", "w") as f:
            json.dump(teams, f, indent=4)
        await interaction.followup.send("Succesfully added team")

    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(name="editteam", description="Edits a team")
    async def editteam(self, interaction, name: str, wins: int, losses: int):
        await interaction.response.defer()
        with open("./json/teams.json", "r", encoding="utf-8") as f:
            teams = json.load(f)
        teamfound = False
        for team in teams:
            if team["name"] == name:
                team["wins"] = wins
                team["losses"] = losses

                em = discord.Embed(title=name, description=f'<@&{team["role"]}>')
                em.set_thumbnail(url=team["logo"])
                em.add_field(name="Wins / Losses", value=f"{wins} / {losses}", inline=False)
                try:
                    em.add_field(name="Members",
                                 value=f"<@!{team['members'][0]}> - Team Captain\n<@!{team['members'][1]}>\n<@!{team['members'][2]}>\n<@!{team['members'][3]}>\n<@!{team['members'][4]}>\n<@!{team['members'][5]}>",
                                 inline=False)
                except:
                    em.add_field(name="Members",
                                 value=f"<@!{team['members'][0]}> - Team Captain\n<@!{team['members'][1]}>\n<@!{team['members'][2]}>\n<@!{team['members'][3]}>\n<@!{team['members'][4]}>",
                                 inline=False)

                em.set_footer(text="----------------------------------------------------------------------------")
                channel = await self.client.fetch_channel(1073985397614444635)
                message = await channel.fetch_message(team["msgId"])
                await message.edit(embed=em)
                teamfound = True
                break

        with open("./json/teams.json", "w") as f:
            json.dump(teams, f, indent=4)
        if teamfound:
            await interaction.followup.send(f"Succesfully edited {name}")
        else:
            await interaction.followup.send(f"Team {name} not found")

    @app_commands.checks.has_role(598307062086107156)
    @app_commands.command(name="updatetournamentroles", description="copy paste the tournament users")
    async def updatetournamentroles(self, interaction, users : str):
        await interaction.response.defer()
        guild = await self.client.fetch_guild(598303095352459305)
        members = {}
        async for member in guild.fetch_members(limit=10000):
            members[str(member).lower()] = member

        lastindex = 0
        userlist = []
        for i, letter in enumerate(users):
            try:
                num = int(users[i])
                if users[i+1] == " ":
                    userlist.append(users[lastindex:i+1])
                    lastindex = i+2

            except IndexError as e:
                userlist.append(users[lastindex:len(users)])
            except:
                pass
        print(userlist)
        role = discord.utils.get(guild.roles, id=1064211501839286412)
        failed_members = []
        for user in userlist:
            try:
                await members[user.lower()].add_roles(role)
            except:
                failed_members.append(user)
        await interaction.followup.send(f"Added tournament roles except for {failed_members} because theyre brainded and have to write a space infront of the #")



    @commands.Cog.listener()
    async def on_member_update(self, beforemember, aftermember):
        if beforemember.timed_out_until is None and aftermember.timed_out_until is None:
            return
        try:
            if beforemember.timed_out_until.replace(tzinfo=pytz.UTC) < datetime.datetime.now().replace(tzinfo=pytz.UTC) and aftermember.timed_out_until is not None and beforemember.timed_out_until != aftermember.timed_out_until:
                em = discord.Embed(title="timeout")
                em.add_field(name="Offender:", value=f"{str(aftermember)}<@{aftermember.id}>", inline=False)
                em.add_field(name="Timed out until:", value=f"{(aftermember.timed_out_until  + datetime.timedelta(hours=2)).strftime('%d/%m/%Y %H:%M')}")
                em.set_footer(text=f"ID: {aftermember.id} • {datetime.datetime.now().strftime('%d/%m/%Y')}")
                channel = await self.client.fetch_channel(662829172888174611)
                await channel.send(embed=em)
                return
        except:
            if beforemember.timed_out_until is None and aftermember.timed_out_until is not None:
                em = discord.Embed(title="timeout")
                em.add_field(name="Offender:", value=f"{str(aftermember)}<@{aftermember.id}>", inline=False)
                em.add_field(name="Timed out until:", value=f"{(aftermember.timed_out_until  + datetime.timedelta(hours=2)).strftime('%d/%m/%Y %H:%M')}")
                em.set_footer(text=f"ID: {aftermember.id} • {datetime.datetime.now().strftime('%d/%m/%Y')}")
                channel = await self.client.fetch_channel(662829172888174611)
                await channel.send(embed=em)
                return

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.type) == "voice" and self.logchannel:
            em = discord.Embed()
            em.set_author(name=message.author.name, icon_url=message.author.avatar)
            em.add_field(name=message.channel.name, value=message.content)
            await self.logchannel.send(embed=em)

            #badwords = ["fag", "farggot", "nigger", "nazi", "cancer", "autist", "retard", "jew", "mentally challenged", "suicide", "kill myself", "kill yourself", "autistic", "kys", "kms", "dick", "cock", "porn", "slut", "niglet", "negro", "dyke", "whore", "chink", "nibba", "braindead", "autism", "nigglet", "beaner", "child-fucker", "motherfucker", "twat", "bellend", "arschgesicht", "rape", "cocknose", "anal", "nonce", "depression", "rape", "rapist", "aids", "nigga", "pedo", "subhuman", "kike", "kyke", "nignog", "cao ni ma", "ape"]
            #if any(word in message.content.lower() for word in badwords):
            #    modchannel = await self.client.fetch_channel(963720915575779358)
            #    em = discord.Embed(title="Warning", description=f"<#967113937634078771> for more information")
            #    em.add_field(name=message.author.name, value=message.content)
            #    await modchannel.send(embed=em)



    class Prediction(ui.Modal, title="Worlds 2022"):

        def __init__(self, client, tournament, resultchannelid, sheetlink):
            super().__init__()
            self.client = client
            self.tournament = tournament
            self.resultchannelid = resultchannelid
            self.sheetlink = sheetlink


        email = ui.TextInput(label='Email Adress', placeholder="Put your email adress here to access the Google Sheet later")

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.send_message(f'You can soon access the prediction sheet!', ephemeral=True, view=self.SheetLink(sheetlink=self.sheetlink))

            # 656636484937449518 this is the suggestion-log channel
            # 651364619402739713 this is the test channel
            # 820728066514354206 prediction sheet
            # the id of the channel the results get sent to
            channel = await self.client.fetch_channel(self.resultchannelid)

            # Make an embed with the results
            em = discord.Embed(title=self.tournament, description=f"by {interaction.user.mention} | {str(interaction.user)}")
            em.add_field(name="Email", value=self.email)

            await channel.send(embed=em)

        class SheetLink(discord.ui.View):
            def __init__(self, sheetlink):
                super().__init__()

                self.add_item(discord.ui.Button(label='Prediction Sheet', url=sheetlink))



    @app_commands.command(name="worlds", description="Sign up for the Prediction Sheet!")
    async def worlds(self, interaction: discord.Interaction):
        modal = self.Prediction(client=self.client, tournament="Worlds 2022", resultchannelid=820728066514354206, sheetlink="https://docs.google.com/spreadsheets/d/1SsnIXuAFAUWcs97ccKotfmurvuUNnHhdf-Jg7i1Bu58/edit?usp=sharing")
        await interaction.response.send_modal(modal)


    #@app_commands.command(name="lec", description="Sign up for the Prediction Sheet!")
    #async def lec(self, interaction: discord.Interaction):
    #    modal = self.Prediction(client=self.client, tournament="LEC Summer Playoffs 2022", resultchannelid=820728066514354206, sheetlink="https://docs.google.com/spreadsheets/d/1SsnIXuAFAUWcs97ccKotfmurvuUNnHhdf-Jg7i1Bu58/edit#gid=715753226")
    #    await interaction.response.send_modal(modal)


    @app_commands.command(name="feedback", description="Give us anonymous feedback!")
    async def feedback(self, interaction: discord.Interaction):
        modal = Feedback(self.client)
        print(f"Feedback by: {interaction.user}")
        print(f"Feedback by: {interaction.user}")
        print(f"Feedback by: {interaction.user}")
        await interaction.response.send_modal(modal)

    @app_commands.command(name="timestamp", description="Get a timestamp of CET")
    async def timestamp(self, interaction: discord.Interaction, day : app_commands.Range[int, 0, 31], month : app_commands.Range[int, 0, 12], year : app_commands.Range[int, 0, 2030], hour : app_commands.Range[int, 0, 23], minutes : app_commands.Range[int, 0, 59]):
        time = datetime.datetime.strptime(f"{'{:02d}'.format(day)}/{'{:02d}'.format(month)}/{'{:04d}'.format(year)} {'{:02d}'.format(hour)}:{'{:02d}'.format(minutes)}", "%d/%m/%Y %H:%M").timestamp()
        time = int(time)
        await interaction.response.send_message(f"`{time}`\nUse `<t:{time}>` to get <t:{time}>")

    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @commands.command(name="permfeedback", description="Permanent message for feedback channel, admincommand")
    async def permfeedback(self, ctx):

        em = discord.Embed(colour=discord.Color.from_rgb(229, 196, 89))
        em.set_image(
            url="https://cdn.discordapp.com/attachments/968210243144261632/994308636488765523/asdsadasdadsa.png")
        await ctx.send(embed=em)

        em = discord.Embed(title="Feedback", description="We are very greatful for any feedback we receive. This feedback form is completely anonymous and no mod is going to know who submitted the feedback. You can give us anything from event ideas, wishes for community nights, feature ideas to what we can improve etc. So click on the button and give it a try! Thank you for your feedback!", colour=discord.Color.from_rgb(229, 196, 89))
        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
        await ctx.send(embed=em, view=FeedbackButtons(self.client))



    @commands.command(name="santorin", description="Bomis vacation photos")
    async def santorin(self, ctx):
        directory = "./img/santorin"
        embeds = []
        links = [
            "https://cdn.discordapp.com/attachments/955170155569250415/994681512769368064/20220613_112858.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681513205563533/20220613_112927.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681513679540294/20220613_115613.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681514002485418/20220613_115632.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681514463854662/20220613_115637.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681514925236315/20220613_121500.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681515445325835/20220613_131112.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681516804276224/20220613_135035.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681517102092318/20220615_182353.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681517907390514/20220615_184131.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681604792389752/20220615_184148.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681605408964608/20220615_201615.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681605807411300/20220615_202536.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681606432378920/20220615_203238.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681606818246826/20220616_081250.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681607455789168/20220616_081255.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681607887790191/20220616_081259.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681608361746522/20220616_081319.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681609989144757/20220616_082834.jpg",
            "https://cdn.discordapp.com/attachments/955170155569250415/994681610605690970/20220616_082914.jpg",
            "https: // cdn.discordapp.com / attachments / 955170155569250415 / 994681701861175397 / 20220616_082917.jpg",
        "https://cdn.discordapp.com/attachments/955170155569250415/994681702330945637/20220616_082927.jpg",
        "https://cdn.discordapp.com/attachments/955170155569250415/994681702666477659/20220616_082953.jpg"
        ]
        for i, filename in enumerate(os.listdir(directory)):
            print(filename)
            path = os.path.join(directory, filename)

            #testbomi = await self.client.fetch_user(783380754238406686)
            #file = discord.File(path)
            #msg = await testbomi.send(file=file)
            #links.append(msg.jump_url)

            embed = discord.Embed(colour=discord.Color.from_str("#009dff"), title="Santorin", description=str(Image.open(path)._getexif()[36867]))
            embed.set_image(url=links[i])
            embeds.append(embed)
        await ctx.send(view=PagesView(ctx.author, embeds), embed=embeds[0].set_footer(text="1 / 23"))


class Val(ui.Modal, title='Valorant Tournament Signup'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    name = ui.TextInput(label='ingame name', placeholder="Put your RiotID HERE")
    desc = ui.TextInput(label='Link/Rank', style=discord.TextStyle.paragraph,
                        placeholder="Put your valorant tracker link here. If your profile is on private then put your rank here!")

    async def on_submit(self, interaction: discord.Interaction):
        guild = await self.client.fetch_guild(598303095352459305)
        role = discord.utils.get(guild.roles, id=1109197301567725710)

        await interaction.user.add_roles(role)

        await interaction.response.send_message(f'Thanks for signing up!', ephemeral=True)

        # 656636484937449518 this is the suggestion-log channel
        # 651364619402739713 this is the test channel
        channel_id = 1109188010303569920  # the id of the channel the results get sent to
        channel = await self.client.fetch_channel(channel_id)

        # Make an embed with the results
        em = discord.Embed(title="Valorant Signup", description=f"by {interaction.user}")
        em.add_field(name=self.name, value=self.desc)

        await channel.send(embed=em)




class Suggestion(ui.Modal, title='Suggestion'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    """ Select menu isnt released yet pepeHands
    options = [
        discord.SelectOption(label='Emoji', description='Submit an Emote', emoji='🟩'),
        discord.SelectOption(label='Suggestion', description='Submit any other Suggestion', emoji='🟩'),
        discord.SelectOption(label='Feedback', description='Give us some Feedback, we\'d love to hear it!',
                             emoji='🟩')
    ]
    dropdown = ui.Select(custom_id = "type", placeholder="type", min_values=1, max_values=1)
    """
    name = ui.TextInput(label='title/emoji name', placeholder="Title or emoji name")
    desc = ui.TextInput(label='Description/Link', style=discord.TextStyle.paragraph,
                        placeholder="If you submit an emoji please put the link to the image here!")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your Suggestion!', ephemeral=True)

        # 656636484937449518 this is the suggestion-log channel
        # 651364619402739713 this is the test channel
        channel_id = 656636484937449518  # the id of the channel the results get sent to
        channel = await self.client.fetch_channel(channel_id)

        # Make an embed with the results
        em = discord.Embed(title="Suggestion", description=f"by {interaction.user}")
        em.add_field(name=self.name, value=self.desc)

        await channel.send(embed=em)



class Feedback(ui.Modal, title='Feedback'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    feedback = ui.TextInput(label='Anonymous Feedback', style=discord.TextStyle.paragraph,
                        placeholder="This Feedback form is completely anonymous!")
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your Feedback!', ephemeral=True)
        channel_id = 656636484937449518
        channel = await self.client.fetch_channel(channel_id)

        em = discord.Embed(title="Feedback", description=self.feedback)
        em.set_footer(text=f"by rion NA Diamond I")
        await channel.send(embed=em)

class FeedbackButtons(discord.ui.View):

    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

    @discord.ui.button(label='Feedback', style=discord.ButtonStyle.primary, custom_id="feedback")
    async def feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = Feedback(self.client)
        print(f"Feedback by: {interaction.user}")
        print(f"Feedback by: {interaction.user}")
        print(f"Feedback by: {interaction.user}")
        await interaction.response.send_modal(modal)

class PagesView(discord.ui.View):

    def __init__(self, user, pages):
        super().__init__()
        self.user = user
        self.pages = pages
        self.current_page = 0
        self.max_pages = len(pages)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.blurple)
    async def left(self, interaction : discord.Interaction, button : discord.Button):
        if self.current_page == 0:
            self.current_page = self.max_pages-1
        else:
            self.current_page = self.current_page-1
        self.pages[self.current_page].set_footer(text=f"{self.current_page+1} / {self.max_pages}")
        await interaction.response.edit_message(view=self, embed=self.pages[self.current_page])

    @discord.ui.button(label="▶", style=discord.ButtonStyle.blurple)
    async def right(self, interaction : discord.Interaction, button : discord.Button):
        if self.current_page == self.max_pages-1:
            self.current_page = 0
        else:
            self.current_page = self.current_page+1
        self.pages[self.current_page].set_footer(text=f"{self.current_page+1} / {self.max_pages}")
        await interaction.response.edit_message(view=self, embed=self.pages[self.current_page])


class QueueContentDropdownView(discord.ui.View):
    def __init__(self, client):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(client))

class Dropdown(discord.ui.Select):
    def __init__(self, client):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Food', description='', emoji='🍗'),
            discord.SelectOption(label='Setups', description='', emoji='🖥️'),
        ]

        super().__init__(placeholder='Select a category', min_values=1, max_values=1,
                         options=options, custom_id='persistent_view:selectdropdown_reviews')
        self.client = client

    async def callback(self, interaction: discord.Interaction):

        # we can get the values of the selection, cause self is the dropdown class and it has the attribute values
        category = self.values[0]
        # Now the embed will be changed depending on the value of the selection
        # Also we set the option to True so it will be shown down in the select menu and not be empty again
        modal = QueueContentModal(self.client, category)
        await interaction.response.send_modal(modal)

class QueueContentModal(ui.Modal, title='Submit Content'):

    def __init__(self, client, category):
        super().__init__()
        self.client = client
        self.category = category


    link = ui.TextInput(label='Link', placeholder="Put your link to an image/video here, you can use imgur.com to generate one", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        if self.category == "food":
            color = discord.Color.red()
            #thread = await self.client.fetch_channel(1158007582854746112)
        else:
            color = discord.Color.blue()
            #thread = await self.client.fetch_channel(1158007765646716988)
        em = discord.Embed(title=f"{interaction.user}", color=color)
        em.add_field(name=self.category, value=self.link)
        em.set_footer(text=f"{interaction.user.id}")
        em.set_image(url=self.link)
        channel = await self.client.fetch_channel(staffqueuecheck_channel_id)
        msg = await channel.send(embed=em)
        await msg.add_reaction("✅")
        await interaction.response.send_message("Thanks for submitting!", ephemeral=True)


async def setup(client):
    await client.add_cog(other(client), guilds=guilds)