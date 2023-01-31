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
