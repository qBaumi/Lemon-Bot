import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice



class prediction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @commands.command(name="prediction")
    async def prediction(self, ctx):
        em = discord.Embed(colour=discord.Color.brand_green(), title="FNC vs G2")
        await ctx.send(embed=em, view=PredictionDropdownView(self.client))


class PredictionDropdownView(discord.ui.View):
    def __init__(self, client):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(PredictionDropdown(client, 1))
        self.add_item(PredictionDropdown(client, 2))

class PredictionDropdown(discord.ui.Select):
    def __init__(self, client, id):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label="1"),
            discord.SelectOption(label="2"),
            discord.SelectOption(label="3"),
        ]
        self.id = id
        super().__init__(placeholder='-', min_values=1, max_values=1,
                         options=options, custom_id=f'persistent_view:predictiondropdown_{self.id}',
                         row=0)
        self.client = client

    async def callback(self, interaction: discord.Interaction):


        await interaction.response.send_message(f"You successfully changed your Prediction to {self.values[0]}")




async def setup(client):
    await client.add_cog(prediction(client), guilds=guilds)