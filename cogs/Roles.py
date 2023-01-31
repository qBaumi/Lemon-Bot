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


async def setup(client):
    await client.add_cog(Roles(client), guilds=guilds)
