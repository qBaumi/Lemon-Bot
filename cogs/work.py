import asyncio
import glob
import math
import random
import time

from riotwatcher import LolWatcher

import cogs.essentialfunctions as es
import discord
from discord.ext import commands
from discord import app_commands
from config import guilds, api_key
from .job import joblist, job_helper, getxp, add_xp

class work(commands.Cog):
    def __init__(self, client):
        self.client = client
        super().__init__()
        watcher = LolWatcher(api_key)
        versions = watcher.data_dragon.versions_for_region("euw")
        champions_version = versions['n']['champion']
        self.champions = watcher.data_dragon.champions(champions_version)["data"]
        self.champions = list(self.champions.keys())


    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="work", description="Time to work Voidge")
    async def work(self, interaction : discord.Interaction):

        if not await es.interaction_check_account(interaction):
            return

        user = interaction.user

        #isOnCooldown, sec = es.isOnCooldown(user, "work")
        #if isOnCooldown:
        #    await interaction.response.send_message(
        #        f"You are still on cooldown until <t:{math.floor(time.time() + sec)}>", ephemeral=True)
        #    return

        await interaction.response.defer()

        try:
            data = es.sql_select(f"SELECT * FROM jobs WHERE id = {user.id}")
            userjob = [{"Name": data[0][1], "Verdienst": data[0][2]}]
        except:
            embed = discord.Embed(title='You cant work without a job!')
            await interaction.followup.send(embed=embed)
            time.sleep(3)
            await interaction.channel.send(embed=job_helper())
            return

        try:
            xp, lvl = await getxp(user.id)
        except:
            xp = 0
            lvl = 1

        await add_xp(user.id, 10)

        lvl_start = lvl
        lvl_end = int(xp ** (1 / 4))
        if lvl_start < lvl_end:
            sql = f"UPDATE users SET lvl = {lvl_end} WHERE id = {user.id}"
            es.sql_exec(sql)
            if lvl != 1:
                embed = discord.Embed(title=f'{user.name} leveled up and can now access better job',
                                      description=f'You are now level {lvl}')
                await interaction.channel.send(embed=embed)

        def check(m):
            return m.author == user and m.channel == interaction.channel

        def checkreaction(reaction, reactionuser):
            return reaction.message.id == message.id and reactionuser == user

        for job in userjob:
            name = job['Name']
            lohn = job['Verdienst']

            if name == 'reddit analyst':
                ausgabe = f"Big PP or small PP?"

                embed = discord.Embed(title=ausgabe)

                file_path_type = ["./memes/*.png", "./memes/*.jpg", "./memes/*.gif"]
                images = glob.glob(random.choice(file_path_type))
                random_image = random.choice(images)
                file = discord.File(random_image)
                print(random_image)
                embed.set_image(url="attachment://" + random_image)
                message = await interaction.channel.send(f"{user.mention}\n", file=file, embed=embed)
                await message.add_reaction('⬆')
                await message.add_reaction('⬇')

                try:
                    useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"{user.mention}\nYou didnt answer fast enough!")
                    es.setCooldown(user, "work")
                    return
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await interaction.followup.send(f"{user.mention}\n", embed=embed)

            elif name == 'cat enjoyer':
                ausgabe = '<a:catJAM:810785548678987776>'

                embed = discord.Embed(title=ausgabe)

                file_path_type = ["./cats/*.png", "./cats/*.jpg"]
                images = glob.glob(random.choice(file_path_type))
                random_image = random.choice(images)
                file = discord.File(random_image)
                print(random_image)
                embed.set_image(url="attachment://" + random_image)
                message = await interaction.channel.send(f"{user.mention}\n", file=file, embed=embed)
                await message.add_reaction('<:catJAM:810785548678987776>')

                try:
                    useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"{user.mention}\nYou didnt answer fast enough!")
                    es.setCooldown(user, "work")
                    return
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await interaction.followup.send(f"{user.mention}\n", embed=embed)
            elif name == 'content creator':
                rndmuser = es.getRandomUser()
                games = ["TFT", "League of Legends", "Aram", "Valorant", "in Hot Tub"]
                game = random.choice(games)
                hours = random.randrange(1, 15)
                embed = discord.Embed(title=f"What do you want to do today?", description=f"1️⃣ stream {game}\n 2️⃣ sorry, no stream today\n 3️⃣ steal other content and react to it\n 4️⃣ collab with someone")
                message = await interaction.channel.send(f"{user.mention}\n", embed=embed)
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')
                await message.add_reaction('4️⃣')
                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"{user.mention}\nYou didnt answer fast enough!")
                    es.setCooldown(user, "work")
                    return
                await es.update_balance(user, lohn, 'pocket')
                if reaction.emoji == '1️⃣':
                    line = f"You streamed {game} for {hours} hours"
                elif reaction.emoji == '2️⃣':
                    line = f"You announced in <#598311673945653258> that you won't stream today and later posted it in <#944417237954093066>"
                elif reaction.emoji == '3️⃣':
                    line = f"You reacted to a MrBeast video"
                elif reaction.emoji == '4️⃣':
                    if game == "in Hot Tub":
                        line = f"You successfully collabed with <@!{rndmuser}> in the Hot Tub for {hours} hours"
                    else:
                        line = f"You successfully collabed with <@!{rndmuser}> \nYou played {game} for {hours} hours"
                else:
                    line = f"You had an accident."
                await interaction.followup.send(f"{user.mention}\n{line}")
            elif name == 'aram proplayer':

                champs = []
                champs.append(random.choice(self.champions))
                champs.append(random.choice(self.champions))
                champs.append(random.choice(self.champions))
                embed = discord.Embed(title=f"Aram, quick - which champion do you take?", description=f"1️⃣ {champs[0]}\n 2️⃣ {champs[1]}\n 3️⃣ {champs[2]}\n ")

                message = await interaction.channel.send(f"{user.mention}\n", embed=embed)
                await message.add_reaction('1️⃣')
                await message.add_reaction('2️⃣')
                await message.add_reaction('3️⃣')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"{user.mention}\nYou didnt answer fast enough!")
                    es.setCooldown(user, "work")
                    return
                await es.update_balance(user, lohn, 'pocket')
                if reaction.emoji == '1️⃣':
                    champ = champs[0]
                elif reaction.emoji == '2️⃣':
                    champ = champs[1]
                elif reaction.emoji == '3️⃣':
                    champ = champs[2]
                else:
                    champ = "<:lolsinged:989931198501486682>"
                win = random.choice([True, False])
                if win:
                    embed = discord.Embed(title=f'You won the game as {champ} (feels nice playing your otp in aram) and you received {lohn} lemons!')
                else:
                    embed = discord.Embed(title=f'You lost the game as first time {champ}, but you still received {lohn} lemons!')
                await interaction.followup.send(f"{user.mention}\n", embed=embed)

            elif name == 'lemonade salesman':
                ausgabe = 'A stranger arrives and asks for some lemonade...he is strange'
                embed = discord.Embed(title=ausgabe)
                message = await interaction.channel.send(f"{user.mention}\n", embed=embed)
                await message.add_reaction('<:lemonade:882239415601213480>')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send('You didnt answer fast enough!')
                    es.setCooldown(user, "work")
                    return

                em = discord.Embed(
                    title="You gave him some lemonade, when you told him the price he gave you a *strange* look. But he paid anyways so you **didnt care**")
                await interaction.channel.send(embed=em)
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await interaction.followup.send(f"{user.mention}\n", embed=embed)

            elif name == 'discord mod':
                ausgabe = 'Mute, Kick or Ban?'
                jokes = ['Singing in the shower is fun until you get soap in your mouth. Then its a soap opera.',
                         'What do you call a fish wearing a bowtie? Sofishticated.',
                         'Dear Math, grow up and solve your own problems.',
                         'Can a kangaroo jump higher than the empire state building? Of course! Buildings can’t jump',
                         'Why was the robot so tired after his road trip? He had a hard drive.',
                         'I was wondering why this frisbee kept looking bigger and bigger. Then it hit me.',
                         'A man rushed into a Doctors surgery, shouting "help me please, Im shrinking" The Doctor calmly said "now settle down a bit… youll just have to learn to be a little patient".',
                         'When I moved into my new igloo my friends threw me a surprise house-warming party. Now Im homeless.',
                         'I met my wife on Tinder. That was awkward.',
                         'My friend is fed up with my constant stream of dad jokes, so I asked her, "How can I stop my addiction?!" She shot back, "Whatever means necessary!!" I replied, "No, it doesnt!”',
                         'What’s the difference between a literalist and a kleptomaniac? A literalist takes things literally. A kleptomaniac takes things, literally.',
                         'ts been months since I bought the book, "How to scam people online." It still hasnt arrived yet.',
                         "why did syndra run away from the fight? Because she had no balls <:OmegaLUL:598583138758950932>",
                         "Why did the scarecrow win an award? Because he was outstanding in his field."]
                joke = random.choice(jokes)
                embed = discord.Embed(title=ausgabe, description=joke)
                message = await interaction.channel.send(embed=embed)
                await message.add_reaction('🔇')
                await message.add_reaction('⛔')
                await message.add_reaction('🚫')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"{user.mention}\nYou didnt answer fast enough!")
                    es.setCooldown(user, "work")
                    return
                print(reaction.emoji)
                if reaction.emoji == '🔇':
                    line = f"You muted him for 24h"
                elif reaction.emoji == '⛔':
                    line = f"You kicked him from the server"
                elif reaction.emoji == '🚫':
                    line = f"You banned him from the server"
                else:
                    line = f"Idk"

                em = discord.Embed(title=line)
                await interaction.channel.send(f"{user.mention}\n", embed=em)
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f"You received {lohn} lemons!")
                await interaction.followup.send(f"{user.mention}\n", embed=embed)

            elif name == 'lemon researcher':
                ausgabe = '*Hmmm* intresting '
                facts = ["Lemons are native to Asia.", "Lemons are a hybrid between a sour orange and a citron.",
                         "Lemons are rich in vitamin C.", "Lemons trees can produce up to 600lbs of lemons every year.",
                         "Lemon trees produce fruit all year round.",
                         "Lemon zest, grated rinds, is often used in baking.",
                         "Lemon tree leaves can be used to make tea.",
                         "The high acidity of lemons make them good cleaning aids.",
                         "California and Arizona produces most of the United States’ lemon crop.",
                         "The most common types of lemons are the Meyer, Eureka, and Lisbon lemons.", ]
                fact = random.choice(facts)
                embed = discord.Embed(title=ausgabe, description=fact + " <:Nerdge:814443289386156033>")
                message = await interaction.channel.send(embed=embed)
                await message.add_reaction('<:Nerdge:814443289386156033>')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"{user.mention}\nYou didnt answer fast enough!")
                    es.setCooldown(user, "work")
                    return

                em = discord.Embed(title="Well, interesting <:Nerdge:814443289386156033>")
                await interaction.channel.send(embed=em)
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await interaction.followup.send(f"{user.mention}\n", embed=embed)

            elif name == 'pizza guy':
                file = discord.File("./jobs/pizza.png")
                embed = discord.Embed(title="Mamma Mia! What topping this beautiful pizza shall get?",
                                      colour=discord.Color.green())
                embed.set_image(url="attachment://pizza.png")
                message = await interaction.channel.send(embed=embed, file=file)
                await message.add_reaction('🍄')
                await message.add_reaction('🍍')
                await message.add_reaction('🌶️')
                await message.add_reaction('🥬')
                await message.add_reaction('🧅')
                await message.add_reaction('🍗')
                await message.add_reaction('🐟')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"{user.mention}\nYou didnt answer fast enough!")
                    es.setCooldown(user, "work")
                    return

                if reaction.emoji == '🍄':
                    await interaction.channel.send("I hope you didnt murder Moooooshroom for that!")
                elif reaction.emoji == '🍍':
                    await interaction.channel.send("WHY DO YOU PUT PINEAPPLE ON PIZZA?!?!?")
                elif reaction.emoji == '🌶️':
                    await interaction.channel.send("Hooooooooooooooooooooooooot")
                elif reaction.emoji == '🥬':
                    await interaction.channel.send("Green stuff, really?")
                elif reaction.emoji == '🧅':
                    await interaction.channel.send("Onions are good in salads, but not on pizza")
                elif reaction.emoji == '🍗':
                    await interaction.channel.send("Chicken, always a great decision")
                elif reaction.emoji == '🐟':
                    await interaction.channel.send("I like fish")
                else:
                    await interaction.channel.send("I have no idea why you put that on your pizza!")
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f"You received {lohn} lemons!")
                await interaction.followup.send(f"{user.mention}\n", embed=embed)

            elif name == 'lemon farmer':
                rndmaufgabe = random.randrange(1, 4)

                if rndmaufgabe == 1:
                    ausgabe = 'Time to plant some grass! uuuhhhfkjdaslf I mean lemons of course... Dont do drugs kids'
                    embed = discord.Embed(title=ausgabe)
                    message = await interaction.channel.send(f"{user.mention}\n", embed=embed)
                    await message.add_reaction('🌱')

                    try:
                        await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await interaction.followup.send(
                            f"{user.mention}\nYou didnt answer in time and the lemons were eaten by some birds")
                        es.setCooldown(user, "work")
                        return


                elif rndmaufgabe == 2:
                    ausgabe = 'Time to water your precious lemons!'
                    embed = discord.Embed(title=ausgabe)
                    message = await interaction.channel.send(embed=embed)
                    await message.add_reaction('🍋')

                    try:
                        await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await interaction.followup.send(
                            f"{user.mention}\nYou didnt answer in time and your lemon trees sadly died :(")
                        es.setCooldown(user, "work")
                        return



                elif rndmaufgabe == 3:
                    ausgabe = 'Time to harvest your perfectly riped lemons'
                    embed = discord.Embed(title=ausgabe)
                    message = await interaction.channel.send(f"{user.mention}\n", embed=embed)
                    await message.add_reaction('⛏')

                    try:
                        await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await interaction.followup.send(f"{user.mention}\nYou didnt answer in time :(")
                        es.setCooldown(user, "work")
                        return
                else:
                    await interaction.followup.send('System Error *lmao*')

                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await interaction.followup.send(f"{user.mention}\n", embed=embed)

            else:
                await interaction.followup.send(f"{user.mention}\nI think the creator didnt finish this job yet...")
            es.setCooldown(user, "work")

    @work.error
    async def on_work_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)
        work.work.cooldown.reset()


async def setup(client):
    await client.add_cog(work(client), guilds=guilds)