import asyncio
import cogs.essentialfunctions as es
from discord.ext import commands
import random


class events(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 1089172348323762176 and message.content.lower() != "gm <@220607932516139010>":
            await message.delete()
            return
        if message.channel.id == 1089180133228818484 and message.content.lower() != "gn <@220607932516139010>":
            await message.delete()
            return
        if message.channel.id != 598309398976397332:
            return

        if message.author.id == message.author.bot:
            return



        channel = self.client.get_channel(598309398976397332)
        chance = random.randrange(0, 100)

        if chance == 69:
            word_list = [
                'something', 'lemon', 'rubiks cube', 'nemesis', 'qbaumi', 'lelmon', 'volleyball', 'cat', 'cat',
                'tictactoe', 'nvidia', 'headset', 'elon musk', 'rgbible', 'viper', 'valorant',
                'leagueoflegends', 'joemama', 'gamba', 'bot', 'discord', 'rocsie', 'toilet paper',
                'apple bad', 'jett', 'nintendo switch', 'heat', 'dictionary',
                'star wars', "spiderman", "charlie", "floooooof", "graves", "pikachu", "pokemon",
                "rito games", "riot games", "java", "intel", "nomel", "hexagon",
                "dog", "ratjam", "dislike button", "christmas", "linux", "tissue", "fer", "nunu and willump",
                "glurak", "pants", "hoodie", "covid", "mom", "i dont know what to write anymore", "bored",
                "connie", "logitech", "wifi", "chocolate", "cacoa", "cereal", "stopbeingmean", "carl", "arcane",
                "batchest", "pete", "melon", "summoner"
                ]



            word = random.choice(word_list)
            task = word[::-1]
            answer = word

            message.content = message.content.lower()

            await channel.send(f"First one to answer gets `50` lemons.\nBUT FIRST, you need to answer my riddle:\n`{task}`")

            def check(m):
                return m.channel == channel and m.content.lower() == answer

            try:
                msg = await self.client.wait_for("message", timeout=20, check=check)
            except asyncio.TimeoutError:
                await channel.send("You didnt answer in time")
                return

            await channel.send(f"Congratulations, {msg.author.mention} won `50` lemons")
            await es.update_balance(msg.author, 50)
        else:
            return




async def setup(client):
    await client.add_cog(events(client))