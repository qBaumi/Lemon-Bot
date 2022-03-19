import asyncio
import glob
import random
import time
from typing import List

import cogs.essentialfunctions as es
import discord
from discord.ext import commands
from cogs.essentialfunctions import mycursor, mydb
from discord import app_commands
from config import guilds

class job(commands.Cog, app_commands.Group):
    def __init__(self, client):
        self.client = client
        super().__init__()

    joblist = [{'Name': 'Lemon Farmer', 'Verdienst': 10, 'Beschreibung': ' Start little as a lemon farmer', 'lvl': 1},
               {'Name': 'Reddit Analyst', 'Verdienst': 20, 'Beschreibung': ' Carefully analyse r/woooosh posts', 'lvl': 3},
               {'Name': 'Lemonade salesman', 'Verdienst': 25, 'Beschreibung': ' sell overpriced lemonade to strangers', 'lvl': 4},
               {'Name': 'Discord Mod', 'Verdienst': 30, 'Beschreibung': ' Be a good Mod! Or Rocsie will get you!', 'lvl': 5},
               {'Name': 'Cat Enjoyer', 'Verdienst': 35, 'Beschreibung': ' <a:catJAM:810785548678987776><a:catJAM:810785548678987776><a:catJAM:810785548678987776>', 'lvl': 6},
               {'Name': 'Lemon Researcher', 'Verdienst': 40, 'Beschreibung': ' research 🔎 lemons 🍋', 'lvl': 7},
               {'Name': 'Pizza guy', 'Verdienst': 45, 'Beschreibung': ' make some pizza 🍕', 'lvl': 8}]

    async def job_helper(self):
        embed = discord.Embed(title='Help for the job command:', description="First use `lem job list` to take a look which jobs you can appeal for, then you can select them with `lem job select lemon farmer` for example. After that you can work with `lem work` and complete several tasks")
        embed.add_field(name='Job info', value='Look up your current job!', inline=False)
        embed.add_field(name='Job list', value='List every job!', inline=False)
        embed.add_field(name='Job select', value='Select a job that is in the list!',
                        inline=False)
        embed.add_field(name='lem work', value='Work, work, work, work...', inline=False)
        embed.set_footer(text='Send job ideas to @qBaumi#1247!')
        return embed

    async def getxp(self, id):
        mycursor.execute(f"SELECT * FROM users WHERE id = {id}")
        data = mycursor.fetchall()
        xp = data[0][3]
        lvl = data[0][4]
        print(xp)
        return xp, lvl
    async def add_xp(self, id, amount):

        xp, lvl = await self.getxp(id)

        sql = f"UPDATE users SET xp = {xp + amount} WHERE id = {id}"
        mycursor.execute(sql)
        mydb.commit()

    @app_commands.command(name="info", description="Your current job, salary and job level")
    async def info(self, interaction : discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        xp, lvl_start, lvl = await self.jobxphelp(interaction)
        user = interaction.user
        try:
            data = es.sql_select(f"SELECT * FROM jobs WHERE id = {user.id}")
            userjob = [{"Name": data[0][1], "Verdienst": data[0][2]}]

        except:
            userjob = []
        if not userjob:
            embed = discord.Embed(title='You dont have a job!',
                                  description='Try: *lem job list*, then *lem job select <Job>*')
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title='Your Job:')
            string = ""

            xp_start = xp
            xp_end = int(pow(lvl_start + 1, 4))

            rest = xp_end - xp_start
            for x in range(int(rest)):
                string += "🟥"
            for i in range(rest):
                string += "⬛"
            for job in userjob:
                name = job['Name']
                verdienst = job['Verdienst']
                lvl = str(lvl)
                dislvl = str(int(lvl) + 1)

                embed.add_field(name=name, value=f'Salary: {verdienst}')

                embed.add_field(
                    name="level",
                    value=f"{lvl} ---{xp_start}/{xp_end}---> {dislvl}", inline=False)

            await interaction.response.send_message(embed=embed)
    @app_commands.command(name="help", description="How jobs work")
    async def help(self, interaction: discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        await self.jobxphelp(interaction)
        await interaction.response.send_message(embed=await self.job_helper())
    @app_commands.command(name="list", description="List all jobs")
    async def list(self, interaction: discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        await self.jobxphelp(interaction)
        embed = discord.Embed(title='Open Jobs:')
        for job in self.joblist:
            name = job['Name']
            desc = job['Beschreibung']
            lvl = str(job['lvl'])
            verdienst = job['Verdienst']
            verdienst = str(verdienst)
            embed.add_field(name=name + '  Salary: ' + verdienst, value=desc + ' | Level ' + lvl + ' needed',
                            inline=False)
        embed.set_footer(text='Every Coorparation mentioned here is owned 51% by Lemon Inc.')
        await interaction.response.send_message(embed=embed)
    @app_commands.command(name="select", description="Select a job from open positions")
    @app_commands.describe(job="The job you want to apply for")
    async def select(self, interaction: discord.Interaction, job : str):
        if not await es.interaction_check_account(interaction):
            return
        a, b, lvl = await self.jobxphelp(interaction)
        arg2 = job.lower()
        user = interaction.user
        for job in self.joblist:
            name = job['Name']
            name = name.lower()
            neededlvl = job['lvl']
            verdienst = job['Verdienst']

            if arg2 == name:

                try:
                    data = es.sql_select(f"SELECT * FROM jobs WHERE id = {user.id}")
                    userjob = [{"Name": data[0][1], "Verdienst": data[0][2]}]


                except:
                    userjob = []

                tf = 0
                if bool(userjob) == True:

                    if userjob[0]["Name"] == name:
                        ausgabe = f'You already work as {name}!'
                        tf = 1
                        break

                if lvl < neededlvl:
                    ausgabe = f'You dont have enough experience to work as {name}!'
                    embed2 = discord.Embed(title=ausgabe)
                    await interaction.response.send_message(embed=embed2)
                    tf = 1
                    return

                if bool(userjob) == False:
                    es.sql_exec(f"INSERT INTO jobs (id, Name, Verdienst) VALUES ({user.id}, '{name}', {verdienst})")
                else:
                    es.sql_exec(f"UPDATE jobs SET Name = '{name}' WHERE id = {user.id}")
                    es.sql_exec(f"UPDATE jobs SET Verdienst = {verdienst} WHERE id = {user.id}")
                mydb.commit()
                ausgabe = 'You wrote an application for the job and not even 2 hours later you received a phone call and got the job'
                tf = 1
                break

            elif arg2 != name:
                ausgabe = 'This job doesnt exist!'
                tf = 1
            else:
                await interaction.response.send_message(embed=self.job_helper())
                return
        if tf != 0:
            embed = discord.Embed(title=ausgabe)
            await interaction.response.send_message(f"{user.mention}", embed=embed)

    async def getjobs(self, user):
        data = es.sql_select(f"SELECT lvl FROM users WHERE id = {user.id}")
        availablejobs = []
        for job in self.joblist:
            if job['lvl'] <= data[0][0]:
                availablejobs.append(job['Name'])
        return availablejobs
    @select.autocomplete('job')
    async def job_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        jobs = await self.getjobs(interaction.user)
        return [
            app_commands.Choice(name=job, value=job.lower())
            for job in jobs if current.lower() in job.lower()
        ]


    async def jobxphelp(self, interaction):
        xp_per_use = 5
        user = interaction.user

        xp, lvl = await self.getxp(user.id)
        await self.add_xp(user.id, xp_per_use)

        lvl_start = lvl
        lvl_end = int(xp ** (1 / 4))
        print(int(2 ** (1/(1/4))))



        if lvl_start < lvl_end:
            es.sql_exec(f"UPDATE users SET lvl = {lvl_end} WHERE id = {user.id}")

            if lvl != 1:
                embed = discord.Embed(title=f'{user.name} leveled up and can now access better job',
                                      description=f'You are now level {lvl}')
                await interaction.channel.send(embed=embed)
        return xp, lvl_start, lvl





    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def work(self, ctx):

        if not await es.check_account(ctx):
            self.work.reset_cooldown(ctx)
            return

        user = ctx.author


        try:
            mycursor.execute(f"SELECT * FROM jobs WHERE id = {user.id}")
            data = mycursor.fetchall()
            userjob = [{"Name": data[0][1], "Verdienst": data[0][2]}]
        except:
            embed = discord.Embed(title='You cant work without a job!')
            self.work.reset_cooldown(ctx)
            await ctx.send(embed=embed)
            time.sleep(3)
            await ctx.send(embed=self.job_helper())
            return


        try:
            xp, lvl = await self.getxp(user.id)
        except:
            xp = 0
            lvl = 1

        await self.add_xp(user.id, 10)

        lvl_start = lvl
        lvl_end = int(xp ** (1 / 4))
        if lvl_start < lvl_end:
            sql = f"UPDATE users SET lvl = {lvl_end} WHERE id = {user.id}"
            mycursor.execute(sql)
            mydb.commit()
            if lvl != 1:
                embed = discord.Embed(title=f'{user.name} leveled up and can now access better job',
                                      description=f'You are now level {lvl}')
                await ctx.send(embed=embed)



        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        def checkreaction(reaction, user):
            return reaction.message.id == message.id and user == ctx.author

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
                embed.set_image(url="attachment://"+random_image)
                message = await ctx.send(f"{ctx.author.mention}\n", file=file, embed=embed)
                await message.add_reaction('⬆')
                await message.add_reaction('⬇')

                try:
                    useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'cat enjoyer':
                ausgabe = '<a:catJAM:810785548678987776>'

                embed = discord.Embed(title=ausgabe)

                file_path_type = ["./cats/*.png", "./cats/*.jpg"]
                images = glob.glob(random.choice(file_path_type))
                random_image = random.choice(images)
                file = discord.File(random_image)
                print(random_image)
                embed.set_image(url="attachment://"+random_image)
                message = await ctx.send(f"{ctx.author.mention}\n", file=file, embed=embed)
                await message.add_reaction('<:catJAM:810785548678987776>')

                try:
                    useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'lemonade salesman':
                ausgabe = 'A stranger arrives and asks for some lemonade...he is strange'
                embed = discord.Embed(title=ausgabe)
                message = await ctx.send(f"{ctx.author.mention}\n", embed=embed)
                await message.add_reaction('<:lemonade:882239415601213480>')



                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send('You didnt answer fast enough!')
                    return

                em = discord.Embed(title="You gave him some lemonade, when you told him the price he gave you a *strange* look. But he paid anyways so you **didnt care**")
                await ctx.send(embed=em)
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'discord mod':
                ausgabe = 'Mute, Kick or Ban?'
                jokes = ['Singing in the shower is fun until you get soap in your mouth. Then its a soap opera.', 'What do you call a fish wearing a bowtie? Sofishticated.', 'Dear Math, grow up and solve your own problems.', 'Can a kangaroo jump higher than the empire state building? Of course! Buildings can’t jump', 'Why was the robot so tired after his road trip? He had a hard drive.', 'I was wondering why this frisbee kept looking bigger and bigger. Then it hit me.', 'A man rushed into a Doctors surgery, shouting "help me please, Im shrinking" The Doctor calmly said "now settle down a bit… youll just have to learn to be a little patient".', 'When I moved into my new igloo my friends threw me a surprise house-warming party. Now Im homeless.', 'I met my wife on Tinder. That was awkward.', 'My friend is fed up with my constant stream of dad jokes, so I asked her, "How can I stop my addiction?!" She shot back, "Whatever means necessary!!" I replied, "No, it doesnt!”', 'What’s the difference between a literalist and a kleptomaniac? A literalist takes things literally. A kleptomaniac takes things, literally.', 'ts been months since I bought the book, "How to scam people online." It still hasnt arrived yet.', "why did syndra run away from the fight? Because she had no balls <:OmegaLUL:598583138758950932>", "Why did the scarecrow win an award? Because he was outstanding in his field."]
                joke = random.choice(jokes)
                embed = discord.Embed(title=ausgabe, description=joke)
                message = await ctx.send(embed=embed)
                await message.add_reaction('🔇')
                await message.add_reaction('⛔')
                await message.add_reaction('🚫')


                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
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
                await ctx.send(f"{ctx.author.mention}\n", embed=em)
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f"You received {lohn} lemons!")
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'lemon researcher':
                ausgabe = '*Hmmm* intresting '
                facts = ["Lemons are native to Asia.", "Lemons are a hybrid between a sour orange and a citron.", "Lemons are rich in vitamin C.", "Lemons trees can produce up to 600lbs of lemons every year.", "Lemon trees produce fruit all year round.", "Lemon zest, grated rinds, is often used in baking.", "Lemon tree leaves can be used to make tea.", "The high acidity of lemons make them good cleaning aids.", "California and Arizona produces most of the United States’ lemon crop.", "The most common types of lemons are the Meyer, Eureka, and Lisbon lemons.", ]
                fact = random.choice(facts)
                embed = discord.Embed(title=ausgabe, description=fact + " <:Nerdge:814443289386156033>")
                message = await ctx.send(embed=embed)
                await message.add_reaction('<:Nerdge:814443289386156033>')

                try:
                    reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return



                em = discord.Embed(title="Well, interesting <:Nerdge:814443289386156033>")
                await ctx.send(embed=em)
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n",embed=embed)

            elif name == 'pizza guy':
                file = discord.File("./jobs/pizza.png")
                embed = discord.Embed(title="Mamma Mia! What topping this beautiful pizza shall get?", colour=discord.Color.green())
                embed.set_image(url="attachment://pizza.png")
                message= await ctx.send(embed=embed, file=file)
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
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer fast enough!")
                    return

                if reaction.emoji == '🍄':
                    await ctx.send("I hope you didnt murder Moooooshroom for that!")
                elif reaction.emoji == '🍍':
                    await ctx.send("WHY DO YOU PUT PINEAPPLE ON PIZZA?!?!?")
                elif reaction.emoji == '🌶️':
                    await ctx.send("Hooooooooooooooooooooooooot")
                elif reaction.emoji == '🥬':
                    await ctx.send("Green stuff, really?")
                elif reaction.emoji == '🧅':
                    await ctx.send("Onions are good in salads, but not on pizza")
                elif reaction.emoji == '🍗':
                    await ctx.send("Chicken, always a great decision")
                elif reaction.emoji == '🐟':
                    await ctx.send("I like fish")
                else:
                    await ctx.send("I have no idea why you put that on your pizza!")
                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f"You received {lohn} lemons!")
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            elif name == 'lemon farmer':
                rndmaufgabe = random.randrange(1, 4)

                if rndmaufgabe == 1:
                    ausgabe = 'Time to plant some grass! uuuhhhfkjdaslf I mean lemons of course... Dont do drugs kids'
                    embed = discord.Embed(title=ausgabe)
                    message = await ctx.send(f"{ctx.author.mention}\n",embed=embed)
                    await message.add_reaction('🌱')

                    try:
                        await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time and the lemons were eaten by some birds")
                        return


                elif rndmaufgabe == 2:
                    ausgabe = 'Time to water your precious lemons!'
                    embed = discord.Embed(title=ausgabe)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('🍋')

                    try:
                        await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time and your lemon trees sadly died :(")
                        return



                elif rndmaufgabe == 3:
                    ausgabe = 'Time to harvest your perfectly riped lemons'
                    embed = discord.Embed(title=ausgabe)
                    message = await ctx.send(f"{ctx.author.mention}\n", embed=embed)
                    await message.add_reaction('⛏')

                    try:
                        await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time :(")
                        return
                else:
                    await ctx.send('System Error *lmao*')

                await es.update_balance(user, lohn, 'pocket')
                embed = discord.Embed(title=f'You received {lohn} lemons!')
                await ctx.send(f"{ctx.author.mention}\n", embed=embed)

            else:
                await ctx.send(f"{ctx.author.mention}\nI think the creator didnt finish this job yet...")
                self.work.reset_cooldown(ctx)

    @work.error
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name='Sorry, in terms of health, we have no health', value=error)
        await ctx.send(embed=embed)
        print(error)




async def setup(client):
    await client.add_cog(job(client), guilds=guilds)