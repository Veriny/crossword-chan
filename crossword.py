import discord
from discord.ext.commands import bot
from discord.ext import commands
import asyncio
import urllib.request
import json
import requests
import random
import sys
from PIL import Image

print("finished imports")

bossiber = Image.open('bossiber.jpg')
bossiber_square = bossiber.crop((0, 0, 481, 481))
bossiber_square = bossiber_square.resize((6465, 6465))

cell_image = Image.open('trans_square.png')
cell_image = cell_image.convert("RGBA")
# cell_image = cell_image.crop((0,0,431,431))

black_cell = Image.open('black_square.png')
black_cell = black_cell.convert("RGBA")
black_cell = black_cell.resize((431, 431))
# black_cell = black_cell.crop((0,0,431,431))

width, height = cell_image.size

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

        crossword_image = Image.new('RGBA', (15 * width, 15 * height))
        x_offset = 0
        y_offset = 0

        for char in xwordData["grid"]:
            # new row after every 15 emojis
            if column % 15 == 0 and column != 0:
                # remove space from last emoji unicode and add \n
                # output = output[:-1] + '\n'
                y_offset += height
                x_offset = 0
            column += 1

            if char == '.':
                # output += "██"
                # output += "\u2b1b "  => black square emoji
                print('. received, this should be a black square gdmt')
                crossword_image.paste(black_cell, (x_offset, y_offset))
                x_offset += width
            elif char == '*':
                output += "\u2b1c "  # white square emoji
                crossword_image.paste(cell_image, (x_offset, y_offset))
                x_offset += width
            else:
                # crossword cell contains a letter
                # emojiName = 'regional_indicator_' + char.lower()
                # unicodeStr = emojiData[emojiName]
                # output += unicodeStr + ' '

                crossword_image.paste(cell_image, (x_offset, y_offset))
                x_offset += width
                # unicodeStr = unicodeStr.encode('utf-16','surrogatepass').decode('utf-16')
                # asciiStr = ascii(json.loads(r'{unicodeStr}'))

        bossiber_square.paste(crossword_image, (0, 0), crossword_image)
        bossiber_square.save('crossword_image.png', 'PNG')

        file = discord.File("crossword_image.png")
        await ctx.channel.send(file=file)
        # print(output)
        # print(len(output)) => emb descriptions have a char limit of 2048 reEEEE
        # emb = discord.Embed(description = output, colour = discord.Color(random.randint(0x000000, 0xFFFFFF)))
        # await ctx.channel.send(embed = emb)

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
