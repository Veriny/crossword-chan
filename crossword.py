import discord
from discord.ext.commands import bot
from discord.ext import commands
import asyncio
import json
import requests
import random
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
# print(blank_cell.size)

# black square = cell with no letters
black_cell = Image.open('black_square.png')
black_cell = black_cell.convert("RGBA")
# print(black_cell.size)

white_cell = Image.open('white_square.png')
white_cell = white_cell.convert("RGBA")
white_cell = white_cell.resize((100,100))
print(white_cell.size)
white_cell.save('white_square.png', "PNG")

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

        # display_command = self.bot.get_command("displayCrossword")
        # await ctx.channel.invoke(display_command)

    @commands.command()
    async def displayCrossword(self, ctx):
        '''makes an image of the current crossword state and sends it in a discord embed'''

        # load crossword info, later will be changed to current state
        with open("xwordData.json") as f:
            xwordData = json.load(f)
            listChars = xwordData["grid"]
            gridNums = xwordData["gridnums"]

        # Image of the entire crossword will be a 15x15 grid of squares
        crossword_image = Image.new('RGBA', (15 * width, 15 * height))
        x_offset = 0
        y_offset = 0
        column = 0

        for i in range(len(listChars)):
            char = listChars[i]
            # new row after every 15 cells
            if column % 15 == 0 and column != 0:
                # moves down a row and resets x offset to the very left
                y_offset += height
                x_offset = 0
            column += 1

            if char == '.':
                # black cell, move x offset to the right for next cell
                crossword_image.paste(black_cell, (x_offset, y_offset))
                x_offset += width
            elif char == '*':
                # blank cell
                # crossword_image.paste(blank_cell, (x_offset, y_offset))
                crossword_image.paste(white_cell, (x_offset, y_offset))
                x_offset += width
            else:
                # cell contains letter, add letter to cell with imagefont and imagedraw
                # crossword_image.paste(blank_cell, (x_offset, y_offset))
                crossword_image.paste(white_cell, (x_offset, y_offset))
                # display text on image
                draw = ImageDraw.Draw(crossword_image)
                # font file, font size
                font = ImageFont.truetype("FRAMD.TTF", 80)
                # (x, y), "Text content", rgb, font
                draw.text((x_offset, y_offset), " " + char, (0,0,0), font=font)

                if gridNums[i] != 0:
                    font = ImageFont.truetype("FRAMD.TTF", 30)
                    draw.text((x_offset, y_offset), str(gridNums[i]), (0,0,0), font=font)

                x_offset += width

        # overlays the image with all the cells on top of the background image
        # background_image.paste(crossword_image, (0, 0), crossword_image)
        # background_image.save('crossword_image.png', 'PNG')
        crossword_image.save('crossword_image.png', 'PNG')

        file = discord.File("crossword_image.png")
        await ctx.channel.send(file=file)

    @commands.command()
    async def clues(self, ctx, direction):
        '''display clues, user specifies whether to get across to down clues'''

        output = ""
        # crossword data from api
        with open('xwordData.json', 'r') as f:
            xwordData = json.load(f)
        directionClues = xwordData["clues"][direction.lower()]

        for clue in directionClues:
            output += clue + '\n'
        emb = discord.Embed(description = output, colour = discord.Color(random.randint(0x000000, 0xFFFFFF)))
        await ctx.channel.send(embed = emb)
    
    @commands.command()
    async def solve(self, ctx, number, direction, guess):
        '''fills in crossword if user guess matches the crossword solution'''

        with open("xwordData.json") as f:
            xwordData = json.load(f)
            listChars = xwordData["grid"]
            gridNums = xwordData["gridnums"]

        with open("currentGrid.json") as f:
            currentGrid = json.load(f)
            currentStateChars = currentGrid["grid"]

        hasAcross = False
        hasDown = False
        number = int(number)
        direction = direction.lower()
        guess = guess.upper()

        # check if the number direction combination is valid
        if number in gridNums and number != 0:
            charAbove = listChars[gridNums.index(number) - 15]
            # the number has a down word if it's in the first row or if the cell above it is black
            if gridNums.index(number) < 15 or charAbove == '.':
                hasDown = True
                print(str(number) + ' down exists')
            # the number has an across word if it's in the first column or if the cell to the left is black
            charLeft = listChars[gridNums.index(number) - 1]
            if gridNums.index(number) % 15 == 0 or charLeft == '.':
                hasAcross = True
                print(str(number) + ' across exists')

        # get the word and compare it to the guess, if the guess is correct update the current state of the crossword
        if (direction == 'across' and hasAcross == True) or (direction == 'down' and hasDown == True):
            actualWord = ''
            if direction == 'across':
                # keep adding letters to actualWord until you run into a black cell or the next row
                currentCellNum = gridNums.index(number)
                currentCellChar = listChars[currentCellNum]
                # while (current cell is not black) or (not in first column and not the start of the word)
                while (currentCellChar != '.') or (currentCellNum % 15 == 0 and currentCellNum != gridNums.index(number)):
                    # print(currentCellChar)
                    actualWord += currentCellChar
                    currentCellNum += 1
                    currentCellChar = listChars[currentCellNum]

            if direction == 'down':
                # keep adding letters to actualWord until you run into a black cell or the next row
                currentCellNum = gridNums.index(number)
                currentCellChar = listChars[currentCellNum]
                # while (current cell is not black) or (not in first row and not the start of the word)
                while (currentCellChar != '.') or (currentCellNum < 15 and currentCellNum != gridNums.index(number)):
                    # print(currentCellChar)
                    actualWord += currentCellChar
                    # move down a row
                    currentCellNum += 15
                    currentCellChar = listChars[currentCellNum]

            # print(actualWord)
            # print(guess)
            
            # guess is correct, update current state of the crossword
            if (actualWord == guess):
                await ctx.channel.send('you guessed correctly')
                # update current state of the crossword
                gridIndex = gridNums.index(number)
                if direction == 'across':
                    for char in actualWord:
                        currentStateChars[gridIndex] = char
                        gridIndex += 1
                if direction == 'down':
                    for char in actualWord:
                        currentStateChars[gridIndex] = char
                        gridIndex += 15

                with open('currentGrid.json', 'w') as json_file:
                    data = {"grid": currentStateChars}
                    json.dump(data, json_file)

            else:
                if (len(actualWord.lower()) != len(guess)):
                    await ctx.channel.send('Your guess is the wrong length')
                else:
                    await ctx.channel.send('Your guess is incorrect')

def setup(bot):
    bot.add_cog(Crossword(bot))

# TO DO:
# command for getting individual clues
# implement a difficulty feature to get easy, medium, hard crosswords by using DoW info
# add emotes to messages so users can easily choose a command, saves space
# define command to get definition of an obscure word
# instead of generating an image of the crossword every time maybe just update whatever changed