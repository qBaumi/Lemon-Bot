import json
import cogs.essentialfunctions as es
from discord.ext import commands
import discord, asyncio
from discord import app_commands
from discord import ui
from config import guilds, allowedAdminRoles
from discord.app_commands import Choice
from config import allowedAdminRoles, guilds

class admincommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="deleteitem", description="Admin command to delete an item from someones inventory")
    #@commands.has_any_role("Admins", "HM", "Developer")
    @app_commands.describe(user="User that gets item removed")
    @app_commands.describe(item="Item that gets deleted")
    @app_commands.choices(item=[
        Choice(name='Mystery Skin', value="mysteryskin"),
        Choice(name='Nitro Classic', value="nitroclassic"),
        Choice(name='Discord Nitro', value="discordnitro"),
        Choice(name='Tier1sub', value="tier1sub"),
        Choice(name='Mystery Skin for 975RP', value="mysteryskin975rp"),
    ])
    async def deleteitem(self, interaction : discord.Interaction, user: discord.User, item : Choice[str]):
        if not await es.checkPerms(interaction, allowedAdminRoles):
            return
        try:
            await es.del_item(user.id, item.value, 1)
        except:
            await interaction.response.send_message("Error item not found or jlfkadsöjfdf @!<442913791215140875>")

        await interaction.response.send_message(f"{item.name} has been successfully removed from {user.name}'s inventory!")


    @app_commands.command(name="gift", description="Admin Command to gift Golden Lemons to users")
    @app_commands.describe(user="User that receives the Lemons")
    @app_commands.describe(amount="Amount of Lemons/Golden Lemons")
    @app_commands.choices(currency=[
        Choice(name='Golden Lemons', value="golden lemons"),
        Choice(name='Lemons', value="lemons")
    ])
    #@commands.has_any_role("Admins", "HM", "Developer")
    async def gift(self, interaction : discord.Interaction, user: discord.User, amount : int, *, currency : Choice[str]):
        adminuser = interaction.user
        currency = currency.value
        if not await es.checkPerms(interaction, allowedAdminRoles):
            return

        async def check_account(userid):
            ids = es.sql_select("SELECT id FROM users")
            for id in ids:
                ### SELECT RETURNS TUPLES WHICH HAVE AN INDEX
                if str(userid) == id[0]:
                    return True
            return False

        if await check_account(user.id) == False:
            # here startup
            await es.open_account(user)
            em = discord.Embed(color=discord.Color.blurple(), title="Hello!",
                               description=f"Let me introduce you to our little friend Lemon right here.")
            em.add_field(name="Welcome you can find out more about me with <lem about>",
                         value="Congrats! You already found the *startup command*. \n"
                               "Next is the `lem lemons` or `lem balance` command. You can look up your balance there, \nbut don't forget to NEVER share your bank account data! \nUse `lem help` for more information")
            await interaction.channel.send(f"{user.mention}", embed=em)
            await es.update_balance(user, 50)
        if currency == "lemons":
            mode = "pocket"
        else:
            mode = "safe"
        print(f"{adminuser.name} gifted {user} {amount} {currency}")
        await es.update_balance(user, int(amount), mode=mode)
        await interaction.response.send_message(f"{user} received {amount} {currency}")


    #@commands.has_any_role("Admins", "Developer", "HM")
    @app_commands.command(name="refill", description="Admin command to refill the Golden Lemon Shop")
    @app_commands.describe(item="Item that gets refilled")
    @app_commands.describe(amount="Amount of Items")
    @app_commands.choices(item=[
        Choice(name='Mystery Skin', value="MysterySkin"),
        Choice(name='Nitro Classic', value="NitroClassic"),
        Choice(name='Discord Nitro', value="DiscordNitro"),
        Choice(name='Tier1sub', value="Tier1sub"),
        Choice(name='Mystery Skin for 975RP', value="MysterySkin975RP"),
    ])
    async def refill(self, interaction : discord.Interaction, item : Choice[str], amount : int):
        item = item.value
        if not await es.checkPerms(interaction, allowedAdminRoles):
            return
        if amount == 0:
            await interaction.response.send_message("You didnt specify the amount `lem refill Mysteryskin 10` for example")
            return
        specialitems = await es.get_item_data()
        index = -1
        exists = 0
        item = item.lower()
        for thing in specialitems:
            for specialitem in specialitems[thing]:
                print(specialitem)
                name = specialitem['name'].lower()
                stock = specialitem['stock']
                index = index + 1
                if name == item:
                    exists = 1
                    break
        if exists == 0:
            await interaction.response.send_message("That item cannot be refilled!")
            str1 = ""
            for thing in specialitems:
                for specialitem in specialitems[thing]:
                    str1 += f"{specialitem['name']}, "
            await interaction.response.send_message(f"List of items that can be refilled {str1}")
            return
        specialitems["MysterySkin"][index]["stock"] = specialitems["MysterySkin"][index]["stock"] + int(amount)
        instock = specialitems["MysterySkin"][index]["stock"]
        with open("./json/spItems.json", "w") as f:
            json.dump(specialitems, f, indent=4)
        await interaction.response.send_message(f"There are now {instock} {name}'s in stock")

    #GETS ITEM AMOUNTS FOR A SPECIFIC ITEM AND RETURNS LIST FROM USERS ONLY FOR ADMINS
    @commands.has_any_role("Admins", "Developer", "HM")
    @commands.command()
    async def listitem(self, ctx, item="None"):
        if item == "None":
            await ctx.send("You didn't specify which item you want to list `lem listItem itemname`")
            return
        mysql = f'SELECT id, amount FROM items WHERE name = "{item.lower()}"'
        es.mycursor.execute(mysql)
        data = es.mycursor.fetchall()
        print(data)

        em = discord.Embed(colour=discord.Color.red(), title=f"List of users with {item}")

        for tuple in data:
            print(tuple)
            user = await self.client.fetch_user(tuple[0])
            em.add_field(name=f"name: {user}", value=f"id: {tuple[0]}\namount: {tuple[1]}", inline=False)

        await ctx.send(embed=em)


    @commands.command()
    @commands.has_any_role("Admins", "HM", "Developer")
    async def presentlist(self, ctx):
        with open("./json/present.json", "r", encoding="utf-8") as f:
            ids = json.load(f)
        list = ""
        for id in ids:
            user = await self.client.fetch_user(id)
            list += str(user) + "\n"
        await ctx.send(list)

    @presentlist.error
    async def on_command_error(self, ctx, error):
        await ctx.send(
            f"{ctx.author.mention}\nYou need to be an Admin, in order to use this command\nIf you are a Mod, please use **lem moddeleteitem** instead")
        await ctx.send(error)


async def setup(client):
    await client.add_cog(admincommands(client), guilds=guilds)