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
mp_games={}
ownerdm=None



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name='minesweeper | ms!help'))
    global ownerdm
    ownerdm = await client.fetch_user(settings.ownerId)
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
    embed.add_field(name="ms!start|restart `width` `height` `mine count`", value="Starts|Restarts a minesweeper game, if values left blank initializes a game with default values (10 width, 10 height, 10% mines)", inline=True)
    embed.add_field(name="ms!addChannel|channel|setChannel `#channel`", value="Enables minesweeper in `#channel`, disabled by default", inline=True)
    embed.add_field(name="ms!removeChannel|disableChannel `#channel`", value="Disables minesweeper in `#channel`", inline=True)
    embed.add_field(name="ms!game|show|showgame", value="Shows your ongoing game, if it exists.", inline=False)
    embed.add_field(name="[FIELD]", value="Opens [FIELD] if you have an ongoing game and the tile is closed", inline=True)
    embed.add_field(name="![FIELD] | [FIELD]!", value="Flags [FIELD], you are unable to open it by mistake, use .[FIELD] | [FIELD]. to unflag it", inline=True)
    embed.add_field(name=".[FIELD] | [FIELD].", value="Unmark [FIELD] from question mark or flag", inline=True)
    embed.add_field(name="?[FIELD] | [FIELD]?", value="Mark [FIELD] as question mark, you are unable to open it by mistake, but it doesen't use flag counter", inline=True)
    embed.add_field(name="@[FIELD] | [FIELD]@", value="If the field is a number and number of marked(flagged or question-marked) tiles surrounding it matches or exceeds it's value, it will open all other tiles surrounding it", inline=True)
    embed.add_field(name="Multiple Commands", value="You can send multiple commands simultaneously, example: `F5! F6@ H7! I7 A1. !E4 @E6 D3 .D7`", inline=True)
    embed.set_footer(text="Invite bot: https://wikibot.tech/SweeperBot")
    await ctx.send(embed=embed)


@client.command(brief='Vote for bot')
async def vote(ctx):
    embed=discord.Embed(colour=0xc21e56,
                        title="Vote for SweeperBot",
                        url="https://top.gg/bot/817765850915274763/vote")
    await ctx.send(embed=embed)


@client.command(brief='Invite bot')
async def invite(ctx):
    embed=discord.Embed(colour=0xc21e56,
                        title="Invite SweeperBot",
                        url="https://top.gg/bot/817765850915274763/invite")
    await ctx.send(embed=embed)


@client.command(aliases=['start', 'restart'], brief='Start a minesweeper game')
async def _start(ctx, width=10, height=10, mines=None):
    if mines==None:
        mines=(width*height)//10
    if "minesweeper" in ctx.channel.name or str(ctx.channel.id) in minesweeperChannel.get(str(ctx.guild.id), []):
        pass
    else:
        await ctx.send("Minesweeper is not enabled in this channel, use `ms!addChannel #channel` to enable minesweeper for `#channel`")
        return
    if mines>width*height:
        await ctx.send("Too many mines for a minefield of this size!")
        return
    if width>26:
        await ctx.send("Width limit exceeded(max 26)")
        return
    if height>50:
        await ctx.send("Height limit exceeded(max 50)")
        return
    minefield=Minesweeper(width, height, mines, ctx)
    embed=discord.Embed(title="Minesweeper",
                        description="Flags left: {nFlags}".format(nFlags=mines))
    filename=str(minefield)
    embed.set_image(url="attachment://{filename}".format(filename=filename))
    embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    file=discord.File("{filename}".format(filename=filename))
    games[str(ctx.author.id)]={ "gameObject": minefield,
                                "message": await ctx.send(file=file, embed=embed),
                                "timeStart": time.time()
    }


@client.command(aliases=['end', 'finish'], brief='Start a minesweeper game')
async def _end(ctx):
    if games.get(str(ctx.user.id), False):
            if games[str(ctx.user.id)]["gameObject"].gameOver or (time.time()-games[str(ctx.user.id)]["timeStart"]):
                games[str(ctx.author.id)]["gameObject"].forfeit()
                embed=discord.Embed(title="<:dead:839610784741195818> You forfeited! <:dead:839610784741195818>",
                            description="Game duration: {time}s".format(time=time.time()-games[str(ctx.author.id)]["timeStart"]))
                filename=str(games[str(ctx.author.id)]["gameObject"])
                embed.set_image(url="attachment://{filename}".format(filename=filename))
                embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                file=discord.File("{filename}".format(filename=filename))
                await ctx.channel.send(file=file, embed=embed)
                return
    else:
        await ctx.send("You don't have an ongoing game")

@client.command(aliases=['leave', 'abandon'], brief='Start a minesweeper game')
async def _leave(ctx):
    ingame=False
    for game in mp_games:
        if str(ctx.author.id) in game:
            ingame=True
            break
    if not ingame:
        await ctx.send("You aren't a member of an ongoing multiplayer game")
        return
    newgame=list(game)
    newgame.remove(str(ctx.author.id))
    newindex=0
    newgame=tuple(newgame)
    mp_games[newgame]=mp_games.pop(game)
    mp_games[newgame]["playercount"]-=1
    mp_games[newgame]["nextPlayer"]=newindex
    
        

@client.command(aliases=['multiplayer', 'multi'], brief='Start a minesweeper game')
async def _multiplayer(ctx, width=10, height=10, mines=None):
    if mines==None:
        mines=(width*height)//10
    if "minesweeper" in ctx.channel.name or str(ctx.channel.id) in minesweeperChannel.get(str(ctx.guild.id), []):
        pass
    else:
        await ctx.send("Minesweeper is not enabled in this channel, use `ms!addChannel #channel` to enable minesweeper for `#channel`")
        return
    if mines>width*height:
        await ctx.send("Too many mines for a minefield of this size!")
        return
    if width>26:
        await ctx.send("Width limit exceeded(max 26)")
        return
    if height>50:
        await ctx.send("Height limit exceeded(max 50)")
        return
    if not ctx.message.mentions:
        await ctx.send("You haven't mentioned anyone to play with")
        return
    playercount=len(ctx.message.mentions)+1
    players=[str(ctx.author.id)]
    for usr in ctx.message.mentions:
        for game in mp_games:
            if str(usr.id) in game and not mp_games[game]["gameObject"].gameOver:
                await ctx.send("User has not yet finished their multiplayer game, use ms!leave to leave")
                return
        if games.get(str(usr.id), False):
            if games[str(usr.id)]["gameObject"].gameOver or (time.time()-games[str(usr.id)]["timeStart"])>3600:
                await ctx.send("User has not yet finished their game, use ms!end to finish your game")
                return
        players.append(str(usr.id))
    players=tuple(players)
    minefield=Minesweeper(width, height, mines, ctx)
    embed=discord.Embed(title="Minesweeper",
                        description="Flags left: {nFlags}".format(nFlags=mines))
    filename=str(minefield)
    embed.set_image(url="attachment://{filename}".format(filename=filename))
    embed.set_footer(text="{user}'s turn".format(user=ctx.author.display_name), icon_url=ctx.author.avatar_url)
    file=discord.File("{filename}".format(filename=filename))
    mp_games[players]={"gameObject": minefield,
                    "message": await ctx.send(file=file, embed=embed),
                    "timeStart": time.time(),
                    "playercount": playercount,
                    "nextPlayer": 0
    }

@client.command(aliases=['addchannel', 'channel', 'setchannel'], brief='Set minesweeper channel')
async def _addChannel(ctx, *, channel):
    if ctx.message.author.id == settings.ownerId or ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator:
        pass
    else:
        await ctx.send("You don't have the permission!")
        return
    if str(ctx.guild.id) in minesweeperChannel:
        minesweeperChannel[str(ctx.guild.id)].append(str(ctx.message.channel_mentions[0].id))
    else:
        minesweeperChannel[str(ctx.guild.id)]=[str(ctx.message.channel_mentions[0].id)]
    await ctx.send("Minesweeper is now enabled in `{Channel}`".format(Channel=ctx.message.channel_mentions[0].name))
    with open('minesweeperChannel.json', 'w') as json_file:
        json.dump(minesweeperChannel, json_file) 

@client.command(aliases=['removechannel', 'disablechannel'], brief='Set minesweeper channel')
async def _removeChannel(ctx, *, channel):
    if ctx.message.author.id == settings.ownerId or ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator:
        pass
    else:
        await ctx.send("You don't have the permission!")
        return
    if str(ctx.guild.id) in minesweeperChannel:
        minesweeperChannel[str(ctx.guild.id)].remove(str(ctx.message.channel_mentions[0].id))
    await ctx.send("Minesweeper is now disabled in `{Channel}`".format(Channel=ctx.message.channel_mentions[0].name))

@client.command(aliases=['showgame', 'game', 'show'], brief='See your game')
async def _showGame(ctx):
    try:
        if games[str(ctx.author.id)]["gameObject"].gameOver:
            await ctx.channel.send("Game over, use ms!start to make a new game")
            return
    except:
        await ctx.channel.send("Use ms!start to make a new game")
    embed=discord.Embed(title="Minesweeper",
                        description="Flags left: {nFlags}".format(nFlags=games[str(ctx.author.id)]["gameObject"].flagCount()))
    filename=str(games[str(ctx.author.id)]["gameObject"])
    embed.set_image(url="attachment://{filename}".format(filename=filename))
    embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    file=discord.File("{filename}".format(filename=filename))
    previousMessage=games[str(ctx.author.id)]["message"]
    games[str(ctx.author.id)]["message"]=await ctx.channel.send(file=file, embed=embed)
    await previousMessage.delete()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)
    if "minesweeper" in message.channel.name or str(message.channel.id) in minesweeperChannel.get(str(message.guild.id), []):
        pass
    else:
        return
    gameInstance=None
    mp=False
    ingame=False
    game=None
    for game in mp_games:
        if str(message.author.id) in game and not mp_games[game].gameOver:
            gameInstance=mp_games[game]
            mp=True
            ingame=True
            if str(message.author.id)!=game[gameInstance["nextPlayer"]]:
                await message.channel.send("It's not your turn!")
                return
            break
    if not ingame:
        gameInstance=games[str(message.author.id)]
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
    if gameInstance["gameObject"].gameOver:
        await message.channel.send("Game over, use ms!start to make a new game")
        return
    specialOperation={
        "!": gameInstance["gameObject"].flagField,
        "?": gameInstance["gameObject"].questionMark,
        ".": gameInstance["gameObject"].clearMarking,
        "@": gameInstance["gameObject"].forceOpen
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
            gameInstance["gameObject"].openField(width, height)
    if not gameInstance["gameObject"].gameOver:
        if gameInstance["gameObject"].checkWin():
            embed=discord.Embed(title="<:win:839610773155217439> You won! <:win:839610773155217439>",
                                description="Game duration: {time}s".format(time=time.time()-gameInstance["timeStart"]))
            filename=str(gameInstance["gameObject"])
            embed.set_image(url="attachment://{filename}".format(filename=filename))
            if mp:
                embed.set_footer(text=" ".join(client.get_user(int(userid)).display_name for userid in game))
            else:
                embed.set_footer(text=message.author.display_name, icon_url=message.author.avatar_url)
            gameInstance["gameObject"].gameOver=True
            file=discord.File("{filename}".format(filename=filename))
            await message.channel.send(file=file, embed=embed)
            return
    else:
        embed=discord.Embed(title="<:dead:839610784741195818> You lost! <:dead:839610784741195818>",
                            description="Game duration: {time}s".format(time=time.time()-gameInstance["timeStart"]))
        filename=str(gameInstance["gameObject"])
        embed.set_image(url="attachment://{filename}".format(filename=filename))
        if mp:
            embed.set_footer(text=" ".join((str(client.get_user(int(userid))) for userid in game)))
        else:
            embed.set_footer(text=message.author.display_name, icon_url=message.author.avatar_url)
        file=discord.File("{filename}".format(filename=filename))
        await message.channel.send(file=file, embed=embed)
        return
    embed=discord.Embed(title="Minesweeper",
                        description="Flags left: {nFlags}".format(nFlags=gameInstance["gameObject"].flagCount()))
    filename=str(gameInstance["gameObject"])
    embed.set_image(url="attachment://{filename}".format(filename=filename))
    if mp:
        gameInstance["nextPlayer"]=(gameInstance["nextPlayer"]+1)%gameInstance["playercount"]
        embed.set_footer(text="{user}'s turn".format(user=client.get_user(int(game[gameInstance["nextPlayer"]])).display_name))
    else:
        embed.set_footer(text=message.author.display_name, icon_url=message.author.avatar_url)
    file=discord.File("{filename}".format(filename=filename))
    await message.delete()
    previousMessage=gameInstance["message"]
    gameInstance["message"]=await message.channel.send(file=file, embed=embed)
    await previousMessage.delete()

client.run(settings.discordBotToken)