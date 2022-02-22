import discord
from discord.ext import commands

class help(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def money_help_msg(self, ctx):
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
        await ctx.send(embed=em)

    async def job_help_msg(self, ctx):
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
        await ctx.send(embed=em)

    async def item_help_msg(self, ctx):
        em = discord.Embed(
            title="How to use, view your items <:handbag:881564066924089365>",
            description="You can buy items from the shop `lem shop`",
            colour=discord.Color.from_rgb(254, 254, 51))
        em.add_field(name="bag", value="Have a look at your items", inline=False)
        em.add_field(name="use", value="Use a specific item", inline=False)
        em.add_field(name="collectibles", value="View all collectibles `lem collectibles *page*`", inline=False)
        em.add_field(name="collection", value="View all your collectibles", inline=False)
        em.add_field(name="vendingmachine", value="Get a random collectible. You can also suggest collectibles (if you have a better name for this command dm qBaumi)", inline=False)
        em.add_field(name="HallOfFame", value="To join the Hall of Fame, you need to collect **ALL** collectibles <:Gladge:792430592636616714>")
        em.set_footer(text="I know, this page is helpful")
        await ctx.send(embed=em)

    async def pet_help_msg(self, ctx):
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
        await ctx.send(embed=em)

    async def game_help_msg(self, ctx):
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
        await ctx.send(embed=em)


    async def misc_help_msg(self, ctx):
        em = discord.Embed(
            title="Things without a category",
            colour=discord.Color.from_rgb(254, 254, 51))
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
        await ctx.send(embed=em)

    async def loyalty_help_msg(self, ctx):
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

        await ctx.send(embed=em)

    async def help_msg(self, ctx):
        em = discord.Embed(
            title="Help <:question:881562906993508374>",
            description="To get help for a specific topic try `lem help money` for example",
            colour=discord.Color.from_rgb(254, 254, 51))
        em.add_field(
            name="Help Money",
            value="Everything with money, the basics and how to earn it(with jobs)",
            inline=False)
        em.add_field(
            name="Help Jobs",
            value="How you can earn money",
            inline=False)
        em.add_field(
            name="Help Items",
            value="How to buy and use items",
            inline=False)
        em.add_field(
            name="Help Pets",
            value="How to get and care for your cute pets",
            inline=False)
        em.add_field(
            name="Help Games",
            value="Play some Games 🎮",
            inline=False)
        em.add_field(
            name="Help Misc",
            value="I wonder whats that 🤔",
            inline=False)
        em.add_field(
            name="Help Loyalty",
            value="Check out how the Loyalty Points work",
            inline=False)
        em.add_field(
            name="Commands",
            value="Every command that the average chad can access",
            inline=False)
        em.set_footer(text="If you still need help ask qBaumi#1247")
        await ctx.send(embed=em)
        await ctx.send(f"{ctx.author.mention}\n**Now you can use** `lem help games` **for example!!!**")

    @commands.command()
    async def help(self, ctx, topic="help"):
        topic = topic.lower()

        if topic in ["money", "economy"]:
            await self.money_help_msg(ctx)
        elif topic in ["job", "jobs"]:
            await self.job_help_msg(ctx)
        elif topic in ["item", "items"]:
            await self.item_help_msg(ctx)
        elif topic in ["pets", "pet"]:
            await self.pet_help_msg(ctx)
        elif topic in ["games", "game"]:
            await self.game_help_msg(ctx)
        elif topic in ["misc", "miscellanous"]:
            await self.misc_help_msg(ctx)
        elif topic in ["loyalty", "loyal"]:
            await self.loyalty_help_msg(ctx)

        elif topic in ["all", "allcommands", "commands"]:
            await self.allcommands_msg(ctx)
        else:
            await self.help_msg(ctx)

    @commands.command()
    async def commands(self, ctx):
        await self.allcommands_msg(ctx)

    async def allcommands_msg(self, ctx):

        em = discord.Embed(
            title="All commands",
            description="All commands the average chad needs!",
            colour=discord.Color.from_rgb(254, 254, 51))
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
            name="steal",
            value="Or you can go and steal money from someone *hehehe*... `lem steal @victim`",
            inline=False)
        em.add_field(
            name="daily",
            value="If you are too lazy for that, you can still get your daily 10 lemons",
            inline=False)
        em.add_field(
            name="leaderboard",
            value="Check out the top 10 richest lemon billionaires",
            inline=False)
        em.add_field(
            name="pay",
            value="Pay someone some money. `lem pay @person 69`",
            inline=False)
        em.add_field(
            name='job info',
            value='Look up your current job!',
            inline=False)
        em.add_field(
            name='job list',
            value='List every job!',
            inline=False)
        em.add_field(
            name='job select',
            value='Select a job that is in the list!',
            inline=False)
        em.add_field(
            name='lem work',
            value='Work, work, work, work...',
            inline=False)
        em.add_field(name="bag", value="Have a look at your items", inline=False)
        em.add_field(name="use", value="Use a specific item", inline=False)
        em.add_field(name="collectibles", value="View all collectibles `lem collectibles *page*`", inline=False)
        em.add_field(name="collection", value="View all your collectibles", inline=False)
        em.add_field(name="vendingmachine",
                     value="Get a random collectible. You can also suggest collectibles (if you have a better name for this command dm qBaumi)",
                     inline=False)
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

        page2 = discord.Embed(
            title="Page 2",
            colour=discord.Color.from_rgb(254, 254, 51))

        page2.add_field(
            name="profile",
            value="Look up your Loyalty Points",
            inline=False)
        page2.add_field(
            name="loyalty",
            value="See who has the most Loyalty Points!",
            inline=False)
        await ctx.send(embed=em)
        await ctx.send(embed=page2)
def setup(client):
    client.add_cog(help(client))