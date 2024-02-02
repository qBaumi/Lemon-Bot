import datetime

import discord, json
from discord.ext import commands
from discord import app_commands
from discord import ui

from config import guilds
from discord.app_commands import Choice
import cogs.essentialfunctions as es

class logs(commands.GroupCog):
    def __init__(self, client):
        self.client = client



    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods", "Mod")
    @app_commands.choices(type=[
        Choice(name='Log', value="log"),
        Choice(name='Action', value="action"),
    ])
    @app_commands.describe(type='If an action like a tempban or verbally warning was made, then choose Action!')
    @app_commands.command(name="log", description="Log a missbehaviour or an action")
    async def log(self, interaction: discord.Interaction, type: Choice[str], user: discord.User, message: str):

        es.sql_exec(f"INSERT INTO logs(user_id, type, msg, date, moderator_id) VALUES ('{user.id}', '{type}', '{message}', '{datetime.datetime.now().strftime('%Y-%m-%d')}', '{interaction.user.id}', )")

        await interaction.response.send_message(f"Log type: {type} was successfully created")


async def setup(client):
    await client.add_cog(logs(client), guilds=guilds)