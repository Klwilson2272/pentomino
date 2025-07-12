
from pentomino import PentominoSolver

class PentominoDateSolver( PentominoSolver):

    def __init__(self, mon, day, dow, pentominos=None, grid: list[list[str]] = None):
        if day < 1 or day > 31:
            raise ValueError("Value error invalid day")

        if dow.upper() not in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
            raise ValueError("Value error invalid day")
        self.mon = mon.upper()
        self.day = str(day)
        self.dow = dow.upper()

        self.dategrid = [
            ["JAN", "FEB", "MAR", "APR", "1", "2", "3", "MON", "TUE",],
            ["MAY", "4", "5", "6", "7", "8", "9", "Wed", "", ],
            ["JUN", "10", "11", "12", "13", "31", "15", "THU", "", ],
            ["JUL", "16", "17", "18", "19", "20", "21", "FRI", "SAT", ],
            ["AUG", "22", "23", "24", "25", "26", "27", "", "SUN", ],
            ["SEP", "OCT", "NOV", "DEC", "28", "29", "30", "14", "X", ],
        ]

        self.exclusions = [(5,8)]
        for r in range(len(self.dategrid)):
            for c in range(len(self.dategrid[r])):
                if (self.dategrid[r][c] == self.mon
                        or self.dategrid[r][c] == self.dow
                        or self.dategrid[r][c] == self.day):
                    print(f"excluding {r},{c} cell {self.dategrid[r][c]}")
                    self.exclusions.append((r,c))


        self.width = len(self.dategrid[0])
        self.height = len(self.dategrid)

        letters = ['I', 'T', 'V', 'Y', 'Z', 'U', 'N', 'P', 'L', 'F']
        if grid:
            for row in grid:
                for letter in row:
                    if letter in letters:
                        letters.remove(letter)

        super().__init__(self.width, self.height, letters, self.exclusions, grid)
