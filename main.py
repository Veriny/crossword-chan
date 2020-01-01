import discord
from discord.ext import commands
import os

desktop = os.path.join(os.environ['USERPROFILE'], "Desktop")
token_file = os.path.join(desktop, "token.txt")
file = open(token_file, 'r')
BOT_TOKEN = file.readline()
file.close()
print(BOT_TOKEN)
bot = commands.Bot(command_prefix = "+")

extensions = ['crossword', 'anime_images']

@bot.event
async def on_ready():
    print('Crossword-Chan is online uWu')

@bot.command()
async def load(ctx, cogname):
    if ctx.author.id == 187733221591482370 or ctx.author.id == 383116010971987971:
        try:
            bot.load_extension(cogname)
            await ctx.send("Loaded {}".format(cogname))

        except Exception as e:
            await ctx.send("Unable to load that cog. `{}`".format(str(e)))
    else:
        await ctx.send("Only Daniel and Justin can use that command! This incident will be reported.")

@bot.command()
async def reload(ctx, cogname):
    if ctx.author.id == 187733221591482370 or ctx.author.id == 383116010971987971:
        try:
            bot.reload_extension(cogname)
            await ctx.send("Reloaded {}".format(cogname))
        except Exception as e:
            await ctx.send("Unable to reload that cog. `{}`".format(str(e)))
    else:
        await ctx.send("Only Daniel and Justin can use that command! This incident will be reported")

for ext in extensions:
    bot.load_extension(ext)

bot.run(BOT_TOKEN)
