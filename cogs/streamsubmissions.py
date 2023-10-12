import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui

from config import guilds
from discord.app_commands import Choice


staffqueuecheck_channel_id = 1158016066543427724
queuecontent_message_id = 1158033761955491881 # message in #stream-submissions
food_thread_id = 1160542693714305035
setups_thread_id = 1160542675796230228

class streamsubmissions(commands.Cog):
    def __init__(self, client):
        self.client = client





    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @commands.command(name="queuecontentthread", description="Permanent message for queue content thread channel, admincommand")
    async def queuecontentthread(self, ctx):
        em = discord.Embed(colour=discord.Color.from_rgb(229, 196, 89))
        em.set_image(
            url="https://cdn.discordapp.com/attachments/651364619402739713/1158035904519229530/streamcontentsmile.png?ex=652bebfa&is=651976fa&hm=53d5f95edce450346e2a52121a7e1f708bb8ad8c35e02f318e70104e420a3ec9&")
        await ctx.send(embed=em)
        em = discord.Embed(title="Nemesis Twitch Stream Submissions!", colour=discord.Color.from_rgb(229, 196, 89))
        em.add_field(name="\u200b", value="""Here you can find approved submissions for the Stream.\nYou can scroll through the content by clicking on the different threads\nHead over to <#1158008053904441367> to submit your own!""")
        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
        await ctx.send(embed=em)


    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @commands.command(name="permqueuecontent", description="Permanent message for stream-submissions channel, admincommand")
    async def permqueuecontent(self, ctx):
        em = discord.Embed(colour=discord.Color.from_rgb(229, 196, 89))
        em.set_image(
            url="https://media.discordapp.net/attachments/651364619402739713/1158021337617531060/streamcontentsmile.png?ex=651abae9&is=65196969&hm=28a33f154353470d8249a3f9f159d897e72bec4845a0c71bc142ae28504c78d8&=&width=1440&height=458")
        await ctx.send(embed=em)

        em = discord.Embed(title="Nemesis Twitch Stream Submissions!", colour=discord.Color.from_rgb(229, 196, 89))
        em.add_field(name="\u200b", value="""Do you want Nemesis to look at your setup or rate your food? This is the channel to submit it in! The contributions from this channel will be sent in <#1158007237894213672> for Nemesis to go through in between his games on stream.

**How to submit**
To submit queue content, you have to:
1. Click on the submit button under this message
2. Choose the category for the content you want to submit
3. Paste the link for the picture or video you want to submit in the textbox 

**Info**
- All server rules still apply!
- Please dont send very long clips, we will not approve that.
- Mods will go through every submission, so if you don't see your submission right away its not approved yet. Sit tight, it will appear in <#1158007237894213672> once its cleared. 
- We do not choose when Nemesis decides to go through it and we do not take responsibility if you miss out on his review of your submission.""")
        em.set_image(url="https://media.discordapp.net/attachments/651364619402739713/881551188879867954/Intermission.png?width=1440&height=38")
        await ctx.send(embed=em, view=QueueContentDropdownView(self.client))

    @app_commands.choices(tag=[
        Choice(name='Food', value="food"),
        Choice(name='Setups', value="setups"),
    ])
    @app_commands.describe(link='A link to the image/gif')
    @app_commands.command(name="submit", description="Submit an image for Nemesis to view on stream!")
    async def submit(self, interaction: discord.Interaction, tag: Choice[str], link: str):

        if tag.value == "food":
            color = discord.Color.red()
            #thread = await self.client.fetch_channel(1158007582854746112)
        else:
            color = discord.Color.blue()
            #thread = await self.client.fetch_channel(1158007765646716988)
        em = discord.Embed(title=f"{interaction.user}", color=color)
        em.add_field(name=tag.name, value=link)
        em.set_footer(text=f"{interaction.user.id}")
        em.set_image(url=link)
        channel = await self.client.fetch_channel(staffqueuecheck_channel_id)
        msg = await channel.send(embed=em)
        await msg.add_reaction("✅")
        await interaction.response.send_message("Thanks for submitting!", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if(reaction.channel_id != staffqueuecheck_channel_id or reaction.user_id == 881476780765093939):
            return
        if(reaction.emoji.name == "✅"):
            print("worked reaction")
            channel = await self.client.fetch_channel(staffqueuecheck_channel_id)
            msg = await channel.fetch_message(reaction.message_id)
            embed = msg.embeds[0]
            if embed.fields[0].name == "Food":
                color = discord.Color.red()
                thread = await self.client.fetch_channel(food_thread_id)
            else:
                color = discord.Color.blue()
                thread = await self.client.fetch_channel(setups_thread_id)
            newTitle = embed.fields[0].name
            oldLink = embed.fields[0].value
            if oldLink.startswith("https://imgur.com/"):
                oldLink = "https://i.imgur.com/" + oldLink.rsplit('/', 1)[1] + "jpeg"
            newLink = f"[Link]({embed.fields[0].value})"
            embed.clear_fields()
            embed.add_field(name = newTitle, value=newLink)
            embed.set_footer(text=None)
            embed.set_image(url=oldLink)
            await thread.send(embed=embed)









class QueueContentDropdownView(discord.ui.View):
    def __init__(self, client):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(client))

class Dropdown(discord.ui.Select):
    def __init__(self, client):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Food', description='', emoji='🍗'),
            discord.SelectOption(label='Setups', description='', emoji='🖥️'),
        ]

        super().__init__(placeholder='Select a category', min_values=1, max_values=1,
                         options=options, custom_id='persistent_view:selectdropdown_reviews')
        self.client = client

    async def callback(self, interaction: discord.Interaction):

        # we can get the values of the selection, cause self is the dropdown class and it has the attribute values
        category = self.values[0]
        # Now the embed will be changed depending on the value of the selection
        # Also we set the option to True so it will be shown down in the select menu and not be empty again
        modal = QueueContentModal(self.client, category)
        await interaction.response.send_modal(modal)

class QueueContentModal(ui.Modal, title='Submit Content'):

    def __init__(self, client, category):
        super().__init__()
        self.client = client
        self.category = category


    link = ui.TextInput(label='Link', placeholder="Put your link to an image/video here, you can use imgur.com to generate one", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        if self.category == "food":
            color = discord.Color.red()
            #thread = await self.client.fetch_channel(1158007582854746112)
        else:
            color = discord.Color.blue()
            #thread = await self.client.fetch_channel(1158007765646716988)
        em = discord.Embed(title=f"{interaction.user}", color=color)
        em.add_field(name=self.category, value=self.link)
        em.set_footer(text=f"{interaction.user.id}")
        em.set_image(url=self.link)
        channel = await self.client.fetch_channel(staffqueuecheck_channel_id)
        msg = await channel.send(embed=em)
        await msg.add_reaction("✅")
        await interaction.response.send_message("Thanks for submitting!", ephemeral=True)


async def setup(client):
    await client.add_cog(streamsubmissions(client), guilds=guilds)