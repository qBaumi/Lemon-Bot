import asyncio
import datetime
import random
import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice
import cogs.essentialfunctions as es

class other(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logchannel = None


    @commands.Cog.listener()
    async def on_ready(self):
        self.logchannel = await self.client.fetch_channel(967113937634078771)

    @app_commands.command(name="suggest", description="Suggest an emote or something else!")
    async def suggest(self, interaction: discord.Interaction):
        modal = Suggestion(client=self.client)
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


    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.type) == "voice" and self.logchannel:
            em = discord.Embed()
            em.set_author(name=message.author.name, icon_url=message.author.avatar)
            em.add_field(name=message.channel.name, value=message.content)
            await self.logchannel.send(embed=em)

            badwords = ["fag", "farggot", "nigger", "nazi", "cancer", "autist", "retard", "jew", "mentally challenged", "suicide", "kill myself", "kill yourself", "autistic", "kys", "kms", "dick", "cock", "porn", "slut", "niglet", "negro", "dyke", "whore", "chink", "nibba", "braindead", "autism", "nigglet", "beaner", "child-fucker", "motherfucker", "twat", "bellend", "arschgesicht", "rape", "cocknose", "anal", "nonce", "depression", "rape", "rapist", "aids", "nigga", "pedo", "subhuman", "kike", "kyke", "nignog", "cao ni ma", "ape"]
            if any(word in message.content.lower() for word in badwords):
                modchannel = await self.client.fetch_channel(963720915575779358)
                em = discord.Embed(title="Warning", description=f"<#967113937634078771> for more information")
                em.add_field(name=message.author.name, value=message.content)
                await modchannel.send(embed=em)



    class Prediction(ui.Modal, title="MSI Pick'ems 2022"):

        def __init__(self, client):
            super().__init__()
            self.client = client


        email = ui.TextInput(label='Email Adress', placeholder="Put your email adress here to access the Google Sheet later")

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.send_message(f'You can soon access the prediction sheet!', ephemeral=True, view=SheetLink())

            # 656636484937449518 this is the suggestion-log channel
            # 651364619402739713 this is the test channel
            # 820728066514354206 prediction sheet
            channel_id = 820728066514354206  # the id of the channel the results get sent to
            channel = await self.client.fetch_channel(channel_id)

            # Make an embed with the results
            em = discord.Embed(title="LEC Spring Split Playoffs 2022", description=f"by {interaction.user.mention}")
            em.add_field(name="Email", value=self.email)

            await channel.send(embed=em)



    @app_commands.command(name="msi", description="Sign up for the Prediction Sheet!")
    async def msi(self, interaction: discord.Interaction):
        modal = self.Prediction(client=self.client)
        await interaction.response.send_modal(modal)


class SheetLink(discord.ui.View):
    def __init__(self):
        super().__init__()

        url = "https://docs.google.com/spreadsheets/d/1SsnIXuAFAUWcs97ccKotfmurvuUNnHhdf-Jg7i1Bu58/edit?usp=sharing"

        self.add_item(discord.ui.Button(label='Prediction Sheet', url=url))
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

async def setup(client):
    await client.add_cog(other(client), guilds=guilds)