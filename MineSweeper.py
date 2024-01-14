
from random import randint, uniform
from time import time, ctime
from math import cos, sin, radians
from ctypes import windll
from sys import exit
import pygame


windll.shcore.SetProcessDpiAwareness(2) # avoid windows auto rescaling to make visible the entire window on low resolutions screens
pygame.init()

WIN_SIZE = [600, 635]

win = pygame.display.set_mode(WIN_SIZE)

pygame.display.set_caption('Minesweeper')
pygame.display.set_icon(pygame.image.load('asset\\logo2.png'))

clock = pygame.time.Clock()


TILE_SIZE = 40

COLOR = (248, 238, 187)
COLOR2 = (228, 218, 167)
LIGHT_COLOR = (255, 252, 240)

BKG1 = (25, 27, 45)
BKG2 = (23, 25, 40)

BKGR1 = (57, 59, 80)
BKGR2 = (53, 55, 75)

ADJACENTS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


levels = {
    'map'  : {1: 10, 2: 15, 3: 25, 4: 40},
    'win'  : {1: 400, 2: 600, 3: 750, 4: 800},
    'tile' : {1: 40, 2: 40, 3: 30, 4: 20},
    'mines': {1: 12, 2: 35, 3: 100, 4: 250}
}

themes = {
    1: {
        'colors': {1: 'blue', 2: 'green', 3: 'red', 4: 'darkblue', 5: 'darkred', 6: 'purple', 7: 'black', 8:'darkgray'},
        'size': {40: 25, 30: 20, 20: 12},
        'flag': 'flag.png'
        },
    2: {
        'colors': {1: 'blue4', 2: 'green4', 3: 'red3', 4: 'darkblue', 5: 'darkred', 6: 'purple3', 7: 'black', 8: 'darkgray'},
        'size': {40: 25, 30: 20, 20: 12},
        'flag': 'flag.png'
        },
    3: {
        'colors': {1: 'yellow', 2: 'orange', 3: 'orangered', 4: 'red3', 5: 'darkred', 6: 'purple', 7: 'black', 8: 'darkgray'},
        'size': {40: 18, 30: 15, 20: 9},
        'flag': 'flag2.png',
        'letters': {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5:'V', 6:'VI', 7:'VII', 8:'VIII'}
        }
    }


def load_theme(theme):
    global flag_img, numbers
    flag_img = pygame.image.load('asset\\'+themes[theme]['flag']).convert_alpha()
    numbers = {}
    for tile_size in levels['tile'].values():
        numbers[tile_size] = {}
        font = pygame.font.Font('asset\\JetBrainsMono-SemiBold.ttf', themes[theme]['size'][tile_size])
        for nb in range(1, 9):
            numbers[tile_size][nb] = font.render(
                str(nb) if theme != 3 else themes[theme]['letters'][nb], True, themes[theme]['colors'][nb])


def load_sound(name, volume=1):
    s = pygame.mixer.Sound('asset\\'+name)
    s.set_volume(volume)
    return s


menu_font = pygame.font.Font('asset\\JetBrainsMono-SemiBold.ttf', 25)
menu_rect = pygame.Rect(0, 0, levels['win'][4], 35)

mine_img = pygame.image.load('asset\\mine.png').convert_alpha()

reload_img = pygame.transform.scale(pygame.image.load('asset\\reload_icon.png'), (25, 25)).convert_alpha()
reload_rect = reload_img.get_rect(center=(160, 17))

flag_icon = pygame.image.load('asset\\flag_icon.png').convert_alpha()
time_icon =  pygame.transform.scale(pygame.image.load('asset\\time_icon.png'), (20, 23)).convert_alpha()

sound_on_img = pygame.transform.scale(pygame.image.load('asset\\sound_on.png'), (25, 25)).convert_alpha()
sound_off_img = pygame.transform.scale(pygame.image.load('asset\\sound_off.png'), (25, 25)).convert_alpha()
sound_rect = sound_on_img.get_rect(center=(WIN_SIZE[0]-25, 17))

sound = True
sound_switch_timer = 0
refresh_sound = load_sound('refresh.mp3', 0.2)
click_sound = load_sound('click_sound.wav', 0.6)
exp_sound = load_sound('explosion_sound.wav')
flag_sound = load_sound('flag_sound.wav', 0.2)
win_sound = load_sound('win_sound.wav', 0.9)

load_theme(3)

screen_shake = False
screen_shake_timer = 0


def blit_center(surface, surf, center, *args, **kwargs):
    surface.blit(surf, (center[0] - surf.get_width()/2, center[1] - surf.get_height()/2), *args, **kwargs)


class Tile():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * TILE_SIZE, 35 + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = None
        self.revealed = False
        self._flaged = False
        self.get_color()
        self.hovered_color = COLOR
    
    @property
    def flaged(self):
        return self._flaged
    
    @flaged.setter
    def flaged(self, value: bool):
        global current_mines
        if value and not self._flaged:
            current_mines -= 1
        elif not value and self._flaged:
            current_mines += 1
        self._flaged = value
        
    def set_type(self, type):
        self.type = type
    
    def reveal(self):
        self.revealed = True
        if self.flaged:
            self.flaged = False
        self.get_color()
        for i in range(self.get_particles_nb(dc.diff_nb[dc.current_diff])):
            particles.append(Particle(self.rect.center, (255, 0, 0, 255) if self.type == -1 else 'purple'))
    
    def get_color(self):
        if self.x % 2 == 0:
            if self.y % 2 == 0:
                self.color = BKG1 if not self.revealed else BKGR1
            else:
                self.color = BKG2 if not self.revealed else BKGR2
        else:
            if self.y % 2 == 0:
                self.color = BKG2 if not self.revealed else BKGR2
            else:
                self.color = BKG1 if not self.revealed else BKGR1
    
    def get_particles_nb(self, diff):
        if self.type != -1:
            return 30
        elif diff < 3:
            return 100
        elif diff == 3:
            return 40
        else:
            return 20
    
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


class Particle():
    def __init__(self, center, color):
        width = randint(4, 10)
        self.rect = pygame.Rect(*center, width, width)
        self.speed = randint(8, 12)
        self.angle = randint(-180, 180)
        if type(color) == str:
            self.color = list(pygame.colordict.THECOLORS[color])
        else:
            self.color = list(color)
        self.image = pygame.Surface((width, width), pygame.SRCALPHA)
        self.alive = True
        
    def update(self, *args):
        self.color[3] -= 15
        self.rect.x += cos(radians(self.angle)) * self.speed
        self.rect.y += sin(radians(self.angle)) * self.speed
        self.speed -= 0.7
        if self.speed <= 0 or self.color[3] <= 0:
            self.alive = False
        
    def render(self, surf):
        self.image.fill(self.color)
        surf.blit(self.image, self.rect)


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
        self.hovered = False
    
    def set_difficulty(self, diff):
        global Map, rows, cols, current_mines, first_click, game_over
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
        Map, rows, cols, current_mines, first_click, game_over = set_level(self.diff_nb[diff])
    
    def is_hovered_exp(self):
        hovered = self.hovered
        if not hovered and self.expanded:
            for opt in self.options.values():
                if opt['rect'].collidepoint(mouse_pos):
                    hovered = True
        return hovered
    
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


def set_level(difficulty):
    global WIN_SIZE, TILE_SIZE, win, sound_rect
     # load variables
    rows = cols = levels['map'][difficulty]
    WIN_SIZE = [levels['win'][difficulty], levels['win'][difficulty] + 35]
    win = pygame.display.set_mode(WIN_SIZE)
    TILE_SIZE = levels['tile'][difficulty]
    sound_rect = sound_on_img.get_rect(center=(WIN_SIZE[0]-25, 17))
    
    # create raw map
    Map = [[Tile(x, y) for x in range(cols)] for y in range(rows)]
    
    # place mines
    mines = 0
    max_mines = levels['mines'][difficulty]
    while mines != max_mines:
        x = randint(0, cols-1)
        y = randint(0, rows-1)
        if Map[y][x].type is None and x != 0 and y != 0:
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
    return Map, rows, cols, mines, True, False


def calculate_screen_shake_timer(num_destroyed_tiles):
    base_shake_duration = 500
    max_tiles_for_scaling = 10
    scaling_factor = min(num_destroyed_tiles / max_tiles_for_scaling, 1.0)
    scaled_shake_timer = base_shake_duration * scaling_factor
    random_factor = uniform(0.8, 1.2)
    scaled_shake_timer *= random_factor
    return round(scaled_shake_timer)


def set_screen_shake(duration):
    global screen_shake, screen_shake_timer
    screen_shake = True
    screen_shake_timer = duration


def check_all_revealed():
    for y, row in enumerate(Map):
        for x, tile in enumerate(row):
            if tile.type != -1:
                if not tile.revealed:
                    return False
    return True


def Win():
    global game_over, final_time
    final_time = time()-start_time
    game_over = True
    if sound:
        win_sound.play()


def GameOver():
    global game_over, final_time
    final_time = time()-start_time
    game_over = True
    if sound:
        exp_sound.play()
    set_screen_shake(1000)
    for y, row in enumerate(Map):
        for x, tile in enumerate(row):
            if tile.type == -1:
                tile.reveal()


def reveal(tile):
    global first_click, start_time
    if first_click:
        first_click = False
        start_time = time()
    tile.reveal()
    if tile.type != 0:
        if tile.type == -1:
            GameOver()
        elif current_mines == 0 and check_all_revealed():
            Win()
    else:
        currents = [tile]
        revealed_tiles = 1
        while currents:
            for t in currents:
                for n in t.get_neighbours(Map, cols, rows):
                    if not n in currents and n.type != -1 and not n.revealed:
                        if n.type == 0:
                            currents.append(n)
                        n.reveal()
                        revealed_tiles += 1
                currents.remove(t)
        if revealed_tiles > 4:
            set_screen_shake(calculate_screen_shake_timer(revealed_tiles))
        if current_mines == 0 and check_all_revealed():
            Win()


def flag(tile):
    global first_click, start_time
    if first_click:
        first_click = False
        start_time = time()
    tile.flaged = not tile.flaged
    if sound:
        if tile.flaged:
            flag_sound.play()
        else:
            ...
    if current_mines == 0 and check_all_revealed():
        Win()


def reset():
    global Map, rows, cols, current_mines, first_click, game_over
    Map, rows, cols, current_mines, first_click, game_over = set_level(dc.diff_nb[dc.current_diff])
    if sound:
        refresh_sound.play()


try:
    particles = []
    dc = DifficultyChooser()
    
    while True:
        dt = clock.tick(30)
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
        
        if sound_switch_timer > 0:
            sound_switch_timer -= dt
        if (keys[pygame.K_m] or (left_click and sound_rect.collidepoint(mouse_pos))) and sound_switch_timer <= 0:
            sound = not sound
            sound_switch_timer = 300
        
        if screen_shake:
            screen_shake_timer -= dt
            if screen_shake_timer <= 0:
                screen_shake = False
            power = round(screen_shake_timer/12)
            offset = [randint(0, max(power, 1)) - power/2, 35 + randint(0, max(power, 1)) - power/2]
            win.fill('black')
        else:
            offset = [0, 35]
        
        pygame.draw.rect(win, 'black', (0, 0, WIN_SIZE[1], 35))
        
        ui_hovered = False
        if menu_rect.collidepoint(mouse_pos):
            ui_hovered = True
        if dc.expanded and not ui_hovered:
            if dc.is_hovered_exp():
                ui_hovered = True
        
        if (ui_hovered and left_click):
            if reload_rect.collidepoint(mouse_pos):
                reset()
        if keys[pygame.K_F5] or (keys[pygame.K_LCTRL] and keys[pygame.K_r]):
            reset()
        
        for y, row in enumerate(Map):
            for x, tile in enumerate(row):
                hovered = tile.is_hovered()
                
                if hovered and not ui_hovered and not game_over and not tile.revealed:
                    if left_click and not tile.flaged:
                        reveal(tile)
                        if sound:
                            click_sound.play()
                    elif right_click:
                        flag(tile)
                
                if hovered and not (tile.revealed and (tile.type == 0 or tile.type == -1)):
                    pygame.draw.rect(win, tile.hovered_color, (x*TILE_SIZE + offset[0], y*TILE_SIZE + offset[1], TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(win, tile.color, (x*TILE_SIZE + offset[0], y*TILE_SIZE + offset[1], TILE_SIZE, TILE_SIZE))
                
                if tile.revealed and tile.type != 0:
                    if tile.type == -1:
                        img = mine_img if TILE_SIZE == 40 else pygame.transform.scale(mine_img, (TILE_SIZE, TILE_SIZE))
                        win.blit(img, (x*TILE_SIZE + offset[0], y*TILE_SIZE + offset[1]))
                    else:
                        blit_center(win, numbers[TILE_SIZE][tile.type], (tile.rect.centerx + offset[0], tile.rect.centery + offset[1] - 35))
                
                elif tile.flaged:
                    img = flag_img if TILE_SIZE == 40 else pygame.transform.scale(flag_img, (TILE_SIZE, TILE_SIZE))
                    win.blit(img, (x*TILE_SIZE + offset[0], y*TILE_SIZE + offset[1]))
        
        for p in particles:
            p.update(dt)
            if not p.alive:
                particles.remove(p)
            else:
                p.render(win)
        
        blit_center(win, menu_font.render(str(current_mines), True, COLOR2), (WIN_SIZE[0]-(80 if dc.current_diff != 'easy' else 62), 17))
        blit_center(win, flag_icon, (WIN_SIZE[0]-(80 if dc.current_diff != 'easy' else 55) - flag_icon.get_width() - 20, 17))
        
        if first_click:
            start_time = time()
        if not game_over:
            img = menu_font.render(str(ctime(time()-start_time)[14:19]), True, COLOR2)
        else:
            img = menu_font.render(str(ctime(final_time)[14:19]), True, COLOR2)
        
        blit_center(win, img, (WIN_SIZE[0]/2 + (52 if dc.current_diff == 'easy' else img.get_width()/2), 17))
        blit_center(win, time_icon, (WIN_SIZE[0]/2 - (6 if dc.current_diff == 'easy' else time_icon.get_width()/2 + 10), 17))
        
        dc.update()
        dc.render()
        
        if sound:
            win.blit(sound_on_img, sound_rect)
        else:
            win.blit(sound_off_img, sound_rect)
        
        win.blit(reload_img, reload_rect)
        
        pygame.display.flip()
        
except Exception as crash:
    pygame.quit()
    raise crash
