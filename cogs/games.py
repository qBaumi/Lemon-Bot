import json

import discord
from PIL import Image, ImageDraw
from discord.ext import commands
import random, asyncio
import cogs.essentialfunctions as es
from discord import app_commands
from config import guilds

class games(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="lottery", description="Gamba in the loterry")
    @app_commands.describe(bet="How much money you want to risk")
    async def lottery(self, interaction : discord.Interaction, bet : int):

        #Globals
        users = await es.get_bank_data(interaction.user.id)
        user = interaction.user

        if not await es.interaction_check_account(interaction):
            return
        if bet == 0:
            await interaction.response.send_message(f"{user.mention}\n<:FeelsDankMan:810802803739983903>")
            return
        if bet < 0:
            await interaction.response.send_message(f"{user.mention}\nYou think I wouldnt see that coming? :)")
            return
        if users[str(user.id)]['pocket'] < bet:
            await interaction.response.send_message(f"{user.mention}\nYou don't have enough money")
            return

        await es.update_balance(user, bet * -1)

        fruits = ['<:pineapple:881594630888620052>', '<:grapes:881594630888620052>', '<:cherries:881594630888620052>',
                  '<:green_apple:881594630888620052>', '<:lemon:881594630888620052>']
        em = discord.Embed(title="Lottery", description="Your bet gets multiplied for each lemon",
                           colour=discord.Color.from_rgb(254, 254, 51))
        fruit1 = random.choice(fruits)
        fruit2 = random.choice(fruits)
        fruit3 = random.choice(fruits)
        fruit4 = random.choice(fruits)
        win = 0
        if fruit1 == "<:lemon:881594630888620052>":
            win += bet
        if fruit2 == "<:lemon:881594630888620052>":
            win += bet
        if fruit3 == "<:lemon:881594630888620052>":
            win += bet
        if fruit4 == "<:lemon:881594630888620052>":
            win += bet

        multiplier = 0
        if win == bet:
            multiplier = 1
        if bet * 2 == win:
            multiplier = 2
        if bet * 3 == win:
            multiplier = 3
        if bet * 4 == win:
            multiplier = 4
        realwin = win - bet
        em.add_field(name=f"\u200b",
                     value=f"<:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052>\n"
                           f"<:red_square:881594630888620052>{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}<:red_square:881594630888620052> \u200b **BET: {bet} lemons**\n"
                           f"<:arrow:881594485023314040>{fruit1}{fruit2}{fruit3}{fruit4}<:arrow_back:881594471521878047> \u200b **MULT: {multiplier}x**\n"
                           f"<:red_square:881594630888620052>{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}{random.choice(fruits)}<:red_square:881594630888620052> \u200b **WIN: {realwin} lemons\n**"
                           f"<:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052><:red_square:881594630888620052>\n")
        if multiplier == 0:
            em.set_footer(text="No luck today? :(")
        if multiplier == 4:
            em.set_footer(text="JACKPOOOOOOOOOOOT")
        await interaction.response.send_message(embed=em)
        await es.update_balance(user, win)

    @app_commands.command(name="roulette", description="Gamba in the casino, set your bet to red, black, odd, even or on a number")
    @app_commands.describe(bet="How much money you want to risk")
    async def roulette(self, interaction : discord.Interaction, bet : int):

        #Globals
        users = await es.get_bank_data(interaction.user.id)
        user = interaction.user

        if not await es.interaction_check_account(interaction):
            await interaction.response.send_message(f"{user.mention}\nYou need to use `/startup` first")
            return
        if bet == 0:
            await interaction.response.send_message(f"{user.mention}\n<:FeelsDankMan:810802803739983903>")
            return
        if bet < 0:
            await interaction.response.send_message(f"{user.mention}\nYou think I wouldnt see that coming? :)")
            return
        if users[str(user.id)]['pocket'] < bet:
            await interaction.response.send_message(f"{user.mention}\nYou don't have enough money in their pocket!")
            return

        def check(message):
            return message.channel == interaction.channel and message.author == user

        await interaction.response.send_message(
            "Where do you set your bet on?\n`red`🟥\n`black`⬛\n`odd` 1️⃣\n`even` 2️⃣\nnumber between `0` and `36`")

        try:
            # I can get both of the parameters of checkreaction like this
            msg = await self.client.wait_for('message', timeout=60, check=check)
            bid = "None"
            if msg.content.lower() == "red" or msg.content.lower() == "black" or msg.content.lower() == "odd" or msg.content.lower() == "even" or int(
                    msg.content) >= 0 and int(msg.content) <= 36:
                await interaction.channel.send(f"{user.mention}\nYou set your bet on {msg.content}")
                try:
                    bid = int(msg.content)
                except:
                    bid = msg.content.lower()

            else:
                await interaction.channel.send(f"{user.mention}\nYou cant set your bet on that!")
                return
            await es.update_balance(user, -bet)
            number = random.randrange(0, 37)
            print(number)
            red = [9, 18, 7, 12, 3, 32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14]
            black = [31, 22, 29, 28, 35, 26, 15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20]
            iswon = False
            timeswin = 1
            if bid == "red":
                if number in red:
                    iswon = True
            if bid == "black":
                if number in black:
                    iswon = True
            if bid == "odd":
                if number % 2 == 1:
                    iswon = True
            if bid == "even":
                if number % 2 == 0 and number != 0:
                    iswon = True
            if bid == number:
                timeswin = 2
                iswon = True
            if iswon == False:
                line = "lost"
            if iswon == True:
                line = "won"

            degreelist = [9, 22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11,
                          30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31]
            index = -1
            for i in degreelist:
                index += 1
                if i == number:
                    break

            img = Image.open("./img/roulette/roulette2.png")
            im2 = img.convert('RGBA')
            # rotated image
            rot = im2.rotate(360 / 37 * index)
            # a white image same size as rotated image
            fff = Image.new('RGBA', rot.size, (255,) * 4)
            # create a composite image using the alpha layer of rot as a mask
            out = Image.composite(rot, fff, rot)
            # save your work (converting back to mode='1' or whatever..)

            # img = img.rotate(45, PIL.Image.NEAREST, expand = 1)
            # img.resize((500, 500))

            draw = ImageDraw.Draw(out)
            draw.ellipse((430, 215, 460, 245), fill=(255, 255, 255))
            out.convert(img.mode).save('./img/roulette/roulettesaved.png')
            # img.save("roulettesaved.png")

            if iswon == True:
                await es.update_balance(user, bet * 2 * timeswin)

            file = discord.File("./img/roulette/roulettesaved.png")
            em = discord.Embed(colour=discord.Color.gold(),
                               title=f"{user.name} {line} {bet * 2 * timeswin - bet} lemons!",
                               description=f"The ball landed on the {number}!")
            em.set_image(url="attachment://roulettesaved.png")
            await interaction.channel.send(f"{user.mention}\n", embed=em, file=file)


        except asyncio.TimeoutError:
            await interaction.response.send_message(f"{user.name} did not answer in time")
            return

    @app_commands.command(name="minesweeper", description="Play a round of minesweeper Gladge")
    async def minesweeper(self, interaction : discord.Interaction):

        rows = 9
        col = 9
        bombs = 10
        bombcoords = []

        empty = "⬛"
        one = "1️⃣"
        two = "2️⃣"
        three = "3️⃣"
        four = "4️⃣"
        five = "5️⃣"
        six = "6️⃣"
        seven = "7️⃣"
        eight = "8️⃣"
        bomb = "💥"


        for i in range(0, bombs):
            while True:
                x = random.randrange(0, col)
                y = random.randrange(0, rows)
                coords = (x, y)
                if coords not in bombcoords:
                    bombcoords.append(coords)
                    break

        """
            return : int
            how many bombs are near
        """
        def bombsnear(x, y, bombcoords):
            bombs = 0
            # ABOTH
            if (x, y + 1) in bombcoords:
                bombs += 1
            # UNDER
            if (x, y - 1) in bombcoords:
                bombs += 1
            # LEFT
            if (x - 1, y) in bombcoords:
                bombs += 1
            # RIGHT
            if (x + 1, y) in bombcoords:
                bombs += 1
            # TOP LEFT
            if (x - 1, y + 1) in bombcoords:
                bombs += 1
            # TOP RIGHT
            if (x + 1, y + 1) in bombcoords:
                bombs += 1
            # BOT LEFT
            if (x - 1, y - 1) in bombcoords:
                bombs += 1
            # BOT RIGHT
            if (x + 1, y - 1) in bombcoords:
                bombs += 1
            return bombs

        """
            return : str
            gives emoji from number
        """
        def numToEmoji(i):
            emoji = ""
            if i == 0:
                emoji = empty
            if i == 1:
                emoji = one
            if i == 2:
                emoji = two
            if i == 3:
                emoji = three
            if i == 4:
                emoji = four
            if i == 5:
                emoji = five
            if i == 6:
                emoji = six
            if i == 7:
                emoji = seven
            if i == 8:
                emoji = eight
            if i == 9:
                emoji = bomb
            return emoji

        """
            Create gameboard
        """
        gameboard = {}
        for i in range(0, rows):
            gameboard[i] = [0] * col

        for x in range(0, col):

            for y in range(0, rows):

                if (x, y) not in bombcoords:
                    gameboard[x][y] = bombsnear(x, y, bombcoords)

                else:
                    gameboard[x][y] = 9






        """
            Now send gameboard with spoilers
        """
        line = ""
        for x in range(0, col):
            for y in range(0, rows):
                line += "||"
                line += numToEmoji(gameboard[x][y])
                line += "||"
            line += "\n"
        await interaction.response.send_message(line)

    @app_commands.command(name="tictactoe", description="Play tictactoe with a friend")
    @app_commands.describe(enemy="Who do you want to play against?")
    async def tictactoe(self, interaction : discord.Interaction, enemy: discord.User):
        # Globals

        challenger = interaction.user
        await interaction.response.defer()

        def checkreaction(reaction, user):
            return reaction.message.id == msg.id and user == enemy and reaction.emoji == "✅" or reaction.message.id == msg.id and user == enemy and reaction.emoji == "❌"

        msg = await interaction.channel.send(f"{enemy.name} has 60 seconds to accept!")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        try:
            # I can get both of the parameters of checkreaction like this
            reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=checkreaction)

            if reaction.emoji == "❌":
                await interaction.followup.send(
                    f"{challenger.mention}\n{enemy.name} dosent wanna play tictactoe with you right now <:Sadge:720250426892615745>")
                return


        except asyncio.TimeoutError:
            await interaction.followup.send(f"{enemy.name} did not accept in time")
            return

        await interaction.followup.send(f"{enemy.name} accepted, let the battle begin!")

        gameboard = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        player1 = challenger
        player2 = enemy
        players = [player1, player2]
        starter = random.choice(players)

        await interaction.channel.send(
            f"{starter.name} starts\nNow type `top left` , `top mid` , `top right` , `mid left`, `mid mid` , `mid right` , `bot left`, `bot mid` or `bot right`")
        topleft1 = "<:rect843:881875152630059019>"
        topleft2 = "<:rect843:881875152630059019>"
        topleft3 = "<:rect843:881875152630059019>"
        topleft4 = "<:rect843:881875152630059019>"
        topmid1 = "<:rect843:881875152630059019>"
        topmid2 = "<:rect843:881875152630059019>"
        topmid3 = "<:rect843:881875152630059019>"
        topmid4 = "<:rect843:881875152630059019>"
        topright1 = "<:rect843:881875152630059019>"
        topright2 = "<:rect843:881875152630059019>"
        topright3 = "<:rect843:881875152630059019>"
        topright4 = "<:rect843:881875152630059019>"
        midleft1 = "<:rect843:881875152630059019>"
        midleft2 = "<:rect843:881875152630059019>"
        midleft3 = "<:rect843:881875152630059019>"
        midleft4 = "<:rect843:881875152630059019>"
        midmid1 = "<:rect843:881875152630059019>"
        midmid2 = "<:rect843:881875152630059019>"
        midmid3 = "<:rect843:881875152630059019>"
        midmid4 = "<:rect843:881875152630059019>"
        midright1 = "<:rect843:881875152630059019>"
        midright2 = "<:rect843:881875152630059019>"
        midright3 = "<:rect843:881875152630059019>"
        midright4 = "<:rect843:881875152630059019>"
        botleft1 = "<:rect843:881875152630059019>"
        botleft2 = "<:rect843:881875152630059019>"
        botleft3 = "<:rect843:881875152630059019>"
        botleft4 = "<:rect843:881875152630059019>"
        botmid1 = "<:rect843:881875152630059019>"
        botmid2 = "<:rect843:881875152630059019>"
        botmid3 = "<:rect843:881875152630059019>"
        botmid4 = "<:rect843:881875152630059019>"
        botright1 = "<:rect843:881875152630059019>"
        botright2 = "<:rect843:881875152630059019>"
        botright3 = "<:rect843:881875152630059019>"
        botright4 = "<:rect843:881875152630059019>"

        isWon = False

        turn = 0
        # turn
        while True:
            if turn != 0:

                if str(starter) == str(player1):
                    starter = player2
                else:
                    starter = player1

            if gameboard[0][0] == 1:
                topleft1 = "<:x1:881870717451391006>"
                topleft2 = "<:x2:881870728339808286>"
                topleft3 = "<:x3:881870748925440030>"
                topleft4 = "<:x4:881870748707336292>"
            if gameboard[0][1] == 1:
                topmid1 = "<:x1:881870717451391006>"
                topmid2 = "<:x2:881870728339808286>"
                topmid3 = "<:x3:881870748925440030>"
                topmid4 = "<:x4:881870748707336292>"
            if gameboard[0][2] == 1:
                topright1 = "<:x1:881870717451391006>"
                topright2 = "<:x2:881870728339808286>"
                topright3 = "<:x3:881870748925440030>"
                topright4 = "<:x4:881870748707336292>"
            if gameboard[1][0] == 1:
                midleft1 = "<:x1:881870717451391006>"
                midleft2 = "<:x2:881870728339808286>"
                midleft3 = "<:x3:881870748925440030>"
                midleft4 = "<:x4:881870748707336292>"
            if gameboard[1][1] == 1:
                midmid1 = "<:x1:881870717451391006>"
                midmid2 = "<:x2:881870728339808286>"
                midmid3 = "<:x3:881870748925440030>"
                midmid4 = "<:x4:881870748707336292>"
            if gameboard[1][2] == 1:
                midright1 = "<:x1:881870717451391006>"
                midright2 = "<:x2:881870728339808286>"
                midright3 = "<:x3:881870748925440030>"
                midright4 = "<:x4:881870748707336292>"
            if gameboard[2][0] == 1:
                botleft1 = "<:x1:881870717451391006>"
                botleft2 = "<:x2:881870728339808286>"
                botleft3 = "<:x3:881870748925440030>"
                botleft4 = "<:x4:881870748707336292>"
            if gameboard[2][1] == 1:
                botmid1 = "<:x1:881870717451391006>"
                botmid2 = "<:x2:881870728339808286>"
                botmid3 = "<:x3:881870748925440030>"
                botmid4 = "<:x4:881870748707336292>"
            if gameboard[2][2] == 1:
                botright1 = "<:x1:881870717451391006>"
                botright2 = "<:x2:881870728339808286>"
                botright3 = "<:x3:881870748925440030>"
                botright4 = "<:x4:881870748707336292>"

            ##player2
            if gameboard[0][0] == 2:
                topleft1 = "<:o1:881935408378822676>"
                topleft2 = "<:o2:881935419313389569>"
                topleft3 = "<:o4:881935448501547018>"
                topleft4 = "<:o4:881935426330431548>"
            if gameboard[0][1] == 2:
                topmid1 = "<:o1:881935408378822676>"
                topmid2 = "<:o2:881935419313389569>"
                topmid3 = "<:o4:881935448501547018>"
                topmid4 = "<:o4:881935426330431548>"
            if gameboard[0][2] == 2:
                topright1 = "<:o1:881935408378822676>"
                topright2 = "<:o2:881935419313389569>"
                topright3 = "<:o4:881935448501547018>"
                topright4 = "<:o4:881935426330431548>"
            if gameboard[1][0] == 2:
                midleft1 = "<:o1:881935408378822676>"
                midleft2 = "<:o2:881935419313389569>"
                midleft3 = "<:o4:881935448501547018>"
                midleft4 = "<:o4:881935426330431548>"
            if gameboard[1][1] == 2:
                midmid1 = "<:o1:881935408378822676>"
                midmid2 = "<:o2:881935419313389569>"
                midmid3 = "<:o4:881935448501547018>"
                midmid4 = "<:o4:881935426330431548>"
            if gameboard[1][2] == 2:
                midright1 = "<:o1:881935408378822676>"
                midright2 = "<:o2:881935419313389569>"
                midright3 = "<:o4:881935448501547018>"
                midright4 = "<:o4:881935426330431548>"
            if gameboard[2][0] == 2:
                botleft1 = "<:o1:881935408378822676>"
                botleft2 = "<:o2:881935419313389569>"
                botleft3 = "<:o4:881935448501547018>"
                botleft4 = "<:o4:881935426330431548>"
            if gameboard[2][1] == 2:
                botmid1 = "<:o1:881935408378822676>"
                botmid2 = "<:o2:881935419313389569>"
                botmid3 = "<:o4:881935448501547018>"
                botmid4 = "<:o4:881935426330431548>"
            if gameboard[2][2] == 2:
                botright1 = "<:o1:881935408378822676>"
                botright2 = "<:o2:881935419313389569>"
                botright3 = "<:o4:881935448501547018>"
                botright4 = "<:o4:881935426330431548>"

            await interaction.channel.send(
                f"{topleft1}{topleft2}:white_large_square:{topmid1}{topmid2}:white_large_square:{topright1}{topright2}\n"
                f"{topleft3}{topleft4}:white_large_square:{topmid3}{topmid4}:white_large_square:{topright3}{topright4}\n"
                f":white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n"
                f"{midleft1}{midleft2}:white_large_square:{midmid1}{midmid2}:white_large_square:{midright1}{midright2}\n"
                f"{midleft3}{midleft4}:white_large_square:{midmid3}{midmid4}:white_large_square:{midright3}{midright4}\n"
                f":white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:\n"
                f"{botleft1}{botleft2}:white_large_square:{botmid1}{botmid2}:white_large_square:{botright1}{botright2}\n"
                f"{botleft3}{botleft4}:white_large_square:{botmid3}{botmid4}:white_large_square:{botright3}{botright4}\n")

            def checkturn(m):
                if m.author != starter or m.channel != interaction.channel:
                    return False
                return m.content == f"top left" or m.content == f"top mid" or m.content == f"top right" or m.content == f"mid left" or m.content == f"mid mid" or m.content == f"mid right" or m.content == f"bot left" or m.content == f"bot mid" or m.content == f"bot right"

            if turn != 0:
                await interaction.channel.send(
                    f"Now it's {starter.mention}'s turn.\nType `top left` , `top mid` , `top right` , `mid left`, `mid mid` , `mid right` , `bot left`, `bot mid` or `bot right`")
            turn = turn + 1
            while True:
                try:
                    msg = await self.client.wait_for('message', timeout=30, check=checkturn)
                    msg.content = msg.content.lower()
                    if msg.content == "top left" and starter == player1:
                        if gameboard[0][0] == 0:
                            gameboard[0][0] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "top mid" and starter == player1:
                        if gameboard[0][1] == 0:
                            gameboard[0][1] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "top right" and starter == player1:
                        if gameboard[0][2] == 0:
                            gameboard[0][2] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "mid left" and starter == player1:
                        if gameboard[1][0] == 0:
                            gameboard[1][0] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "mid mid" and starter == player1:
                        if gameboard[1][1] == 0:
                            gameboard[1][1] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "mid right" and starter == player1:
                        if gameboard[1][2] == 0:
                            gameboard[1][2] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "bot left" and starter == player1:
                        if gameboard[2][0] == 0:
                            gameboard[2][0] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "bot mid" and starter == player1:
                        if gameboard[2][1] == 0:
                            gameboard[2][1] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "bot right" and starter == player1:
                        if gameboard[2][2] == 0:
                            gameboard[2][2] = 1
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")

                    # player2
                    if msg.content == "top left" and starter == player2:
                        if gameboard[0][0] == 0:
                            gameboard[0][0] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "top mid" and starter == player2:
                        if gameboard[0][1] == 0:
                            gameboard[0][1] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "top right" and starter == player2:
                        if gameboard[0][2] == 0:
                            gameboard[0][2] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "mid left" and starter == player2:
                        if gameboard[1][0] == 0:
                            gameboard[1][0] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "mid mid" and starter == player2:
                        if gameboard[1][1] == 0:
                            gameboard[1][1] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "mid right" and starter == player2:
                        if gameboard[1][2] == 0:
                            gameboard[1][2] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "bot left" and starter == player2:
                        if gameboard[2][0] == 0:
                            gameboard[2][0] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "bot mid" and starter == player2:
                        if gameboard[2][1] == 0:
                            gameboard[2][1] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")
                    if msg.content == "bot right" and starter == player2:
                        if gameboard[2][2] == 0:
                            gameboard[2][2] = 2
                            break
                        else:
                            await interaction.channel.send("You can't mark this field")

                except:
                    await interaction.channel.send(f"{enemy.name} did not answer in time")
                    return

            if gameboard[0][0] == 1 and gameboard[0][1] == 1 and gameboard[0][2] == 1:
                isWon = True
                winner = player1
            if gameboard[1][0] == 1 and gameboard[1][1] == 1 and gameboard[1][2] == 1:
                isWon = True
                winner = player1
            if gameboard[2][0] == 1 and gameboard[2][1] == 1 and gameboard[2][2] == 1:
                isWon = True
                winner = player1

            if gameboard[0][0] == 1 and gameboard[1][0] == 1 and gameboard[2][0] == 1:
                isWon = True
                winner = player1
            if gameboard[0][1] == 1 and gameboard[1][1] == 1 and gameboard[2][1] == 1:
                isWon = True
                winner = player1
            if gameboard[0][2] == 1 and gameboard[1][2] == 1 and gameboard[2][2] == 1:
                isWon = True
                winner = player1

            if gameboard[0][0] == 1 and gameboard[1][1] == 1 and gameboard[2][2] == 1:
                isWon = True
                winner = player1
            if gameboard[0][2] == 1 and gameboard[1][1] == 1 and gameboard[2][0] == 1:
                isWon = True
                winner = player1

            if gameboard[0][0] == 2 and gameboard[0][1] == 2 and gameboard[0][2] == 2:
                isWon = True
                winner = player2
            if gameboard[1][0] == 2 and gameboard[1][1] == 2 and gameboard[1][2] == 2:
                isWon = True
                winner = player2
            if gameboard[2][0] == 2 and gameboard[2][1] == 2 and gameboard[2][2] == 2:
                isWon = True
                winner = player2

            if gameboard[0][0] == 2 and gameboard[1][0] == 2 and gameboard[2][0] == 2:
                isWon = True
                winner = player2
            if gameboard[0][1] == 2 and gameboard[1][1] == 2 and gameboard[2][1] == 2:
                isWon = True
                winner = player2
            if gameboard[0][2] == 2 and gameboard[1][2] == 2 and gameboard[2][2] == 2:
                isWon = True
                winner = player2

            if gameboard[0][0] == 2 and gameboard[1][1] == 2 and gameboard[2][2] == 2:
                isWon = True
                winner = player2
            if gameboard[0][2] == 2 and gameboard[1][1] == 2 and gameboard[2][0] == 2:
                isWon = True
                winner = player2

            if isWon == True:

                em = discord.Embed(colour=discord.Color.gold(),
                                   title=f"Congratulations, {winner.name} won!")
                if winner == player2:
                    looser = player1
                else:
                    looser = player2

                await interaction.channel.send(embed=em)
                return

            if gameboard[0][0] != 0 and gameboard[0][1] != 0 and gameboard[0][2] != 0 and gameboard[1][0] != 0 and \
                    gameboard[1][1] != 0 and gameboard[1][2] != 0 and gameboard[2][0] != 0 and gameboard[2][1] != 0 and \
                    gameboard[2][2] != 0:
                await interaction.channel.send("It's a draw, nobody won. What a pitty!")
                return

    # TODO: BLACKJACK
    """
    @commands.command()
    async def blackjack(self, ctx, bet=0):
        if await self.check_account(ctx.author) == False:
            await ctx.send(f"{ctx.author.mention}\nYou need to use `/startup` first")
            return
        if bet==0:
            await ctx.send(f"{ctx.author.mention}\nYou didn't set a bet, try again `/roulette 10` for example")
            return
        if bet<0:
            await ctx.send(f"{ctx.author.mention}\nYou think I wouldnt see that coming? :)")
            return
        users = await self.get_bank_data(ctx.author.id)
        user = ctx.author
        if users[str(user.id)]['pocket'] < bet:
            await ctx.send(f"{ctx.author.mention}\nYou don't have enough money in their pocket!")
            return
        def create_deck():
            deck = []
            for x in range(0, 4):
                for i in range(1, 12):
                    deck.append(i)
            for i in range(0, 4):
                deck.append(10)
                deck.append(10)
                deck.append(10)
            print(deck)
            return deck
        def draw(deck):
            card = random.randrange(0, len(deck))
            card = deck[card]
            symbol = random.randrange(1, 5)
            print(symbol)
            if symbol == 1:
                symbol = "♥"
            elif symbol == 2:
                symbol = "♠"
            elif symbol == 3:
                symbol = "♣"
            elif symbol == 4:
                symbol = "♦"
            print(symbol)
            if card == 10:
                kingqueenboyor10 = random.randrange(1, 5)
                print(kingqueenboyor10)
                if kingqueenboyor10 == 1:
                    out = "king"
                elif kingqueenboyor10 == 2:
                    out = "queen"
                elif kingqueenboyor10 == 3:
                    out = "boy"
                elif kingqueenboyor10 == 4:
                    out = 10
            elif card == 11:
                out = "ace"
            else:
                out = str(card)
            out = symbol + " " + str(out)
            return card, out
        deck = create_deck()
        score = 0
        bankscore = 0
        cardvalue, out = draw(deck)
        score += cardvalue
        await ctx.send("You drew " + out)
        """

    @app_commands.command(name="wouldyourather", description="Hmm, what am I gonna put as description?")
    async def wouldyourather(self, interaction : discord.Interaction):

        with open("./json/wyr.json", "r") as f:
            wyr = json.load(f)
        while True:
            scenedict = random.choice(wyr)
            scenedict2 = random.choice(wyr)
            if scenedict["category"] == scenedict2["category"]:
                break
        scene = scenedict["scene"]
        scene2 = scenedict2["scene"]
        await interaction.response.send_message(f"{interaction.user.mention}\nWould you rather {scene} or {scene2}")

    @app_commands.command(name="wordle", description="Play a game of wordle")
    async def wordle(self, interaction : discord.Interaction):

        with open("./json/wordle_emojis.json", "r") as f:
            emojis = json.load(f)

        empty = "<:empty:941356986476408873>"
        guesses = {0 : "", 1 : "", 2 : "", 3 : "", 4 : "", 5 : ""}

        # Get solution
        with open("./json/wordlist.json", "r") as f:
            wordlist = json.load(f)
        solution = random.choice(wordlist)
        print(solution)

        async def howtoplay():
            await interaction.response.send_message("""**Wordle**\n
**How to play**
Type a word that has **5 letters**
It will appear :green_square: if it is at the **right place** of the **solution**
If it is :yellow_square: the letter is in the word but at a **different spot**
And if the letter appears :blue_square: it the word **doesn't contain the letter at all**
You can try **6 times**
**Good Luck!**\n \n<:rect843:881875152630059019>""")

        # sends messages with fields
        async def sendembed(guesses):
            previousguess = "asdfjklö"
            for i in range(6):
                if previousguess == "":
                    return
                if guesses[i] == "":
                    await interaction.channel.send(f"{empty} {empty} {empty} {empty} {empty} ")
                else:
                    sendstr = ""
                    for x in range(5):
                        sendstr += f"{convertToEmoji(guesses[i], x)} "
                    await interaction.channel.send(sendstr)
                previousguess = guesses[i]
        def convertToEmoji(guess, letterindex):
            return emojis[getLetterColor(guess, letterindex)][guess[letterindex]]
        def getLetterColor(guess, letterpos):
            if guess[letterpos] == solution[letterpos]:
                return "green"
            if guess[letterpos] in solution:
                return "yellow"
            return "blue"
        def check(message):
            return message.channel == interaction.channel and message.author == interaction.user
        async def getguess():
            try:
                while True:
                    msg = await self.client.wait_for('message', timeout=300, check=check)
                    msg.content = msg.content.lower()
                    if len(msg.content) != 5:
                        await interaction.channel.send("**The word must be 5 letters long!**")
                        #await getguess()
                    elif not msg.content.isalpha() or " " in msg.content:
                        await interaction.channel.send("**Only letters are allowed! Nice try MTD :)**")
                        #await getguess()
                    elif not msg.content in wordlist:
                        await interaction.channel.send("**This isn't an allowed word**")
                    else:
                        return msg.content
            except asyncio.TimeoutError:
                await interaction.channel.send(f"You didn't answer in time")
                return "0"
        def win():
            try:
                print("update")
                es.mycursor.execute(f"SELECT wins FROM wordle WHERE id = '{interaction.user.id}'")
                data = es.mycursor.fetchall()
                prevpoints = int(data[0][0])
                sql = f"UPDATE wordle SET wins = {prevpoints + 1} WHERE id = '{interaction.user.id}'"
            except:
                sql = f"INSERT INTO wordle (id, wins) VALUES ('{interaction.user.id}', 1)"
                print("insert")
            es.mycursor.execute(sql)
            es.mydb.commit()
            return prevpoints + 1


        await howtoplay()
        await sendembed(guesses)

        #loop through the 6 tries
        for i in range(6):
            guesses[i] = await getguess()
            if guesses[i] == "0":
                return
            if guesses[i] == solution:
                await interaction.channel.send("**Congratulations you won!!!**")
                await interaction.channel.send(f"{convertToEmoji(solution, 0)} {convertToEmoji(solution, 1)} {convertToEmoji(solution, 2)} {convertToEmoji(solution, 3)} {convertToEmoji(solution, 4)} ")
                wins = win()
                await interaction.channel.send(f"**You now have {wins} wins in total!**")
                return
            await sendembed(guesses)
        await interaction.channel.send(f"**Unfortunately you used all your six tries without guessing the solution :(, the solution was**\n**{solution}**")



    async def getemojidict(self):

        # fetch guild
        guild = await self.client.fetch_guild(828921143507288064)
        emojis = guild.emojis
        print(emojis)

        emojidict = {
            "green":
                {},
            "yellow":
                {}
        }

        for emoji in emojis:
            print(emoji.name)
            if emoji.name.startswith("green_"):
                emojidict["green"][emoji.name[len(emoji.name)-1:len(emoji.name)]] = str(emoji)
            elif emoji.name.startswith("yellow_"):
                emojidict["yellow"][emoji.name[len(emoji.name)-1:len(emoji.name)]] = str(emoji)

        print(emojidict)

    @app_commands.command(name="wordleaderboard", description="Leaderboard for Wordle")
    async def wordleaderboard(self, interaction : discord.Interaction):

        """
        list of tuples
        user = (user.id, points)
        data = [(user.id, points), (user.id, points), (user.id, points)...]
        """
        data = es.sql_select(f"SELECT * FROM wordle ORDER BY wins DESC LIMIT 10")


        em = discord.Embed(colour=discord.Color.teal(), title="Wordle Leaderboard")
        for user in data:
            member = await self.client.fetch_user(user[0])
            em.add_field(name=str(member), value=f"{user[1]} Wins", inline=False)
        await interaction.response.send_message(embed=em)



async def setup(client):
    await client.add_cog(games(client), guilds=guilds)