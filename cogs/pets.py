#goose
#kuriboh
#poro
#lemon like patricks pet stone...but better
# Yoshi?
#puffle
#cat
#crows
#Asmol

import discord
from discord import Colour
from discord.ext import commands
from .economy import *

class pets(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pet(self, ctx, arg1="None", arg2 = "None"):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nYou need to use `lem startup` first")
            return
        user = ctx.author
        arg1 = arg1.lower()
        arg2 = arg2.lower()
        pets = await self.allpets()
        if await self.check_account(user) == False:
            await ctx.send("Try `lem startup` first")
            return
        if arg1 == "shop":
            em = discord.Embed(title="Pet shop", colour=discord.Color.teal())

            for pet in pets:
                print(pet)
                if pet["stock"] > 0:
                    name = pet["name"]
                    rarity = pet["rarity"]
                    size = pet["size"]
                    price = pet["price"]
                    em.add_field(name=name, value=f"{size} | {rarity} | `{price}` <:lemon2:881595266757713920>", inline=False)
            await ctx.send(embed=em)
            return
        elif arg1 == "buy" or arg1 == "adopt":
            users = await self.get_bank_data()
            if bool(users[str(user.id)]["equippedpet"]) == True:
                await ctx.send("You currently have a pet equipped, to move it to a different slot try `lem pet move <petname> <petslot>`")
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
                await ctx.send("This pet does not exist!")
                return
            if stock < 1:
                await ctx.send("This pet is not available right now!")
                return
            if users[str(user.id)]["pocket"] < price:
                await ctx.send("You dont have enough money!")
                return
            hp = random.randrange(pet["minhp"], pet["maxhp"]+1)
            print(hp)
            attack = random.randrange(pet["minattack"], pet["maxattack"]+1)
            print(attack)
            speed = random.randrange(pet["minspeed"], pet["maxspeed"]+1)
            print(speed)

            if size == "adult":
                xp = 100
                lvl = pet["maxlvl"]
            else:
                xp = 0
                lvl = 0
            attack1 = pet["attack1"]
            attack2 = pet["attack2"]
            petdict = {"name" : pet["name"], "hp" : hp,"attack" : attack, "speed" : speed, "xp" : xp, "lvl" : lvl, "item" : "None", "accessoire" : "None", "attack1" : attack1, "attack2" : attack2, "food" : 100, "stamina" : 100, "care" : 100, "fun" : 100, "img": pet["img"]}
            users[str(user.id)]["equippedpet"] = petdict
            with open("lemonbank.json", "w") as f:
                json.dump(users, f, indent=4)
            await self.update_balance(user, -price)
            await ctx.send(f"Congratulations, you officially adopted {name}! You can view your pet now with `lem pet info` or `lem pet view`")
            return
        elif arg1 == "info" or arg1 == "view":
            users = await self.get_bank_data()

            pet = users[str(user.id)]["equippedpet"]
            if bool(pet) == False and bool(users[str(user.id)]["petslot1"]) == False and bool(users[str(user.id)]["petslot2"]) == False and bool(users[str(user.id)]["petslot3"]) == False:
                await ctx.send("You dont have a pet!")
                return
            if bool(pet) == False:
                await ctx.send("You dont have a pet equipped!")
                return
            print(pet)

            em = discord.Embed(colour=discord.Color.teal(), title=pet["name"])
            em.add_field(name="Stats:", value=f'{pet["hp"]} ❤\n{pet["attack"]}  🗡️\n{pet["speed"]}  💨', inline=False)
            string = ""
            xpbar = pet["xp"]/8
            xpbar = int(xpbar)
            rest = 12-xpbar
            for x in range(xpbar):
                string += "🟦"
            for i in range(rest):
                string += "⬛"
            em.add_field(name=f'Level: {pet["lvl"]}', value=string, inline=False)
            string = ""
            foodbar = pet["food"] / 8
            foodbar = int(foodbar)
            rest = 12 - foodbar
            for x in range(foodbar):
                string += "🟥"
            for i in range(rest):
                string += "⬛"
            em.add_field(name=f'Food', value=string, inline=False)
            string = ""
            staminabar = pet["stamina"] / 8
            staminabar = int(staminabar)
            rest = 12 - staminabar
            for x in range(staminabar):
                string += "🟥"
            for i in range(rest):
                string += "⬛"
            em.add_field(name=f'Stamina', value=string, inline=False)

            string = ""
            staminabar = pet["care"] / 8
            staminabar = int(staminabar)
            rest = 12 - staminabar
            for x in range(staminabar):
                string += "🟥"
            for i in range(rest):
                string += "⬛"
            em.add_field(name=f'Care', value=string, inline=False)

            string = ""
            staminabar = pet["fun"] / 8
            staminabar = int(staminabar)
            rest = 12 - staminabar
            for x in range(staminabar):
                string += "🟥"
            for i in range(rest):
                string += "⬛"
            em.add_field(name=f'Fun', value=string, inline=False)
            em.add_field(name="Item:", value="Added soon", inline=False)
            em.add_field(name="Moveset:", value=f'{pet["attack1"]}\n{pet["attack2"]}', inline=False)

            file = discord.File(f'./pets/{pet["img"]}')
            em.set_image(url=f'attachment://{pet["img"]}')
            await ctx.send(file=file, embed=em)

            return
        elif arg1 == "equip":
            users = await self.get_bank_data()

            pet = users[str(user.id)]["equippedpet"]
            if bool(pet) == False and bool(users[str(user.id)]["petslot1"]) == False and bool(users[str(user.id)]["petslot2"]) == False and bool(users[str(user.id)]["petslot3"]) == False:
                await ctx.send("You dont have a pet!")
                return
            if bool(users[str(user.id)]["petslot1"]) == False and bool(users[str(user.id)]["petslot2"]) == False and bool(users[str(user.id)]["petslot3"]) == False:
                await ctx.send("You dont have a pet in other slots!")
                return
            currentpet = users[str(user.id)]["equippedpet"]

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content == "1" or m.author == ctx.author and m.channel == ctx.channel and m.content == "2" or m.author == ctx.author and m.channel == ctx.channel and m.content == "3"
            await ctx.send("Which slot you want to move to your equipped? `1`, `2` or `3` ?")
            try:
                msg = await self.client.wait_for('message', timeout=15, check=check)
            except asyncio.TimeoutError:
                await ctx.send('You didnt answer in time!')
                return
            slot = "petslot" + msg.content
            if bool(users[str(user.id)][slot]) == False:
                await ctx.send(f'{user.mention}\nYou dont have a pet in this slot to equip!')
                return
            print(slot)
            currentpet = users[str(user.id)][slot]
            users[str(user.id)][slot] = users[str(user.id)]["equippedpet"]
            users[str(user.id)]["equippedpet"] = currentpet
            with open("lemonbank.json", "w") as f:
                json.dump(users, f, indent=4)
            if bool(users[str(user.id)][slot]) == True:
                await ctx.send(f'{user.mention}\nYou equipped your {users[str(user.id)]["equippedpet"]["name"]} and moved your {users[str(user.id)][slot]["name"]} to slot {msg.content}')
                return
            else:
                await ctx.send(f'{user.mention}\nYou equipped your {users[str(user.id)]["equippedpet"]["name"]}')
                return

        elif arg1 == "unequip":
            users = await self.get_bank_data()

            pet = users[str(user.id)]["equippedpet"]
            if bool(pet) == False and bool(users[str(user.id)]["petslot1"]) == False and bool(
                    users[str(user.id)]["petslot2"]) == False and bool(users[str(user.id)]["petslot3"]) == False:
                await ctx.send("You dont have a pet!")
                return
            if bool(users[str(user.id)]["petslot1"]) == True and bool(
                    users[str(user.id)]["petslot2"]) == True and bool(users[str(user.id)]["petslot3"]) == True:
                await ctx.send("You dont have an empty slot!")
                return


            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content == "1" or m.author == ctx.author and m.channel == ctx.channel and m.content == "2" or m.author == ctx.author and m.channel == ctx.channel and m.content == "3"

            await ctx.send("Which slot you want to equip? `1`, `2` or `3` ?")
            try:
                msg = await self.client.wait_for('message', timeout=15, check=check)
            except asyncio.TimeoutError:
                await ctx.send('You didnt answer in time!')
                return
            slot = "petslot" + msg.content
            print(slot)
            if bool(users[str(user.id)][slot]) == True:
                await ctx.send(f'{user.mention}\nThere is already a pet in this slot, if you want it equipped do so with `lem pet equip`')
                return
            users[str(user.id)][slot] = users[str(user.id)]["equippedpet"]
            users[str(user.id)]["equippedpet"] = {}
            with open("lemonbank.json", "w") as f:
                json.dump(users, f, indent=4)
            await ctx.send(f'{user.mention}\nYour pet was moved to slot {msg.content}')

        elif arg1 == "pets":

            users = await self.get_bank_data()

            pet1 = users[str(user.id)]["equippedpet"]
            pet2 = users[str(user.id)]["petslot1"]
            pet3 = users[str(user.id)]["petslot2"]
            pet4 = users[str(user.id)]["petslot3"]
            em = discord.Embed(colour=discord.Color.teal(), title="Your pets")
            if bool(pet1) == True:
                em.add_field(name=pet1["name"], value=f'Lvl {pet1["lvl"]}', inline=False)
            if bool(pet2) == True:
                em.add_field(name=pet2["name"], value=f'Lvl {pet2["lvl"]}', inline=False)
            if bool(pet3) == True:
                em.add_field(name=pet3["name"], value=f'Lvl {pet3["lvl"]}', inline=False)
            if bool(pet4) == True:
                em.add_field(name=pet4["name"], value=f'Lvl {pet4["lvl"]}', inline=False)

            await ctx.send(f"{user.mention}", embed = em)
            return
        elif arg1=="help":
            await self.pet_help(ctx)
            return
        else:
            await self.pet_help(ctx)
            return

    @commands.command()
    async def pets(self, ctx):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nYou need to use `lem startup` first")
            return
        users = await self.get_bank_data()
        user = ctx.author

        pet1 = users[str(user.id)]["equippedpet"]
        pet2 = users[str(user.id)]["petslot1"]
        pet3 = users[str(user.id)]["petslot2"]
        pet4 = users[str(user.id)]["petslot3"]
        em = discord.Embed(colour=discord.Color.teal(), title="Your pets")
        if bool(pet1) == True:
            em.add_field(name=pet1["name"], value=f'Lvl {pet1["lvl"]}', inline=False)
        if bool(pet2) == True:
            em.add_field(name=pet2["name"], value=f'Lvl {pet2["lvl"]}', inline=False)
        if bool(pet3) == True:
            em.add_field(name=pet3["name"], value=f'Lvl {pet3["lvl"]}', inline=False)
        if bool(pet4) == True:
            em.add_field(name=pet4["name"], value=f'Lvl {pet4["lvl"]}', inline=False)

        await ctx.send(f"{user.mention}", embed=em)


    async def pet_help(self, ctx):
        em = discord.Embed(title="Pets", colour=discord.Color.from_rgb(254, 254, 51), description="You can buy a pet from the `lem pet shop` and look and care for your equipped pet with `lem pet info`. You can have a maximum of 4 pets. You can buy them as adults and babys, an adult is the maximum level but has not that good stats as the same pet leveled up from a baby to the maximum level!")
        em.add_field(name="shop", value="Look which pets are currently available!", inline=False)
        em.add_field(name="adopt | buy", value="Adopt a pet from the shop", inline=False)
        em.add_field(name="info", value="Have a look at your equipped pet's stats!", inline=False)
        em.add_field(name="pets", value="View all your pets", inline=False)
        await ctx.send(embed=em)

    # Setup a new json with asmolpets and return it per function because of....problems
    async def allpets(self):
        # open the json file in read mode to load users and return them
        with open("allpets.json", "r") as f:
            allpets = json.load(f)
        return allpets

    # Helper function to get a pet
    async def getpet(self, ctx, starrating):
        # Get the user for reply and his data to display the pet infos
        user = ctx.author
        users = await economy.get_bank_data()
        # create a new pet and in the variable is True or False stored
        new_pet = await self.generatepet(ctx.author, starrating)
        if new_pet == False:
            reply = "You don't have an empty pet slot, equip a pet if you don't have one equipped or sell one!"
            # Copy the embed in here because of the return :/
            em = discord.Embed(title=reply, colour=Colour.from_rgb(198, 226, 255))
            await ctx.send(embed=em)
            return
        # Set petslot to the second returned value from the newpet function
        petslot = new_pet[1]
        # INITIALISE THE USERS OTHERWISE THE PET WONT BE IN THE BECAUSE IT WAS FIRST GOTTEN AT THE BEGINNING
        users = await economy.get_bank_data()
        # Get the petname and rarity
        petname = users[str(user.id)][petslot]["name"]
        petrarity = users[str(user.id)][petslot]["rarity"]
        reply = f"You new {petrarity} {petname} was sent to your `{petslot}`"

        # Make a nice embed
        em = discord.Embed(title=reply, colour=Colour.from_rgb(198, 226, 255))
        await ctx.send(embed=em)

    # Function to generate a pet with loot crates that have different star ratings like 1 star 2 stars 3 stars etc
    async def generatepet(self, user, starrating):
        users = await economy.get_bank_data()
        # Check at the beginning if the user has an empty pet slot if not return False
        # An empty dict is always False
        if bool(users[str(user.id)]["petslot1"]) == False:
            petslot = "petslot1"
        elif bool(users[str(user.id)]["petslot2"]) == False:
            petslot = "petslot2"
        elif bool(users[str(user.id)]["petslot3"]) == False:
            petslot = "petslot3"
        else:
            return False

        # Get all the pets that exist per function
        pets = await self.allpets()
        # Get the starrating crate to choose the pets
        if starrating == "1":
            # Get alle the pets with 1 star rating and get a random one choosen
            # Create a list that appends when the rarity is common or uncommon
            common_uncommon_pets = []

            # For every pet in the pets dict append the
            for pet in pets:
                # If the pet has 1 star it gets appended to the list and you can choose one random one with the random.choice later
                if pets[pet]["stars"] == 1:
                    common_uncommon_pets.append(pets[pet]["name"])

            print(common_uncommon_pets)
            choosenpet = random.choice(common_uncommon_pets)
            print(choosenpet)

            # Make the stats random depending on the rarity
            # That means we first check if the pet is uncommon OR common
            if pets[choosenpet]["rarity"] == "common":
                # If the pet is common you get stats from 3 to 7 depending on your luck with random.randrange
                pets[choosenpet]["attack"] = random.randrange(3, 8)
                pets[choosenpet]["defense"] = random.randrange(3, 8)
                pets[choosenpet]["speed"] = random.randrange(3, 8)
            if pets[choosenpet]["rarity"] == "uncommon":
                # If the pet is common you get stats from 5 to 10 depending on your luck with random.randrange
                pets[choosenpet]["attack"] = random.randrange(3, 11)
                pets[choosenpet]["defense"] = random.randrange(3, 11)
                pets[choosenpet]["speed"] = random.randrange(3, 11)

        if starrating == "2":
            # Same as the first if with adapted stats etc
            rare_epic_pets = []
            for pet in pets:
                if pets[pet]["stars"] == 2:
                    rare_epic_pets.append(pets[pet]["name"])
            print(rare_epic_pets)
            choosenpet = random.choice(rare_epic_pets)
            print(choosenpet)
            if pets[choosenpet]["rarity"] == "rare":
                pets[choosenpet]["attack"] = random.randrange(10, 17)
                pets[choosenpet]["defense"] = random.randrange(10, 17)
                pets[choosenpet]["speed"] = random.randrange(10, 17)
            if pets[choosenpet]["rarity"] == "epic":
                pets[choosenpet]["attack"] = random.randrange(15, 21)
                pets[choosenpet]["defense"] = random.randrange(15, 21)
                pets[choosenpet]["speed"] = random.randrange(15, 21)

        if starrating == "3":
            # Same as the first if with adapted stats etc
            legendary_mythic_pets = []
            for pet in pets:
                if pets[pet]["stars"] == 3:
                    legendary_mythic_pets.append(pets[pet]["name"])
            print(legendary_mythic_pets)
            choosenpet = random.choice(legendary_mythic_pets)
            print(choosenpet)
            if pets[choosenpet]["rarity"] == "legendary":
                pets[choosenpet]["attack"] = random.randrange(20, 27)
                pets[choosenpet]["defense"] = random.randrange(20, 27)
                pets[choosenpet]["speed"] = random.randrange(20, 27)
            if pets[choosenpet]["rarity"] == "mythic":
                pets[choosenpet]["attack"] = random.randrange(25, 31)
                pets[choosenpet]["defense"] = random.randrange(25, 31)
                pets[choosenpet]["speed"] = random.randrange(25, 31)

        # Now that everything works and we choose the random stats we can break our heads about how we store the pet
        print(pets[choosenpet])
        # We just copy the update_balance and dump the choosenpet
        # Dont forget the write mode and get the user data

        users[str(user.id)][petslot] = pets[choosenpet]
        with open('Asmolbank.json', 'w') as f:
            # indent makes the json pretty :)
            json.dump(users, f, indent=4)
        # If all worked properly THEN return True and the petslot it got stored
        return [True, petslot]

    # Check if you have an account opened
    async def check_account(self, user):
        # Open the file with the getbankdata function
        users = await self.get_bank_data()
        # If they are already in there return False to check later on the startup command
        if str(user.id) in users:
            return True
        return False

    # Get the Bank, user data stored in the json file
    async def get_bank_data(self):
        # open the json file in read mode to load users and return them
        with open("lemonbank.json", "r") as f:
            users = json.load(f)
        return users

    # Give or withdraw money from your account
    async def update_balance(self, user, change=0, mode="pocket"):
        # Get the bank file data
        users = await self.get_bank_data()
        # Update the value in the mode you want
        users[str(user.id)][mode] += change
        with open('lemonbank.json', 'w') as f:
            json.dump(users, f, indent=4)
        # Return a currency value for text purposes
        bal = users[str(user.id)]["pocket"], users[str(user.id)]["safe"]
        return bal

def setup(client):
    client.add_cog(pets(client))