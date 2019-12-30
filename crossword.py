import discord
from discord.ext.commands import bot
from discord.ext import commands
import asyncio
import urllib.request
import json
import requests
import random
import sys
from PIL import Image, ImageFont, ImageDraw

print("Finished imports")

# background image, JAPANESE CARTOON IMAGES HERE
background_image = Image.open('bossiber.jpg')
# crop to make the background image a square
# background_image = background_image.crop((0, 0, 481, 481))
background_image = background_image.resize((1500, 1500))

# transparent square = empty cell
blank_cell = Image.open('trans_square.png')
blank_cell = blank_cell.convert("RGBA")
print(blank_cell.size)

# black square = cell with no letters
black_cell = Image.open('black_square.png')
black_cell = black_cell.convert("RGBA")
print(black_cell.size)

width, height = blank_cell.size

class Crossword(commands.Cog):
    '''nytimes crosswords + discord + japanese cartoon images = fun'''

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

            # example url: https://raw.githubusercontent.com/doshea/nyt_crosswords/master/2010/06/15.json
            
            xwordURL = "https://raw.githubusercontent.com/doshea/nyt_crosswords/master/" + year + "/" + month + "/" + day + ".json"

            try:
                # send get request and save data in json format
                r = requests.get(url = xwordURL)
                xwordData = r.json()
                dataRetrieved = True
            except ValueError:
                # some gaps in api coverage
                print("Failed to get JSON data, making another request")

        # save crossword data as local json file
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
        '''makes an image of the current crossword state and sends it in a discord embed'''

        # load current state of crossword
        with open("currentGrid.json") as f:
            xwordData = json.load(f)

        # Image of the entire crossword will be a 15x15 grid of squares
        crossword_image = Image.new('RGBA', (15 * width, 15 * height))
        x_offset = 0
        y_offset = 0
        column = 0

        for char in xwordData["grid"]:
            # new row after every 15 cells
            if column % 15 == 0 and column != 0:
                # moves down a row and resets x offset to the very left
                y_offset += height
                x_offset = 0
            column += 1

            if char == '.':
                # black cell, move x offset to the right
                crossword_image.paste(black_cell, (x_offset, y_offset))
                x_offset += width
            elif char == '*':
                # blank cell
                crossword_image.paste(blank_cell, (x_offset, y_offset))
                x_offset += width
            else:
                # cell with letter, will add letter with imagefont and imagedraw
                crossword_image.paste(blank_cell, (x_offset, y_offset))
                x_offset += width

        # overlays the image with all the cells on top of the background image
        background_image.paste(crossword_image, (0, 0), crossword_image)
        # display text on image
        draw = ImageDraw.Draw(background_image)
        # font file, font size
        font = ImageFont.truetype("FRAMD.TTF", 100)
        # (x, y), "Text content", rgb, font
        draw.text((10, 10), "hello world", (0,0,0), font=font)
        background_image.save('crossword_image.png', 'PNG')

        file = discord.File("crossword_image.png")
        await ctx.channel.send(file=file)

    @commands.command()
    async def clues(self, ctx, arg):
        '''display clues, user specifies whether to get across to down clues'''

        output = ""
        # crossword data from api
        with open('xwordData.json', 'r') as f:
            xwordData = json.load(f)
        acrossClues = xwordData["clues"][arg.lower()]

        for clue in acrossClues:
            output += clue + '\n'
        emb = discord.Embed(description = output, colour = discord.Color(random.randint(0x000000, 0xFFFFFF)))
        await ctx.channel.send(embed = emb)

def setup(bot):
    bot.add_cog(Crossword(bot))

# TO DO:
# command for getting individual clues
# command for solving row or column of puzzle