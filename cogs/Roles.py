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
        balance, safe, total = await es.currency(interaction.user)
        price = 5000
        if balance < price:
            await interaction.response.send_message("You're too poor for such a premium feature")
            return
        await es.update_balance(interaction.user, -5000)
        role = self.getRoleByName(role)
        es.sql_exec(f"INSERT INTO roles(id, category, name, tier) VALUES('{interaction.user.id}', '{self.getCategoryByName(role['name'])}', '{role['name']}', {role['tier']})")

        await interaction.response.send_message(f"{interaction.user.mention}\nYou've successfully bought the Tier 1 - {role['name']}")

    @buy.autocomplete('role')
    async def buy_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        availableRoles = await self.getAvailableRoles(interaction.user.id)
        return [
            app_commands.Choice(name=role["name"], value=role["name"].lower())
            for role in availableRoles if current.lower() in role["name"].lower()
        ]

    async def getAvailableRoles(self, userid):
        print(es.sql_select(f"SELECT category FROM roles WHERE id = '{userid}'"))
        userCategories = es.sql_select(f"SELECT category FROM roles WHERE id = '{userid}'")[0]
        availableRoles = []
        for category in roles:
            if not category["category"] in userCategories:
                availableRoles.append(category["roles"][0])
        return availableRoles

    def getRoleByName(self, rolename):
        for category in roles:
            for role in category["roles"]:
                if role["name"].lower() == rolename:
                    return role
    def getCategoryByName(self, rolename):
        for category in roles:
            for role in category["roles"]:
                if role["name"].lower() == rolename:
                    return category["category"]

async def setup(client):
    await client.add_cog(Roles(client), guilds=guilds)
