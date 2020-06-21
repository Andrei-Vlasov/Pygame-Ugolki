import pygame
import datetime

white = (255, 255, 255)
black = (0, 0, 0)
grey = (127, 127, 127)

WIN_WIDTH = 1200
WIN_HEIGHT = 800
FPS = 60

pygame.init()
pygame.mixer.init()
# MEDIA
# tiles
w = pygame.image.load('media/w.png')
b = pygame.image.load('media/b.png')
wob = pygame.image.load('media/wob.png')
bob = pygame.image.load('media/bob.png')
wow = pygame.image.load('media/wow.png')
bow = pygame.image.load('media/bow.png')

sound = pygame.mixer.Sound('media/knock.wav')
font = pygame.font.Font('consola.ttf', 30)
small_font = pygame.font.Font('consola.ttf', 15)
big_font = pygame.font.Font('consola.ttf', 50)
rules = 'media/rules_rus.txt'
about = 'media/about.txt'


screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
screen.fill(grey)
pygame.display.set_caption("Corners")
icon = pygame.image.load('media/checker-board.png')
pygame.display.set_icon(icon)


# 1 = white, -1 = black
class Tile(pygame.sprite.Sprite):
    def __init__(self, clr, x, y):  # initialises with piece
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

    def draw(self):  # png pictures
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


class Button(pygame.sprite.Sprite):
    global screen_width, screen_height, screen

    def __init__(self, x, y, width, height, text_color, background_color, text, time=None):
        super().__init__()

        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.background_color = background_color
        self.time = time

    @staticmethod
    def drawTextcenter(text, font, screen, x, y, color):
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect(center=(int(x), int(y)))
        screen.blit(textobj, textrect)

    def draw(self):
        pygame.draw.rect(screen, self.background_color, (self.rect), 0)
        self.drawTextcenter(self.text, font, screen, self.x + self.width / 2, self.y + self.height / 2, self.text_color)
        pygame.draw.rect(screen, self.text_color, self.rect, 3)

    def clicked(self, pos, time):
        if self.rect.collidepoint(pos):
            if self.time is None:
                self.time = pygame.time.get_ticks()
                return True
            elif time - self.time > 1000:
                self.time = time
                return True
        return False


class Game:
    def __init__(self):
        self.tile_list = pygame.sprite.Group()
        self.menu = pygame.sprite.Group()

        cl = 1
        for row in range(8):
            cl *= -1
            for column in range(8):
                tile = Tile(cl, column + 1, row + 1)
                cl *= -1
                self.tile_list.add(tile)
        self.tile_list.draw(screen)

        b1 = Button(850, 200, 300, 50, black, white, 'New Game')
        b2 = Button(850, 275, 300, 50, black, white, 'Rules')
        b3 = Button(850, 350, 300, 50, black, white, 'Demo')
        b4 = Button(850, 425, 300, 50, black, white, 'About')

        for btn in [b1, b2, b3, b4]:
            btn.draw()
            self.menu.add(btn)

        self.running = True
        self.team = 1
        self.turn = 1

        self.move = []  # from ... to ...
        self.base = None  # second move must start with same piece
        self.visited = []  # no walking in circles
        print('Turn # 1 by player white')

        self._start_time = pygame.time.get_ticks()  # for timer widget
        self.game_loop()

    def reset_board(self):
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
        self._start_time = pygame.time.get_ticks()

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

    def run_demo(self):  # play out scripted game
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
                    self.team *= 1
                    self.turn += 1

                self.tile_list.update()
                pygame.display.update()
                pygame.time.wait(500)

    def win(self):  # check if game is over
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
                            self.congratulate('White')
                            return True

            for row2 in range(1, 4):
                for column2 in range(5, 9):
                    if elem.row == row2 and elem.column == column2:
                        if elem.piece == -1:
                            black_stack += 1
                        elif self.turn >= 79 and elem.piece == 1:
                            print('Black won')
                            self.congratulate('Black')
                            return True

        if white_stack == 12:
            print('White won')
            self.congratulate('White')
            return True

        elif black_stack == 12:
            print('Black won')
            self.congratulate('Black')
            return True

        return False

    def legal(self, pos1, pos2):  # check if the move is legal
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
        print(chr(96+pos1.column)+str(pos1.row)+' '+chr(96+pos2.column)+str(pos2.row))  # logging

    def auto_ender(self):  # if you HAVE to end your move, this function does it for you. else press space
        for distant in self.tile_list:
            if (distant.column == self.base.column and abs(distant.row - self.base.row) == 2 or
            distant.row == self.base.row and abs(distant.column - self.base.column) == 2) and distant.piece == 0 and\
            distant not in self.visited and distant != self.base:
                for neighbour in self.tile_list:
                    if neighbour.row == (self.base.row + distant.row)/2\
                    and neighbour.column == (self.base.column + distant.column)/2 and neighbour.piece != 0:
                        return False
        return True

    def game_loop(self):  # controls and logic
        while True:
            pygame.time.delay(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.tile_list.draw(screen)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.base is not None:
                    self.next_turn()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    frame = pygame.time.get_ticks()
                    for i in self.tile_list:
                        if i.rect.collidepoint(pos):
                            if self.running:
                                self.move.append(i)
                                if len(self.move) == 2:
                                    if self.legal(self.move[0], self.move[1]):
                                        self.swap(self.move[0], self.move[1])
                                        self.running = not self.win()
                                        self.base = self.move[1]
                                        self.visited.append(self.move[0])
                                        self.move = [self.base]
                                        if self.auto_ender() is True and self.running:
                                            self.next_turn()
                                    else:
                                        if self.base is None:
                                            self.move.remove(self.move[0])
                                        else:
                                            self.move.remove(self.move[1])
                        else:
                            for i in self.menu:
                                if i.clicked(pos, frame):
                                    if i.text == 'New Game':
                                        self.reset_board()
                                        print('New Game')
                                    elif i.text == 'Demo':
                                        print('Demo')
                                        self.reset_board()
                                        self.run_demo()
                                        self.running = not self.win()
                                    elif i.text == 'Rules':
                                        self.print_doc(rules)
                                    elif i.text == 'About':
                                        self.print_doc(about)
            self.tile_list.update()
            pygame.display.update()
            self.widget()

    def widget(self):
        first = 'Time: ' + str(datetime.timedelta(seconds=(pygame.time.get_ticks() - self._start_time) / 1000))[:7]
        second = 'Player: ' + {1: 'White', -1: 'Black'}[self.team]
        third = 'Turn: ' + str(self.turn)

        widget_surface = pygame.Surface((0, 0))
        widget_surface.fill(grey)
        i = 0
        for el in [first, second, third]:
            widget = font.render(el, True, white, grey)
            widgetRect = widget.get_rect()
            widgetRect.center = (1000, 50*(1+i))
            screen.blit(widget, widgetRect)
            i += 1

    @staticmethod
    def print_doc(doc):
        background = pygame.Surface((800, 1200))
        background.fill(grey)
        screen.blit(background, (0, 0))
        i = 0
        with open(doc) as rules:
            for line in rules.readlines():
                sentence = small_font.render(line.rstrip(), True, white, grey)
                sentenceRect = sentence.get_rect()
                sentenceRect.center = (400, 25 * (1 + i))
                i += 1
                screen.blit(sentence, sentenceRect)

    @staticmethod
    def congratulate(clr):
        background = pygame.Surface((800, 1200))
        background.fill(grey)
        screen.blit(background, (0, 0))
        sentence = big_font.render(clr + ' Wins!', True, white, grey)
        sentenceRect = sentence.get_rect()
        sentenceRect.center = (400, 400)
        screen.blit(sentence, sentenceRect)


Game()
