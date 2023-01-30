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

joblist = [{'Name': 'Lemon Farmer', 'Verdienst': 10, 'Beschreibung': ' Start little as a lemon farmer', 'lvl': 1},
           {'Name': 'Reddit Analyst', 'Verdienst': 20, 'Beschreibung': ' Carefully analyse r/woooosh posts', 'lvl': 3},
           {'Name': 'Lemonade salesman', 'Verdienst': 25, 'Beschreibung': ' sell overpriced lemonade to strangers','lvl': 4},
           {'Name': 'Discord Mod', 'Verdienst': 30, 'Beschreibung': ' Be a good Mod! Or Rocsie will get you!','lvl': 5},
           {'Name': 'Cat Enjoyer', 'Verdienst': 35,'Beschreibung': ' <a:catJAM:810785548678987776><a:catJAM:810785548678987776><a:catJAM:810785548678987776>','lvl': 6},
           {'Name': 'Lemon Researcher', 'Verdienst': 40, 'Beschreibung': ' research 🔎 lemons 🍋', 'lvl': 7},
           {'Name': 'Pizza guy', 'Verdienst': 45, 'Beschreibung': ' make some pizza 🍕', 'lvl': 8},
           {'Name': 'Aram Proplayer', 'Verdienst': 45, 'Beschreibung': ' na team, thats why high salary', 'lvl': 8},
           {'Name': 'Content Creator', 'Verdienst': 45, 'Beschreibung': ' -', 'lvl': 1000}]


async def job_helper():
    embed = discord.Embed(title='Help for the job command:',
                          description="First use `/job list` to take a look which jobs you can appeal for, then you can select them with `/job select lemon farmer` for example. After that you can work with `/work` and complete several tasks")
    embed.add_field(name='Job info', value='Look up your current job!', inline=False)
    embed.add_field(name='Job list', value='List every job!', inline=False)
    embed.add_field(name='Job select', value='Select a job that is in the list!',
                    inline=False)
    embed.add_field(name='/work', value='Work, work, work, work...', inline=False)
    embed.set_footer(text='Send job ideas to @qBaumi#1247!')
    return embed


async def getxp(id):
    data = es.sql_select(f"SELECT * FROM users WHERE id = {id}")
    xp = data[0][3]
    lvl = data[0][4]
    print(xp)
    return xp, lvl


async def add_xp(id, amount):
    xp, lvl = await getxp(id)

    sql = f"UPDATE users SET xp = {xp + amount} WHERE id = {id}"
    es.sql_exec(sql)

class job(commands.GroupCog):
    def __init__(self, client):
        self.client = client
        super().__init__()



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
                                  description='Try: */job list*, then */job select <Job>*')
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
        await interaction.response.send_message(embed=await job_helper())
    @app_commands.command(name="list", description="List all jobs")
    async def list(self, interaction: discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        await self.jobxphelp(interaction)
        embed = discord.Embed(title='Open Jobs:')
        for job in joblist:
            if job['Name'] == "Content Creator":
                continue
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
        for job in joblist:
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
                ausgabe = 'You wrote an application for the job and not even 2 hours later you received a phone call and got the job'
                tf = 1
                break

            elif arg2 != name:
                ausgabe = 'This job doesnt exist!'
                tf = 1
            else:
                await interaction.response.send_message(embed=job_helper())
                return
        if tf != 0:
            embed = discord.Embed(title=ausgabe)
            await interaction.response.send_message(f"{user.mention}", embed=embed)

    async def getjobs(self, user):
        data = es.sql_select(f"SELECT lvl FROM users WHERE id = {user.id}")
        availablejobs = []
        for job in joblist:
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

        xp, lvl = await getxp(user.id)
        await add_xp(user.id, xp_per_use)

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









async def setup(client):
    await client.add_cog(job(client), guilds=guilds)