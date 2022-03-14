import datetime

import discord, json
from discord.ext import commands
import cogs.essentialfunctions as es
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice


class other(commands.Cog):
    def __init__(self, client):
        self.client = client


    # Hall of Fame for all people who collect all collectibles
    @app_commands.command(description="Have a look at legends", name="halloffame")
    async def halloffame(self, interaction: discord.Interaction):
        with open("./json/halloffame.json", "r") as f:
            users = json.load(f)
        em = discord.Embed(colour=discord.Color.dark_purple(), title="Hall of Fame",
                           description="only true and loyal legends get there...")
        # Fetch every user that is in the halloffame and add them to the embed
        for userid in users:
            user = await self.client.fetch_user(userid)
            em.add_field(name=user.name, value="\u200b", inline=False)
        await interaction.response.send_message(embed=em)

    """
    Present 100 golden lemons for christmas
    ARCHIVED
    
    @commands.command()
    async def present(self, ctx):
        with open("./json/present.json", "r") as f:
            users = json.load(f)
        if ctx.author.id in users:
            await ctx.send("You already claimed your present!")
            return
        date = datetime.date.today()
        date = str(date)
        print(date)
        if (date != "2021-12-25"):
            await ctx.send("No gift to claim <:Sadge:720250426892615745>\nSanta Veigar arrives at the **25. December** 2021 in the early morning!")
            return
        await es.update_balance(ctx.author, 100, "safe")
        users.append(ctx.author.id)
        with open("./json/present.json", "w") as f:
            json.dump(users, f)
        em = discord.Embed(title="Merry Christmas", description="You claimed your 100 golden lemons!")
        await ctx.send(f"{ctx.author.mention}\n", embed=em)
    """
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == message.author.bot:
            return
        if message.author.id == 881476780765093939:
            return
        message.content = message.content.lower()
        if " fair enough" in message.content or message.content.startswith("fair enough"):
            await message.reply("*fer enough")
            return
        if " fair" in message.content or message.content.startswith("fair"):
            await message.reply("~~fair~~\n*fer")
            return

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

            channel_id = 651364619402739713  # the id of the channel the results get sent to
            channel = await self.client.fetch_channel(channel_id)

            # Make an embed with the results
            em = discord.Embed(title="Suggestion", description=f"by {interaction.user}")
            em.add_field(name=self.name, value=self.desc)

            await channel.send(embed=em)

    @app_commands.command(name="suggest", description="Suggest an emote or something else!")
    async def suggest(self, interaction: discord.Interaction):
        modal = self.Suggestion(client=self.client)
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
        Choice(name='Putt Party', value="945737671223947305")
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


async def setup(client):
    await client.add_cog(other(client), guilds=guilds)