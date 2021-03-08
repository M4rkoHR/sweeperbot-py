import json
import random
import discord
import settings
import FieldTypes
import time
from Minesweeper import Minesweeper
from discord.ext import commands
if settings.usePostgres:
    from db_interface import backup, restore
    restore()
intents = discord.Intents(messages=True, guilds=True, members=True)
client = commands.Bot(command_prefix = 'ms!', intents=intents, case_insensitive=True)
minesweeperChannel={}
games={}
ownerdm=None

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global ownerdm
    ownerdm = client.get_user(settings.ownerId)
    try:
        global minesweeperChannel
        with open('minesweeperChannel.json') as json_file:
            minesweeperChannel = json.load(json_file)
        await ownerdm.send('minesweeperChannel.json loaded')
    except:
        await ownerdm.send('minesweeperChannel.json not found')
    print("Done")


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
    games[str(ctx.author.id)]={ "gameObject": minefield }
    file=discord.File("{filename}".format(filename=filename))
    await ctx.send(file=file, embed=embed)

@client.command(aliases=['addchannel', 'channel', 'setchannel'], brief='Set minesweeper channel')
async def _addChannel(ctx, *, channel):
    if str(ctx.guild.id) in minesweeperChannel:
        minesweeperChannel[str(ctx.guild.id)].append(str(ctx.message.channel_mentions[0].id))
    else:
        minesweeperChannel[str(ctx.guild.id)]=[str(ctx.message.channel_mentions[0].id)]
    await ctx.send("Minesweeper is now enabled in `{Channel}`".format(Channel=ctx.message.channel_mentions[0].name))

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
    for msg in message.content.split():
        if len(msg)>4:
            return
    if games[str(message.author.id)]["gameObject"].gameOver:
        await message.channel.send("Game over lol, use ms!start to make a new game")
        return
    for msg in message.content.split():
        start=0
        end=len(msg)
        specialIndex=None
        if "?" in msg or "!" in msg or "." in msg:
            if ("?" in msg and "!" in msg) or ("?" in msg and "." in msg) or ("!" in msg and "." in msg):
                continue
            if msg[0]=="?":
                specialIndex=0
                start=1
            if msg[0]=="!":
                specialIndex=0
                start=1
            if msg[0]==".":
                specialIndex=0
                start=1
            if msg[-1]=="?":
                specialIndex=-1
                end-=1
            if msg[-1]=="!":
                specialIndex=-1
                end-=1
            if msg[-1]==".":
                specialIndex=-1
                end-=1
        width=ord(msg.lower()[start])-97
        if width<0:
            await message.channel.send("Invalid format")
        height=int(msg.lower()[start+1:end])-1
        if specialIndex != None:
            if "?" in msg:
                games[str(message.author.id)]["gameObject"].questionMark(width, height)
            if "!" in msg:
                games[str(message.author.id)]["gameObject"].flagField(width, height)
            if "." in msg:
                games[str(message.author.id)]["gameObject"].clearMarking(width, height)
        else:
            games[str(message.author.id)]["gameObject"].openField(width, height)
    if not games[str(message.author.id)]["gameObject"].gameOver:
        if games[str(message.author.id)]["gameObject"].checkWin():
            embed=discord.Embed(title="You won LOL")
            filename=str(games[str(message.author.id)]["gameObject"])
            embed.set_image(url="attachment://{filename}".format(filename=filename))
            games[str(message.author.id)]["gameObject"].gameOver=True
            file=discord.File("{filename}".format(filename=filename))
            await message.channel.send(file=file, embed=embed)
            return
    else:
        embed=discord.Embed(title="You lost LOL")
        filename=str(games[str(message.author.id)]["gameObject"])
        embed.set_image(url="attachment://{filename}".format(filename=filename))
        file=discord.File("{filename}".format(filename=filename))
        await message.channel.send(file=file, embed=embed)
        return
    embed=discord.Embed(title="Minesweeper")
    filename=str(games[str(message.author.id)]["gameObject"])
    embed.set_image(url="attachment://{filename}".format(filename=filename))
    file=discord.File("{filename}".format(filename=filename))
    await message.channel.send(file=file, embed=embed)

client.run(settings.discordBotToken)