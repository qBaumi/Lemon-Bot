import asyncio
import datetime
import random
from typing import Optional

import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice
import cogs.essentialfunctions as es

milestone_channel_id = 651364619402739713 # 651364619402739713 testing

@app_commands.default_permissions(manage_roles=True)
class milestones(commands.GroupCog):
    def __init__(self, client):
        self.client = client


    async def send_milestone(self, id):
        milestones = self.getMilestones()
        milestone = milestones[id]
        channel = await self.client.fetch_channel(milestone_channel_id)
        date = datetime.datetime.strptime(f"{milestone['date']}", "%d/%m/%Y").timestamp()
        date = int(date)
        em = discord.Embed(
            colour=discord.Color.from_rgb(milestone["color"][0], milestone["color"][1], milestone["color"][2]),
            title=milestone["name"], description=f"<t:{date}:D>")

        self.getImageFromMilestone(milestone)
        file = discord.File("./img/milestone_changed.png", filename=f"milestone_changed.png")
        em.set_image(url=f"attachment://milestone_changed.png")

        await channel.send(embed=em, file=file)

    @app_commands.command(name="send", description="Send all milestones in a channel")
    async def send(self, interaction : discord.Interaction, id : Optional[int]):

        await interaction.response.send_message(f"Milestones summoned", ephemeral=True)

        if id:
            await self.send_milestone(id)
            await interaction.response.send_message(f"Sent Milestone with id {id} to the milestone channel", ephemeral=True)
            return

        channel = await self.client.fetch_channel(interaction.channel.id)

        milestones = self.getMilestones()
        for milestone in milestones:
            date = datetime.datetime.strptime(f"{milestone['date']}", "%d/%m/%Y").timestamp()
            date = int(date)
            em = discord.Embed(colour=discord.Color.from_rgb(milestone["color"][0], milestone["color"][1], milestone["color"][2]), title=milestone["name"], description=f"<t:{date}:D>")

            self.getImageFromMilestone(milestone)
            file = discord.File("./img/milestone_changed.png", filename=f"milestone_changed.png")
            em.set_image(url=f"attachment://milestone_changed.png")

            await channel.send(embed=em, file=file)


    @app_commands.command(name="list", description="List all milestones")
    async def list(self, interaction: discord.Interaction):

        channel = await self.client.fetch_channel(interaction.channel.id)

        milestones = self.getMilestones()

        s = ""
        for milestone in milestones:
            s += f"**{milestone['name']}**\n**id: {milestone['id']}**\n{milestone['date']}\nrgb: {milestone['color']}\n\n"
        em = discord.Embed(colour=discord.Color.brand_green(), title="Milestones", description=s)

        await interaction.response.send_message(embed=em)

    @app_commands.command(name="add", description="Add a milestones")
    @app_commands.describe(name="The name of the Milestone")
    @app_commands.describe(date="Date of the Milestone e.g. 06/09/2022")
    @app_commands.describe(red="Red amount of RGB color")
    @app_commands.describe(green="Green amount of RGB color")
    @app_commands.describe(blue="Blue amount of RGB color")
    async def add(self, interaction: discord.Interaction, name : str, date: str, red : Optional[app_commands.Range[int, 0, 255]], green : Optional[app_commands.Range[int, 0, 255]], blue : Optional[app_commands.Range[int, 0, 255]]):

        if len(date) != 10:
            await interaction.response.send_message(f"**The date needs to be in the format e.g. 06/09/2420**")
            return

        milestones = self.getMilestones()
        if not red:
            red = random.randrange(0, 255)
        if not green:
            green = random.randrange(0, 255)
        if not blue:
            blue = random.randrange(0, 255)


        milestones.append({
        "id":len(milestones),
        "color" : [red, green, blue],
        "name" : name,
        "date" : date
        })
        self.saveMilestones(milestones)

        await interaction.response.send_message(f"**Successfully added Milestone {name} with id {len(milestones)}**")

    @app_commands.command(name="remove", description="Remove a milestones")
    @app_commands.describe(id="The id of the Milestone")
    async def remove(self, interaction: discord.Interaction, id: int):


        milestones = self.getMilestones()
        try:
            milestones.pop(id)
        except:
            await interaction.response.send_message(f"**Milestone with id {id} does not exist!**")
            return


        self.saveMilestones(milestones)

        await interaction.response.send_message(f"**Successfully removed Milestone with id {id} BUT DONT FORGET TO DELETE THE MESSAGE IN THE MILESTONE CHANNEL**")

    @app_commands.command(name="edit", description="Edit a milestones")
    @app_commands.describe(id="The id of the Milestone you wish to edit")
    @app_commands.describe(name="The name of the Milestone")
    @app_commands.describe(date="Date of the Milestone e.g. 06/09/2022")
    @app_commands.describe(red="Red amount of RGB color")
    @app_commands.describe(green="Green amount of RGB color")
    @app_commands.describe(blue="Blue amount of RGB color")
    async def edit(self, interaction: discord.Interaction, id : int, name : Optional[str], date: Optional[str], red : Optional[app_commands.Range[int, 0, 255]], green : Optional[app_commands.Range[int, 0, 255]], blue : Optional[app_commands.Range[int, 0, 255]]):



        milestones = self.getMilestones()
        if red:
            milestones[id]["color"][0] = red
        if green:
            milestones[id]["color"][1] = green
        if blue:
            milestones[id]["color"][2] = blue
        if name:
            milestones[id]["name"] = name
        if date:
            if len(date) != 10:
                await interaction.response.send_message(f"**The date needs to be in the format e.g. 06/09/2420**")
                return
            milestones[id]["date"] = date

        self.saveMilestones(milestones)

        await interaction.response.send_message(f"**Successfully edited Milestone {milestones[id]['name']}**\nBut you need to use **/milestones send** again")



    def getMilestones(self):
        with open("./json/milestones.json", "r") as f:
            milestones = json.load(f)
        return milestones

    def saveMilestones(self, milestones):
        with open("./json/milestones.json", "w") as f:
            json.dump(milestones, f, indent=4)


    def getImageFromMilestone(self, milestone):
        from PIL import Image, ImageDraw
        img = Image.open("./img/milestone.png")
        img = img.convert("RGBA")

        w, h = 650, 750
        shape = [(40+100, 40), (w - 10, h - 10)]

        # creating new Image object
        img = Image.new("RGBA", (w+200, h))

        # create rectangle image
        img1 = ImageDraw.Draw(img)
        img1.rounded_rectangle(shape, fill=(milestone["color"][0], milestone["color"][1], milestone["color"][2]), radius=20)

        # save new image
        img.save("./img/milestone_changed.png")

        # show image in preview
        #img.show()

async def setup(client):
    await client.add_cog(milestones(client), guilds=guilds)