import random
import discord
from discord.ext import commands
from discord import Emoji

from cogs.other import FeedbackButtons
from cogs.streamsubmissions import QueueContentDropdownView, queuecontent_message_id
from cogs.support import DropdownView, support_message_id, getmsgids, CloseButtons, feedback_message_id
from config import token
from discord import app_commands
from config import guilds, guild

intents = discord.Intents.all()



client = commands.Bot(command_prefix=['lem ', 'Lem ', 'LEM ', 'LEm ', 'lEm ', 'lEM '], case_insensitive=True, intents=intents)
client.remove_command("help")
# Current permission integer 414501436481
# mit nickname 1514449271889



# Print a message in the console when he works properly
@client.event
async def on_ready():
    print('Where am I?')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="When life gives you lemons, make lemonade!"))
    #channel = client.get_channel(720069988324474971)
    #await channel.send("I am much better than this turtle <:Evilge:949646545832271934>")
    for g in guilds:
        await client.tree.sync(guild=g)
    """
    i = 0
    print(client.tree.get_commands(guild=guild))
    for command in client.tree.get_commands(guild=guild):
        print(command)
        i+=1
    print(i)
    """

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
    #await client.load_extension("cogs.googlesheets")
    await client.load_extension("cogs.Roles")
    await client.load_extension("cogs.streamsubmissions")
    await client.load_extension("cogs.prediction")
    client.add_view(DropdownView(client), message_id=support_message_id)
    client.add_view(QueueContentDropdownView(client), message_id=queuecontent_message_id)
    client.add_view(FeedbackButtons(client), message_id=feedback_message_id)
    guild = await client.fetch_guild(598303095352459305)
    for msg in getmsgids():
        msgid = msg["msg_id"]
        ticketchannel = await guild.fetch_channel(msg["ticketchannel_id"])
        opener = await guild.fetch_member(msg["opener_id"])
        client.add_view(CloseButtons(client=client, ticketchannel=ticketchannel, opener=opener), message_id=msgid)

    #channel = await client.fetch_channel(955476670352093204)
    #msg = await channel.fetch_message(971321595803082802)
    #em = discord.Embed(title="Ticket Support", colour=discord.Color.from_rgb(229, 196, 89))
    #em.add_field(name="\u200b", value="""🪙 **- Verification** If you have trouble seeing all channels after verifying yourself in <#1108741931518922862> you can open a ticket here.
#
#    🎁 **- Claim a reward** If you claimed a reward through <@881476780765093939>, please open a ticket to claim it.
#
#    ❗ **- Make a report** If you notice someone breaking the rules or you're negatively affected by someone's behavior, open a ticket to discuss it with our staff members.
#
#    📔 **- Other** If you have any other issue with the server, questions for the staff members, event ideas or suggestions you'd like to further discuss etc. feel free to open a ticket.
#
#    📥 **- Suggestions** This will open a form that will be sent to us to consider, however, this will not open a channel where we can discuss it, so make sure you include as much detail as you can (e.g. Emote name and a link we can download it from)""")
#
#    em.set_image(
#        url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
#    await msg.edit(embed=em)











client.run(token)