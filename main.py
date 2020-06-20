import pygame


white = (255, 255, 255)
black = (0, 0, 0)

WIN_WIDTH = 800
WIN_HEIGHT = 800
FPS = 60

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()


w = pygame.image.load('media/w.png')
b = pygame.image.load('media/b.png')
wob = pygame.image.load('media/wob.png')
bob = pygame.image.load('media/bob.png')
wow = pygame.image.load('media/wow.png')
bow = pygame.image.load('media/bow.png')

bu1 = pygame.image.load('media/button1.png')
bu2 = pygame.image.load('media/button2.png')
bu3 = pygame.image.load('media/button3.png')
bu4 = pygame.image.load('media/button4.png')

sound = pygame.mixer.Sound('media/knock.wav')


screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Corners")
icon = pygame.image.load('media/checker-board.png')
pygame.display.set_icon(icon)


class Tile(pygame.sprite.Sprite):
    def __init__(self, clr, x, y):
        super().__init__()

        self.clr = clr
        self.column = x
        self.row = y
        self.image = pygame.Surface((100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = 100 * (x-1)
        self.rect.y = 700-(100 * (y-1))

        if self.row in range(1, 4) and self.column in range(5, 9):
            self.piece = 1
        elif self.row in range(6, 9) and self.column in range(1, 5):
            self.piece = -1
        else:
            self.piece = 0

        self.draw()

    def draw(self):
        if self.clr == 1:
            if self.piece == 0:
                self.image = w
            elif self.piece == 1:
                self.image = wow
            elif self.piece == -1:
                self.image = bow

        elif self.clr == -1:
            if self.piece == 0:
                self.image = b
            elif self.piece == 1:
                self.image = wob
            elif self.piece == -1:
                self.image = bob

        screen.blit(self.image, (self.rect.x, self.rect.y))


class Game:
    def __init__(self):
        self.tile_list = pygame.sprite.Group()

        cl = 1
        for row in range(8):
            cl *= -1
            for column in range(8):
                tile = Tile(cl, column + 1, row + 1)
                cl *= -1
                self.tile_list.add(tile)
        self.tile_list.draw(screen)

        self.running = True
        self.team = 1
        self.turn = 1

        self.move = []
        self.base = None
        self.visited = []
        print('Turn # 1 by player white')
        self.game_loop()

    def next_turn(self):
        self.base = None
        self.visited = []
        self.move = []
        self.turn += 1
        self.team *= -1
        print('Turn #', self.turn, 'by player', end=' ')
        if self.team == 1:
            print('white')
        else:
            print('black')

    def run_demo(self):
        pair = [None, None]
        with open('logs/demo.txt') as log:
            for line in log.readlines()[1:]:
                if len(line) == 6:
                    x1 = ord(line[0]) - 96
                    y1 = int(line[1])
                    x2 = ord(line[3]) - 96
                    y2 = int(line[4])
                    while pair[0] is None or pair[1] is None:
                        for tile in self.tile_list:
                            if tile.column == x1 and tile.row == y1:
                                pair[0] = tile
                            elif tile.column == x2 and tile.row == y2:
                                pair[1] = tile
                    self.swap(pair[0], pair[1])
                    pair = [None, None]
                else:
                    self.turn += 1
                    self.team *= -1

                self.tile_list.update()
                pygame.display.update()
                pygame.time.wait(500)

    def win(self):
        black_stack = 0
        white_stack = 0

        for elem in self.tile_list:
            for row1 in range(6, 9):
                for column1 in range(1, 5):
                    if elem.row == row1 and elem.column == column1:
                        if elem.piece == 1:
                            white_stack += 1
                        elif self.turn >= 80 and elem.piece == -1:
                            print('White won')
                            return True

            for row2 in range(1, 4):
                for column2 in range(5, 9):
                    if elem.row == row2 and elem.column == column2:
                        if elem.piece == -1:
                            black_stack += 1
                        elif self.turn >= 79 and elem.piece == 1:
                            print('Black won')
                            return True

        if white_stack == 12:
            print('White won')
            return True

        elif black_stack == 12:
            print('Black won')
            return True

        return False

    def legal(self, pos1, pos2):
        if pos1.piece != self.team:
            return False
        if self.base is not None and pos1 != self.base:
            return False
        if pos2 in self.visited:
            return False
        if pos2.piece != 0:
            return False
        if pos1.column != pos2.column and pos1.row != pos2.row:
            return False

        if abs(pos1.row - pos2.row) > 2 or abs(pos1.column - pos2.column) > 2:
            return False

        if abs(pos1.row - pos2.row) == 2 and pos1.column == pos2.column:
            for middle in self.tile_list:
                if middle.row == min(pos1.row, pos2.row) + 1 and middle.column == pos1.column:
                    if middle.piece != 0:
                        return True
            return False

        if abs(pos1.column - pos2.column) == 2 and pos1.row == pos2.row:
            for middle in self.tile_list:
                if middle.column == min(pos1.column, pos2.column) + 1 and middle.row == pos1.row:
                    if middle.piece != 0:
                        return True
            return False

        if self.base is None:
            return True
        else:
            return False

    def swap(self, pos1, pos2):
        pos1.piece, pos2.piece = pos2.piece, pos1.piece
        pos1.draw()
        pos2.draw()
        sound.play()
        print(chr(96+pos1.column)+str(pos1.row)+' '+chr(96+pos2.column)+str(pos2.row))

    def game_loop(self):
        while self.running:
            pygame.time.delay(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.base is not None:
                    self.next_turn()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.turn == 1:
                    self.run_demo()
                    self.running = not self.win()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for i in self.tile_list:
                        if i.rect.collidepoint(pos):
                            self.move.append(i)
                            if len(self.move) == 2:
                                if self.legal(self.move[0], self.move[1]):
                                    self.swap(self.move[0], self.move[1])
                                    self.running = not self.win()
                                    self.base = self.move[1]
                                    self.visited.append(self.move[0])
                                    self.move = [self.base]
                                else:
                                    if self.base is None:
                                        self.move.remove(self.move[0])
                                    else:
                                        self.move.remove(self.move[1])
            self.tile_list.update()
            pygame.display.update()

Game()