import json
import random
import discord
import settings
import FieldTypes
import time
import TopGG
from Minesweeper import Minesweeper
from discord.ext import commands
if settings.usePostgres:
    from db_interface import backup, restore
    restore()
    
intents = discord.Intents(messages=True, guilds=True, members=True)
client = commands.Bot(command_prefix = 'ms!', intents=intents, case_insensitive=True, help_command=None)
minesweeperChannel={}
games={}
ownerdm=None



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name='minesweeper | ms!help'))
    global ownerdm
    ownerdm = client.get_user(settings.ownerId)
    try:
        global minesweeperChannel
        with open('minesweeperChannel.json') as json_file:
            minesweeperChannel = json.load(json_file)
        await ownerdm.send('minesweeperChannel.json loaded')
    except:
        await ownerdm.send('minesweeperChannel.json not found')
    try:
        print("Setting up TopGG cog")
        TopGG.setup(client=client)
    except:
        print("Error setting up TopGG cog")
    print("Done")


@client.command(brief='Help command')
async def help(ctx, *, command=None):
    embed=discord.Embed(colour=0xF04747,
                        title="SweeperBot Help",
                        description="[FIELD] example: A1, E5, J10, f7, g3\n `|` between commands displays multiple ways of typing it",
                        url="https://wikibot.tech/SweeperBot")
    embed.add_field(name="ms!start|game `width` `height` `mine count`", value="Starts a minesweeper game, if values left blank initializes a game with all values set to 10", inline=True)
    embed.add_field(name="ms!addChannel|channel|setChannel `#channel`", value="Enables minesweeper in `#channel`, disabled by default", inline=True)
    embed.add_field(name="ms!removeChannel|disableChannel `#channel`", value="Disables minesweeper in `#channel`", inline=True)
    embed.add_field(name="[FIELD]", value="Opens [FIELD] if you have an ongoing game and the tile is closed", inline=True)
    embed.add_field(name="![FIELD] | [FIELD]!", value="Flags [FIELD], you are unable to open it by mistake, use .[FIELD] | [FIELD]. to unflag it", inline=True)
    embed.add_field(name=".[FIELD] | [FIELD].", value="Unmark [FIELD] from question mark or flag", inline=True)
    embed.add_field(name="?[FIELD] | [FIELD]?", value="Mark [FIELD] as question mark, you are unable to open it by mistake, but it doesen't use flag counter", inline=True)
    embed.add_field(name="@[FIELD] | [FIELD]@", value="If the field is a number and number of marked(flagged or question-marked) tiles surrounding it matches or exceeds it's value, it will open all other tiles surrounding it", inline=True)
    embed.add_field(name="Multiple Commands", value="You can send multiple commands simultaneously, example: `F5! F6@ H7! I7 A1. !E4 @E6 D3 .D7`", inline=True)
    embed.set_footer(text="Invite bot: https://wikibot.tech/SweeperBot")
    await ctx.send(embed=embed)


@client.command(aliases=['start', 'game'], brief='Minesweeper duh')
async def _start(ctx, width=10, height=10, mines=10):
    if "minesweeper" in ctx.channel.name or str(ctx.channel.id) in minesweeperChannel.get(str(ctx.guild.id), []):
        pass
    else:
        await ctx.send("Minesweeper is not enabled in this channel, use `ms!addChannel #channel` to enable minesweeper for `#channel`")
    if mines>width*height:
        await ctx.send("Too many mines for a minefield of this size!")
        return
    if width>25:
        await ctx.send("Width limit exceeded(max 25)")
        return
    if height>50:
        await ctx.send("Height limit exceeded(max 50)")
        return
    minefield=Minesweeper(width, height, mines, ctx)
    embed=discord.Embed(title="Minesweeper")
    filename=str(minefield)
    embed.set_image(url="attachment://{filename}".format(filename=filename))
    file=discord.File("{filename}".format(filename=filename))
    games[str(ctx.author.id)]={ "gameObject": minefield,
                                "message": await ctx.send(file=file, embed=embed),
                                "timeStart": time.time()
    }

@client.command(aliases=['addchannel', 'channel', 'setchannel'], brief='Set minesweeper channel')
async def _addChannel(ctx, *, channel):
    if str(ctx.guild.id) in minesweeperChannel:
        minesweeperChannel[str(ctx.guild.id)].append(str(ctx.message.channel_mentions[0].id))
    else:
        minesweeperChannel[str(ctx.guild.id)]=[str(ctx.message.channel_mentions[0].id)]
    await ctx.send("Minesweeper is now enabled in `{Channel}`".format(Channel=ctx.message.channel_mentions[0].name))
    with open('minesweeperChannel.json', 'w') as json_file:
        json.dump(minesweeperChannel, json_file) 

@client.command(aliases=['removechannel', 'disablechannel'], brief='Set minesweeper channel')
async def _removeChannel(ctx, *, channel):
    if str(ctx.guild.id) in minesweeperChannel:
        minesweeperChannel[str(ctx.guild.id)].remove(str(ctx.message.channel_mentions[0].id))
    await ctx.send("Minesweeper is now disabled in `{Channel}`".format(Channel=ctx.message.channel_mentions[0].name))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)
    if "minesweeper" in message.channel.name or str(message.channel.id) in minesweeperChannel.get(str(message.guild.id), []):
        pass
    else:
        return
    numbers=False
    for letter in message.content:
        if 57>=ord(letter)>=48:
            numbers=True
        if numbers:
            break
    if not numbers:
        return
    for msg in message.content.split():
        if len(msg)>4:
            return
    if games[str(message.author.id)]["gameObject"].gameOver:
        await message.channel.send("Game over lol, use ms!start to make a new game")
        return
    specialOperation={
        "!": games[str(message.author.id)]["gameObject"].flagField,
        "?": games[str(message.author.id)]["gameObject"].questionMark,
        ".": games[str(message.author.id)]["gameObject"].clearMarking,
        "@": games[str(message.author.id)]["gameObject"].forceOpen
    }
    for msg in message.content.split():
        start=0
        end=len(msg)
        specialIndex=None
        specialOp=None
        for key in specialOperation:
            if msg[0]==key:
                specialIndex=0
                start=1
                specialOp=specialOperation[key]
                break
            if msg[-1]==key:
                specialIndex=-1
                end-=1
                specialOp=specialOperation[key]
                break
        width=ord(msg.lower()[start])-97
        if width<0:
            await message.channel.send("Invalid format")
            return
        height=int(msg.lower()[start+1:end])-1
        if specialIndex != None:
            specialOp(width, height)
        else:
            games[str(message.author.id)]["gameObject"].openField(width, height)
    if not games[str(message.author.id)]["gameObject"].gameOver:
        if games[str(message.author.id)]["gameObject"].checkWin():
            embed=discord.Embed(title="You won LOL",
                                description="Game duration: {time}s".format(time=time.time()-games[str(message.author.id)]["timeStart"]))
            filename=str(games[str(message.author.id)]["gameObject"])
            embed.set_image(url="attachment://{filename}".format(filename=filename))
            games[str(message.author.id)]["gameObject"].gameOver=True
            file=discord.File("{filename}".format(filename=filename))
            await message.channel.send(file=file, embed=embed)
            return
    else:
        embed=discord.Embed(title="You lost LOL",
                            description="Game duration: {time}s".format(time=time.time()-games[str(message.author.id)]["timeStart"]))
        filename=str(games[str(message.author.id)]["gameObject"])
        embed.set_image(url="attachment://{filename}".format(filename=filename))
        file=discord.File("{filename}".format(filename=filename))
        await message.channel.send(file=file, embed=embed)
        return
    embed=discord.Embed(title="Minesweeper",
                        description="Flags left: {nFlags}".format(nFlags=games[str(message.author.id)]["gameObject"].flagsLeft))
    filename=str(games[str(message.author.id)]["gameObject"])
    embed.set_image(url="attachment://{filename}".format(filename=filename))
    file=discord.File("{filename}".format(filename=filename))
    await message.delete()
    previousMessage=games[str(message.author.id)]["message"]
    games[str(message.author.id)]["message"]=await message.channel.send(file=file, embed=embed)
    await previousMessage.delete()

client.run(settings.discordBotToken)