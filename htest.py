import discord
import requests
import json
import random
from discord.ext.commands import bot
from discord.ext import commands

API_TOKEN = "&api_key=6edceb08a4ab5c6c6d4fb8d65f7db50dec2ffcf6acbb4905d40751bed9cb0660&user_id=500094"
tags = "&tags=ahegao+azur_lane"

class Htest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def getH(self, ctx):
        url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index" + tags + API_TOKEN + "&json=1"
        r = requests.get(url=url)
        with open('r.json', 'w') as json_file:
            json.dump(r.json(), json_file)
        await ctx.channel.send("Accessed API with status code" + str(r.status_code))
        print(r.json()[1])




    @commands.command()
    async def test(self, ctx):
        await self.getH(ctx)

    @commands.command()
    async def h(self, ctx):
        url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index" + tags + API_TOKEN + "&json=1"
        r = requests.get(url=url)
        with open('r.json', 'w') as json_file:
            json.dump(r.json(), json_file)
        data = r.json()
        post = data[random.randint(1,99)]
        await ctx.channel.send(post['file_url'])





def setup(Bot):
    Bot.add_cog(Htest(Bot))
