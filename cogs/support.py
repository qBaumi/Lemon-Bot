import datetime
import math
import random
import time

import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice
from .other import Suggestion
import chat_exporter
import io

channel_id = 651364619402739713  # test channel
support_category_id = 955151615252385854
openmessage = "{} @ Rocsie @ Head Mods"

class support(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @commands.command(name="permsupport", description="Permanent message for support channel, admincommand")
    async def permsupport(self, ctx):
        await ctx.send(view=DropdownView(self.client))

class DropdownView(discord.ui.View):
    def __init__(self, client):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=300)

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(client))

"""
Verification
  - description
Claim reward
  - reward name
Report a user
  - User name
  - Description
Suggestion
  - like in the command
"""

class Dropdown(discord.ui.Select):
    def __init__(self, client):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Verification', description='Get support for the Verification', emoji='❔'),
            discord.SelectOption(label='Claim a reward', description='Claim a reward you won', emoji='❔'),
            discord.SelectOption(label='Make a Report', description='Report one or multiple users', emoji='❔'),
            discord.SelectOption(label='Other', description='Open a ticket with staff members', emoji='❔'),
            discord.SelectOption(label='Suggestion', description='Suggest and emote or something else', emoji='❔'),

        ]

        super().__init__(placeholder='Open a Ticket', min_values=1, max_values=1,
                         options=options)
        self.client = client

    async def callback(self, interaction: discord.Interaction):

        # we can get the values of the selection, cause self is the dropdown class and it has the attribute values
        category = self.values[0]

        # Now the embed will be changed depending on the value of the selection
        # Also we set the option to True so it will be shown down in the select menu and not be empty again
        if category == "Verification":
            modal = Verification(self.client)
        elif category == "Claim a reward":
            modal = Claim(self.client)
        elif category == "Make a Report":
            modal = Report(self.client)
        elif category == "Suggestion":
            modal = Suggestion(self.client)
        else: # this is for category other
            modal = Other(self.client)


        await interaction.response.send_modal(modal)

class GetToChannelButton(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__()

        url = f"https://discord.com/channels/598303095352459305/{channel_id}/"

        self.add_item(discord.ui.Button(label='Ticket Channel', url=url))


class CloseButtons(discord.ui.View):

    def __init__(self, client, ticketchannel, opener):
        super().__init__()
        self.client = client
        self.ticketchannel = ticketchannel
        self.opener = opener



    @discord.ui.button(label='Close', style=discord.ButtonStyle.red)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        resultschannel = await self.client.fetch_channel(channel_id)
        await archive(self.ticketchannel, resultschannel, self.client, self.opener, interaction.user.mention)

        await interaction.response.send_message("Ticket closed", ephemeral=True)
        time.sleep(5)
        await self.ticketchannel.delete()

    @discord.ui.button(label='Close with Reason', style=discord.ButtonStyle.red)
    async def closewithreason(self, button: discord.ui.Button, interaction: discord.Interaction):

        modal = CloseWithReason(client=self.client, ticketchannel=self.ticketchannel, opener=self.opener)
        await interaction.response.send_modal(modal)




class Verification(ui.Modal, title='Verification'):

    def __init__(self, client):
        super().__init__()
        self.client = client


    description = ui.TextInput(label='Description', placeholder="Describe your problem and we will try to help you :)")

    async def on_submit(self, interaction: discord.Interaction):

        ticketchannel = await openticket(self.client, interaction)

        # Make an embed with the results
        em = discord.Embed(title="Verification", description=f"by {interaction.user.mention}")
        em.add_field(name="Description", value=self.description, inline=False)

        await ticketchannel.send(openmessage.format(interaction.user.mention), embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))

        await interaction.response.send_message(f'Click on the button to get to your ticket channel!', ephemeral=True, view=GetToChannelButton(ticketchannel.id))

async def openticket(client, interaction):
    category = await client.fetch_channel(support_category_id)
    guild = await client.fetch_guild(598303095352459305)
    ticketchannel = await guild.create_text_channel(f'ticket-{interaction.user}', category=category)
    return ticketchannel

class Claim(ui.Modal, title='Claim a reward'):

    def __init__(self, client):
        super().__init__()
        self.client = client


    name = ui.TextInput(label='Name of the reward', placeholder="Put the prize you want to claim here")
    description = ui.TextInput(label='Description', placeholder="If you have something else to say", required=False)

    async def on_submit(self, interaction: discord.Interaction):

        ticketchannel = await openticket(self.client, interaction)

        # Make an embed with the results
        em = discord.Embed(title="Claim a reward", description=f"by {interaction.user.mention}")
        em.add_field(name="Name", value=self.name, inline=False)
        if str(self.description) != "":
            em.add_field(name="Description", value=self.description, inline=False)

        await ticketchannel.send(openmessage.format(interaction.user.mention), embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))

        await interaction.response.send_message(f'Click on the button to get to your ticket channel!', ephemeral=True, view=GetToChannelButton(ticketchannel.id))


class Report(ui.Modal, title='Report'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    name = ui.TextInput(label='Title', placeholder="Title of your Report")
    description = ui.TextInput(label='Description', placeholder="Please put a detailed description here to make it easier for us :)")

    async def on_submit(self, interaction: discord.Interaction):

        ticketchannel = await openticket(self.client, interaction)

        # Make an embed with the results
        em = discord.Embed(title="Report", description=f"by {interaction.user.mention}")
        em.add_field(name="Title", value=self.name, inline=False)
        em.add_field(name="Description", value=self.description, inline=False)

        await ticketchannel.send(openmessage.format(interaction.user.mention), embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))
        await interaction.response.send_message(f'Click on the button to get to your ticket channel!', ephemeral=True, view=GetToChannelButton(ticketchannel.id))

class Other(ui.Modal, title='Other'):

    def __init__(self, client):
        super().__init__()
        self.client = client

    name = ui.TextInput(label='Title', placeholder="I like trains")
    description = ui.TextInput(label='Description', placeholder="Please put a detailed description here to make it easier for us :)")

    async def on_submit(self, interaction: discord.Interaction):

        ticketchannel = await openticket(self.client, interaction)


        # Make an embed with the results
        em = discord.Embed(title="Other", description=f"by {interaction.user.mention}")
        em.add_field(name="Title", value=self.name, inline=False)
        em.add_field(name="Description", value=self.description, inline=False)

        await ticketchannel.send(openmessage.format(interaction.user.mention), embed=em, view=CloseButtons(self.client, ticketchannel, interaction.user.mention))
        await interaction.response.send_message(f'Click on the button to get to your ticket channel!', ephemeral=True, view=GetToChannelButton(ticketchannel.id))

class CloseWithReason(ui.Modal, title='Close Ticket with Reason'):

    def __init__(self, client, ticketchannel, opener):
        super().__init__()
        self.client = client
        self.ticketchannel = ticketchannel
        self.opener = opener
    reason = ui.TextInput(label='Reason', placeholder="Sara, hello, didnt ask + ratio")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Closed Ticket with reason {self.reason}', ephemeral=True)

        resultschannel = await self.client.fetch_channel(channel_id)
        await archive(self.ticketchannel, resultschannel, self.client, self.opener,interaction.user.mention,str(self.reason))
        time.sleep(5)
        await self.ticketchannel.delete()
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

        await archive_channel.send(embed=em, view=ticketlinkbutton(url=message.attachments[0].url))

class ticketlinkbutton(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label='Archive', url=url))


async def setup(client):
    await client.add_cog(support(client), guilds=guilds)