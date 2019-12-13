import discord
from discord.ext.commands import bot
from discord.ext import commands
import asyncio
import urllib.request
import json
import requests
import random
# from PIL import Image, ImageDraw #, ImageFont

print("finished imports")

# codec error when trying to save emojis as an image, possibly because the default font doesn't support emojis
# text = u"\u2b1b" # black large square
# # text = unicode(text, errors='ignore')
# # print(text)
# print(text)
# text.encode('utf-8')
# print(text)
# text.encode('ascii','replace')
# print(text)
# image = Image.new("RGBA", (100,100), (255,255,255))
# # font = ImageFont.truetype("Symbola.ttf", 60, encoding='unic')
# draw = ImageDraw.Draw(image)
# draw.text((0,0), text, (0,0,0))
# image.save("Test.png")

# Emojis
# blackSquare = client.get_emoji(648625053344464945)

class Crossword(commands.Cog):
    '''nytimes crosswords + discord + h*ntai = fun'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def new(self, ctx):
        '''Gets data of a random nytimes crossword from the github repository: https://github.com/doshea/nyt_crosswords'''

        dataRetrieved = False
        while not dataRetrieved:
            day = str(random.randint(1,29))
            year = str(random.randint(1976,2017))
            month = str(random.randint(1,12))
            if int(month) < 10:
                month = "0" + month
            if int(day) < 10:
                day = "0" + day

            xwordURL = "https://raw.githubusercontent.com/doshea/nyt_crosswords/master/" + year + "/" + month + "/" + day + ".json"
            # print(xwordURL)
            # example url: https://raw.githubusercontent.com/doshea/nyt_crosswords/master/2010/06/15.json

            try:
                # send get request and save response as a response object
                r = requests.get(url = xwordURL)
                # extract data in json format
                xwordData = r.json()
                dataRetrieved = True
            except ValueError:
                # some gaps in api coverage
                print("Failed to get JSON data")

        # save crossword data as json file
        with open('xwordData.json', 'w') as json_file:
            json.dump(xwordData, json_file)

        # create a list for the empty crossword
        blankGrid = xwordData["grid"]
        for i in range(0, len(blankGrid)):
            # replace all letters with "*" - represents a blank space
            if blankGrid[i].isalpha():
                blankGrid[i] = "*"
        emptyGrid = {"grid": blankGrid}
        # save the empty grid, will be updated as people fill it in
        with open('currentGrid.json', 'w') as json_file:
            json.dump(emptyGrid, json_file)

        # find a way to invoke the crossword method immediately after it is created

    @commands.command()
    async def crossword(self, ctx):
        '''displays the crossword in a discord embed'''

        column = 0
        output = "" # string of unicode characters representing emojis -> emb description
        with open("currentGrid.json") as f:
            xwordData = json.load(f)
        for char in xwordData["grid"]:
            # new row after every 15 emojis
            if column % 15 == 0:
                # remove space from last emoji unicode and add \n
                output = output[:-1] + '\n'
            column += 1

            if char == '.':
                output += "██"
                # output += "\u2b1b "  => black square emoji
            elif char == '*':
                output += "\u2b1c "  # white square emoji
            else:
                # crossword cell contains a letter
                emojiName = 'regional_indicator_' + char.lower()
                unicodeStr = emojiData[emojiName]
                output += unicodeStr + ' '

                # unicodeStr = unicodeStr.encode('utf-16','surrogatepass').decode('utf-16')
                # asciiStr = ascii(json.loads(r'{unicodeStr}'))

        # print(output)
        # print(len(output)) => emb descriptions have a char limit of 2048 reEEEE
        emb = discord.Embed(description = output, colour = discord.Color(random.randint(0x000000, 0xFFFFFF)))
        await ctx.channel.send(embed = emb)

    @commands.command()
    async def clues(self, ctx, arg):
        '''display clues, user specifies whether to get across to down clues'''

        output = ""
        acrossClues = xwordData["clues"][arg.lower()]
        for clue in acrossClues:
            # print(clue)
            output += clue + '\n'
        emb = discord.Embed(description = output, colour = discord.Color(random.randint(0x000000, 0xFFFFFF)))
        await ctx.channel.send(embed = emb)

def setup(bot):
    bot.add_cog(Crossword(bot))

# TO DO:
# command for getting individual clues
# command for solving row or column of puzzle

# instead of embedding emojis in the description of the embed
# create an image of the crossword using pillow/image to yoink the emojis together
# better for mobile too because the rows and columns get messed up when using description to embed
