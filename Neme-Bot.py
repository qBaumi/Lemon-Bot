import random
import discord
from discord.ext import commands
from discord import Emoji

# Setup the clinet with the prefix and case_insensitive (write BiG or smAll commands) and remove the default help command to make a custom one
client = commands.Bot(command_prefix=['lem ', 'Lem ', 'LEM ', 'LEm ', 'lEm ', 'lEM '], case_insensitive=True)
client.remove_command("help")
# Current permission integer 173949705280
# NEW ONE WITH MANAGE MESSAGES 414534990912


# Print a message in the console when he works properly
@client.event
async def on_ready():
    print('Where am I?')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="When life gives you lemons, make lemonade!"))


client.load_extension("cogs.admincommands")
client.load_extension("cogs.collectibles")
client.load_extension("cogs.economy")
client.load_extension("cogs.events")
client.load_extension("cogs.games")
client.load_extension("cogs.help")
client.load_extension("cogs.items")
client.load_extension("cogs.jobs")
client.load_extension("cogs.LeagueAPI")
client.load_extension("cogs.pets")
client.load_extension("cogs.other")
client.load_extension("cogs.loyalty")
#client.load_extension("cogs.googlesheets")


# About section
@client.command()
async def about(ctx):
    em = discord.Embed(title="About me", description="Thanks to all the people that helped me making this bot!")
    em.add_field(name="Creator / Developer", value="qBaumi#1247", inline=False)
    em.add_field(name="Developer", value="Menxs#0592", inline=False)
    em.add_field(name="Artist", value="https://twitter.com/lilRoundabout/", inline=False)
    em.add_field(name="Description", value=f"Hello, I am the Lemon Bot. \n Let me introduce real quick.\nI am an economy bot for the Nemesis discord server. I can get you precious lemons, if you get some work done for me...of course\nYou can find out more about me when you type **lem help** for example. But only in bot-commands, otherwise my boss will get angry...\nIf you have ANY ideas for items or commands, please share them with my Boss, you will find him at the beginning of this message.\n Thank you to all who helped creating me!", inline=False)
    await ctx.send(embed=em)

@client.command(pass_context=True)
async def debug(ctx, emoji: Emoji):
    embed = discord.Embed(description=f"<:{repr(emoji.name)}:{repr(emoji.id)}>", title=f"emoji: {emoji}")
    embed.add_field(name="id", value=repr(emoji.id))
    embed.add_field(name="name", value=repr(emoji.name))
    await ctx.send(embed=embed)



@client.command()
async def hug(ctx, user):
    hugs = ["<:nemeHug:834605591846584391>", "<:nemeHugBack:834971356873490462>", "<:nemeportalhug1:835504785285316648>", "<:nemeportalhug2:835504785586257939>", "<:wideHug1:834605591393206323><:widehug2:835116553812967444><:wideHug3:834605592022220860>", "<:dankHug:832245187614212106>"]
    hug =random.choice(hugs)
    await ctx.send(f"{ctx.author.mention} gave {user} a hug")
    await ctx.send(hug)







with open('token.txt', 'r') as file:
    token = file.read()
client.run(token)