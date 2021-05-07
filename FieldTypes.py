class Clear:
    gameOver=False
    opened=False
    flagged=False
    questionmarked=False
    def __init__(self, minecount=0):
        self.minecount=minecount
    def flag(self):
        if not self.opened:
            self.flagged=True
    def questionmark(self):
        if not self.opened:
            self.questionmarked=True
    def __bool__(self):
        return False
    def __str__(self):
        if self.flagged:
            return "sprites/flag.png" if not self.gameOver else "sprites/mine_wrong.png"
        if self.questionmarked:
            return "sprites/questionmark.png" if not self.gameOver else "sprites/questionmark2.png"
        return sprites[self.minecount] if self.opened else "sprites/hidden.png"
    def __repr__(self):
        return self.__str__()

class Mine:
    gameOver=False
    opened=False
    triggered=False
    flagged=False
    questionmarked=False
    def flag(self):
        if not self.opened:
            self.flagged=True
    def questionmark(self):
        if not self.opened:
            self.questionmarked=True
    def __bool__(self):
        return True
    def __str__(self):
        if self.flagged:
            return "sprites/flag.png"
        if self.questionmarked:
            return "sprites/questionmark.png" if not self.gameOver else "sprites/mine_location.png"
        return ("sprites/mine_hit.png" if self.triggered else "sprites/mine_location.png") if self.gameOver else "sprites/hidden.png"
    def __repr__(self):
        return self.__str__()

sprites={
    0: "sprites/clear.png",
    1: "sprites/one.png",
    2: "sprites/two.png",
    3: "sprites/three.png",
    4: "sprites/four.png",
    5: "sprites/five.png",
    6: "sprites/six.png",
    7: "sprites/seven.png",
    8: "sprites/eight.png",
}