
from sys import exit
from random import randint
import pygame
pygame.init()


WIN_SIZE = [600, 635]

TILE_SIZE = 40

COLOR = (248, 238, 187)
COLOR2 = (228, 218, 167)
LIGHT_COLOR = (255, 252, 240)

BKG1 = (25, 27, 45)
BKG2 = (23, 25, 40)


win = pygame.display.set_mode(WIN_SIZE)
pygame.display.set_caption('MineSweeper')

clock = pygame.time.Clock()


menu_font = pygame.font.Font('JetBrainsMono-SemiBold.ttf', 25)


ADJACENTS = [
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1)
]


levels = {
    'map'  : {1: 10, 2: 15, 3: 25, 4: 40},
    'win'  : {1: 400, 2: 600, 3: 750, 4: 800},
    'tile' : {1: 40, 2: 40, 3: 30, 4: 20},
    'mines': {1: 12, 2: 36, 3: 100, 4: 250}
}


def blit_center(surface, surf, center, *args, **kwargs):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2), *args, **kwargs)


class DifficultyChooser():
    current_diff = 'medium'
    def  __init__(self):
        c = COLOR2
        self.images = {
            'easy':  menu_font.render('easy', True, c),
            'medium': menu_font.render('medium', True, c),
            'hard': menu_font.render('hard', True, c),
            'extreme': menu_font.render('extreme', True, c)
            }
        self.image = pygame.Surface(WIN_SIZE, pygame.SRCALPHA)
        self.rect = self.images['extreme'].get_rect()
        self.rect.inflate_ip(32, -2)
        self.rect.centery = 17
        self.rect.left = 3
        self.expanded = False
        self.triangle_points = [(self.rect.right-10, self.rect.top+11), (self.rect.right-18, self.rect.top+11), (self.rect.right-14, self.rect.top+17)]
        self.diff_nb = {'easy': 1, 'medium': 2, 'hard': 3, 'extreme': 4}
        self.opt_size = self.images['extreme'].get_rect().height
        self.options_name = ['easy', 'medium', 'hard', 'extreme']
        self.options = {}
        self.set_difficulty(self.current_diff)
        self.hovered_color = list(pygame.colordict.THECOLORS['navyblue'])
        self.hovered_color[3] = 200
    
    def set_difficulty(self, diff):
        global Map, rows, cols, current_mines
        self.current_diff = diff
        self.options = {}
        index = 0
        for opt in self.options_name:
            if opt != diff:
                self.options[index] = {
                    'name': opt,
                    'rect': pygame.Rect(self.rect.left, self.rect.bottom + self.opt_size*index, self.rect.width, self.opt_size),
                    'index': index
                    }
                index += 1
        Map, rows, cols, current_mines = set_level(self.diff_nb[diff])
    
    def update(self):
        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
            if left_click:
                self.expanded = not self.expanded
        else:
            self.hovered = False
        if self.expanded:
            if left_click and not self.hovered:
                self.expanded = False
            if left_click:
                for opt in self.options.values():
                    if opt['rect'].collidepoint(mouse_pos):
                        self.set_difficulty(opt['name'])
    
    def is_hovered_exp(self):
        hovered = self.hovered
        if not hovered:
            for opt in self.options.values():
                if opt['rect'].collidepoint(mouse_pos):
                    hovered = True
        return hovered
    
    def render(self):
        self.image.fill((0, 0, 0, 0))
        if self.hovered:
            pygame.draw.rect(self.image, self.hovered_color, self.rect)
        self.image.blit(self.images[self.current_diff], (self.rect.x + 5, self.rect.top - 3))
        pygame.draw.rect(self.image, COLOR2, self.rect, 2)
        pygame.draw.polygon(self.image, COLOR2, self.triangle_points)
        if self.expanded:
            for opt in self.options.values():
                if opt['rect'].collidepoint(mouse_pos):
                    pygame.draw.rect(self.image, self.hovered_color, opt['rect'])
                self.image.blit(self.images[opt['name']], (self.rect.x + 5, self.rect.bottom + self.opt_size*opt['index'] - 2))
            pygame.draw.rect(self.image, COLOR2, (self.rect.left, self.rect.bottom-2, self.rect.width, self.opt_size*3+4), 2)
        win.blit(self.image, (0, 0))


class Tile():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * TILE_SIZE, 35 + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.get_color()
        self.hovered_color = COLOR
        self.type = None
        self.revealed = False
    
    def set_type(self, type):
        self.type = type
    
    def get_color(self):
        if self.x % 2 == 0:
            if self.y % 2 == 0:
                self.color = BKG1
            else:
                self.color = BKG2
        else:
            if self.y % 2 == 0:
                self.color = BKG2
            else:
                self.color = BKG1
    
    def is_hovered(self):
        if self.rect.collidepoint(mouse_pos):
            return True
        else:
            return False
    
    def get_neighbours(self, Map, cols, rows):
        neighbours = []
        for (x, y) in ADJACENTS:
            if 0 <= self.x + x <= cols-1 and 0 <= self.y + y <= rows-1:
                neighbours.append(Map[self.y + y][self.x + x])
        return neighbours


def set_level(difficulty):
    global WIN_SIZE, TILE_SIZE, win
     # load variables
    rows = cols = levels['map'][difficulty]
    WIN_SIZE = [levels['win'][difficulty], levels['win'][difficulty] + 35]
    win = pygame.display.set_mode(WIN_SIZE)
    TILE_SIZE = levels['tile'][difficulty]
    
    # create raw map
    Map = [[Tile(x, y) for x in range(cols)] for y in range(rows)]
    
    # place mines
    mines = 0
    max_mines = levels['mines'][difficulty]
    while mines != max_mines:
        x = randint(0, cols-1)
        y = randint(0, rows-1)
        if Map[y][x].type is None:
            Map[y][x].set_type(-1)
            mines += 1
    
    # determine tiles numbers
    for y, row in enumerate(Map):
        for x, tile in enumerate(row):
            if tile.type is None:
                neighbours_mines = 0
                for t in tile.get_neighbours(Map, cols, rows):
                    if t.type == -1:
                        neighbours_mines += 1
                tile.set_type(neighbours_mines)
    return Map, rows, cols, mines


try:
    dc = DifficultyChooser()
    
    while True:
        clock.tick(30)
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        left_click = False
        right_click = False
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    left_click = True
                elif e.button == 3:
                    right_click = True
            elif e.type == pygame.QUIT:
                pygame.quit()
                exit()
        mouse_pos = pygame.mouse.get_pos()
        
        win.fill('white')
        
        pygame.draw.rect(win, 'black', (0, 0, WIN_SIZE[1], 35))
        
        for y, row in enumerate(Map):
            for x, tile in enumerate(row):
                # if tile.is_hovered():
                #     pygame.draw.rect(win, tile.hovered_color, (x*TILE_SIZE, 35 + y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                # else:
                #     pygame.draw.rect(win, tile.color, (x*TILE_SIZE, 35 + y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                if tile.type == 0:
                    pygame.draw.rect(win, 'gray', (x*TILE_SIZE, 35 + y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif tile.type == -1:
                    pygame.draw.rect(win, 'red', (x*TILE_SIZE, 35 + y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(win, tile.color, (x*TILE_SIZE, 35 + y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    blit_center(win, menu_font.render(str(tile.type), True, 'black'), tile.rect.center)
        
        blit_center(win, menu_font.render(str(current_mines), True, COLOR2), (WIN_SIZE[0]-200, 17))
        
        dc.update()
        dc.render()
        
        # for x in range(1, cols):
        #     pygame.draw.line(win, COLOR, (x*TILE_SIZE, 37), (x*TILE_SIZE, WIN_SIZE[1]))
        # for y in range(1, rows):
        #     pygame.draw.line(win, COLOR, (0, 35+y*TILE_SIZE), (WIN_SIZE[0], 35+y*TILE_SIZE))
        
        pygame.display.flip()
        
except Exception as crash:
    pygame.quit()
    raise crash
