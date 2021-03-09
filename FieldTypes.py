class Clear:
    gameOver=False
    opened=False
    def __bool__(self):
        return False
    def __repr__(self):
        return "sprites/clear.png" if self.opened else "sprites/hidden.png"

class Mine:
    gameOver=False
    opened=False
    triggered=False
    def __bool__(self):
        return True
    def __str__(self):
        return ("sprites/mine_hit.png" if self.triggered else "sprites/mine_location.png") if self.gameOver else "sprites/hidden.png"
    def __repr__(self):
        return ("sprites/mine_hit.png" if self.triggered else "sprites/mine_location.png") if self.gameOver else "sprites/hidden.png"

class One:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/one.png"
    def __repr__(self):
        return "sprites/one.png"

class Two:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/two.png"
    def __repr__(self):
        return "sprites/two.png"

class Three:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/three.png"
    def __repr__(self):
        return "sprites/three.png"

class Four:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/four.png"
    def __repr__(self):
        return "sprites/four.png"

class Five:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/five.png"
    def __repr__(self):
        return "sprites/five.png"

class Six:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/six.png"
    def __repr__(self):
        return "sprites/six.png"

class Seven:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/seven.png"
    def __repr__(self):
        return "sprites/seven.png"

class Eight:
    gameOver=False
    opened=True
    def __bool__(self):
        return False
    def __str__(self):
        return "sprites/eight.png"
    def __repr__(self):
        return "sprites/eight.png"

class Flag:
    gameOver=False
    opened=False
    def __init__(self, mine=True):
        self.mine=mine
    def __bool__(self):
        return self.mine
    def __str__(self):
        return "sprites/flag.png" if not self.gameOver else("sprites/flag.png" if self.mine else "sprites/mine_wrong.png")
    def __repr__(self):
        return "sprites/flag.png" if not self.gameOver else("sprites/flag.png" if self.mine else "sprites/mine_wrong.png")

class Question:
    gameOver=False
    opened=False
    def __init__(self, mine=False):
        self.mine=mine
    def __bool__(self):
        return self.mine
    def __str__(self):
        return "sprites/questionmark.png" if not self.gameOver else ("sprites/mine_location.png" if self.mine else "sprites/questionmark2.png")
    def __repr__(self):
        return "sprites/questionmark.png" if not self.gameOver else ("sprites/mine_location.png" if self.mine else "sprites/questionmark2.png")

numbers={
    0: Clear,
    1: One,
    2: Two,
    3: Three,
    4: Four,
    5: Five,
    6: Six,
    7: Seven,
    8: Eight
}

numbersReverse={
    One: 1,
    Two: 2,
    Three: 3,
    Four: 4,
    Five: 5,
    Six: 6,
    Seven: 7,
    Eight: 8
}

def fieldReverse(fieldType):
    return numbersReverse[fieldType]

def field(num):
    return numbers[num]