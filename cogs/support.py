import datetime
import math
import random
import time

import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from config import guilds, allowedAdminRoles, allowedRoles
from discord.app_commands import Choice
from .other import Suggestion
import chat_exporter
import io

channel_id = 970083491586900068  # this is the channel where results get sent in archive, aka #actions ITS #tickets NOW
twitchmod_channel_id = 841020368323870761 # this is the channel for the twitch tickets
support_category_id = 955151615252385854
support_channel_id = 955476670352093204 # #support for the claim message in cogs.economy
feedback_message_id = 994313931877257386
support_message_id = 971321595803082802 # message in #support
TESTMODE = False

def getmsgids():
    with open("./json/viewmsgids.json", "r", encoding="utf-8") as f:
        msgids = json.load(f)
    return msgids
def addid(msgid, ticketchannelid, openerid):
    msgids = getmsgids()
    msgids.append({"msg_id" : msgid, "ticketchannel_id" : ticketchannelid, "opener_id" : openerid})
    with open("./json/viewmsgids.json", "w") as f:
        json.dump(msgids, f, indent=4)
async def removeid(ticketchannelid):
    msgids = getmsgids()
    for msg in msgids:
        print(ticketchannelid)
        print(msg["msg_id"])
        if msg["ticketchannel_id"] == ticketchannelid:
            msgids.remove(msg)
    with open("./json/viewmsgids.json", "w") as f:
        json.dump(msgids, f, indent=4)

async def setheadmodperms(user, channel, client, enabled):
    guild = await client.fetch_guild(598303095352459305)
    role = discord.utils.get(guild.roles, id=845280788001849345)
    await channel.set_permissions(guild.default_role, view_channel=False)
    await channel.set_permissions(role, view_channel=enabled)
    await channel.set_permissions(user, view_channel=True)
async def setmodperms(user, channel, client, enabled):
    guild = await client.fetch_guild(598303095352459305)

    role = discord.utils.get(guild.roles, id=598307062086107156)
    await channel.set_permissions(guild.default_role, view_channel=False)
    await channel.set_permissions(role, view_channel=enabled)
    await channel.set_permissions(user, view_channel=True)
async def setverifiedperms(user, channel, client, enabled):
    guild = await client.fetch_guild(598303095352459305)
    role = discord.utils.get(guild.roles, id=598307062086107156) # changed these perms to mod because verification helper role doesn't exist anymore
    await channel.set_permissions(guild.default_role, view_channel=False)
    await channel.set_permissions(role, view_channel=enabled)
    await channel.set_permissions(user, view_channel=True)
async def settwitchmodperms(user, channel, client, enabled):
    guild = await client.fetch_guild(598303095352459305)

    role = discord.utils.get(guild.roles, id=841020059945009193)
    await channel.set_permissions(guild.default_role, view_channel=False)
    await channel.set_permissions(role, view_channel=enabled)
    await channel.set_permissions(user, view_channel=True)

class support(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @commands.command(name="permsupport", description="Permanent message for support channel, admincommand")
    async def permsupport(self, ctx):
        em = discord.Embed(colour=discord.Color.from_rgb(229, 196, 89))
        em.set_image(
            url="https://media.discordapp.net/attachments/651364619402739713/881551197608218644/Support.png?width=1440&height=458")
        await ctx.send(embed=em)

        em = discord.Embed(title="Ticket Support", colour=discord.Color.from_rgb(229, 196, 89))
        em.add_field(name="\u200b", value="""🪙 **- Verification** If you have read the Verification tab under <#945162520275079199> and you need further support, feel free to open a ticket that will allow our staff members to offer you further assistance.

🎁 **- Claim a reward** If you claimed a reward through <@881476780765093939>, please open a ticket to claim it.

📺 **- Twitch Support** Get help from twitch mods or ask questions about Nemesis stream

❗ **- Make a report** If you notice someone breaking the rules or you're negatively affected by someone's behavior, open a ticket to discuss it with our staff members.

📔 **- Other** If you have any other issue with the server, questions for the staff members, event ideas or suggestions you'd like to further discuss etc. feel free to open a ticket.

📥 **- Suggestions** This will open a form that will be sent to us to consider, however, this will not open a channel where we can discuss it, so make sure you include as much detail as you can (e.g. Emote name and a link we can download it from)""")
        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
        await ctx.send(embed=em, view=DropdownView(self.client))

    @app_commands.command(name="support", description="Open a Support Ticket")
    async def support(self, interaction : discord.Interaction):
        em = discord.Embed(title="Ticket Support", colour=discord.Color.from_rgb(229, 196, 89))
        em.add_field(name="\u200b", value="""🪙 **- Verification** If you have trouble seeing all channels after verifying yourself in <#1108741931518922862> you can open a ticket here.

        🎁 **- Claim a reward** If you claimed a reward through <@881476780765093939>, please open a ticket to claim it.

        ❗ **- Make a report** If you notice someone breaking the rules or you're negatively affected by someone's behavior, open a ticket to discuss it with our staff members.

        📔 **- Other** If you have any other issue with the server, questions for the staff members, event ideas or suggestions you'd like to further discuss etc. feel free to open a ticket.

        📥 **- Suggestions** This will open a form that will be sent to us to consider, however, this will not open a channel where we can discuss it, so make sure you include as much detail as you can (e.g. Emote name and a link we can download it from)""")

        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
        await interaction.response.send_message(embed=em, view=DropdownView(self.client), ephemeral=True)

class DropdownView(discord.ui.View):
    def __init__(self, client):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(client))
class Dropdown(discord.ui.Select):
    def __init__(self, client):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Verification', description='Get support for the Verification', emoji='🪙'),
            discord.SelectOption(label='Claim a reward', description='Claim a reward you won', emoji='🎁'),
            discord.SelectOption(label='Twitch Support', description='Get help from twitch mods', emoji='📺'),
            discord.SelectOption(label='Make a Report', description='Report one or multiple users', emoji='❗'),
            discord.SelectOption(label='Other', description='Open a ticket with staff members', emoji='📔'),
            discord.SelectOption(label='Suggestion', description='Suggest and emote or something else', emoji='📥')
        ]

        super().__init__(placeholder='Open a Ticket', min_values=1, max_values=1,
                         options=options, custom_id='persistent_view:selectdropdown')
        self.client = client

    async def callback(self, interaction: discord.Interaction):

        # we can get the values of the selection, cause self is the dropdown class and it has the attribute values
        category = self.values[0]

        # Check if user has Lemon role
        user = interaction.user
        verified = False
        for role in user.roles:
            if role.id == 955101166088368179:
                verified = True
        # Now the embed will be changed depending on the value of the selection
        # Also we set the option to True so it will be shown down in the select menu and not be empty again
        if category == "Verification":
            modal = Verification(self.client)
        elif category == "Claim a reward":
            modal = Claim(self.client)
        elif category == "Twitch Support":
            modal = Twitch(self.client)
        elif category == "Make a Report":
            modal = Report(self.client)
        elif category == "Suggestion":
            modal = Suggestion(self.client)
        else: # this is for category other
            modal = Other(self.client)
        if category != "Verification" and verified == False:
            await interaction.response.send_message("You need to be verified to open a ticket!", ephemeral=True)
            return

        await interaction.response.send_modal(modal)

class GetToChannelButton(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__()

        url = f"https://discord.com/channels/598303095352459305/{channel_id}/"

        self.add_item(discord.ui.Button(label='Ticket Channel', url=url))
"""
class ticketlinkbutton(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label='Archive', url=url))
"""
class CloseButtons(discord.ui.View):

    def __init__(self, client, ticketchannel, opener, type=""):
        super().__init__(timeout=None)
        self.client = client
        self.ticketchannel = ticketchannel
        self.opener = opener
        self.type = type


    @discord.ui.button(label='Close', style=discord.ButtonStyle.red, custom_id="close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket closed", ephemeral=True)

        if self.type == "twitch":
            resultschannel = await self.client.fetch_channel(twitchmod_channel_id)
        else:
            resultschannel = await self.client.fetch_channel(channel_id)

        print(self.ticketchannel)
        print(resultschannel)
        print(self.client)
        print(self.opener)
        print(interaction.user.mention)

        await archive(self.ticketchannel, resultschannel, self.client, self.opener, interaction.user.mention)

        time.sleep(5)
        await removeid(self.ticketchannel.id)
        await self.ticketchannel.delete()
    @discord.ui.button(label='Close with Reason', style=discord.ButtonStyle.red, custom_id="closewithreason")
    async def closewithreason(self, interaction: discord.Interaction, button: discord.ui.Button):

        modal = CloseWithReason(client=self.client, ticketchannel=self.ticketchannel, opener=self.opener, type=self.type)
        await interaction.response.send_modal(modal)

async def openTicketResponse(interaction, ticketchannel):
    await interaction.followup.send(f'{interaction.user.mention}\nClick on the button to get to your ticket channel!', ephemeral=True,
                                            view=GetToChannelButton(ticketchannel.id))
async def openticket(client, interaction):
    category = await client.fetch_channel(support_category_id)
    guild = await client.fetch_guild(598303095352459305)
    for channel in category.channels:

        if str(channel) == f"ticket-{interaction.user}".lower().replace("#", "") and str(channel) != "ticket-qbaumi1247":
            print("here")
            return None
    ticketchannel = await guild.create_text_channel(f'ticket-{interaction.user}', category=category)
    return ticketchannel
async def archive(channel, archive_channel, client, opener, closer, reason=""):

    if channel and archive_channel:
        transcript = await chat_exporter.export(channel)
        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                       filename=f"{channel.name}.html")
        member = await client.fetch_user(442913791215140875)
        message = await member.send(file=transcript_file)

        # now make pretty embed for #actions
        em = discord.Embed(title="Ticket Closed", colour=discord.Color.green())
        if reason != "":
            em.add_field(name="Reason", value=reason, inline=False)
        em.add_field(name="Opened by", value=opener, inline=False)
        em.add_field(name="Closed by", value=closer, inline=False)
        em.add_field(name="Opened at", value=f"<t:{math.floor(time.time())}>", inline=False)
        em.add_field(name="Archive", value=f"[Click here]({message.attachments[0].url})", inline=False)
        await archive_channel.send(embed=em) # , view=ticketlinkbutton(url=message.attachments[0].url)
class CloseWithReason(ui.Modal, title='Close Ticket with Reason'):

    def __init__(self, client, ticketchannel, opener, type=""):
        super().__init__()
        self.client = client
        self.ticketchannel = ticketchannel
        self.opener = opener
        self.type = type
    reason = ui.TextInput(label='Reason', placeholder="Sara, hello, didnt ask + ratio")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Closed Ticket with reason {self.reason}', ephemeral=True)
        if self.type == "twitch":
            resultschannel = await self.client.fetch_channel(twitchmod_channel_id)
        else:
            resultschannel = await self.client.fetch_channel(channel_id)

        await archive(self.ticketchannel, resultschannel, self.client, self.opener,interaction.user.mention,str(self.reason))
        time.sleep(5)
        await removeid(self.ticketchannel.id)
        await self.ticketchannel.delete()


"""
Verification
  - description
Claim reward
  - reward name
Report
  - Title
  - Description
Suggestion
  - like in the command
"""
class Verification(ui.Modal, title='Verification'):

    def __init__(self, client):
        super().__init__()
        self.client = client


    description = ui.TextInput(label='Description', placeholder="Describe your problem and we will try to help you :)", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # openticket returns None if user already has an open ticket
        ticketchannel = await openticket(self.client, interaction)
        if ticketchannel == None:
            await interaction.followup.send(f"{interaction.user.mention}\nYou can only open one ticket at a time!", ephemeral=True)
            return

        # Make an embed with the results
        em = discord.Embed(title="Verification", description=f"by {interaction.user}", colour=discord.Color.dark_teal())
        em.add_field(name="Description", value=self.description, inline=False)

        guild = await self.client.fetch_guild(598303095352459305)
        verificationrole = guild.get_role(598307062086107156) # CHANGED TO MODERATOR ROLE

        await setmodperms(interaction.user, ticketchannel, self.client, False)
        await setheadmodperms(interaction.user, ticketchannel, self.client, False)
        await setverifiedperms(interaction.user, ticketchannel, self.client, True)

        mention = verificationrole
        if TESTMODE == False:
            mention = verificationrole.mention

        msg = await ticketchannel.send(f"{interaction.user.mention}{mention}", embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))
        addid(msg.id, ticketchannel.id, interaction.user.id)
        await openTicketResponse(interaction, ticketchannel)
class Claim(ui.Modal, title='Claim a reward'):

    def __init__(self, client):
        super().__init__()
        self.client = client


    name = ui.TextInput(label='Name of the reward', placeholder="Put the prize you want to claim here")
    description = ui.TextInput(label='Description', placeholder="If you have something else to say", required=False, style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.defer()
        ticketchannel = await openticket(self.client, interaction)
        if ticketchannel == None:
            await interaction.followup.send(f"{interaction.user.mention}\nYou can only open one ticket at a time!", ephemeral=True)
            return

        # Make an embed with the results
        em = discord.Embed(title="Claim a reward", description=f"by {interaction.user}", colour=discord.Color.dark_teal())
        em.add_field(name="Name", value=self.name, inline=False)
        if str(self.description) != "":
            em.add_field(name="Description", value=self.description, inline=False)

        # Get Rocsie
        naughty = await self.client.fetch_user(497508029923852299)
        ing = await self.client.fetch_user(198218633955115008)
        mention = f"{naughty} {ing}"
        if TESTMODE == False:
            mention = f"{naughty.mention}{ing.mention}"

        await setmodperms(interaction.user, ticketchannel, self.client, False)
        await setheadmodperms(interaction.user, ticketchannel, self.client, False)

        msg = await ticketchannel.send(f"{interaction.user.mention}{mention}", embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))
        addid(msg.id, ticketchannel.id, interaction.user.id)

        await openTicketResponse(interaction, ticketchannel)
class Report(ui.Modal, title='Report'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    name = ui.TextInput(label='Title', placeholder="Title of your Report")
    description = ui.TextInput(label='Description', placeholder="Please put a detailed description here to make it easier for us :)", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ticketchannel = await openticket(self.client, interaction)
        if ticketchannel == None:
            await interaction.followup.send(f"{interaction.user.mention}\nYou can only open one ticket at a time!", ephemeral=True)
            return

        # Make an embed with the results
        em = discord.Embed(title="Report", description=f"by {interaction.user}", colour=discord.Color.dark_teal())
        em.add_field(name="Title", value=self.name, inline=False)
        em.add_field(name="Description", value=self.description, inline=False)


        guild = await self.client.fetch_guild(598303095352459305)
        modrole = guild.get_role(598307062086107156)
        headmodrole = guild.get_role(845280788001849345)

        mention = modrole
        mention2 = headmodrole
        if TESTMODE == False:
            mention = modrole.mention
            mention2 = headmodrole.mention

        await setmodperms(interaction.user, ticketchannel, self.client, True)
        await setheadmodperms(interaction.user, ticketchannel, self.client, True)

        msg = await ticketchannel.send(f"{interaction.user.mention}{mention}{mention2}", embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))
        addid(msg.id, ticketchannel.id, interaction.user.id)

        await openTicketResponse(interaction, ticketchannel)
class Other(ui.Modal, title='Other'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    name = ui.TextInput(label='Title', placeholder="I like trains")
    description = ui.TextInput(label='Description', placeholder="Please put a detailed description here to make it easier for us :)", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ticketchannel = await openticket(self.client, interaction)
        if ticketchannel == None:
            await interaction.followup.send(f"{interaction.user.mention}\nYou can only open one ticket at a time!", ephemeral=True)
            return

        # Make an embed with the results
        em = discord.Embed(title="Other", description=f"by {interaction.user}", colour=discord.Color.dark_teal())
        em.add_field(name="Title", value=self.name, inline=False)
        em.add_field(name="Description", value=self.description, inline=False)
        guild = await self.client.fetch_guild(598303095352459305)
        modrole = guild.get_role(598307062086107156)
        headmodrole = guild.get_role(845280788001849345)

        mention = modrole
        mention2 = headmodrole
        if TESTMODE == False:
            mention = modrole.mention
            mention2 = headmodrole.mention


        await setmodperms(interaction.user, ticketchannel, self.client, True)
        await setheadmodperms(interaction.user, ticketchannel, self.client, True)

        msg = await ticketchannel.send(f"{interaction.user.mention}{mention}{mention2}", embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))
        addid(msg.id, ticketchannel.id, interaction.user.id)
        await openTicketResponse(interaction, ticketchannel)

class Twitch(ui.Modal, title='Twitch Support'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    name = ui.TextInput(label='Twitch username', placeholder="Put your twitch username here")
    description = ui.TextInput(label='Description', placeholder="Please put a detailed description here to make it easier for us :)", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ticketchannel = await openticket(self.client, interaction)
        if ticketchannel == None:
            await interaction.followup.send(f"{interaction.user.mention}\nYou can only open one ticket at a time!", ephemeral=True)
            return

        # Make an embed with the results
        em = discord.Embed(title="Other", description=f"by {interaction.user}", colour=discord.Color.dark_teal())
        em.add_field(name="Twitch Username", value=self.name, inline=False)
        em.add_field(name="Description", value=self.description, inline=False)
        guild = await self.client.fetch_guild(598303095352459305)
        twitchmodrole = guild.get_role(841020059945009193)

        mention = twitchmodrole
        if TESTMODE == False:
            mention = twitchmodrole.mention


        await setmodperms(interaction.user, ticketchannel, self.client, False)
        await setheadmodperms(interaction.user, ticketchannel, self.client, False)
        await settwitchmodperms(interaction.user, ticketchannel, self.client, True)

        msg = await ticketchannel.send(f"{interaction.user.mention}{mention}", embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention, "twitch"))
        addid(msg.id, ticketchannel.id, interaction.user.id)
        await openTicketResponse(interaction, ticketchannel)

async def setup(client):
    await client.add_cog(support(client), guilds=guilds)