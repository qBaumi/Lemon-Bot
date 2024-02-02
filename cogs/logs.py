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
    @app_commands.command(name="logs", description="See all logs of a member")
    async def logs(self, interaction: discord.Interaction, user: discord.User):

        result = es.sql_select(f"SELECT * FROM logs WHERE user_id = {user.id}")
        em = discord.Embed(colour=discord.Color.light_grey(), title=f"Logs of {user.name}")
        em.set_footer(text=f"user_id={user.id}")
        print(result)
        my_str = ""
        # id, user_id, type, msg, date, moderator_id
        for log in result:
            emoji = '🔴'
            if log[2].decode('utf-8')=='action':
                emoji = '🟣'
            my_str += f"{emoji} **ID: {log[0]} Date: {log[4].decode('utf-8')}** \n{log[3].decode('utf-8')} \n(responsible: <@{log[5].decode('utf-8')}>)"
        em.description = my_str
        await interaction.response.send_message(embed=em)


    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods", "Mod")
    @app_commands.command(name="remove", description="remove a log")
    async def remove(self, interaction: discord.Interaction, log_id: int):

        es.sql_exec(f"DELETE FROM logs WHERE id = {log_id}")

        await interaction.response.send_message(f"Log {log_id} was successfully removed!")

    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods", "Mod")
    @app_commands.choices(type=[
        Choice(name='Log', value="log"),
        Choice(name='Action', value="action"),
    ])
    @app_commands.describe(type='If an action like a tempban or verbally warning was made, then choose Action!')
    @app_commands.command(name="edit", description="Edit a log")
    async def edit(self, interaction: discord.Interaction, log_id: int, type: Choice[str], message: str):

        es.sql_exec(f"UPDATE logs SET type='{type.value}', msg='{message}' WHERE id={log_id}")

        await interaction.response.send_message(f"Log {log_id} was successfully edited!")


    @commands.has_any_role("Admins", "Head Mods", "Developer", "Mods", "Mod")
    @app_commands.choices(type=[
        Choice(name='Log', value="log"),
        Choice(name='Action', value="action"),
    ])
    @app_commands.describe(type='If an action like a tempban or verbally warning was made, then choose Action!')
    @app_commands.command(name="create", description="Log a missbehaviour or an action")
    async def create(self, interaction: discord.Interaction, type: Choice[str], user: discord.User, message: str):

        es.sql_exec(f"INSERT INTO logs(user_id, type, msg, date, moderator_id) VALUES ('{user.id}', '{type.value}', '{message}', '{datetime.datetime.now().strftime('%Y-%m-%d')}', '{interaction.user.id}')")

        await interaction.response.send_message(f"Log type: {type.value} was successfully created for user {user.mention}")


async def setup(client):
    await client.add_cog(logs(client), guilds=guilds)