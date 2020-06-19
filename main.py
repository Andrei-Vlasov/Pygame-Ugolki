import pygame

white = (255, 255, 255)
black = (0, 0, 0)

WIN_WIDTH = 800
WIN_HEIGHT = 800
FPS = 60

pygame.init()
pygame.mixer.init()

w = pygame.image.load('media/w.png')
b = pygame.image.load('media/b.png')
wob = pygame.image.load('media/wob.png')
bob = pygame.image.load('media/bob.png')
wow = pygame.image.load('media/wow.png')
bow = pygame.image.load('media/bow.png')

sound = pygame.mixer.Sound('media/knock.wav')


screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Corners")
icon = pygame.image.load('media/checker-board.png')
pygame.display.set_icon(icon)

clock = pygame.time.Clock()


class Tile(pygame.sprite.Sprite):
    def __init__(self, cl, x, y):
        super().__init__()

        self.clr = cl
        self.column = x
        self.row = y
        self.image = pygame.Surface((100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = 100 * column
        self.rect.y = 700-(100 * row)

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

def swap(pos1, pos2):
    pos1.piece, pos2.piece = pos2.piece, pos1.piece
    pos1.draw()
    pos2.draw()
    sound.play()



tile_list = pygame.sprite.Group()

cl = 1
for row in range(8):
    cl *= -1
    for column in range(8):
        tile = Tile(cl, column+1, row+1)
        cl *= -1
        tile_list.add(tile)
tile_list.draw(screen)


def redraw():
    pygame.display.update()
    tile_list.update()


def legal(pos1, pos2):
    if pos1.piece != team:
        return False
    if base is not None and pos1 != base:
        return False
    if pos2 in visited:
        return False
    if pos2.piece != 0:
        return False
    if pos1.column != pos2.column and pos1.row != pos2.row:
        return False

    if abs(pos1.row - pos2.row) > 2 or abs(pos1.column - pos2.column) > 2:
        return False

    if abs(pos1.row - pos2.row) == 2 and pos1.column == pos2.column:
        for middle in tile_list:
            if middle.row == min(pos1.row, pos2.row)+1 and middle.column == pos1.column:
                if middle.piece != 0:
                    return True
        return False

    if abs(pos1.column - pos2.column) == 2 and pos1.row == pos2.row:
        for middle in tile_list:
            if middle.column == min(pos1.column, pos2.column) + 1 and middle.row == pos1.row:
                if middle.piece != 0:
                    return True
        return False

    if base is None:
        return True
    else:
        return False


def win():
    black_stack = 0
    white_stack = 0

    for elem in tile_list:
        for row1 in range(6, 9):
            for column1 in range(1, 5):
                if elem.row == row1 and elem.column == column1:
                    if elem.piece == 1:
                        white_stack += 1
                    elif turn >= 80 and elem.piece == -1:
                        print('White won')
                        return True

        for row2 in range(1, 4):
            for column2 in range(5, 9):
                if elem.row == row2 and elem.column == column2:
                    if elem.piece == -1:
                        black_stack += 1
                    elif turn >= 79 and elem.piece == 1:
                        print('Black won')
                        return True

    if white_stack == 12:
        print('White won')
        return True

    elif black_stack == 12:
        print('Black won')
        return True

    return False


running = True
team = 1
move = []
base = None
visited = []
turn = 1


while running:
    pygame.time.delay(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and base is not None:
            base = None
            visited = []
            move = []
            turn += 1
            team *= -1

            print('Крок', turn, 'гравця ', end='')
            if team == 1:
                print('білими')
            else:
                print('чорними')

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for i in tile_list:
                if i.rect.collidepoint(pos):
                    move.append(i)
                    if len(move) == 2:
                        if legal(move[0], move[1]):
                            swap(move[0], move[1])
                            running = not win()
                            base = move[1]
                            visited.append(move[0])
                            move = [base]
                        else:
                            if base is None:
                                move.remove(move[0])
                            else:
                                move.remove(move[1])

    redraw()

