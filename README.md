# [SweeperBot](https://top.gg/bot/817765850915274763)
Discord Minesweeper bot, invite [here](https://top.gg/bot/817765850915274763/invite/)


# Instructions

[FIELD] example: `A1`, `E5`, `J10`, `f7`, `g3`

`|` between commands displays multiple ways of typing it

Minesweeper is automatically enabled in channels that contain `minesweeper` in the name

![Minesweeper](https://cdn.discordapp.com/attachments/795406810844495944/819693160988278814/unknown.png)

# Playing


## ms!start | game `width` `height` `mine count`

Starts a minesweeper game, if values left blank initializes a game with all values set to 10


## [FIELD]

Opens [FIELD] if you have an ongoing game and the tile is closed


## ![FIELD] | [FIELD]!

Flags [FIELD], you are unable to open it by mistake, use .[FIELD] | [FIELD]. to unflag it


## ?[FIELD] | [FIELD]?

Mark [FIELD] as question mark, you are unable to open it by mistake, but it doesen't use flag counter


## @[FIELD] | [FIELD]@

(Equivalent to shift-clicking a numbered field in minesweeper)

If the field is a number and number of marked(flagged or question-marked) tiles surrounding it matches or exceeds it's value, it will open all other tiles surrounding it


## .[FIELD] | [FIELD].

Unmark [FIELD] from question mark or flag


## Multiple Commands

You can send multiple commands simultaneously, example: `F5! F6@ H7! I7 A1. !E4 @E6 D3 .D7`


# Help commands


## ms!help

Everything listed here.


## ms!addChannel | channel | setChannel `#channel`

Enables minesweeper in #channel, disabled by default


## ms!removeChannel | disableChannel `#channel`

Disables minesweeper in `#channel`


# Deploying
Enter your API key and user ID in settings.py and run bot.py
