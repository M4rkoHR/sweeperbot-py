import FieldTypes
import random
from PIL import Image, ImageDraw, ImageFont


class Minesweeper:
    def __init__(self, width, height, mines, ctx):
        self.gameOver=False
        self.minecount=mines
        self.flagsLeft=mines
        self.width=width
        self.height=height
        self.userid=ctx.author.id
        self.minefield=[[FieldTypes.Clear() for x in range(width)] for y in range(height)]
        while self.mines()<self.minecount:
            row, field = (random.randrange(0,self.height), random.randrange(0,self.width))
            if not bool(self.minefield[row][field]):
                self.minefield[row][field]=FieldTypes.Mine()

    def mines(self):
        _mineCount=0
        for row in self.minefield:
            for field in row:
                if bool(field): _mineCount+=1
        return _mineCount

    def openField(self, field, row):
        if type(self.minefield[row][field]) in [FieldTypes.Question, FieldTypes.Flag]:
            return
        if bool(self.minefield[row][field]):
            self.minefield[row][field]=FieldTypes.Mine()
            self.minefield[row][field].triggered=True
            for row in range(self.height):
                for column in range(self.width):
                    self.minefield[row][column].gameOver=True
            self.gameOver=True
        else:
            self.minefield[row][field]=FieldTypes.field(self.minesNear(row, field))()
            self.openFields(row, field)
    
    def questionMark(self, field, row):
        if not self.minefield[row][field].opened:
            self.minefield[row][field]=FieldTypes.Question(bool(self.minefield[row][field]))

    def flagField(self, field, row):
        if not self.minefield[row][field].opened and self.flagsLeft>0:
            self.minefield[row][field]=FieldTypes.Flag(bool(self.minefield[row][field]))
            self.flagsLeft-=1

    def forceOpen(self, field, row):
        if type(self.minefield[row][field]) not in FieldTypes.numbersReverse:
            return
        if self.markedNear(row, field)<FieldTypes.fieldReverse(type(self.minefield[row][field])):
            return
        row_low = (row-1) if (row-1)>=0 else 0
        row_high = (row+2) if not (row+2)>self.height else (row+1)
        column_low = (field-1) if (field-1)>=0 else 0
        column_high = (field+2) if not (field+2)>self.width else (field+1)
        for r in range(row_low, row_high):
            for c in range(column_low, column_high):
                if not type(self.minefield[r][c]) in [FieldTypes.Flag, FieldTypes.Question] and not self.minefield[r][c].opened:
                    if self.minesNear(r, c) == 0:
                        self.minefield[r][c].opened=True
                        self.openFields(r, c)
                    else:
                        self.minefield[r][c]=FieldTypes.field(self.minesNear(r, c))()

    def clearMarking(self, field, row):
        if type(self.minefield[row][field]) in [FieldTypes.Question, FieldTypes.Flag]:
            if type(self.minefield[row][field])==FieldTypes.Flag:
                self.flagsLeft+=1
            if bool(self.minefield[row][field]):
                self.minefield[row][field]=FieldTypes.Mine()
            else:
                self.minefield[row][field]=FieldTypes.Clear()
        return

    def openFields(self, row, field):
        row_low = (row-1) if (row-1)>=0 else 0
        row_high = (row+2) if not (row+2)>self.height else (row+1)
        column_low = (field-1) if (field-1)>=0 else 0
        column_high = (field+2) if not (field+2)>self.width else (field+1)
        for r in range(row_low, row_high):
            for c in range(column_low, column_high):
                if not bool(self.minefield[r][c]) and not self.minefield[r][c].opened:
                    if self.minesNear(r, c) == 0:
                        self.minefield[r][c].opened=True
                        self.openFields(r, c)
                    else:
                        self.minefield[r][c]=FieldTypes.field(self.minesNear(r, c))()

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
                if type(self.minefield[r][c]) in [FieldTypes.Flag, FieldTypes.Question]: _numMarked+=1
        return _numMarked

    def checkWin(self):
        ok=True
        for r in range(self.height):
            for c in range(self.width):
                if not bool(self.minefield[r][c]):
                    if self.minefield[r][c].opened:
                        pass
                    else:
                        ok=False
        if ok:
            return True
        ok=True
        for r in range(self.height):
            for c in range(self.width):
                if bool(self.minefield[r][c]):
                    if type(self.minefield[r][c])==FieldTypes.Flag:
                        pass
                    else:
                        ok=False
        return ok


    def __str__(self):
        img=Image.new('RGB', (self.width*16+24, self.height*16+16), 0xC0C0C0)
        for row in range(self.height):
            for column in range(self.width):
                img.paste(Image.open(str(self.minefield[row][column])), (24+column*16, row*16+16))
        d=ImageDraw.Draw(img)
        fnt = ImageFont.truetype('fonts/mine-sweeper.ttf', 10)
        d.text((27, 0), " ".join([chr(i+97) for i in range(self.width)]), font=fnt, fill=0x0)
        for i in range(16, self.height*16+16, 16):
            d.text((2, i+2), str(int((i-16)/16)+1),font=fnt, fill=0x0)
        img.save("{id}.png".format(id=self.userid))
        return "{id}.png".format(id=self.userid)

    def __repr__(self):
        img=Image.new('RGB', (self.width*16+24, self.height*16+16), 0xC0C0C0)
        for row in range(self.height):
            for column in range(self.width):
                img.paste(Image.open(str(self.minefield[row][column])), (24+column*16, row*16+16))
        d=ImageDraw.Draw(img)
        fnt = ImageFont.truetype('fonts/mine-sweeper.ttf', 10)
        d.text((27, 0), " ".join([chr(i+97) for i in range(self.width)]), font=fnt, fill=0x0)
        for i in range(16, self.height*16+16, 16):
            d.text((2, i+2), str(int((i-16)/16)+1),font=fnt, fill=0x0)
        img.save("{id}.png".format(id=self.userid))
        return "{id}.png".format(id=self.userid)
