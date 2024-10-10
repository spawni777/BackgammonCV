from ...utils.point_in_poly import point_in_poly

class Board:
    def __init__(self):
        self.bbox = []
        self.points = []
        self.dices = []
        self.disks = []  # Initialize self.disks

    def reset(self):
        self.clear()
        for point in self.points:
            point.reset()

    def clear(self):
        for point in self.points:
            point.clear()
        self.dices.clear()
        self.disks.clear()  # Clear the disks list

    def addPoint(self, point):
        self.points.append(point)

    def addDice(self, dice):
        # Check if the detected dice is on the board
        if point_in_poly(dice.center, self.bbox):
            self.dices.append(dice)

    def addDisk(self, disk):
        self.disks.append(disk)  # Add the disk to the disks list
        # Determine correct point to add
        for point in self.points:
            if point_in_poly(disk.center, point.bbox_warped):
                point.addDisk(disk)

    def getBar(self):
        return self.points[-1]  # Get the last point, assuming it's the bar

    def __str__(self):
        res = "dices: "
        for dice in self.dices:
            res += str(dice) + " "
        res += "\n"
        for point in self.points:
            res += str(point) + "\n"
        return res

    def copy(self):
        board = Board()
        board.bbox = self.bbox.copy()
        for point in self.points:
            newPoint = point.copy()
            board.addPoint(newPoint)
        board.dices = self.dices.copy()
        board.disks = self.disks.copy()  # Copy the disks list
        return board
