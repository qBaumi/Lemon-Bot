import datetime
import discord
from discord.ext import commands, tasks
import random, asyncio, json

from pytz import timezone

import cogs.essentialfunctions as es
from discord import app_commands
from config import guilds

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=21, minute=58)
time.replace(timezone('CET'))

class pet(commands.GroupCog):
    def __init__(self, client):
        super().__init__()
        self.client = client


    @app_commands.command(name="info", description="View your pet, its stats and interact with it")
    async def info(self, interaction : discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        pet1 = await self.userpet(user.id, "petslot1")
        pet2 = await self.userpet(user.id, "petslot2")
        pet3 = await self.userpet(user.id, "petslot3")
        if bool(pet) == False and bool(pet1) == False and bool(pet2) == False and bool(pet3) == False:
            await interaction.response.send_message("You dont have a pet!")
            return
        if bool(pet) == False:
            await interaction.response.send_message(
                "You dont have a pet equipped! You can buy one with `/pet buy petname` from the `/pet shop` or equip a pet with `/pet equip`.\nFor further information try `/pet help`")
            return

        em = discord.Embed(colour=discord.Color.teal(), title=pet["name"])
        em.add_field(name="Stats:", value=f'{pet["hp"]} ❤\n{pet["attack"]}  🗡️\n{pet["speed"]}  💨', inline=False)

        def bar(bar, emoji="🟥"):
            string = ""
            xpbar = pet[bar] / 8
            xpbar = int(xpbar)
            rest = 12 - xpbar
            for x in range(xpbar):
                string += emoji
            for i in range(rest):
                string += "⬛"
            return string

        em.add_field(name=f'Level: {pet["lvl"]}', value=bar("xp", "🟦"), inline=False)
        em.add_field(name=f'🥩Food', value=bar("food"), inline=False)
        em.add_field(name=f'⚡Stamina', value=bar("stamina"), inline=False)
        em.add_field(name=f'🧼Care', value=bar("care"), inline=False)
        em.add_field(name=f'😸Fun', value=bar("fun"), inline=False)

        em.add_field(name="Item:", value="Added soon", inline=False)
        em.add_field(name="Moveset:", value=f'{pet["attack1"]}\n{pet["attack2"]}', inline=False)

        file = discord.File(f'./pets/{pet["img"]}')
        em.set_image(url=f'attachment://{pet["img"]}')
        await interaction.response.send_message(file=file, embed=em, view=self.InfoButtons(petsclass=self))


    # Define a simple View that gives us buttons
    class InfoButtons(discord.ui.View):

        def __init__(self, petsclass):
            super().__init__()
            self.petsclass = petsclass

        @discord.ui.button(label='🥫', style=discord.ButtonStyle.blurple)
        async def feed(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.petsclass.feed_helper(interaction)


        @discord.ui.button(label='🛀🏻', style=discord.ButtonStyle.blurple)
        async def care(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.petsclass.care_helper(interaction)

        @discord.ui.button(label='⚾', style=discord.ButtonStyle.blurple)
        async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.petsclass.play_helper(interaction)

        @discord.ui.button(label='🦮', style=discord.ButtonStyle.blurple)
        async def walk(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.petsclass.walk_helper(interaction)

    @app_commands.command(name='feed', description="Feed your equiped pet, if you don't you get sent to hell")
    async def feed(self, interaction: discord.Interaction):
        await self.feed_helper(interaction)
    @app_commands.command(name='care', description="Take care of your pet, wash it, care for their health...")
    async def care(self, interaction: discord.Interaction):
        await self.care_helper(interaction)
    @app_commands.command(name='play', description="Play with your cutie Gladge")
    async def play(self, interaction: discord.Interaction):
        await self.play_helper(interaction)
    @app_commands.command(name='help', description="Show all pet commands")
    async def help(self, interaction : discord.Interaction):
        await self.pet_help(interaction)
    @app_commands.command(name='pets', description="Show all your pets")
    async def pets(self, interaction : discord.Interaction):
        await self.pets_embed(interaction)
    @app_commands.command(name='pat', description="Pat your pet Gladge")
    async def pat(self, interaction : discord.Interaction):
        await self.pat_helper(interaction)
    @app_commands.command(name='walk', description="Take a walk with your pet")
    async def walk(self, interaction : discord.Interaction):
        await self.walk_helper(interaction)

    @app_commands.command(name='shop', description="Go into the pet store, different pets every day")
    async def shop(self, interaction: discord.Interaction):
        pets = await self.allpets()
        em = discord.Embed(title="Pet shop", colour=discord.Color.teal())
        for pet in pets:
            if pet["stock"] > 0:
                name = pet["name"]
                rarity = pet["rarity"]
                price = pet["price"]
                em.add_field(name=name, value=f"{rarity} | `{price}` <:lemon2:881595266757713920>", inline=False)
        em.set_footer(text="Check out the new shop everyday at 12:00")
        await interaction.response.send_message(embed=em)
    @app_commands.command(name='buy', description="Buy a pet from the pet shop")
    @app_commands.describe(pet="The pet that you want to buy")
    async def buy(self, interaction: discord.Interaction, pet : str):
        pet = pet.lower()
        arg2 = pet
        pets = await self.allpets()
        user = interaction.user
        users = await es.get_bank_data(user.id)
        equippedpet = await self.userpet(user.id, "equippedpet")
        if bool(equippedpet) == True:
            await interaction.response.send_message("You currently have a pet equipped, to move it to a different slot try `/pet unequip`")
            return
        doespetexist = False
        for pet in pets:
            name = pet["name"]
            rarity = pet["rarity"]
            size = pet["size"]
            stock = pet["stock"]
            price = pet["price"]
            if name.lower() == arg2:
                doespetexist = True
                break
        if doespetexist == False:
            await interaction.response.send_message("This pet does not exist!")
            return
        if stock < 1:
            await interaction.response.send_message("This pet is not available right now!")
            return
        if users[str(user.id)]["pocket"] < price:
            await interaction.response.send_message("You dont have enough money!")
            return
        hp = random.randrange(pet["minhp"], pet["maxhp"] + 1)
        print(hp)
        attack = random.randrange(pet["minattack"], pet["maxattack"] + 1)
        print(attack)
        speed = random.randrange(pet["minspeed"], pet["maxspeed"] + 1)
        print(speed)

        if size == "adult":
            xp = 100
            lvl = pet["maxlvl"]
        else:
            xp = 0
            lvl = 1
        attack1 = pet["attack1"]
        attack2 = pet["attack2"]

        def savepet(id, slot):
            mysql = f"INSERT INTO {slot} (id, name, hp, attack, speed, xp, lvl, item, attack1, attack2, food, stamina, care, fun, img) VALUES ('{user.id}', '{name}', {hp}, {attack}, {speed}, {xp}, {lvl}, 'None', '{attack1}', '{attack2}', 50, 100, 50, 50, '{pet['img']}')"
            print(mysql)
            es.sql_exec(mysql)

        savepet(user.id, "equippedpet")

        await es.update_balance(user, -price)
        await interaction.response.send_message(
            f"Congratulations, you officially adopted {name}! You can view your pet now with `/pet info` or `/pet view`")
        pet["stock"] = pet["stock"] - 1
        with open("./json/allpets.json", "w") as f:
            json.dump(pets, f, indent=4)
        return
    @app_commands.command(name='sell', description="Sell the pet on your EQUIPPED SLOT!")
    async def sell(self, interaction: discord.Interaction):
        user = interaction.user
        pets = await self.allpets()
        equippedpet = await self.userpet(user.id, "equippedpet")
        if bool(equippedpet) == False:
            await interaction.response.send_message(
                f"{user.mention}\nYou dont have a pet equipped!")
            return
        doespetexist = False
        for pet in pets:
            name = pet["name"]
            stock = pet["stock"]
            price = pet["price"]
            if name.lower() == equippedpet["name"].lower():
                doespetexist = True
                break
        if doespetexist == False:
            await interaction.response.send_message("Your pet is not in shop list?!?! @qBaumi")
            return

        def checkreaction(reaction, reactionuser):
            return reaction.message.id == msg.id and reactionuser == user and reaction.emoji == "✅" or reaction.message.id == msg.id and reactionuser == user and reaction.emoji == "❌"
        await interaction.response.defer()
        msg = await interaction.channel.send(f"{user.mention}\nDo you really wanna sell your **equipped pet {name}** ?")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=checkreaction)

            if reaction.emoji != "✅":
                await interaction.followup.send(
                    f"{user.mention}\nGood decision <:Gladge:792430592636616714>")
                return
        except asyncio.TimeoutError:
            await interaction.followup.send(f"{user.mention} did not answer in time")
            return
        es.sql_exec(f"DELETE FROM equippedpet WHERE id = {user.id}")
        pet["stock"] = pet["stock"] + 1
        with open("./json/allpets.json", "w") as f:
            json.dump(pets, f, indent=4)
        await es.update_balance(user, int(price / 2))
        await interaction.followup.send(f"{user.mention}\nYou sold your {name} to a man in a dark alley")
        await interaction.channel.send("<:Cryge:829750407496204361>")
    @app_commands.command(name='equip', description="Equip a pet from your other slots")
    async def equip(self, interaction: discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        pet2 = await self.userpet(user.id, "petslot1")
        pet3 = await self.userpet(user.id, "petslot2")
        pet4 = await self.userpet(user.id, "petslot3")
        if bool(pet) == False and bool(pet2) == False and bool(pet3) == False and bool(pet4) == False:
            await interaction.response.send_message("You dont have a pet!")
            return
        if bool(pet2) == False and bool(pet3) == False and bool(pet4) == False:
            await interaction.response.send_message("You dont have a pet in other slots!")
            return

        def check(m):
            return m.author == user and m.channel == interaction.channel and m.content == "1" or m.author == user and m.channel == interaction.channel and m.content == "2" or m.author == user and m.channel == interaction.channel and m.content == "3"

        await interaction.response.send_message("Which slot you want to move to your equipped? `1`, `2` or `3` ?")
        try:
            msg = await self.client.wait_for('message', timeout=15, check=check)
        except asyncio.TimeoutError:
            await interaction.channel.send('You didnt answer in time!')
            return
        slot = "petslot" + msg.content
        if bool(await self.userpet(user.id, slot)) == False:
            await interaction.channel.send(f'{user.mention}\nYou dont have a pet in this slot to equip!')
            return
        slotfull = False
        if bool(await self.userpet(user.id, "equippedpet")):
            mysql = f"SELECT * FROM equippedpet WHERE id = {user.id}"
            data = es.sql_select(mysql)
            print(data)
            name = data[0][1]
            hp = data[0][2]
            attack = data[0][3]
            speed = data[0][4]
            xp = data[0][5]
            lvl = data[0][6]
            item = data[0][7]
            attack1 = data[0][8]
            attack2 = data[0][9]
            food = data[0][10]
            stamina = data[0][11]
            care = data[0][12]
            fun = data[0][13]
            img = data[0][14]
            val = (user.id, name, hp, attack, speed, xp, lvl, item, attack1, attack2, food, stamina, care, fun, img)
            slotfull = True

        mysql = f"INSERT INTO {slot} (id, name, hp, attack, speed, xp, lvl, item, attack1, attack2, food, stamina, care, fun, img) VALUES ('{user.id}', '{name}', {hp}, {attack}, {speed}, {xp}, {lvl}, 'None', '{attack1}', '{attack2}', 50, 100, 50, 50, '{pet['img']}')"
        es.sql_exec(f"DELETE FROM equippedpet WHERE id = '{user.id}'")
        es.sql_exec(f"INSERT INTO equippedpet SELECT * FROM {slot} WHERE id = '{user.id}'")
        es.sql_exec(f"DELETE FROM {slot} WHERE id = '{user.id}'")
        if slotfull == True:
            es.sql_exec(mysql)
        data = es.sql_select(f"SELECT name FROM equippedpet WHERE id = '{user.id}'")

        if bool(await self.userpet(user.id, slot)) == True:
            await interaction.channel.send(
                f'{user.mention}\nYou equipped your {data[0][0]} and moved your {name} to slot {msg.content}')
            return
        else:
            await interaction.channel.send(f'{user.mention}\nYou equipped your {data[0][0]}')
    @app_commands.command(name='unequip', description="Unequip a pet from your main slot")
    async def unequip(self, interaction: discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        pet2 = await self.userpet(user.id, "petslot1")
        pet3 = await self.userpet(user.id, "petslot2")
        pet4 = await self.userpet(user.id, "petslot3")
        if bool(pet) == False and bool(pet2) == False and bool(pet3) == False and bool(pet4) == False:
            await interaction.response.send_message("You dont have a pet!")
            return
        if bool(pet2) == True and bool(pet3) == True and bool(pet4) == True:
            await interaction.response.send_message("You dont have an empty slot!")
            return

        def check(m):
            return m.author == user and m.channel == interaction.channel and m.content == "1" or m.author == user and m.channel == interaction.channel and m.content == "2" or m.author == user and m.channel == interaction.channel and m.content == "3"

        await interaction.response.send_message("Which slot you want to move your equipped pet to? `1`, `2` or `3` ?")
        try:
            msg = await self.client.wait_for('message', timeout=15, check=check)
        except asyncio.TimeoutError:
            await interaction.channel.send('You didnt answer in time!')
            return
        slot = "petslot" + msg.content
        print(slot)
        if bool(await self.userpet(user.id, slot)) == True:
            await interaction.channel.send(
                f'{user.mention}\nThere is already a pet in this slot, if you want it equipped do so with `/pet equip`')
            return
        es.sql_exec(f"INSERT INTO {slot} SELECT * FROM equippedpet WHERE id = '{user.id}'")
        es.sql_exec(f"DELETE FROM equippedpet WHERE id = '{user.id}';")
        await interaction.channel.send(f'{user.mention}\nYour pet was moved to slot {msg.content}')


    async def pets_embed(self, interaction : discord.Interaction):
        user = interaction.user
        pet1 = await self.userpet(user.id, "equippedpet")
        pet2 = await self.userpet(user.id, "petslot1")
        pet3 = await self.userpet(user.id, "petslot2")
        pet4 = await self.userpet(user.id, "petslot3")
        em = discord.Embed(colour=discord.Color.teal(), title="Your pets")
        if bool(pet1) == True:
            em.add_field(name=f'Equipped:\n{pet1["name"]}', value=f'Lvl {pet1["lvl"]}', inline=False)
        if bool(pet2) == True:
            em.add_field(name=f'Slot 1:\n{pet2["name"]}', value=f'Lvl {pet2["lvl"]}', inline=False)
        if bool(pet3) == True:
            em.add_field(name=f'Slot 2:\n{pet3["name"]}', value=f'Lvl {pet3["lvl"]}', inline=False)
        if bool(pet4) == True:
            em.add_field(name=f'Slot 3:\n{pet4["name"]}', value=f'Lvl {pet4["lvl"]}', inline=False)

        await interaction.response.send_message(f"{user.mention}", embed=em)
        return
    async def pet_help(self, interaction : discord.Interaction):
        em = discord.Embed(title="Pets", colour=discord.Color.from_rgb(254, 254, 51), description="You can buy a pet from the `/pet shop` and look and care for your equipped pet with `/pet info`. You can have a maximum of 4 pets. You can buy them as adults and babys, an adult is the maximum level but has not that good stats as the same pet leveled up from a baby to the maximum level!")
        em.add_field(name="pet shop", value="Look which pets are currently available!", inline=False)
        em.add_field(name="pet adopt | pet buy", value="Adopt a pet from the shop", inline=False)
        em.add_field(name="pet sell", value="Sadge", inline=False)
        em.add_field(name="pet info", value="Have a look at your equipped pet's stats!", inline=False)
        em.add_field(name="pet feed | pet care | pet play", value="You can also use them with `/pet info` and then react to the emojis!", inline=False)
        em.add_field(name="pet pat", value="Gladge", inline=False)
        em.add_field(name="pet walk", value="Walk your pet, it needs to go to the toilet as well", inline=False)
        em.add_field(name="pet equip | pet unequip", value="Equip a pet from a different slot | Unequip a pet to buy another one", inline=False)
        em.add_field(name="pet pets", value="View all your pets", inline=False)
        em.add_field(name="pet fight", value="COMING SOON!!!", inline=False)
        await interaction.response.send_message(embed=em)
    async def userpet(self, id, slot):
        data = es.sql_select(f"SELECT * FROM {slot} WHERE id = {id}")
        pet = {}
        try:
            data = data[0]
            pet = {"name" : data[1], "hp" : data[2], "attack" : data[3], "speed" : data[4], "xp" : data[5], "lvl" : data[6], "item" : data[7], "attack1" : data[8], "attack2" : data[9], "food" : data[10], "stamina" : data[11], "care" : data[12], "fun" : data[13], "img" : data[14]}
        except:
            None
        return pet
    async def pat_helper(self, interaction : discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        pet1 = await self.userpet(user.id, "petslot1")
        pet2 = await self.userpet(user.id, "petslot2")
        pet3 = await self.userpet(user.id, "petslot3")
        if bool(pet) == False and bool(pet1) == False and bool(pet2) == False and bool(pet3) == False:
            await interaction.response.send_message("You dont have a pet!")
            return
        if bool(pet) == False:
            await interaction.response.send_message("You dont have a pet equipped!")
            return
        stats = await self.getstats(user.id)
        if stats["fun"] <= 95:
            self.updatestat(user.id, "fun", stats["fun"]+5)
        await interaction.response.send_message(f"{user.mention}\nYou started petting {pet['name']}")
        await interaction.channel.send("<:nemePat:781659265244200981><:nemePat:781659265244200981><:nemePat:781659265244200981>")
    async def walk_helper(self, interaction : discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        pet1 = await self.userpet(user.id, "petslot1")
        pet2 = await self.userpet(user.id, "petslot2")
        pet3 = await self.userpet(user.id, "petslot3")
        if bool(pet) == False and bool(pet1) == False and bool(pet2) == False and bool(pet3) == False:
            await interaction.response.send_message("You dont have a pet!")
            return
        if bool(pet) == False:
            await interaction.response.send_message("You dont have a pet equipped!")
            return
        stats = await self.getstats(user.id)
        if stats["fun"] <= 90:
            self.updatestat(user.id, "fun", stats["fun"] + 10)
        await interaction.response.send_message("<a:nemerub:853296247606476800>") # Respond to interaction
        message = await interaction.channel.send(f"{user.mention}\n*You are putting a leash on {pet['name']}*")
        await asyncio.sleep(4)
        if stats["stamina"] < 25:
            await interaction.channel.send(f"{user.mention}\n{pet['name']} is too tired")
            await interaction.channel.send("<:Bedge:829750057502375997>")
            return
        self.updatestat(user.id, "stamina", stats["stamina"]-25)
        lemons = random.randrange(10, 50)
        events = [f"You and {pet['name']} are humming to Life is a highway!", f"{pet['name']} smells something...maybe you should go shower", f"{pet['name']} starts barking at a dog", f"A lemon from an lemon tree fell on {pet['name']}, you put in in your wallet", f"{pet['name']} found {lemons} lemons on the street", f"A stranger gave {pet['name']} 10 lemons because they where so cute <:nemePat:781659265244200981>", f"An old man pat {pet['name']}"]
        rndmevent = random.choice(events)
        if rndmevent == events[3]:
            await es.update_balance(user, 1)
        elif rndmevent == events[4]:
            await es.update_balance(user, lemons)
        elif rndmevent == events[5]:
            await es.update_balance(user, 10)
        await message.edit(content=f"{user.mention}\nYou leave the house with {pet['name']}")
        await asyncio.sleep(3)
        await message.edit(content=f"{user.mention}\nYou are going down the road")
        await asyncio.sleep(3)
        await message.edit(content=f"{user.mention}\n{rndmevent}")
        await asyncio.sleep(5)
        await message.edit(content=f"{user.mention}\nYou continue your journey")
        await asyncio.sleep(3)
        await message.edit(content=f"{user.mention}\nYou and {pet['name']} are back home again!")
    async def feed_helper(self, interaction : discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        if bool(pet) == False:
            await interaction.response.send_message(f"{user.mention}\nYou dont have a pet equipped!")
            return
        stats = await self.getstats(user.id)
        # feed and shower gives 10 - 20 xp, costs 100 lemons every 20 min you can feed on average 1 hour per lvl up on average I hope
        if stats["food"] > 80:
            await interaction.response.send_message(f"{user.mention}\n{pet['name']} isn't hungry! Try again later")
            return
        xp = random.randrange(10, 21)
        users = await es.get_bank_data(user.id)
        if users[str(user.id)]["pocket"] < 5:
            await interaction.response.send_message(f"{user.mention}\nYou dont have enough money!")
            return
        hunger = int(stats["food"])+20
        self.updatestat(user.id, "food", hunger)
        addxp = await self.addxp(user.id, xp)
        if addxp == 1:
            embed = discord.Embed(title=f'{pet["name"]} leveled up!', colour=discord.Color.teal(), description=f"{pet['name']} now has:\n❤{pet['hp']+3}\n🗡️{pet['attack']+3}\n💨{pet['speed']+3}")
            await interaction.channel.send(f"{user.mention}\n", embed=embed)
        foodlist = ["peas", "a cheesecake", "tacos", "pizza", "chicken with pasta", "chimken with rice", "pasta with tomato sauce", "pizza selam aleykum", "fish", "canned food", "dried animal food", "vegetables", "fruits", "sushi", "tuna", "carrots"]
        realshi = random.choice(foodlist)
        petreaction = ["they liked it", "they didnt like it", "they didnt eat it", "they threw it up later", "they said guß for food", "they want more!"]
        line = random.choice(petreaction)
        await es.update_balance(user, -5)
        embed = discord.Embed(title=f"You fed {pet['name']} {realshi} {line}!", colour=discord.Color.teal(), description=f"You paid 5 lemons for their luxury...pets are expensive, but worth <:nemePat:781659265244200981>")
        await interaction.response.send_message(f"{user.mention}\n", embed=embed)

        return
    async def play_helper(self, interaction : discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        await interaction.response.defer()
        if bool(pet) == False:
            await interaction.response.send_message("You dont have a pet equipped!")
            return
        stats = await self.getstats(user.id)
        if stats["fun"] > 90 or stats["stamina"] < 15:
            await interaction.response.send_message(f"{user.mention}\n{pet['name']} dosent want to play right now! <:Madge:786069469020815391> \nTry again later")
            return
        xp = random.randrange(1, 10)
        newfun = random.randrange(15, 20)
        fun = int(stats["fun"]) + newfun
        stamina = int(stats["stamina"]) - 15

        self.updatestat(user.id, "stamina", stamina)



        # IF TASK SUCCESSFUL HAPPY
        # IF NOT SADGE PET
        gamelist = ["football", "fetch", "fetch", "fetch", "volleyball", "basketball", "football", "frisbee", "boomer rang"]
        emojilist = ["⚽", "🎾", "⚾", "🥎", "🏐", "🏀", "🏈", "🥏", "🪃"]
        game = random.randrange(0, len(gamelist))
        em = discord.Embed(title=f"{pet['name']} wants to play {gamelist[game]}")
        message = await interaction.channel.send(f"{user.mention}\n", embed=em)
        await message.add_reaction(emojilist[game])

        def checkreaction(reaction, reactionuser):
            return reaction.message.id == message.id and reactionuser == interaction.user
        out = "<:widepeepoHappy:755460994100232272>"
        try:
            reaction, useremoji = await self.client.wait_for('reaction_add', timeout=10, check=checkreaction)
        except asyncio.TimeoutError:
            out = "<:Sadge:720250426892615745>"
        try:
            if reaction.emoji != emojilist[game]:
                out = "<:Sadge:720250426892615745>"
        except:
            pass
        await interaction.followup.send(f"**{pet['name']}:**")
        await interaction.channel.send(f"{out}")
        if out == "<:Sadge:720250426892615745>":
            return
        self.updatestat(user.id, "fun", fun)
        addxp = await self.addxp(user.id, xp)
        if addxp == 1:
            embed = discord.Embed(title=f'{pet["name"]} leveled up!', colour=discord.Color.teal(),
                                  description=f"{pet['name']} now has:\n❤{pet['hp'] + 3}\n🗡️{pet['attack'] + 3}\n💨{pet['speed'] + 3}")
            await interaction.channel.send(f"{user.mention}\n", embed=embed)

        return
    async def care_helper(self, interaction : discord.Interaction):
        user = interaction.user
        pet = await self.userpet(user.id, "equippedpet")
        if bool(pet) == False:
            await interaction.response.send_message("You dont have a pet equipped!")
            return
        stats = await self.getstats(user.id)
        # feed and shower gives 10 - 20 xp, costs 100 lemons every 20 min you can feed on average 1 hour per lvl up on average I hope
        if stats["care"] > 69:
            await interaction.response.send_message(f"{user.mention}\n{pet['name']} has everything they need! Try again later")
            return
        xp = random.randrange(10, 21)
        users = await es.get_bank_data(user.id)
        if users[str(user.id)]["pocket"] < 50:
            await interaction.response.send_message(f"{user.mention}\nYou dont have enough money!")
            return
        hunger = int(stats["care"]) + 30
        self.updatestat(user.id, "care", hunger)
        addxp = await self.addxp(user.id, xp)
        if addxp == 1:
            embed = discord.Embed(title=f'{pet["name"]} leveled up!', colour=discord.Color.teal(),
                                  description=f"{pet['name']} now has:\n❤{pet['hp'] + 3}\n🗡️{pet['attack'] + 3}\n💨{pet['speed'] + 3}")
            await interaction.channel.send(f"{user.mention}\n", embed=embed)
        lines = [f"gave {pet['name']} a bath", f"took {pet['name']} to the vet", f"showered {pet['name']}", f"gave {pet['name']} their medicine", f"brushed {pet['name']}", f"splashed water at {pet['name']} on a hot summerday", f"gave {pet['name']} a hug"]
        realshi = random.choice(lines)
        petreaction = ["they liked it", "they didnt like it", "they enjoyed it <3", "they were scared", "they loved it", "they hated it"]
        line = random.choice(petreaction)
        embed = discord.Embed(title=f"You {realshi}, {line}!", colour=discord.Color.teal())
        if realshi == lines[1]:
            await es.update_balance(user, -50)
            embed.set_footer(text="You paid 50 lemons for the vet!")
        await interaction.channel.send(f"{user.mention}\n", embed=embed)

        return
    async def getstats(self, id, slot="equippedpet"):
        pet = await self.userpet(id, slot)
        stats = {"food":pet["food"], "stamina":pet["stamina"], "care":pet["care"], "fun":pet["fun"], "xp":pet["xp"], "lvl":pet["lvl"]}
        return stats
    def updatestat(self, id, stat, value, slot="equippedpet"):
        es.sql_exec(f"UPDATE {slot} SET {stat} = {value} WHERE id = {id}")
        return
    async def addxp(self, id, xp):
        pets = await self.allpets()
        userpet = await self.userpet(id, "equippedpet")
        for pet in pets:
            name = pet["name"]
            maxlvl = pet["maxlvl"]
            if name.lower() == userpet["name"].lower():
                break
        stats = await self.getstats(id)
        oldxp = stats["xp"]
        newxp = oldxp+xp

        if newxp >= 100 and stats["lvl"] < maxlvl:
            # levelup
            newlvl =  int(stats["lvl"])+1
            self.updatestat(id, "lvl", newlvl)
            newxp -= 100
            self.updatestat(id, "xp", newxp)

            # give +3 on evry stat
            self.updatestat(id, "attack", userpet["attack"]+3)
            self.updatestat(id, "hp", userpet["hp"]+3)
            self.updatestat(id, "speed", userpet["speed"]+3)

            return 1
        if stats["lvl"] == maxlvl and newxp >= 100:
            self.updatestat(id, "xp", 100)
            return

        self.updatestat(id, "xp", newxp)
        return 0


        return


    @tasks.loop(time=time)
    async def ch_shop(self):
        await self.client.wait_until_ready()
        await self.rotateshop(5)

    @commands.command()
    async def changeshop(self, ctx):
        id = 442913791215140875
        if ctx.author.id != id:
            await ctx.send("You are not my Master!")
            await ctx.send("<:Madge:786069469020815391>")
            return
        await self.rotateshop(7)
        await ctx.send("Shop rotated, Sir!")
    async def rotateshop(self, shopsize):
        pets = await self.allpets()
        shop = []
        i = 0
        while True:
            if i == shopsize:
                break
            index = random.randrange(0, len(pets))
            pet = pets[index]["name"]
            if not pet in shop:
                shop.append(pet)
                i+=1
        print(shop)
        for pet in pets:
            pet["stock"] = 0
        for pet in pets:
            if pet["name"] in shop:
                pet["stock"] = 1
        with open("./json/allpets.json", "w") as f:
            json.dump(pets, f, indent=4)
        return
    async def getminustats(self, slot):
        pets = es.sql_select(f"SELECT * FROM {slot}")
        for pet in pets:
            stats = await self.getstats(pet[0], slot)
            if stats["food"] > 0:
                self.updatestat(pet[0], "food", pet[10]-1, slot)
            if stats["stamina"] < 100:
                self.updatestat(pet[0], "stamina", pet[11]+1, slot)
            if stats["care"] > 0:
                self.updatestat(pet[0], "care", pet[12]-1, slot)
            if stats["fun"] > 0:
                self.updatestat(pet[0], "fun", pet[13]-1, slot)
    async def ch_stats(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await self.getminustats("equippedpet")
            await self.getminustats("petslot1")
            await self.getminustats("petslot2")
            await self.getminustats("petslot3")
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.ch_shop.start()
        await self.client.loop.create_task(self.ch_shop())
    async def allpets(self):
        # open the json file in read mode to load users and return them
        with open("./json/allpets.json", "r") as f:
            allpets = json.load(f)
        return allpets
    @staticmethod
    async def treat_helper(self, interaction : discord.Interaction):
        pet = await self.userpet(interaction.user.id, "equippedpet")
        if bool(pet) == False:
            await interaction.response.send_message(f"{interaction.user.mention}\nYou dont have a pet equipped!")
            return
        stats = await self.getstats(interaction.user.id)
        if stats["food"] > 80:
            await interaction.response.send_message(f"{interaction.user.mention}\n{pet['name']} isn't hungry! Try again later")
            return
        users = await es.get_bank_data(interaction.user.id)
        hunger = int(stats["food"]) + 5
        self.updatestat(interaction.user.id, "food", hunger)
        addxp = await self.addxp(interaction.user.id, 5)
        if addxp == 1:
            embed = discord.Embed(title=f'{pet["name"]} leveled up!', colour=discord.Color.teal(),
                                  description=f"{pet['name']} now has:\n❤{pet['hp'] + 3}\n🗡️{pet['attack'] + 3}\n💨{pet['speed'] + 3}")
            await interaction.response.send_message(f"{interaction.user.mention}\n", embed=embed)

        embed = discord.Embed(title=f"You gave {pet['name']} a treat!", colour=discord.Color.teal())
        await interaction.response.send_message(f"{interaction.user.mention}\n", embed=embed)
        await interaction.channel.send(f"<a:nemerub:853296247606476800>")





async def setup(client):
    await client.add_cog(pet(client), guilds=guilds)