import asyncio
import json
import discord
from discord.ext import commands
import random
import mysql.connector

with open("password.txt", "r") as f:
    password = f.read()
with open("IP.txt", "r") as f:
    ip = f.read()

mydb = mysql.connector.connect(
  host=ip,
  user="myserver",
  password=password,
  port="3306",
  database = "lemonbot",
  auth_plugin="mysql_native_password"

)
mycursor = mydb.cursor()


class events(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def get_bank_data(self, id):
        mycursor.execute(f"SELECT * FROM users WHERE id = {id}")
        data = mycursor.fetchall()

        users = {data[0][0]: {"pocket": data[0][1], "safe": data[0][2]}}
        return users

    # Give or withdraw money from your account
    async def update_balance(self, user, change=0, mode="pocket"):
        # Get the bank file data
        users = await self.get_bank_data(id=user.id)
        sql = f"UPDATE users SET {mode} = {users[str(user.id)]['pocket'] + change} WHERE id = {user.id}"
        mycursor.execute(sql)
        mydb.commit()
        bal = users[str(user.id)]["pocket"] + change
        return bal

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.channel.id != 598309398976397332:
            return
        if message.author.id == message.author.bot:
            return
        channel = self.client.get_channel(598309398976397332)
        chance = random.randrange(0, 100)

        if chance == 69:
            answers = {"answer1": {"question": "gnihtemos", "answer": "something"},
                       "answer2": {"question": "nomel", "answer": "lemon"},
                       "answer3": {"question": "ebuc skibur", "answer": "rubiks cube"},
                       "answer4": {"question": "sisemen", "answer": "nemesis"},
                       "answer5": {"question": "imuabq", "answer": "qbaumi"},
                       "answer6": {"question": "nomlel", "answer": "lelmon"},
                       "answer8": {"question": "llabyellov", "answer": "volleyball"},
                       "answer9": {"question": "tac", "answer": "cat"},
                       "answer10": {"question": "tac", "answer": "cat"},
                       "answer11": {"question": "eotcatcit", "answer": "tictactoe"},
                       "answer12": {"question": "aidivn", "answer": "nvidia"},
                       "answer13": {"question": "tesdaeh", "answer": "headset"},
                       "answer14": {"question": "ksum nole", "answer": "elon musk"},
                       "answer15": {"question": "elbibgr", "answer": "rgbible"},
                       "answer16": {"question": "repiv", "answer": "viper"},
                       "answer17": {"question": "tnarolav", "answer": "valorant"},
                       "answer18": {"question": "sdnegelfoeugael", "answer": "leagueoflegends"},
                       "answer19": {"question": "amameoj", "answer": "joemama"},
                       "answer20": {"question": "abmag", "answer": "gamba"},
                       "answer21": {"question": "tob", "answer": "bot"},
                       "answer22": {"question": "drocsid", "answer": "discord"},
                       "answer23": {"question": "eiscor", "answer": "rocsie"},
                       "answer24": {"question": "repap teliot", "answer": "toilet paper"},
                       "answer25": {"question": "enihcamgnidnev mel", "answer": "lem vendingmachine"},
                       "answer26": {"question": "dab elppa", "answer": "apple bad"},
                       "answer27": {"question": "ttej", "answer": "jett"},
                       "answer28": {"question": "hctiws odnetnin", "answer": "nintendo switch"},}

            message.content = message.content.lower()

            dict = random.choice(list(answers.values()))

            task = dict["question"]
            answer = dict["answer"]

            await channel.send(f"First one to answer gets `50` lemons.\nBUT FIRST, you need to answer my riddle:\n`{task}`")

            def check(m):
                return m.channel == channel and m.content.lower() == answer

            try:
                msg = await self.client.wait_for("message", timeout=20, check=check)
            except asyncio.TimeoutError:
                await channel.send("You didnt answer in time")
                return

            await channel.send(f"Congratulations, {msg.author.mention} won `50` lemons")
            await self.update_balance(msg.author, 50)
        else:
            return
        await self.client.process_commands(message)



def setup(client):
    client.add_cog(events(client))