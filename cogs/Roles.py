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
        {"roleid": 1082942544582807563, "tier": 1},
        {"roleid": 1082942635838296115, "tier": 2}
    ]},
    {"category": "general", "roles": [
        {"roleid": 1082942702615797780, "tier": 1},
        {"roleid": 1082942735343951942, "tier": 2}
    ]}
]


class Roles(commands.GroupCog):
    def __init__(self, client):
        self.guild = None
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = await self.client.fetch_guild(598303095352459305)

    # shop
    # buy all roles you don't already have
    # upgrade role
    # activate role
    # deactivate role
    # see all your roles with the highest tier


    @app_commands.command(name="shop", description="Show all roles that you can buy")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Roles Tier 1",
                              description="You can buy permanent Tier 1 roles here which you can then further upgrade for more mone.\nA tier 1 role costs **5000 Lemons**")
        for category in roles:
            for role in category["roles"]:
                if role["tier"] == 1:
                    embed.add_field(name=f'{self.getRoleNameById(role["roleid"])} [{category["category"]}]', value=f"Tier {role['tier']}", inline=False)
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
        rolename = self.getRoleNameById(role['roleid'])
        es.sql_exec(f"INSERT INTO roles(id, category, name, tier) VALUES('{interaction.user.id}', '{self.getCategoryByName(rolename)}', '{self.getRoleNameById(role['roleid'])}', {role['tier']})")

        await interaction.response.send_message(f"{interaction.user.mention}\nYou've successfully bought the Tier 1 - {rolename}")

    @buy.autocomplete('role')
    async def buy_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        availableRoles = await self.getAvailableRoles(interaction.user.id)
        return [
            app_commands.Choice(name=self.getRoleNameById(role["roleid"]), value=self.getRoleNameById(role["roleid"]).lower())
            for role in availableRoles if current.lower() in self.getRoleNameById(role["roleid"]).lower()
        ]

    async def getAvailableRoles(self, userid):
        userCategories = es.sql_select(f"SELECT category FROM roles WHERE id = '{userid}'")
        for i in userCategories:
            i = i[0]
        availableRoles = []
        for category in roles:
            print(category["category"])
            if not category["category"] in userCategories:
                availableRoles.append(category["roles"][0])
        return availableRoles

    def getRoleByName(self, rolename):
        for category in roles:
            for role in category["roles"]:
                if self.getRoleNameById(role['roleid']).lower() == rolename.lower():
                    return role
    def getCategoryByName(self, rolename):
        for category in roles:
            for role in category["roles"]:
                if self.getRoleNameById(role['roleid']).lower() == rolename.lower():
                    return category["category"]

    def getRoleNameById(self, roleid):
        role = discord.utils.get(self.guild.roles, id=roleid)
        return role.name

async def setup(client):
    await client.add_cog(Roles(client), guilds=guilds)
