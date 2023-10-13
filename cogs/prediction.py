from functools import partial

import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice

teams = [
    Choice(name='FNC', value="<:FNC:1162308600128086096>"),
    Choice(name='G2', value="<:G2:1162308625763672154>")
    ]

class prediction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_any_role("Admins", "Head Mods", "Developer")
    @app_commands.choices(team1=teams)
    @app_commands.choices(team2=teams)
    @app_commands.choices(bestof=[
        Choice(name="Best of one", value="1"),
        Choice(name="Best of two", value="2"),
        Choice(name="Best of three", value="3"),
    ])
    @app_commands.command(name="prediction", description="Create a prediction")
    async def prediction(self, interaction, team1: Choice[str], team2: Choice[str], bestof: Choice[str]):
        em = discord.Embed(colour=discord.Color.brand_green(), title="FNC vs G2", description="Predictions close at 19:00 on the 13.10.2023")
        if bestof.value == "1":
            view = PredictionDropdownViewBestofOne(self.client, [team1, team2])
        else:
            view = PredictionDropdownView(self.client)
        await interaction.channel.send(embed=em, view=view)
        await interaction.response.send_message("Successfully created prediction", ephemeral=True)


class PredictionDropdownView(discord.ui.View):
    def __init__(self, client):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(PredictionDropdown(client, 1))
        self.add_item(PredictionDropdown(client, 2))
class PredictionDropdownViewBestofOne(discord.ui.View):
    def __init__(self, client, teams):
        # Pass the timeout in the initilization of the super class
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(PredictionSelectBestofOne(client, teams))
class PredictionSelectBestofOne(discord.ui.Select):
    def __init__(self, client, teams):
        self.client = client
        self.teams = teams
        options = [
            discord.SelectOption(label=teams[0].name, emoji=teams[0].value, description=f"Pick {teams[0].name} as winner"),
            discord.SelectOption(label=teams[1].name, emoji=teams[1].value, description=f"Pick {teams[1].name} as winner"),
        ]
        super().__init__(placeholder='Pick a winner', min_values=1, max_values=1,
                         options=options, custom_id='persistent_view:selectbestofone')



    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You predicted a **win for {self.values[0]}**", ephemeral=True)

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
                         options=options, custom_id=f'persistent_view:predictiondropdown_{self.id}')
        self.client = client

    async def callback(self, interaction: discord.Interaction):


        await interaction.response.send_message(f"You successfully changed your Prediction to {self.values[0]}")




async def setup(client):
    await client.add_cog(prediction(client), guilds=guilds)