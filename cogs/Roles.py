import asyncio
import glob
import random
import time
from typing import List

import cogs.essentialfunctions as es
import discord
from discord.ext import commands
from discord import app_commands
from config import guilds

roles = [
    {"category": "lolesports", "roles": [
        {"name": "Pseudo Lolesports Chatter", "tier": 1},
        {"name": "Lolesports Chatter", "tier": 2}
    ]},
    {"category": "general", "roles": [
        {"name": "General Chatter", "tier": 1},
        {"name": "Silver Player", "tier": 2}
    ]}
]


class Roles(commands.GroupCog):
    def __init__(self, client):
        self.client = client
        super().__init__()

    # shop
    # buy allroles you dont already have
    # upgrade role
    # activate role
    # deactivate role


    @app_commands.command(name="shop", description="Show all roles that you can buy")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Roles Tier 1",
                              description="You can buy permanent Tier 1 roles here which you can then further upgrade for more mone.")
        for category in roles:
            for role in category["roles"]:
                embed.add_field(name=f'{role["name"]} [{category["category"]}]', value=f"Tier {role['tier']}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy a Tier 1 role")
    @app_commands.describe(role="The Tier 1 role you want to buy")
    async def buy(self, interaction: discord.Interaction, role: str):
        if not await es.interaction_check_account(interaction):
            return
        embed = discord.Embed(title="Roles Tier 1",
                              description="You can buy Tier 1 roles here which you can then further upgrade for more money.")
        for category in roles:
            for role in category["roles"]:
                embed.add_field(name=role["name"], value=f"Tier {role['tier']}")
        await interaction.response.send_message(embed=embed)

    @buy.autocomplete('role')
    async def buy_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        availableRoles = await self.getAvailableRoles(interaction.user.id)
        return [
            app_commands.Choice(name=role, value=role.lower())
            for role in availableRoles if current.lower() in role.lower()
        ]

    async def getAvailableRoles(self, userid):
        userCategories = es.sql_select(f"SELECT category FROM roles WHERE id = '{userid}'")
        availableRoles = []
        for category in roles:
            if not category["category"] in userCategories:
                availableRoles.append(category["roles"][0])
        return availableRoles




async def setup(client):
    await client.add_cog(Roles(client), guilds=guilds)
