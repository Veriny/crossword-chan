import discord
from discord.ext.commands import bot
from discord.ext import commands
import asyncio
import json
import requests
import random
from PIL import Image, ImageFont, ImageDraw
import wikipediaapi

print("Finished imports")

class Crossword(commands.Cog):
    '''nytimes crosswords + discord + japanese cartoon images = fun'''

    def __init__(self, bot):
        self.bot = bot
        self.backgroundImg = False

    async def displayCrossword(self):
        '''Constructs and saves an image of the current crossword state'''

        # background image, JAPANESE CARTOON IMAGES HERE
        # background_image = Image.open('bossiber.jpg')
        # crop to make the background image a square
        # background_image = background_image.crop((0, 0, 481, 481))
        # background_image = background_image.resize((1500, 1500))

        # transparent empty cell
        blank_cell = Image.open('trans_square.png')
        blank_cell = blank_cell.convert("RGBA")

        # black cell without letters
        black_cell = Image.open('black_square.png')
        black_cell = black_cell.convert("RGBA")

        # white empty cell
        white_cell = Image.open('white_square.png')
        white_cell = white_cell.convert("RGBA")

        width, height = blank_cell.size

        # load crossword info, later will be changed to current state
        # with open("xwordData.json") as f:
        with open("currentGrid.json") as f:
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

                if gridNums[i] != 0:
                    draw = ImageDraw.Draw(crossword_image)
                    font = ImageFont.truetype("FRAMD.TTF", 30)
                    draw.text((x_offset, y_offset), str(gridNums[i]), (0,0,0), font=font)

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

        # file = discord.File("crossword_image.png")
        # await ctx.channel.send(file=file)

    @commands.command()
    async def crossword(self, ctx):
        '''Displays the crossword'''
        await self.displayCrossword()
        file = discord.File("crossword_image.png")
        await ctx.channel.send(file=file)

    @commands.command()
    async def new(self, ctx, difficulty=None):
        '''Generates a random NYTimes Crossword and displays it as an unfilled crossword
        Optional parameter: difficulty (easy, medium, hard)'''

        # Gets data of a random nytimes crossword from the github repository: https://github.com/doshea/nyt_crosswords

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
                if difficulty == None:
                    dataRetrieved = True
                else:
                    difficulty = difficulty.lower()
                    # date of week, Monday (Easiest) -> Saturday (Hardest)
                    dow = xwordData["dow"]
                    if (difficulty == 'easy' and (dow == 'Monday' or dow == 'Tuesday')) or (difficulty == 'medium' and (dow == 'Wednesday' or dow == 'Thursday')) or (difficulty == 'hard' and (dow == 'Friday' or dow == 'Saturday')):
                        dataRetrieved = True

            except ValueError:
                # some gaps in api coverage
                print("Failed to get JSON data, making another request")

        # save crossword data as local json file
        with open('xwordData.json', 'w') as json_file:
            json.dump(xwordData, json_file)

        # create a list for the empty crossword
        blankGrid = xwordData["grid"]
        gridNums = xwordData["gridnums"]
        for i in range(0, len(blankGrid)):
            # replace all letters with "*" - represents a blank space
            if blankGrid[i].isalpha():
                blankGrid[i] = "*"
        emptyGrid = {"grid": blankGrid, "gridnums": gridNums}
        # save the empty grid, will be updated as people fill it in
        with open('currentGrid.json', 'w') as json_file:
            json.dump(emptyGrid, json_file)

        await self.displayCrossword()
        file = discord.File("crossword_image.png")
        await ctx.channel.send(file=file)

    @commands.command()
    async def cluelist(self, ctx, direction):
        '''Display all the clues in a certain direction
        Required parameter: direction (across, down)'''

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
    async def clue(self, ctx, direction, number):
        '''Gets a specific clue
        Required parameters: direction (across, down) and valid number (see crossword image)'''
        ans = ""
        found = False
        with open('xwordData.json', 'r') as f:
            data = json.load(f)
        clues = data["clues"][direction.lower()]
        number = number + "."
        for clue in clues:
            if clue.startswith(number):
                ans = clue
                found = True
        if found:
            await ctx.channel.send(ans)
        else:
            await ctx.channel.send("there's nothing like that which exists, you actual human garbage")

    @commands.command()
    async def solve(self, ctx, number, direction, guess):
        '''Fills in crossword if user guess matches the crossword solution
        Required parameters: number (see crossword), direction (across, down), guess (user guess)'''

        with open("xwordData.json") as f:
            xwordData = json.load(f)
            listChars = xwordData["grid"]
            gridNums = xwordData["gridnums"]

        with open("currentGrid.json") as f:
            currentGrid = json.load(f)
            currentStateChars = currentGrid["grid"]
            currentGridNums = currentGrid["gridnums"]

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
                # print(str(number) + ' down exists')
            # the number has an across word if it's in the first column or if the cell to the left is black
            charLeft = listChars[gridNums.index(number) - 1]
            if gridNums.index(number) % 15 == 0 or charLeft == '.':
                hasAcross = True
                # print(str(number) + ' across exists')

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
                await ctx.channel.send('Your guess is correct!')
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
                    data = {"grid": currentStateChars, "gridnums": currentGridNums}
                    json.dump(data, json_file)

                await self.displayCrossword()
                file = discord.File("crossword_image.png")
                await ctx.channel.send(file=file)

            else:
                if (len(actualWord.lower()) != len(guess)):
                    await ctx.channel.send('Your guess is the wrong length, you fucking idiot sandwich')
                else:
                    await ctx.channel.send('Your guess is incorrect')

    @commands.command()
    async def lookup(self, ctx, *args):
        '''Searches for a word/expression/person/event/whatever in wikipedia and returns the summary'''

        # ex user input +search harder daddy -> harder_daddy
        searchStr = ''
        for i in range(len(args)):
            searchStr += args[i] + '_'
        searchStr = searchStr[:-1]

        wiki = wikipediaapi.Wikipedia('en')
        page = wiki.page(searchStr)
        pageSummary = page.summary

        await ctx.channel.send(pageSummary)

def setup(bot):
    bot.add_cog(Crossword(bot))

# TO DO:
# add emotes to messages so users can easily choose a command, saves space
# instead of generating an image of the crossword every time maybe just update whatever changed
# anime background images