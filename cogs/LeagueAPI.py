import discord
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
from config import api_key

class LeagueAPI(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def rank(self, ctx, *, summonername):

        watcher = LolWatcher(api_key)
        my_region = 'euw1'

        try:
            me = watcher.summoner.by_name(my_region, summonername)
            my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])

            i = 0
            embed = discord.Embed(title=my_ranked_stats[i]['summonerName'])

            for queuetype in my_ranked_stats:

                if my_ranked_stats[i]['tier'] == "IRON":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299576100028416/Emblem_Iron.png'
                elif my_ranked_stats[i]['tier'] == "BRONZE":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299567040200714/Emblem_Bronze.png'
                elif my_ranked_stats[i]['tier'] == "SILVER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299582518100018/Emblem_Silver.png'
                elif my_ranked_stats[i]['tier'] == "GOLD":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299572329611274/Emblem_Gold.png'
                elif my_ranked_stats[i]['tier'] == "PLATINUM":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299579681964102/Emblem_Platinum.png'
                elif my_ranked_stats[i]['tier'] == "DIAMOND":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299570508890162/Emblem_Diamond.png'
                elif my_ranked_stats[i]['tier'] == "MASTER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299578318946344/Emblem_Master.png'
                elif my_ranked_stats[i]['tier'] == "GRANDMASTER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299574842261561/Emblem_Grandmaster.png'
                elif my_ranked_stats[i]['tier'] == "CHALLENGER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299570080940052/Emblem_Challenger.png'
                else:
                    tierurl = 'https://cdn.discordapp.com/attachments/756469260951224361/780786830768603146/Fragezeichen.png'
                if my_ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5':
                    embed.set_thumbnail(url=tierurl)
                    qtype = 'Ranked Solo/Duo'
                elif my_ranked_stats[i]['queueType'] == 'RANKED_FLEX_SR':
                    qtype = 'Ranked Flex'

                embed.add_field(name=qtype,
                                value=my_ranked_stats[i]['tier'] + " " + my_ranked_stats[i]['rank'] + "\nLP: " + str(
                                    my_ranked_stats[i]['leaguePoints']), inline=False)
                embed.add_field(name='Wins/Losses',
                                value=str(my_ranked_stats[i]['wins']) + ' / ' + str(my_ranked_stats[i]['losses']),
                                inline=True)
                print(my_ranked_stats[i])
                i = i + 1
            await ctx.send(embed=embed)
        except ApiError as err:
            if err.response.status_code == 429:
                await ctx.send('Connection error')
            elif err.response.status_code == 404:
                await ctx.send('We couldnt find this summoner on EUW')
            else:
                raise

    @commands.command()
    async def rankNA(self, ctx, *, summonername):
        api_key = 'RGAPI-ed5208d6-1fd2-4494-a75e-99cf587f5fea'
        watcher = LolWatcher(api_key)
        my_region = 'na1'

        try:
            me = watcher.summoner.by_name(my_region, summonername)
            my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])

            i = 0
            embed = discord.Embed(title=my_ranked_stats[i]['summonerName'])

            for queuetype in my_ranked_stats:

                if my_ranked_stats[i]['tier'] == "IRON":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299576100028416/Emblem_Iron.png'
                elif my_ranked_stats[i]['tier'] == "BRONZE":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299567040200714/Emblem_Bronze.png'
                elif my_ranked_stats[i]['tier'] == "SILVER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299582518100018/Emblem_Silver.png'
                elif my_ranked_stats[i]['tier'] == "GOLD":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299572329611274/Emblem_Gold.png'
                elif my_ranked_stats[i]['tier'] == "PLATINUM":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299579681964102/Emblem_Platinum.png'
                elif my_ranked_stats[i]['tier'] == "DIAMOND":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299570508890162/Emblem_Diamond.png'
                elif my_ranked_stats[i]['tier'] == "MASTER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299578318946344/Emblem_Master.png'
                elif my_ranked_stats[i]['tier'] == "GRANDMASTER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299574842261561/Emblem_Grandmaster.png'
                elif my_ranked_stats[i]['tier'] == "CHALLENGER":
                    tierurl = 'https://cdn.discordapp.com/attachments/530106038129655810/807299570080940052/Emblem_Challenger.png'
                else:
                    tierurl = 'https://cdn.discordapp.com/attachments/756469260951224361/780786830768603146/Fragezeichen.png'
                if my_ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5':
                    embed.set_thumbnail(url=tierurl)
                    qtype = 'Ranked Solo/Duo'
                elif my_ranked_stats[i]['queueType'] == 'RANKED_FLEX_SR':
                    qtype = 'Ranked Flex'

                embed.add_field(name=qtype,
                                value=my_ranked_stats[i]['tier'] + " " + my_ranked_stats[i]['rank'] + "\nLP: " + str(
                                    my_ranked_stats[i]['leaguePoints']), inline=False)
                embed.add_field(name='Wins/Losses',
                                value=str(my_ranked_stats[i]['wins']) + ' / ' + str(my_ranked_stats[i]['losses']),
                                inline=True)
                print(my_ranked_stats[i])
                i = i + 1
            await ctx.send(embed=embed)
        except ApiError as err:
            if err.response.status_code == 429:
                await ctx.send('Connection error')
            elif err.response.status_code == 404:
                await ctx.send('We couldnt find this summoner on NA')
            else:
                raise

def setup(client):
    client.add_cog(LeagueAPI(client))

