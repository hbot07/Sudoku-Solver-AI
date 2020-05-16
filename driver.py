import copy
import sys

input_board = sys.argv[1]


class Board:
    def __init__(self, board_config_string):
        rows = "ABCDEFGHI"
        columns = "123456789"
        self.board_config = {}
        i = 0
        for box in [a + b for a in rows for b in columns]:
            self.board_config[box] = board_config_string[i]
            i += 1 if i < 81 else 0
        self.boxes = []
        for row in "ABCDEFGHI":
            for column in "123456789":
                self.boxes.append(row + column)
                if self.board_config[row + column] == '0':
                    self.board_config[row + column] = columns

    def test_goal(self):
        for row in "ABCDEFGHI":
            for column in "123456789":
                if len(self.board_config[row + column]) != 1:
                    return False
        return True

    def to_string(self):
        board_config_string = ""
        for row in "ABCDEFGHI":
            for column in "123456789":
                board_config_string += self.board_config[row + column]
        return board_config_string

    @staticmethod
    def constraints(box_i, i, box_j, j):
        return i != j

    def prune(self, box, digit):
        self.board_config[box] = self.board_config[box].replace(digit, '')


def peers(a):
    def cross(A, B):
        return [a + b for a in A for b in B]

    boxes = cross("ABCDEFGHI", "123456789")
    row_units = [cross(r, "123456789") for r in "ABCDEFGHI"]
    col_units = [cross("ABCDEFGHI", c) for c in "123456789"]
    square_units = [cross(r, c) for r in ('ABC', 'DEF', 'GHI') for c in ('123', '456', '789')]
    unitlist = row_units + col_units + square_units
    units = dict((box, [u for u in unitlist if box in u]) for box in boxes)
    peers_dict = dict((b, set(sum(units[b], [])) - {b}) for b in boxes)
    return peers_dict[a]


def revise(csp, xi, xj):
    revised = False
    for x in csp.board_config[xi]:
        if all(not csp.constraints(xi, x, xj, y) for y in csp.board_config[xj]):
            csp.prune(xi, x)
            revised = True
    return revised


def AC3(csp):
    arc_queue = [(a, b) for a in [x + y for x in "ABCDEFGHI" for y in "123456789"] for b in peers(a)]
    while arc_queue:
        xi, xj = arc_queue.pop()
        if revise(csp, xi, xj):
            if not csp.board_config[xi]:
                return False
            for Xk in peers(xi):
                if Xk != xi:
                    arc_queue.append((Xk, xi))
    return True


sudoku = Board(input_board)
row_dict = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8}


def BTS(sudoku):
    if not AC3(sudoku):
        return False
    if sudoku.test_goal():
        return sudoku

    _, box = mrv(sudoku)

    for digit in sudoku.board_config[box]:
        new_sudoku = copy.deepcopy(sudoku)
        if forwardCheck(new_sudoku, box, digit):
            new_sudoku.board_config[box] = digit
            attempt = BTS(new_sudoku)
            if attempt:
                return attempt


def forwardCheck(sudoku, box, digit):
    for peer in peers(box):
        if len(sudoku.board_config[peer]) == 1 and digit == sudoku.board_config[peer]:
            return False
        else:
            sudoku.prune(peer, digit)
            if len(sudoku.board_config[peer]) == 0:
                return False
    return True


def mrv(Sudoku):
    n, s = min((len(Sudoku.board_config[b]), b) for b in Sudoku.boxes if len(Sudoku.board_config[b]) > 1)
    return n, s


if AC3(sudoku) and sudoku.test_goal():
    print(sudoku.to_string())
else:
    print(BTS(sudoku).to_string())
