import random
import discord
from discord.ext import commands
from discord import Emoji
from config import token

intents = discord.Intents.default()
intents.message_content = True



client = commands.Bot(command_prefix=['lem ', 'Lem ', 'LEM ', 'LEm ', 'lEm ', 'lEM '], case_insensitive=True, intents=intents)
client.remove_command("help")
# Current permission integer 414501436481

guild = discord.Object(id=598303095352459305)


# Print a message in the console when he works properly
@client.event
async def on_ready():
    print('Where am I?')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="When life gives you lemons, make lemonade!"))
    #channel = client.get_channel(720069988324474971)
    #await channel.send("I am much better than this turtle <:Evilge:949646545832271934>")
    await client.tree.sync(guild=guild)

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


from discord.app_commands import Choice
@app_commands.describe(game='fruits to choose from')
@app_commands.choices(fruits=[
    Choice(name='Watch Together', value=880218394199220334),
    Choice(name='Poker Night', value=755827207812677713),
    Choice(name='Betrayal.io', value=773336526917861400),
    Choice(name='Fishington.io', value=814288819477020702),
    Choice(name='Chess In The Park', value=832012774040141894),
    Choice(name='Sketchy Artist', value=879864070101172255),
    Choice(name='Awkword', value=879863881349087252),
    Choice(name='Doodle Crew', value=878067389634314250),
    Choice(name='Sketch Heads', value=902271654783242291),
    Choice(name='Letter League', value=879863686565621790),
    Choice(name='Word Snacks', value=879863976006127627),
    Choice(name='SpellCast', value=852509694341283871),
    Choice(name='Checkers In The Park', value=832013003968348200),
    Choice(name='Blazing 8s', value=832025144389533716),
    Choice(name='Putt Party', value=945737671223947305)
])
@client.tree.command(guild=guild, name="game", description="Start a discord voice channel activity!")
async def game(interaction : discord.Interaction, game: Choice[int]):
    invite = await interaction.user.voice.channel.create_invite(
        target_application_id=891001866073296967,
        target_type=discord.InviteTarget.embedded_application
    )
    print(invite)
    await interaction.response.send_message(invite)






client.run(token)