import asyncio
import datetime
from typing import List

import cogs.essentialfunctions as es
import glob
import os
import random
import time
import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from cogs.economy import globalmainshop
import cogs.pet
from discord import app_commands
from discord import ui
from config import guilds, allowedAdminRoles
from discord.app_commands import Choice
from config import allowedAdminRoles, guilds




class items(commands.Cog):
    def __init__(self, client):
        self.client = client

    mainshop = globalmainshop

    #DISPLAYS USER BAG
    @app_commands.command(name="bag", description="Show your items")
    async def bag(self, interaction : discord.Interaction):
        if not await es.interaction_check_account(interaction):
            return
        await es.open_account(interaction.user)
        user = interaction.user

        try:
            bag = await es.getbag(user.id)
        except:
            bag = []

        em = discord.Embed(title="Bag")
        for item in bag:
            name = item["item"]
            name_ = name.capitalize()
            amount = item["amount"]
            if amount > 0:
                em.add_field(name=name_, value=amount, inline=False)
        await interaction.response.send_message(embed=em)





    @app_commands.command(name="use", description="Use an item from your bag")
    @app_commands.describe(item="The item you use")
    async def use(self, interaction : discord.Interaction, item : str):
        if not await es.interaction_check_account(interaction):
            return
        if item == "None":
            await interaction.response.send_message(f"{interaction.user.mention}\nYou cant use nothing")
            return
        class ctx():
            author = interaction.user
            channel = interaction.channel

        """Globals"""
        user = interaction.user

        """
        Check if an item is in users bag and amount is bigger than 0
        checkifitem == 0 : user doesnt have item
        checkifitem == 1 : user has item
        """
        checkifitem = 0
        index = -1
        userbag = await es.getbag(user.id)
        for item_ in userbag:
            item_name = item_["item"]
            item_amount = item_["amount"]
            index = index + 1
            if item.lower() == item_name.lower():
                if item_amount <= 0:
                    await interaction.response.send_message(f"{ctx.author.mention}\nYou dont have {item_name.capitalize()}")
                    return
                else:
                    checkifitem = 1
                break
        if checkifitem == 0:
            if userbag[index]["item"] != item.lower():
                await interaction.response.send_message(f"{ctx.author.mention}\nYou dont have {item.capitalize()}")
                return


        item = item.lower()
        if item == "lemonade":
            await interaction.response.send_message(
                f"{ctx.author.mention}\nYou just drank lemonade that was made by lemons, that you bought with the lemons, that you get paid as a lemon farmer for harvesting lemons")
            await interaction.channel.send("But atleast you got refreshed, so who cares")
            await interaction.channel.send("<:FeelsDankMan:810802803739983903>")
            await es.del_item(ctx.author.id, item)

            return
        if item == "candy":
            lines = ["You like the candy, because it tasted like lemon!", "You didnt like this candy",
                     "You spit the candy out, because it was so gross", "Mmmmm lime also tastes good",
                     "You threw the ananas candy in the trash, because you were eating pizza at the same time"]
            line = random.choice(lines)
            await interaction.response.send_message(line)
            await es.del_item(ctx.author.id, item)
            return

        if item == "flowers":
            await interaction.response.send_message(f"{ctx.author.mention}\nWho will be the happy one that gets your beautiful flowers?")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send("You didnt answer in time")
                return
            lines = ["cried of happiness", "said thank you", "thanked you for them", "put them in a vase",
                     "was confused", "is allergic to flowers", "was angry because they are bad ones",
                     "doesnt like the colour of the flowers"]
            line = random.choice(lines)

            try:
                class id:
                    id = msg.content[3:len(msg.content) - 1]
                    id = int(id)

                print(msg.content)

                print(id)

                await es.del_item(ctx.author.id, item)
                await interaction.channel.send(f"You gifted your flowers to {msg.content}, they " + line)

                try:
                    await es.add_item(item_name="flowers", userid=id.id, amount=1)
                    return
                except:
                    await interaction.channel.send(
                        f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                    return

            except:
                await interaction.channel.send(
                    f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                return

        if item == "safe":

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "dep" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "depot" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "with" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "withdraw" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "witd" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "deposit"

            users = await es.get_bank_data(user.id)
            try:
                mysql = f"SELECT money FROM safe WHERE id = {user.id}"
                data = es.sql_select(mysql)
                print(data[0][0])
                money = data[0][0]
            except:
                mysql = f"INSERT INTO safe (id, money) VALUES ({user.id}, 0)"
                es.sql_exec(mysql)
                money = 0
            em = discord.Embed(colour=discord.Color.dark_gray(), title="Your safe <:safe:885811224418332692>",
                               description=f"`{money}` lemons")
            await interaction.response.send_message(f"{user.mention}\nDo you want to `deposit` or `withdraw` money from your safe?", embed=em)
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send(f"{user.mention}\nYou didnt answer in time")
                return

            if msg.content.lower() == "dep" or msg.content.lower() == "depot" or msg.content.lower() == "deposit":
                userbal = users[str(user.id)]["pocket"]

                def checkmoney(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                await interaction.channel.send(f"{user.mention}\nHow much lemons do you want to deposit?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkmoney)
                except:
                    await interaction.channel.send(f"{user.mention}\nYou didnt answer in time")
                    return
                try:

                    amountmoney = int(msg.content)
                except:
                    await interaction.channel.send(f"{user.mention}\nNo")
                    return
                if amountmoney < 0:
                    await interaction.channel.send(f"{user.mention}\nYou know, you can also `withdraw` money")
                    return
                if userbal < amountmoney:
                    await interaction.channel.send(f"{user.mention}\nYou dont have enough money!")
                    return
                maxamount = 5000
                if money + amountmoney > 5000:
                    await interaction.channel.send(f"{user.mention}\nYou can only store `5000` lemons in your safe!")
                    return

                newamt = money + amountmoney
                sql = f"UPDATE safe SET money = {newamt} WHERE id = {user.id}"
                es.sql_exec(sql)
                await es.update_balance(user, -1 * amountmoney)
                await interaction.channel.send(f"{user.mention}\nYou now have `{newamt}` lemons stored in your safe")
                return
            if msg.content.lower() == "withdraw" or msg.content.lower() == "witd" or msg.content.lower() == "with":
                userbal = users[str(user.id)]["pocket"]

                def checkmoney(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                await interaction.response.send_message(f"{user.mention}\nHow much lemons do you want to withdraw?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkmoney)
                except:
                    await interaction.channel.send(f"{user.mention}\nYou didnt answer in time")
                    return
                try:
                    amountmoney = int(msg.content)
                except:
                    await interaction.channel.send(f"{user.mention}\nNo")
                    return
                if amountmoney < 0:
                    await interaction.channel.send(f"{user.mention}\nYou know, you can also `deposit` money")
                    return

                if amountmoney > money:
                    await interaction.channel.send(f"{user.mention}\nYou dont have enough lemons in your safe!")
                    return

                newamt = money - amountmoney
                sql = f"UPDATE safe SET money = {newamt} WHERE id = {user.id}"
                es.sql_exec(sql)

                await es.update_balance(user, amountmoney)
                await interaction.channel.send(f"{user.mention}\nYou now have `{newamt}` lemons stored in your safe")
                return
            return

        if item == "present":
            await interaction.response.send_message(f"{ctx.author.mention}\nWhat item do you want to gift?")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return

            present_item_index = -1
            itemreal = 0
            userbag = await es.getbag(ctx.author.id)
            for present_item in userbag:
                present_item_name = present_item["item"]
                present_item_amount = present_item["amount"]
                present_item_index = index + 1
                present_item_name = present_item_name.lower()
                if msg.content.lower() == present_item_name.lower():
                    if present_item_amount <= 0:
                        await interaction.channel.send(f"{ctx.author.mention}\nYou dont have {present_item_name.capitalize()}")
                        return
                    itemreal = 1
                    break
            if itemreal == 0:
                await interaction.channel.send(f"{ctx.author.mention}\nThat item doesnt exist or you dont have it!")
                return

            ###now user
            lines = ["cried of happiness", "said thank you", "thanked you for it",
                     "was confused"]
            line = random.choice(lines)

            await interaction.channel.send(f"{ctx.author.mention}\nWho will be the happy one? (@ them)")

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return

            try:
                class id:
                    id = msg.content[3:len(msg.content) - 1]
                    id = int(id)

                print(msg.content)

                print(id)
                if user.id == id.id:
                    await interaction.channel.send(f"{ctx.author.mention}\nYou cant just give yourself a present!")
                    return

                await es.del_item(ctx.author.id, item)

                await interaction.channel.send(f"{ctx.author.mention}\nYou gifted {present_item_name} to {msg.content}, they " + line)

                for shopitem in self.mainshop:
                    price = shopitem["price"]
                    if shopitem["name"].lower() == present_item_name.lower():
                        break
                try:
                    await es.del_item(ctx.author.id, present_item_name.lower())
                    await es.add_item(item_name=present_item_name, userid=id.id, amount=1)
                    return
                except:
                    await interaction.channel.send(
                        f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                    return

            except:
                await interaction.channel.send(
                    f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                return

            return

        if item == "conchshell":
            await interaction.response.send_message.send(
                f"{ctx.author.mention}\nAhhh I see, you need Trustpilot 10⭐ advice...what lies on your heart my friendo?")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            message = await interaction.channel.send("*Ziiip*")
            time.sleep(4)
            lines = ["Yes", "No", "Why", "I dont know", "Ask again", "Of course", "No you are not", "Take the RTX 3060",
                     "No dont buy Intel CPUs", "I know the answer", "The answer is:",
                     "Why always ask me? You dont have a brain?", "No Squidward, you cant have anything to eat",
                     "Long live the Conch Shell"]
            advice = random.choice(lines)
            await message.edit(content=advice)
            return

        if item == "mobile":
            em = discord.Embed(title="Who do you want to call?", colour=discord.Color.dark_blue(),
                               description="`krusty crab`\n`telephone joker`\n`911`")
            em.set_footer(text="Just type the name")
            await interaction.response.send_message(embed=em)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "krusty crab" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "telephone joker" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "911"

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send("You didnt answer in time")
                return
            message = await interaction.channel.send("Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
            time.sleep(2.5)
            await message.edit(content="Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
            time.sleep(3)
            if msg.content.lower() == "krusty crab":
                await message.edit(content="You: Hello, is this the Krusty Crab?")
                time.sleep(4)
                await message.edit(content="Krusty Crab: No, this is Patrick")
                time.sleep(4.2)
                await message.edit(content="You: Are you sure this isn't the Krusty Crab?")
                time.sleep(4.5)
                await message.edit(content="Krusty Crab: NO, THIS IS PATRICK")
                time.sleep(4)
                await message.edit(content="Patrick hung up on you...but you are calling again")
                time.sleep(4.5)
                await message.edit(content="Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
                time.sleep(4.5)
                await message.edit(content="Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
                time.sleep(4.5)
                await message.edit(
                    content="You are talking in a slightly higher voice: Hello, is this the Krusty Crab?")
                time.sleep(4)
                await message.edit(content="KrUsTy CrAb: NoOoOoOoOoOoOoOo ThIs Is PaTrIcK")
                time.sleep(4)
                await message.edit(content="`deeeeepieeebieeep`")
                return
            if msg.content == "911":
                await message.edit(content="You: HELP ME HELP ME PLEASE IM GETTING ROBBED")
                time.sleep(7)
                await message.edit(content="Someone: You're POOR so it doesn't matter anyway")
                time.sleep(7.5)
                await message.edit(content="`deeeeepieeebieeep`")
                return
            if msg.content == "telephone joker":
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
                await message.edit(content=joke)
                return

        if item == "laptop":
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            def checkreaction(reaction_, reactionuser):
                return reaction_.message.id == message.id and reactionuser == ctx.author
            await interaction.response.send_message("💻")
            message = await interaction.channel.send("What do you want to do on your computer?\n`Browse`\n`Minecraft`\n`Make memes`\n`Stream`")
            await message.add_reaction('<:GoogleChrome:883281638270844958>')
            await message.add_reaction('<:minecra:883287114270261268>')
            await message.add_reaction('<:FeelsDankMan:810802803739983903>')
            await message.add_reaction('💻')
            # YOU NEED TO AWAIT LMAO
            try:
                reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
            except asyncio.TimeoutError:
                await interaction.channel.send('You didnt answer fast enough!')
                return
            print(reaction.emoji)
            if str(reaction.emoji) == "<:GoogleChrome:883281638270844958>":
                msg = await interaction.channel.send(
                    f"{ctx.author.mention}\nWhat do you want to browse on the web?\n`animals`\n`memes`\n`random facts`")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=check)
                except:
                    await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                if msg.content.lower() == "animals":
                    embed = discord.Embed(title="*Cute?*")

                    file_path_type = ["./animals/*.png", "./animals/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await interaction.channel.send(file=file, embed=embed)
                    return
                elif msg.content.lower() == "memes":

                    embed = discord.Embed(title="*Funney?*")

                    file_path_type = ["./memes/*.png", "./memes/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await interaction.channel.send(file=file, embed=embed)

                    return
                elif msg.content.lower() == "random facts":

                    embed = discord.Embed(title="*Interestestestesting*")

                    file_path_type = ["./randomfacts/*.png", "./randomfacts/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await interaction.channel.send(file=file, embed=embed)

                    return
                else:
                    await interaction.channel.send("You cant browse that!")
                    return
                return
            if str(reaction.emoji) == "<:minecra:883287114270261268>":
                sql = "SELECT id FROM users"
                data = es.sql_select(sql)
                print(data)
                users = data

                userlist = []
                for user in users:
                    userlist.append(user)
                print(userlist)
                user = random.choice(userlist)
                print(user)
                user = user[0]
                lines = [f"You and <@!{user}> built a wooden house!",
                         f"You and <@!{user}> played Minecraft for 5 hours",
                         f"<@!{user}> set you a redstone trap and you fell for it",
                         f"<@!{user}> and you built a lemon tree", f"<@!{user}> and you built a big mansion",
                         f"<@!{user}> and you built a giant mob farm"]
                line = random.choice(lines)
                await interaction.channel.send(line)
                return
            if str(reaction.emoji) == "💻":
                sql = "SELECT id FROM users"
                data = es.sql_select(sql)
                users = data
                userlist = []
                for user in users:
                    userlist.append(user)
                user = random.choice(userlist)
                user = user[0]
                viewerlist = [0, 30, 100, 300, 500, 1000, 3000]
                viewerlistindexes = [0, 1, 2, 3, 4, 5, 6]
                minviewersindex = 6#random.choices(viewerlistindexes, weights=(70, 50, 30, 20, 10, 5, 2), k=1)[0]
                minviewers = viewerlist[minviewersindex]
                if minviewersindex != 6:
                    maxviewers = viewerlist[minviewersindex+1]
                else:
                    maxviewers = 5000
                viewers = random.randrange(minviewers, maxviewers)
                games = ["TFT", "League of Legends", "Aram", "Valorant", "Hot Tub Stream"]
                hours = random.randrange(1, 15)
                line = f"You streamed `{random.choice(games)}` for `{hours}` hours with on average `{viewers}` viewers"
                await interaction.channel.send(line)
                if viewers >= 1000:
                    msg = await interaction.channel.send(f"🎉 Congratulations, you blew up on the internet. You have enough following now to pursue a career as a streamer. Do you want to quit your job to become a content creator?")
                    await msg.add_reaction('✅')
                    try:
                        reaction2, useremoji2 = await self.client.wait_for('reaction_add', timeout=5, check=checkreaction)
                    except asyncio.TimeoutError:
                        await interaction.channel.send(f"{user.mention}\nYou didnt answer fast enough!")
                        return
                    print("streamer")
                    print(reaction2.emoji)
                    if str(reaction2.emoji) == '✅':
                        try:
                            data = es.sql_select(f"SELECT * FROM jobs WHERE id = {user.id}")
                            userjob = [{"Name": data[0][1], "Verdienst": data[0][2]}]
                        except:
                            userjob = []
                        if bool(userjob) == False:
                            es.sql_exec(
                                f"INSERT INTO jobs (id, Name, Verdienst) VALUES ({user.id}, 'Content Creator', 50)")
                        else:
                            es.sql_exec(f"UPDATE jobs SET Name = 'Content Creator' WHERE id = {user.id}")
                            es.sql_exec(f"UPDATE jobs SET Verdienst = 50 WHERE id = {user.id}")
                        await interaction.channel.send(f"{user.mention}\nYou now work as Content Creator!")

                return
            if str(reaction.emoji) == "<:FeelsDankMan:810802803739983903>":
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                folder = os.listdir('./memes/templates')
                print(folder)
                em = discord.Embed(title="Which template you would like to use?", colour=discord.Color.green())
                for path in folder:
                    if path != "img.png":
                        string = path.split(".")
                        em.add_field(name=string[0], value="\u200b", inline=False)
                em.set_footer(text="Send your templates to qBaumi, NOW!")
                message = await interaction.channel.send(f"{user.mention}\n", embed=em)
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=check)
                except:
                    await interaction.channel.send("You didnt answer in time!")
                    return
                isreal = False

                for path in folder:

                    string = path.split(".")
                    print(msg.content.lower())
                    print(string)
                    if msg.content.lower() == string[0].lower():
                        isreal = True
                        break
                if isreal == False:
                    await interaction.channel.send("This template does not exist! *But if you have one send it to qBaumi*")
                    return
                await interaction.channel.send(f"{user.mention}\nWhat do you want to write on that beautiful template?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=check)
                except:
                    await interaction.channel.send("You didnt answer in time!")
                    return
                img = Image.open("./memes/templates/" + path)
                width, height = img.size
                draw = ImageDraw.Draw(img)
                color = 'rgb(255, 255, 255)'  # white color
                font = ImageFont.truetype('./fonts/Roboto-Bold.ttf', size=45)
                draw.text((10, height - 55), msg.content, fill=color, font=font)
                img.save("./memes/templates/img.png")

                em = discord.Embed(colour=discord.Color.green(), title="Great job!")
                file = discord.File("./memes/templates/img.png")
                em.set_image(url="attachment://img.png")
                await interaction.channel.send(file=file, embed=em)

                return

        if item == "cheesecake":
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "eat" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "throw" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "share"

            def checkperson(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await interaction.response.send_message(
                f"{ctx.author.mention}\nDo you want to `eat`, `throw` or `share` the cake? (Answer with `eat`, `throw` or `share`)")

            # YOU NEED TO AWAIT LMAO
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            if msg.content.lower() == "eat":
                await interaction.channel.send(f"{ctx.author.mention}\nYou ate your cheesecake, it was very delicious")

            elif msg.content.lower() == "share":
                await interaction.channel.send(f"{ctx.author.mention}\nWith whom you want to share your cheesecake?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                person = msg.content
                await interaction.channel.send(f"{ctx.author.mention}\nYou shared your cake with {person}!")

            else:
                await interaction.channel.send(f"{ctx.author.mention}\nWho will be your victim?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                person = msg.content
                await interaction.channel.send(f"{ctx.author.mention}\nYou throw your cake at {person}")

            await es.del_item(interaction.user.id, item)
            return

        if item == "pinata":

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "use" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "gift"

            def checkperson(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await interaction.response.send_message(
                f"{ctx.author.mention}\nDo you want to `use` or `gift` the pinata? (Answer with `use` or `gift`)")

            # YOU NEED TO AWAIT LMAO
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            if msg.content.lower() == "use":
                times = random.randrange(2, 10)
                candy = random.randrange(3, 7)
                print(candy)
                await interaction.channel.send(
                    f"{ctx.author.mention}\nAfter you hit 🏏 the pinata `{times}` times you got {candy} candy!")
                await es.del_item(ctx.author.id, item)

                # IMPORTANT THE WITH OPEN BEFORE THE UPDATE OR IT WILL OVERWRITE THIS STUPID BAL AND BUYTHIS
                await es.add_item("candy", user.id, candy)



            else:
                await interaction.channel.send(f"{ctx.author.mention}\nWho gets the pinata?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await interaction.channel.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                try:
                    class id:
                        id = msg.content[3:len(msg.content) - 1]
                        id = int(id)

                    print(msg.content)
                    print(id)
                    await es.del_item(ctx.author.id, item)
                    await interaction.channel.send(
                        f"{ctx.author.mention}\nYou gifted your pinata to {msg.content}, muchas gracias they said")

                    try:
                        await es.add_item("pinata", id.id, 1)
                        return
                    except:
                        await interaction.channel.send(
                            f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                        return
                except:
                    await interaction.channel.send(
                        f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                    return
        """
        if item == "adventcalendar":
            date = datetime.date.today()
            date = str(date)
            print(date)
            if(date[0:8] != "2021-11-"):
                await ctx.send("It's unfortunately not December <:Sadge:720250426892615745>")
                return

            day = int(date[8:len(date)])
            print(day)
            prizes = [{"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"},
                      {"amount" : 10, "moneyform" : "pocket"}]

            
            Here comes the part to check if user can still claim the prize
            
            sql = f"SELECT * FROM adventcalendar WHERE id = '{ctx.author.id}' AND day = {day}"
            mycursor.execute(sql)
            data = mycursor.fetchall()
            print(data)
            if data:
                em = discord.Embed(title="You already opened todays door! Come back tomorrow!", colour=discord.Color.teal())
                await ctx.send(embed=em)
                return
            i = day-1
            await es.update_balance(ctx.author, prizes[i]["amount"], prizes[i]["moneyform"])
            sql = f"INSERT INTO adventcalendar (id, day) VALUES ('{ctx.author.id}', {day})"
            mycursor.execute(sql)
            mydb.commit()
            if prizes[i]['moneyform'] == "pocket":
                money = "lemons"
                moneyemoji = "<:lemon2:881595266757713920>"
            else:
                money = "golden lemons"
                moneyemoji = "<:GoldenLemon:882634893039923290>"
            em = discord.Embed(title=f"You opened the door of the {day}th december and you got `{prizes[i]['amount']}` {moneyemoji} {money}!", colour=discord.Color.teal(), description="Have a great day!")
            await ctx.send(embed=em)"""
        if item == "treat":
            stupidpetsclass = cogs.pet.pet(self.client)
            await cogs.pet.pet.treat_helper(stupidpetsclass, interaction)
            await es.del_item(interaction.user.id, item)
            stupidpetsclass = None
        else:
            await interaction.response.send_message.send(f"{ctx.author.mention}\nThat item does not exist or has no usage yet")

    @use.autocomplete('item')
    async def use_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        items = await es.getChoices(interaction.user)
        return [
            app_commands.Choice(name=item, value=item.lower())
            for item in items if current.lower() in item.lower()
        ]

async def setup(client):
    await client.add_cog(items(client), guilds=guilds)

