import sys
import random
import FieldTypes
from PIL import Image, ImageDraw, ImageFont
sys.setrecursionlimit(2000)

class Minesweeper:
    def __init__(self, width, height, mines, ctx):
        self.gameOver=False
        self.minecount=mines
        self.width=width
        self.height=height
        self.userid=ctx.author.id
        self.win=False
        self.minefield=[[FieldTypes.Clear() for x in range(width)] for y in range(height)]
        while self.mines()<self.minecount:
            row, field = (random.randrange(0,self.height), random.randrange(0,self.width))
            if not bool(self.minefield[row][field]):
                self.minefield[row][field]=FieldTypes.Mine()
        for row in range(self.height):
                for column in range(self.width):
                    if not bool(self.minefield[row][column]):
                        self.minefield[row][column]=FieldTypes.Clear(self.minesNear(row, column))

    def mines(self):
        _mineCount=0
        for row in self.minefield:
            for field in row:
                if bool(field): _mineCount+=1
        return _mineCount
    
    def flagCount(self):
        nPlaced=0
        for row in range(self.height):
                for column in range(self.width):
                    if self.minefield[row][column].flagged:
                        nPlaced+=1
        return self.minecount-nPlaced

    def openField(self, field, row):
        if self.minefield[row][field].flagged or self.minefield[row][field].questionmarked:
            return
        if bool(self.minefield[row][field]):
            self.minefield[row][field].triggered=True
            for row in range(self.height):
                for column in range(self.width):
                    self.minefield[row][column].gameOver=True
            self.gameOver=True
        else:
            self.minefield[row][field].opened=True
            self.openFields(row, field)
    
    def questionMark(self, field, row):
        self.minefield[row][field].questionmark()

    def flagField(self, field, row):
        if self.flagCount()<=0:
            return
        self.minefield[row][field].flag()

    def forceOpen(self, field, row):
        if self.minefield[row][field].minecount == 0:
            return
        if self.markedNear(row, field)<self.minefield[row][field].minecount:
            return
        row_low = (row-1) if (row-1)>=0 else 0
        row_high = (row+2) if not (row+2)>self.height else (row+1)
        column_low = (field-1) if (field-1)>=0 else 0
        column_high = (field+2) if not (field+2)>self.width else (field+1)
        for r in range(row_low, row_high):
            for c in range(column_low, column_high):
                if not (self.minefield[r][c].flagged or self.minefield[r][c].questionmarked) and not self.minefield[r][c].opened:
                    if self.minefield[r][c].minecount == 0:
                        self.minefield[r][c].opened=True
                        self.openFields(r, c)
                    else:
                        self.minefield[r][c].opened=True

    def clearMarking(self, field, row):
        if self.minefield[row][field].flagged:
            self.minefield[row][field].flagged=False
        if self.minefield[row][field].questionmarked:
            self.minefield[row][field].questionmarked=False
        return

    def openFields(self, row, field):
        if self.minefield[row][field].minecount != 0:
            self.minefield[row][field].opened=True
            return
        row_low = (row-1) if (row-1)>=0 else 0
        row_high = (row+2) if not (row+2)>self.height else (row+1)
        column_low = (field-1) if (field-1)>=0 else 0
        column_high = (field+2) if not (field+2)>self.width else (field+1)
        for r in range(row_low, row_high):
            for c in range(column_low, column_high):
                if not bool(self.minefield[r][c]) and not self.minefield[r][c].opened:
                    if self.minefield[r][c].minecount == 0:
                        self.minefield[r][c].opened=True
                        self.openFields(r, c)
                    else:
                        self.minefield[r][c].opened=True

    def minesNear(self, row, field):
        row_low = (row-1) if (row-1)>=0 else 0
        row_high = (row+2) if not (row+2)>self.height else (row+1)
        column_low = (field-1) if (field-1)>=0 else 0
        column_high = (field+2) if not (field+2)>self.width else (field+1)
        _numMines=0
        for r in range(row_low, row_high):
            for c in range(column_low, column_high):
                if bool(self.minefield[r][c]): _numMines+=1
        return _numMines

    def markedNear(self, row, field):
        row_low = (row-1) if (row-1)>=0 else 0
        row_high = (row+2) if not (row+2)>self.height else (row+1)
        column_low = (field-1) if (field-1)>=0 else 0
        column_high = (field+2) if not (field+2)>self.width else (field+1)
        _numMarked=0
        for r in range(row_low, row_high):
            for c in range(column_low, column_high):
                if self.minefield[r][c].flagged or self.minefield[r][c].questionmarked: _numMarked+=1
        return _numMarked

    def checkWin(self):
        for r in range(self.height):
            for c in range(self.width):
                if type(self.minefield[r][c])==FieldTypes.Mine:
                    if self.minefield[r][c].triggered:
                        return False
        ok=True
        for r in range(self.height):
            for c in range(self.width):
                if not bool(self.minefield[r][c]):
                    if self.minefield[r][c].opened:
                        pass
                    else:
                        ok=False
        if ok:
            self.win=True
            return True
        ok=True
        for r in range(self.height):
            for c in range(self.width):
                if bool(self.minefield[r][c]):
                    if self.minefield[r][c].flagged:
                        pass
                    else:
                        ok=False
        if ok:
            self.win=True
        return ok

    def forfeit(self):
        for row in range(self.height):
            for column in range(self.width):
                self.minefield[row][column].gameOver=True
        self.gameOver=True

    def __str__(self):
        img=Image.new('RGB', (self.width*16+16, self.height*16+16), 0xC0C0C0)
        status=Image.open("sprites/win.png" if self.win else ("sprites/lose.png" if self.gameOver else "sprites/alive.png"))
        img.paste(status, (0, 0))
        for row in range(self.height):
            for column in range(self.width):
                img.paste(Image.open(str(self.minefield[row][column])), (16+column*16, row*16+16))
        d=ImageDraw.Draw(img)
        fnt = ImageFont.truetype('fonts/mine-sweeper.ttf', 10)
        fntlarge = ImageFont.truetype('fonts/mine-sweeper.ttf', 7)
        for i in range(19, self.width*16+19, 16):
            j=(i-19)//16
            d.text((i, 0), chr(j+97), font=fnt, fill=0x0)
        # d.text((19, 0), " ".join([chr(i+97) for i in range(self.width)]), font=fnt, fill=0x0)
        for i in range(16, self.height*16+16, 16):
            d.text( ((2 if int((i-16)/16)+1<10 else 1), (i+2 if int((i-16)/16)+1<10 else i+3)),
                    str(int((i-16)/16)+1),
                    font=(fnt if int((i-16)/16)+1<10 else fntlarge),
                    fill=0x0)
        img.save("{id}.png".format(id=self.userid))
        return "{id}.png".format(id=self.userid)

    def __repr__(self):
        return self.__str__()