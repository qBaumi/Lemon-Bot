import asyncio
import datetime

import cogs.essentialfunctions as es
import glob
import os
import random
import time
import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from cogs.economy import globalmainshop


"""Globals"""
mycursor = es.mycursor
mydb = es.mydb

class items(commands.Cog):
    def __init__(self, client):
        self.client = client

    mainshop = globalmainshop

    """DISPLAYS USER BAG"""
    @commands.command(aliases=["items"])
    async def bag(self, ctx):
        """FALSY CHECKS"""
        if not await es.check_account(ctx):
            return
        await es.open_account(ctx.author)
        user = ctx.author

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
        await ctx.send(embed=em)

    @commands.command()
    async def use(self, ctx, item="None"):


        if not await es.check_account(ctx):
            return
        if item == "None":
            await ctx.send(f"{ctx.author.mention}\nYou cant use nothing")
            return

        """Globals"""
        user = ctx.author

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
                    await ctx.send(f"{ctx.author.mention}\nYou dont have {item_name.capitalize()}")
                    return
                else:
                    checkifitem = 1
                break
        if checkifitem == 0:
            if userbag[index]["item"] != item.lower():
                await ctx.send(f"{ctx.author.mention}\nYou dont have {item.capitalize()}")
                return


        item = item.lower()
        if item == "lemonade":
            await ctx.send(
                f"{ctx.author.mention}\nYou just drank lemonade that was made by lemons, that you bought with the lemons, that you get paid as a lemon farmer for harvesting lemons")
            await ctx.send("But atleast you got refreshed, so who cares")
            await ctx.send("<:FeelsDankMan:810802803739983903>")
            await es.del_item(ctx.author.id, item)

            return
        if item == "candy":
            lines = ["You like the candy, because it tasted like lemon!", "You didnt like this candy",
                     "You spit the candy out, because it was so gross", "Mmmmm lime also tastes good",
                     "You threw the ananas candy in the trash, because you were eating pizza at the same time"]
            line = random.choice(lines)
            await ctx.send(line)
            await es.del_item(ctx.author.id, item)
            return

        if item == "flowers":
            await ctx.send(f"{ctx.author.mention}\nWho will be the happy one that gets your beautiful flowers?")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send("You didnt answer in time")
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
                await ctx.send(f"You gifted your flowers to {msg.content}, they " + line)

                try:
                    await es.add_item(item_name="flowers", userid=id.id, amount=1)
                    return
                except:
                    await ctx.send(
                        f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                    return

            except:
                await ctx.send(
                    f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                return

        if item == "safe":

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "dep" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "depot" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "with" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "withdraw" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "witd" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "deposit"

            users = await es.get_bank_data(user.id)
            try:
                mysql = f"SELECT money FROM safe WHERE id = {user.id}"
                mycursor.execute(mysql)
                data = mycursor.fetchall()
                print(data[0][0])
                money = data[0][0]
            except:
                mysql = f"INSERT INTO safe (id, money) VALUES ({user.id}, 0)"
                mycursor.execute(mysql)
                mydb.commit()
                money = 0
            em = discord.Embed(colour=discord.Color.dark_gray(), title="Your safe <:safe:885811224418332692>",
                               description=f"`{money}` lemons")
            await ctx.send(f"{user.mention}\nDo you want to `deposit` or `withdraw` money from your safe?", embed=em)
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{user.mention}\nYou didnt answer in time")
                return

            if msg.content.lower() == "dep" or msg.content.lower() == "depot" or msg.content.lower() == "deposit":
                userbal = users[str(user.id)]["pocket"]

                def checkmoney(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                await ctx.send(f"{user.mention}\nHow much lemons do you want to deposit?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkmoney)
                except:
                    await ctx.send(f"{user.mention}\nYou didnt answer in time")
                    return
                try:

                    amountmoney = int(msg.content)
                except:
                    await ctx.send(f"{user.mention}\nNo")
                    return
                if amountmoney < 0:
                    await ctx.send(f"{user.mention}\nYou know, you can also `withdraw` money")
                    return
                if userbal < amountmoney:
                    await ctx.send(f"{user.mention}\nYou dont have enough money!")
                    return
                maxamount = 5000
                if money + amountmoney > 5000:
                    await ctx.send(f"{user.mention}\nYou can only store `5000` lemons in your safe!")
                    return

                newamt = money + amountmoney
                sql = f"UPDATE safe SET money = {newamt} WHERE id = {user.id}"
                mycursor.execute(sql)
                mydb.commit()
                await es.update_balance(user, -1 * amountmoney)
                await ctx.send(f"{user.mention}\nYou now have `{newamt}` lemons stored in your safe")
                return
            if msg.content.lower() == "withdraw" or msg.content.lower() == "witd" or msg.content.lower() == "with":
                userbal = users[str(user.id)]["pocket"]

                def checkmoney(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                await ctx.send(f"{user.mention}\nHow much lemons do you want to withdraw?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkmoney)
                except:
                    await ctx.send(f"{user.mention}\nYou didnt answer in time")
                    return
                try:
                    amountmoney = int(msg.content)
                except:
                    await ctx.send(f"{user.mention}\nNo")
                    return
                if amountmoney < 0:
                    await ctx.send(f"{user.mention}\nYou know, you can also `deposit` money")
                    return

                if amountmoney > money:
                    await ctx.send(f"{user.mention}\nYou dont have enough lemons in your safe!")
                    return

                newamt = money - amountmoney
                sql = f"UPDATE safe SET money = {newamt} WHERE id = {user.id}"
                mycursor.execute(sql)
                mydb.commit()

                await es.update_balance(user, amountmoney)
                await ctx.send(f"{user.mention}\nYou now have `{newamt}` lemons stored in your safe")
                return
            return

        if item == "present":
            await ctx.send(f"{ctx.author.mention}\nWhat item do you want to gift?")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
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
                        await ctx.send(f"{ctx.author.mention}\nYou dont have {present_item_name.capitalize()}")
                        return
                    itemreal = 1
                    break
            if itemreal == 0:
                await ctx.send(f"{ctx.author.mention}\nThat item doesnt exist or you dont have it!")
                return

            ###now user
            lines = ["cried of happiness", "said thank you", "thanked you for it",
                     "was confused"]
            line = random.choice(lines)

            await ctx.send(f"{ctx.author.mention}\nWho will be the happy one? (@ them)")

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return

            try:
                class id:
                    id = msg.content[3:len(msg.content) - 1]
                    id = int(id)

                print(msg.content)

                print(id)
                if user.id == id.id:
                    await ctx.send(f"{ctx.author.mention}\nYou cant just give yourself a present!")
                    return

                await es.del_item(ctx.author.id, item)

                await ctx.send(f"{ctx.author.mention}\nYou gifted {present_item_name} to {msg.content}, they " + line)

                for shopitem in self.mainshop:
                    price = shopitem["price"]
                    if shopitem["name"].lower() == present_item_name.lower():
                        break
                try:
                    await es.del_item(ctx.author.id, present_item_name.lower())
                    await es.add_item(item_name=present_item_name, userid=id.id, amount=1)
                    return
                except:
                    await ctx.send(
                        f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                    return

            except:
                await ctx.send(
                    f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                return

            return

        if item == "conchshell":
            await ctx.send(
                f"{ctx.author.mention}\nAhhh I see, you need Trustpilot 10⭐ advice...what lies on your heart my friendo?")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            message = await ctx.send("*Ziiip*")
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
            await ctx.send(embed=em)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "krusty crab" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "telephone joker" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "911"

            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send("You didnt answer in time")
                return
            message = await ctx.send("Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep")
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

            def checkreaction(reaction, user):
                return reaction.message.id == message.id and user == ctx.author

            message = await ctx.send("What do you want to do on your computer?\n`Browse`\n`Minecraft`\n`Make memes`")
            await message.add_reaction('<:GoogleChrome:883281638270844958>')
            await message.add_reaction('<:minecra:883287114270261268>')
            await message.add_reaction('<:FeelsDankMan:810802803739983903>')
            # YOU NEED TO AWAIT LMAO
            try:
                reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
            except asyncio.TimeoutError:
                await ctx.send('You didnt answer fast enough!')
                return
            print(reaction.emoji)
            if str(reaction.emoji) == "<:GoogleChrome:883281638270844958>":
                msg = await ctx.send(
                    f"{ctx.author.mention}\nWhat do you want to browse on the web?\n`animals`\n`memes`\n`random facts`")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=check)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                if msg.content.lower() == "animals":
                    embed = discord.Embed(title="*Cute?*")

                    file_path_type = ["./animals/*.png", "./animals/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await ctx.send(file=file, embed=embed)
                    return
                elif msg.content.lower() == "memes":

                    embed = discord.Embed(title="*Funney?*")

                    file_path_type = ["./memes/*.png", "./memes/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await ctx.send(file=file, embed=embed)

                    return
                elif msg.content.lower() == "random facts":

                    embed = discord.Embed(title="*Interestestestesting*")

                    file_path_type = ["./randomfacts/*.png", "./randomfacts/*.jpg"]
                    images = glob.glob(random.choice(file_path_type))
                    random_image = random.choice(images)
                    file = discord.File(random_image)
                    print(random_image)
                    embed.set_image(url="attachment://" + random_image)
                    message = await ctx.send(file=file, embed=embed)

                    return
                else:
                    await ctx.send("You cant browse that!")
                    return
                return
            if str(reaction.emoji) == "<:minecra:883287114270261268>":
                sql = "SELECT id FROM users"
                mycursor.execute(sql)
                data = mycursor.fetchall()
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
                await ctx.send(line)
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
                message = await ctx.send(f"{user.mention}\n", embed=em)
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=check)
                except:
                    await ctx.send("You didnt answer in time!")
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
                    await ctx.send("This template does not exist! *But if you have one send it to qBaumi*")
                    return
                await ctx.send(f"{user.mention}\nWhat do you want to write on that beautiful template?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=check)
                except:
                    await ctx.send("You didnt answer in time!")
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
                await ctx.send(file=file, embed=em)

                return

        if item == "cheesecake":
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "eat" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "throw" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "share"

            def checkperson(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send(
                f"{ctx.author.mention}\nDo you want to `eat`, `throw` or `share` the cake? (Answer with `eat`, `throw` or `share`)")

            # YOU NEED TO AWAIT LMAO
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            if msg.content.lower() == "eat":
                await ctx.send(f"{ctx.author.mention}\nYou ate your cheesecake, it was very delicious")

            elif msg.content.lower() == "share":
                await ctx.send(f"{ctx.author.mention}\nWith whom you want to share your cheesecake?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                person = msg.content
                await ctx.send(f"{ctx.author.mention}\nYou shared your cake with {person}!")

            else:
                await ctx.send(f"{ctx.author.mention}\nWho will be your victim?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                person = msg.content
                await ctx.send(f"{ctx.author.mention}\nYou throw your cake at {person}")

            await es.del_item(ctx.author.id, item)
            return

        if item == "pinata":

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "use" or m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "gift"

            def checkperson(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send(
                f"{ctx.author.mention}\nDo you want to `use` or `gift` the pinata? (Answer with `use` or `gift`)")

            # YOU NEED TO AWAIT LMAO
            try:
                msg = await self.client.wait_for("message", timeout=60, check=check)
            except:
                await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                return
            if msg.content.lower() == "use":
                times = random.randrange(2, 10)
                candy = random.randrange(3, 7)
                print(candy)
                await ctx.send(
                    f"{ctx.author.mention}\nAfter you hit 🏏 the pinata `{times}` times you got {candy} candy!")
                await es.del_item(ctx.author.id, item)

                # IMPORTANT THE WITH OPEN BEFORE THE UPDATE OR IT WILL OVERWRITE THIS STUPID BAL AND BUYTHIS

                await es.add_item("candy", user.id, candy)



            else:
                await ctx.send(f"{ctx.author.mention}\nWho gets the pinata?")
                try:
                    msg = await self.client.wait_for("message", timeout=60, check=checkperson)
                except:
                    await ctx.send(f"{ctx.author.mention}\nYou didnt answer in time")
                    return
                try:
                    class id:
                        id = msg.content[3:len(msg.content) - 1]
                        id = int(id)

                    print(msg.content)
                    print(id)
                    await es.del_item(ctx.author.id, item)
                    await ctx.send(
                        f"{ctx.author.mention}\nYou gifted your pinata to {msg.content}, muchas gracias they said")

                    try:
                        await es.add_item("pinata", id.id, 1)
                        return
                    except:
                        await ctx.send(
                            f"{ctx.author.mention}\nSelf defending mechanism activated. Something didnt work, qBaumi doesnt know why, but if anyone lost something CONTACT him. RIGHT NOW")
                        return
                except:
                    await ctx.send(
                        f"{ctx.author.mention}\n{msg.content} is not a user or has never used this bot before. `Answer with @friend if you just typed their name`")
                    return
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

            """
                Here comes the part to check if user can still claim the prize
            """
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
            await ctx.send(embed=em)
        else:
            await ctx.send(f"{ctx.author.mention}\nThat item does not exist or has no usage yet")


def setup(client):
    client.add_cog(items(client))