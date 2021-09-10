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
    async def pet(self, ctx, arg1, arg2 = "None"):
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
                    em.add_field(name=name, value=f"{size} | {rarity}", inline=False)
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
            petdict = {"name" : pet["name"], "hp" : hp,"attack" : attack, "speed" : speed, "xp" : xp, "lvl" : lvl, "item" : "None", "accessoire" : "None", "attack1" : attack1, "attack2" : attack2, "food" : 100, "stamina" : 100, "care" : 100, "fun" : 100}
            users[str(user.id)]["equippedpet"] = petdict
            with open("lemonbank.json", "w") as f:
                json.dump(users, f, indent=4)
            await self.update_balance(user, -price)
            await ctx.send(f"Congratulations, you officially adopted {name}! You can view your pet now with `lem pet info` or `lem pet view`")
            return




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