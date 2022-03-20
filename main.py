import random
import discord
from discord.ext import commands
from discord import Emoji
from config import token
from discord import app_commands
from config import guilds

intents = discord.Intents.all()



client = commands.Bot(command_prefix=['lem ', 'Lem ', 'LEM ', 'LEm ', 'lEm ', 'lEM '], case_insensitive=True, intents=intents)
client.remove_command("help")
# Current permission integer 414501436481



# Print a message in the console when he works properly
@client.event
async def on_ready():
    print('Where am I?')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="When life gives you lemons, make lemonade!"))
    #channel = client.get_channel(720069988324474971)
    #await channel.send("I am much better than this turtle <:Evilge:949646545832271934>")
    for g in guilds:
        await client.tree.sync(guild=g)


#client.load_extension("cogs.googlesheets")

@client.event
async def setup_hook():
    await client.load_extension("cogs.admincommands")
    await client.load_extension("cogs.collectibles")
    await client.load_extension("cogs.economy")
    await client.load_extension("cogs.events")
    await client.load_extension("cogs.games")
    await client.load_extension("cogs.help")
    await client.load_extension("cogs.items")
    await client.load_extension("cogs.job")
    await client.load_extension("cogs.LeagueAPI")
    await client.load_extension("cogs.pet")
    await client.load_extension("cogs.other")
    await client.load_extension("cogs.loyalty")
    await client.load_extension("cogs.work")
    await client.load_extension("cogs.support")













client.run(token)