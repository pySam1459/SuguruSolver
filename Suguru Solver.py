import pygame
import pickle
from re import fullmatch
from time import sleep
from random import randint
pygame.init()

w, h = 8, 7
CELL_SIZE = 75
FRAMEWIDTH, FRAMEHEIGHT = w * CELL_SIZE, h * CELL_SIZE
screen = pygame.display.set_mode((FRAMEWIDTH, FRAMEHEIGHT))
pygame.display.set_caption("Suguru Solver")

AROUND = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]


class Cell:
    id = 1

    def __init__(self, i, j):
        self.i, self.j = i, j
        self.n = 0
        self.pos = []
        self.group = None
        self.on = 0

    def reset(self):
        self.n = 0
        self.on = 0
        self.group = None
        self.pos = []

    def render(self, solving):
        if (self.i + self.j) % 2 == 0 and not solving:
            pygame.draw.rect(screen, [127, 127, 127], self.getRect(), 1)

        if self.n == 0:
            for i in range(1, 10):
                if i in self.pos:
                    x = self.i * CELL_SIZE + ((i-1) % 3) * CELL_SIZE/3 + CELL_SIZE/6
                    y = self.j * CELL_SIZE + ((i-1) //3) * CELL_SIZE/3 + CELL_SIZE/6
                    text(i, [x, y], int(CELL_SIZE/5), [10, 10, 10])

        else:
            if self.on == 0:
                col = [255, 225, 0]
            else:
                col = [10, 10, 10]

            text(self.n, [self.i*CELL_SIZE + CELL_SIZE/2, self.j*CELL_SIZE + CELL_SIZE/2], int(CELL_SIZE/2), col)

    def getRect(self):
        return [self.i*CELL_SIZE, self.j*CELL_SIZE, CELL_SIZE, CELL_SIZE]

    def createPos(self):
        if self.n == 0:
            self.pos = [i for i in range(1, self.group.length()+1)]


class EmptyCell:
    id = 2
    def __init__(self, i, j):
        self.i, self.j = i, j


class Group:
    def __init__(self, arr):
        self.arr = arr
        self.cells = [arr[0][0]]

        self.col = [randint(0, 255), randint(0, 255), randint(0, 255)]

    def render(self):
        for j, row in enumerate(self.arr):
            for i, c in enumerate(row):
                if c.id == 1:
                    screen.fill(self.col, c.getRect())

                    if i == 0 or self.arr[j][i-1].id == 2:
                        pygame.draw.line(screen, [0, 0, 0], [c.i*CELL_SIZE, c.j*CELL_SIZE], [c.i*CELL_SIZE, (c.j+1)*CELL_SIZE], 4)

                    if i == len(self.arr[0])-1 or self.arr[j][i+1].id == 2:
                        pygame.draw.line(screen, [0, 0, 0], [(c.i+1) * CELL_SIZE, c.j * CELL_SIZE], [(c.i+1) * CELL_SIZE, (c.j + 1) * CELL_SIZE], 4)


                    if j == 0 or self.arr[j-1][i].id == 2:
                        pygame.draw.line(screen, [0, 0, 0], [c.i * CELL_SIZE, c.j * CELL_SIZE], [(c.i+1) * CELL_SIZE, c.j * CELL_SIZE], 4)

                    if j == len(self.arr) - 1 or self.arr[j+1][i].id == 2:
                        pygame.draw.line(screen, [0, 0, 0], [c.i * CELL_SIZE, (c.j+1) * CELL_SIZE], [(c.i + 1) * CELL_SIZE, (c.j + 1) * CELL_SIZE], 4)


    def contains(self, cell):
        return cell in self.cells

    def length(self):
        return len(self.cells)

    def getN(self):
        N = []
        for cell in self.cells:
            if cell.n != 0:
                N.append(cell.n)

        return N

    def add(self, cell):
        if cell.i < self.arr[0][0].i:
            for row in self.arr:
                row.insert(0, EmptyCell(row[0].i-1, row[0].j))
            i = 0

        elif cell.i > self.arr[0][-1].i:
            for row in self.arr:
                row.append(EmptyCell(row[-1].i+1, row[0].j))
            i = -1

        else:
            i = cell.i - self.arr[0][0].i

        if cell.j < self.arr[0][0].j:
            self.arr.insert(0, [EmptyCell(self.arr[0][i].i, self.arr[0][0].j-1) for i in range(len(self.arr[0]))])
            j = 0

        elif cell.j > self.arr[-1][0].j:
            self.arr.append([EmptyCell(self.arr[0][i].i, self.arr[-1][0].j+1) for i in range(len(self.arr[0]))])
            j = -1

        else:
            j = cell.j - self.arr[0][0].j

        self.arr[j][i] = cell
        self.cells.append(cell)


class Board:
    auto = True

    def __init__(self, width, height):
        self.w, self.h = width, height

        self.array = [[Cell(i, j) for i in range(width)] for j in range(height)]
        self.groups = []

        self.selCell = None
        self.selGroup = None
        self.prev = pygame.mouse.get_pressed()
        self.holding = False

        self.solving = False

    def tick(self):
        self.createGroup()

        self.render()

    def createGroup(self):
        mouse = pygame.mouse.get_pressed()
        if mouse[0] and not self.prev[0]:
            i, j = getIJ()
            self.selCell = self.array[j][i]
            self.holding = True

            self.selGroup = self.selCell.group
            if self.selGroup is None:
                self.selGroup = Group([[self.selCell]])
                self.groups.append(self.selGroup)
                self.selCell.group = self.selGroup

        elif mouse[0] and self.prev[0] and self.holding:
            i, j = getIJ()
            if self.array[j][i] != self.selCell and self.array[j][i].group is None:
                self.selGroup.add(self.array[j][i])
                self.selCell = self.array[j][i]
                self.selCell.group = self.selGroup


        self.prev = mouse

    def render(self):
        for g in self.groups:
            g.render()

        for row in self.array:
            for cell in row:
                cell.render(self.solving)


    def solve(self):
        for row in self.array:
            for cell in row:
                cell.createPos()

        self.solving = True
        solved = False
        rot = False
        while not solved:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        rot = False

            if not rot:
                for row in self.array:
                    for cell in row:
                        if len(cell.pos) == 1 and cell.n == 0:
                            cell.n = cell.pos[0]

                con = True
                for row in self.array:
                    for cell in row:
                        if cell.n == 0:
                            for n in cell.group.getN():
                                if n in cell.pos:
                                    cell.pos.remove(n)
                                    con = False

                if con:
                    for j, row in enumerate(self.array):
                        for i, cell in enumerate(row):
                            if cell.n == 0:
                                for di, dj in AROUND:
                                    ni, nj = i + di, j + dj

                                    if 0 <= ni < w and 0 <= nj < h:
                                        if self.array[nj][ni].n != 0 and self.array[nj][ni].n in cell.pos:
                                            cell.pos.remove(self.array[nj][ni].n)
                                            con = False

                if con:
                    for g in self.groups:
                        com = {}
                        for cell in g.cells:
                            if cell.n == 0:
                                for n in cell.pos:
                                    if n in com:
                                        com[n].append(cell)
                                    else:
                                        com[n] = [cell]

                        for n, cs in com.items():
                            if len(cs) == 1:
                                cs[0].n = n
                                con = True


                if con:
                    for n in self.getNs():
                        for g in self.groups:
                            com = {}
                            count = 0
                            for cell in g.cells:
                                if cell.n == 0:
                                    if n in cell.pos:
                                        count += 1
                                        for di, dj in AROUND:
                                            ni, nj = cell.i + di, cell.j + dj

                                            if 0 <= ni < w and 0 <= nj < h:
                                                if self.array[nj][ni] not in g.cells:
                                                    if self.array[nj][ni] in com:
                                                        com[self.array[nj][ni]] += 1
                                                    else:
                                                        com[self.array[nj][ni]] = 1

                            for cell, val in com.items():
                                if val == count and n in cell.pos:
                                    cell.pos.remove(n)
                                    con = False

                if con:
                    for g in self.groups:
                        for i, cell in enumerate(g.cells):
                            com = []
                            if cell.n == 0:
                                for c2 in g.cells[i+1:]:
                                    if c2.pos == cell.pos:
                                        com.append(c2)

                            if len(com) == len(cell.pos)-1:
                                for c2 in g.cells:
                                    if c2.pos != cell.pos:
                                        for n in cell.pos:
                                            if n in c2.pos:
                                                c2.pos.remove(n)
                                                #con = False


                solved = True
                for row in self.array:
                    for cell in row:
                        if cell.n == 0:
                            solved = False

                if not self.auto:
                    rot = True

            self.render()
            pygame.display.update()
            sleep(0.05)

    def getNs(self):
        N = []
        for g in self.groups:
            for cell in g.cells:
                if cell.n == 0:
                    for n in cell.pos:
                        if n not in N:
                            N.append(n)

        return N


def text(n, pos, size, col):
    font = pygame.font.SysFont("comicsansms", size)
    surf = font.render(str(n), True, col)
    rect = surf.get_rect()
    rect.center = pos
    screen.blit(surf, rect)


def getIJ():
    pos = pygame.mouse.get_pos()
    return int(pos[0] // CELL_SIZE), int(pos[1] // CELL_SIZE)


def main():
    global w, h, screen
    board = Board(w, h)

    while True:
        screen.fill([255, 255, 255])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if fullmatch(r"[0-9]", event.unicode):
                    i, j = getIJ()

                    board.array[j][i].n = int(event.unicode)
                    board.array[j][i].on = int(event.unicode)

                if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                    board.solving = not board.solving

                    if event.key == pygame.K_RETURN:
                        board.solve()

                if event.key == pygame.K_DELETE:
                    i, j = getIJ()
                    cell = board.array[j][i]
                    board.groups.remove(cell.group)
                    group = cell.group

                    for cell in group.cells:
                        cell.reset()

                    del group

                if event.key == pygame.K_s:
                    fn = input('Filename >> ')
                    if fn:
                        with open(f"saves/{fn}.pkl", "wb") as file:
                            pickle.dump(board, file)

                if event.key == pygame.K_l:
                    fn = input('Filename >> ')
                    if fn:
                        with open(f"saves/{fn}.pkl", "rb") as file:
                            board = pickle.load(file)
                            w, h = board.w, board.h
                            screen = pygame.display.set_mode((CELL_SIZE * w, CELL_SIZE * h))


        board.tick()

        pygame.display.update()


if __name__ == '__main__':
    main()
