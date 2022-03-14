import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import enum
from typing import Literal
from config import guilds


async def money_help_msg():
    em = discord.Embed(
        title="Help to the economy system <:coin:881559702033535067>",
        description="You can earn money through various commands, but most important is the difference between lemons and golden lemons. You use lemons to buy normal items in the shop and golden lemons are the more precious ones which you can earn through events",
        colour=discord.Color.from_rgb(254, 254, 51))
    em.add_field(
        name="startup",
        value="Use this command first to get a quick introduction",
        inline=False)
    em.add_field(
        name="lemons",
        value="View how much lemons you got in your pocket and golden lemons in your safe",
        inline=False)
    em.add_field(
        name="shop",
        value="Take a look at the shop!",
        inline=False)
    em.add_field(
        name="buy | sell",
        value="Buy items or sell them, but for just half the price",
        inline=False)
    em.add_field(
        name="jobs",
        value="To earn money you need to get a job, for more information use `lem job help`",
        inline=False)
    em.add_field(
        name="jobs",
        value="Or you can go and steal money from someone *hehehe*... `lem steal @victim`",
        inline=False)
    em.add_field(
        name="daily",
        value="If you are too lazy for that, you can still get your daily 20 lemons",
        inline=False)
    em.add_field(
        name="leaderboard",
        value="Check out the top 10 richest lemon billionaires",
        inline=False)
    em.add_field(
        name="pay",
        value="Pay someone some money. `lem pay @person 69`",
        inline=False)
    return em


async def job_help_msg():
    em = discord.Embed(
        title='Help for the job command:',
        description="First use `lem job list` to take a look which jobs you can appeal for, then you can select them with `lem job select lemon farmer` for example. After that you can work with `lem work` and complete several tasks",
        colour=discord.Color.from_rgb(254, 254, 51))
    em.add_field(
        name='Job info',
        value='Look up your current job!',
        inline=False)
    em.add_field(
        name='Job list',
        value='List every job!',
        inline=False)
    em.add_field(
        name='Job select',
        value='Select a job that is in the list!',
        inline=False)
    em.add_field(
        name='lem work',
        value='Work, work, work, work...',
        inline=False)
    em.set_footer(text='Send job ideas to @qBaumi#1247!')
    return em


async def item_help_msg():
    em = discord.Embed(
        title="How to use, view your items <:handbag:881564066924089365>",
        description="You can buy items from the shop `lem shop`",
        colour=discord.Color.from_rgb(254, 254, 51))
    em.add_field(name="bag", value="Have a look at your items", inline=False)
    em.add_field(name="use", value="Use a specific item", inline=False)
    em.add_field(name="collectibles", value="View all collectibles `lem collectibles *page*`", inline=False)
    em.add_field(name="collection", value="View all your collectibles", inline=False)
    em.add_field(name="vendingmachine",
                 value="Get a random collectible. You can also suggest collectibles (if you have a better name for this command dm qBaumi)",
                 inline=False)
    em.add_field(name="HallOfFame",
                 value="To join the Hall of Fame, you need to collect **ALL** collectibles <:Gladge:792430592636616714>")
    em.set_footer(text="I know, this page is helpful")
    return em


async def pet_help_msg():
    em = discord.Embed(title="Pets", colour=discord.Color.from_rgb(254, 254, 51),
                       description="You can buy a pet from the `lem pet shop` and look and care for your equipped pet with `lem pet info`. You can have a maximum of 4 pets. You can buy them as adults and babys, an adult is the maximum level but has not that good stats as the same pet leveled up from a baby to the maximum level!")
    em.add_field(name="pet shop", value="Look which pets are currently available!", inline=False)
    em.add_field(name="pet adopt | pet buy", value="Adopt a pet from the shop", inline=False)
    em.add_field(name="pet sell", value="Sadge", inline=False)
    em.add_field(name="pet info", value="Have a look at your equipped pet's stats!", inline=False)
    em.add_field(name="pet feed | pet care | pet play",
                 value="You can also use them with `lem pet info` and then react to the emojis!", inline=False)
    em.add_field(name="pet pat", value="Gladge", inline=False)
    em.add_field(name="pet walk", value="Walk your pet, it needs to go to the toilet as well", inline=False)
    em.add_field(name="pet equip | pet unequip",
                 value="Equip a pet from a different slot | Unequip a pet to buy another one", inline=False)
    em.add_field(name="pet pets", value="View all your pets", inline=False)
    em.add_field(name="pet fight", value="COMING SOON!!!", inline=False)
    return em


async def game_help_msg():
    em = discord.Embed(
        title="Yes, there are games! Not much, but enought",
        description="Which champions has the voiceline of the second sentence in the title? You get 10 lemons if you tell it qBaumi",
        colour=discord.Color.from_rgb(254, 254, 51))
    em.add_field(
        name="tictactoe",
        value="`lem tictactoe @friend 10` (10 is the amount of lemons you play against)",
        inline=False)
    em.add_field(
        name="lottery",
        value="Set a bet and play the lottery! `lem lottery 10`",
        inline=False)
    em.add_field(
        name="roulette",
        value="More Gamba! `lem roulette 10`",
        inline=False)
    em.add_field(
        name="wouldyourather",
        value="Answer a would you rather question!",
        inline=False)
    em.add_field(
        name="minesweeper 💥",
        value="Our favourite Microsoft Game!",
        inline=False)
    em.add_field(
        name="wordle",
        value="try it out!",
        inline=False)
    em.add_field(
        name="wordleaderboard",
        value="A leaderboard for the master minds of Wordle",
        inline=False)
    return em


async def misc_help_msg():
    em = discord.Embed(
        title="Things without a category",
        colour=discord.Color.from_rgb(254, 254, 51))
    em.add_field(
        name="suggest",
        value="Suggest an emoji or something else",
        inline=False)
    em.add_field(
        name="about",
        value="Just try it",
        inline=False)
    em.add_field(
        name="rank",
        value="Get the rank stats for a summoner in EUW or NA `lem rank <summonername>` or `lem rankNA <summonername>`",
        inline=False)
    em.add_field(
        name="hug",
        value="<:nemeHug:834605591846584391> `lem hug @ingrioo`",
        inline=False)
    return em


async def loyalty_help_msg():
    em = discord.Embed(
        title="Loyalty",
        colour=discord.Color.from_rgb(254, 254, 51),
        description="You earn Loyalty Points from events and at the end of the year, the person with the most points gets a custom color role!")
    em.add_field(
        name="profile",
        value="Look up your Loyalty Points",
        inline=False)
    em.add_field(
        name="loyalty",
        value="See who has the most Loyalty Points!",
        inline=False)

    return em

async def golden_lemon_help_msg():
    em = discord.Embed(
        title="Golden Lemons",
        colour=discord.Color.from_rgb(254, 254, 51),
        description="You can earn Golden Lemons <:GoldenLemon:882634893039923290> through events. You can trade them for prizes, read on for more.")
    em.add_field(
        name="`lem balance`",
        value="First you can look up how many Golden Lemons you have with this command.",
        inline=False)
    em.add_field(
        name="`lem shop`",
        value="Now you look up what prizes there are and how much they cost in the shop. **Just react with the Golden Lemon Emoji to switch to the prize shop**\nThe normal shop consist just out of ingame-items!",
        inline=False)
    em.add_field(
        name="`lem buy prizename`",
        value="If you have enough Golden Lemons, you can now buy a prize from the shop. To check your items try `lem bag`",
        inline=False)
    em.add_field(
        name="Message Rocsie",
        value="**To redeem your prize please make sure to message Rocsie!**",
        inline=False)
    em.set_footer(text="Don't be afraid to @ a Mod if you need help to redeem your prize.")


    return em

async def help_msg(client):
    em = discord.Embed(
        title="Help <:question:881562906993508374>",
        description="Frequently asked questions",
        colour=discord.Color.from_rgb(254, 254, 51))
    em.add_field(
        name="IMPORTANT NOTE!!!",
        value="The bot is currently transferring to slash commands, all commands that have something to do with money are normal commands and you can access them via `lem ` and then the command name. This is because I am currently not able to use features like cooldowns yet, but I hope it will be added soon to the library.",
        inline=False)
    em.add_field(
        name="What is the bot about",
        value="The bot is mainly an economy bot themed around Nemesis. You can earn money, buy items and pets, play games, gamble, and much more.",
        inline=False)
    em.add_field(
        name="What commands are there",
        value="As mentioned there are a lot of features and you can look all the commands up with `/help`",
        inline=False)
    em.add_field(
        name="I encountered an error",
        value="If the bot does something weird, doesn't work don't be afraid to @qBaumi",
        inline=False)
    em.add_field(
        name="I can't find what I am looking for",
        value="Just @qBaumi",
        inline=False)
    em.set_thumbnail(url=client.user.avatar.url)
    return em

class help(commands.Cog):
    def __init__(self, client):
        self.client = client



    @app_commands.command(description="Get some help", name="help")
    async def help(self, interaction: discord.Interaction):



        # Custom Help Command with Select View

        # Class for initializing the Dropdown menu, we can edit the default options later
        class Dropdown(discord.ui.Select):
            def __init__(self):
                # Set the options that will be presented inside the dropdown
                options = [
                    discord.SelectOption(label='FAQ', description='Fundamentals for the bot', emoji='❔', default=True),
                    discord.SelectOption(label='Economy',
                                         description='Everything with money, the basics and how to earn it(with jobs)',
                                         emoji='🪙'),
                    discord.SelectOption(label='Golden Lemons', description='How to get and spend Golden Lemons', emoji='<:GoldenLemon:882634893039923290>'),
                    discord.SelectOption(label='Jobs', description='You ofcourse need a job to get money', emoji='💰'),
                    discord.SelectOption(label='Pets', description='How to get and care for your cute pets',
                                         emoji='🐕'),
                    discord.SelectOption(label='Games', description='Play some Games', emoji='🎮'),
                    discord.SelectOption(label='Items', description='How to buy and use items', emoji='🎒'),
                    discord.SelectOption(label='Loyalty', description='Check out how the Loyalty Points work',
                                         emoji='🟠'),
                    discord.SelectOption(label='Miscellaneous', description='Check out how the Loyalty Points work',
                                         emoji='📜')
                ]
                # Default means it will be shown down in the select menu
                # The placeholder is what will be shown when no option is chosen
                # The min and max values indicate we can only pick one of the three options
                # The options parameter defines the dropdown options. We defined this above
                super().__init__(placeholder='Category', min_values=1, max_values=1,
                                 options=options)


            # Callback will be called every time the user changes the selection
            # self equals the Dropdown class, a discord.ui.Select type
            async def callback(self, interaction: discord.Interaction):

                # we can get the values of the selection, cause self is the dropdown class and it has the attribute values
                category = self.values[0]

                # We set all the options to false because we later change one of them to true when the user makes an input
                for option in self.options:
                    option.default = False

                # Now the embed will be changed depending on the value of the selection
                # Also we set the option to True so it will be shown down in the select menu and not be empty again
                if category == "Economy":
                    em = await money_help_msg()
                    self.options[1].default = True
                elif category == "Golden Lemons":
                    em = await golden_lemon_help_msg()
                    self.options[2].default = True
                elif category == "Jobs":
                    em = await job_help_msg()
                    self.options[3].default = True
                elif category == "Pets":
                    em = await pet_help_msg()
                    self.options[4].default = True
                elif category == "Games":
                    em = await game_help_msg()
                    self.options[5].default = True
                elif category == "Items":
                    em = await item_help_msg()
                    self.options[6].default = True
                elif category == "Loyalty":
                    em = await loyalty_help_msg()
                    self.options[7].default = True
                elif category == "Miscellaneous":
                    em = await misc_help_msg()
                    self.options[8].default = True
                else:
                    em = await help_msg(self.client)
                    self.options[0].default = True

                # Now we edit the message and put the new embed in
                # We also change the view by initializing a new class, the same as the Dropdown class, because we can't
                # take the super class of Dropdown() which is self and edit the view right there
                await interaction.response.edit_message(embed=em, view=EditedDropdownView(self))

        class DropdownView(discord.ui.View):
            def __init__(self):
                # Pass the timeout in the initilization of the super class
                super().__init__(timeout=300)

                # Adds the dropdown to our view object.
                self.add_item(Dropdown())

            async def on_timeout(self):
                # Set every component on disabled
                for child in self.children:  # We need to iterate over all the buttons/selects in the View (self.children returns a list of all the Items in the View)
                    child.disabled = True  # And set disabled = True to disable them

                # Update the message
                await self.message.edit(
                    view=self)  # Now we just need to update our old message with the updated buttons

        # This class is for making a new view, so we can initialize the old menu with the dropdown() class and put it as parameter
        class EditedDropdownView(discord.ui.View):
            def __init__(self, dropdown):
                super().__init__()

                # Adds the dropdown to our view object.
                self.add_item(dropdown)

        # this is for the default message
        view = DropdownView()
        await interaction.response.send_message(embed=await help_msg(self.client), view=view)
        # interaction.response.send_message() returns None, that is why we have to fetch the message first and then set the message attribute
        view.message = await interaction.original_message()

async def setup(client):
    await client.add_cog(help(client), guilds=guilds)
