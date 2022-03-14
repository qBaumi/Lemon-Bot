import discord
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
from config import api_key
from discord import app_commands
from discord import ui
from config import guilds
from discord.app_commands import Choice

class LeagueAPI(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="rank", description="Look up your League of Legends rank")
    @app_commands.choices(region=[
        Choice(name='EUW', value="euw1"),
        Choice(name='NA', value="na1"),
        Choice(name='KR', value="kr"),
        Choice(name='EUN', value="eun1"),
        Choice(name='OCE', value="oc1"),
        Choice(name='LA1', value="la1"),
        Choice(name='LA2', value="la2"),
        Choice(name='TR', value="tr1"),
        Choice(name='RU', value="ru"),
        Choice(name='BR', value="br1"),
        Choice(name='JP', value="jp1"),
    ])
    async def rank(self, interaction: discord.Interaction, region: Choice[str], summonername: str):
        watcher = LolWatcher(api_key)
        my_region = region.value

        try:
            me = watcher.summoner.by_name(my_region, summonername)
            my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
            print(my_ranked_stats)
            if not my_ranked_stats:
                await interaction.response.send_message("This user hasn't played ranked yet!")
                return
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
            await interaction.response.send_message(embed=embed)
        except ApiError as err:
            if err.response.status_code == 429:
                await interaction.response.send_message('Connection error')
            elif err.response.status_code == 404:
                await interaction.response.send_message('We couldnt find this summoner on EUW')
            else:
                raise

async def setup(client):
    await client.add_cog(LeagueAPI(client), guilds=guilds)

