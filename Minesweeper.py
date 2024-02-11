
from random import randint, uniform, choice
from time import time, ctime
from math import cos, sin, radians
from os.path import join
from os import name
from sys import exit
import pygame


if name == 'nt':
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(2) # avoid windows auto rescaling to make visible the entire window on low resolutions screens


# Pygame setup ----------------------------------------------------------------

pygame.init()

WIN_SIZE = [600, 635]

win = pygame.display.set_mode(WIN_SIZE)

display = pygame.Surface(WIN_SIZE)

pygame.display.set_caption('Minesweeper')
pygame.display.set_icon(pygame.image.load(join('asset', 'logos', 'logo2.png')))

clock = pygame.time.Clock()


# Constants -------------------------------------------------------------------

TILE_SIZE = 40

COLOR = (228, 218, 167) # color for all ui elements

BKG1 = (25, 27, 45) # background colors
BKG2 = (23, 25, 40)

BKGR1 = (57, 59, 80) # background colors for revealed tiles
BKGR2 = (53, 55, 75)

PURPLE = (160, 32, 240, 255) # particles colors with alpha values
RED = (255, 0, 0, 255)

TILE_HOVERED_COLOR = (248, 238, 187)

ADJACENTS = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))


# Levels and Themes configurations --------------------------------------------

levels = {
    'map'  : {1: 10, 2: 15, 3: 25, 4: 40},
    'win'  : {1: 400, 2: 600, 3: 750, 4: 800},
    'tile' : {1: 40, 2: 40, 3: 30, 4: 20},
    'mines': {1: 12, 2: 35, 3: 100, 4: 250}
}

themes = {
    0: {
        'colors': {1: 'blue', 2: 'green', 3: 'red', 4: 'darkblue', 5: 'darkred', 6: 'purple', 7: 'black', 8:'darkgray'},
        'size': {40: 25, 30: 20, 20: 12},
        'flag': 'flag.png',
        'name': 'theme',
        'font': 'JetBrainsMono-SemiBold.ttf'
        },
    1: {
        'colors': {1: 'yellow', 2: 'orange', 3: 'orangered', 4: 'red3', 5: 'darkred', 6: 'lightgray', 7: 'darkgray', 8: 'black'},
        'size': {40: 18, 30: 15, 20: 9},
        'flag': 'flag2.png',
        'letters': {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5:'V', 6:'VI', 7:'VII', 8: 'VI\nII'},
        'name': 'main theme'
        },
    2: {
        'name': 'classic theme'
        },
    3: {
        'flag': 'flag2.png',
        'colors': {1: 'LightBlue', 2: 'DeepSkyBlue', 3: 'DodgerBlue', 4: 'SteelBlue', 5: 'MediumSlateBlue', 6: 'DarkSlateBlue', 7: 'MediumPurple', 8: 'DarkSlateGray'}
        },
    4: {
        'colors': {1: 'blue4', 2: 'green4', 3: 'red3', 4: 'darkblue', 5: 'darkred', 6: 'purple3', 7: 'black', 8: 'darkgray'}
        },
    5: {
        'colors': {1: 'yellow', 2: 'orange', 3: 'orangered', 4: 'red3', 5: 'darkred', 6: 'lightgray', 7: 'darkgray', 8: 'black'},
        'flag': 'flag2.png'
        },
    6: {
        'size': {40: 18, 30: 15, 20: 9},
        'flag': 'flag2.png',
        'letters': {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5:'V', 6:'VI', 7:'VII', 8: 'VI\nII'}
        }
    }


# Utils functions -------------------------------------------------------------

def blit_center(dst, src, center, *args, **kwargs):
    dst.blit(src, (center[0] - src.get_width()/2, center[1] - src.get_height()/2), *args, **kwargs)


def load_sound(name, volume=1):
    s = pygame.mixer.Sound(join('asset', 'sounds', name))
    s.set_volume(volume)
    return s


def get_color(x, y, color1, color2):
    if x % 2 == 0:
        if y % 2 == 0:
            return color1
        else:
            return color2
    else:
        if y % 2 == 0:
            return color2
        else:
            return color1


def create_numbers(theme):
    numbers = {}
    for tile_size in levels['tile'].values():
        numbers[tile_size] = {}
        font = pygame.font.Font(join('asset', 'font', theme['font']), theme['size'][tile_size])
        for nb in range(1, 9):
            numbers[tile_size][nb] = font.render(str(nb) if not 'letters' in theme else theme['letters'][nb], True, theme['colors'][nb])
    return numbers


def load_theme(theme):
    global flag_img, numbers
    flag_img = themes[theme]['flag_img']
    numbers = themes[theme]['numerals']


def create_theme_preview(theme):
    surface = pygame.Surface((120, 120))
    surface.blit(r.theme_preview_bkg, (0, 0))
    blit_center(surface, theme['numerals'][40][1], (20, 20))
    blit_center(surface, theme['numerals'][40][2], (60, 20))
    blit_center(surface, theme['numerals'][40][3], (60, 60))
    blit_center(surface, theme['flag_img'],       (100, 60))
    blit_center(surface, r.mine_img,             (100, 100))
    return surface


# load ressources -------------------------------------------------------------

class RessourceManager():
    def __init__(self):
        self.font = pygame.font.Font(join('asset', 'font', 'JetBrainsMono-SemiBold.ttf'), 25)
        self.font_small = pygame.font.Font(join('asset', 'font', 'JetBrainsMono-SemiBold.ttf'), 20)
        
        self.mine_img = pygame.image.load(join('asset', 'images', 'mine.png')).convert_alpha()
        
        self.reload_img = pygame.transform.scale(pygame.image.load(join('asset', 'icons', 'reload_icon.png')), (25, 25)).convert_alpha()
        self.settings_icon = pygame.transform.scale(pygame.image.load(join('asset', 'icons', 'settings_icon.png')), (22, 22)).convert_alpha()
        self.flag_icon = pygame.image.load(join('asset', 'icons', 'flag_icon.png')).convert_alpha()
        self.time_icon =  pygame.transform.scale(pygame.image.load(join('asset', 'icons', 'time_icon.png')), (20, 23)).convert_alpha()
        
        self.theme_preview_bkg = pygame.image.load(join('asset', 'logos', 'theme_preview_bkg.png')).convert()
        
        self.refresh_sound = load_sound('refresh.mp3', 0.2)
        self.click_sound = load_sound('click_sound.wav', 0.6)
        self.exp_sound = load_sound('explosion_sound.wav')
        self.flag_sound = load_sound('flag_sound.wav', 0.2)
        self.unflag_sound = load_sound('unflag_sound.wav', 0.5)
        self.win_sound = load_sound('win_sound.wav', 0.9)

r = RessourceManager()

# menu buttons rects
menu_rect = pygame.Rect(0, 0, levels['win'][4], 35)
reload_rect = r.reload_img.get_rect(center=(160, 17))
settings_rect = r.settings_icon.get_rect(center=(WIN_SIZE[0]-25, 17))

controls_text = """- Reveal a tile : left click or [RETURN]
- Flag / unflag a tile : right click or [f]
- Chord : middle click or both left and right click or [SPACE]
- Reset the level : Ctrl+r or F5
- Zoom in hard and extreme levels : mouse wheel up/down or +/-
- Move when the board is zoomed : arrows UP/DOWN RIGHT/LEFT
- Switch sound : [m]
- Show the suggested safe starting tile : [t]
- Navigate between themes : scoll up/down or arrows [UP]/[DOWN]
- Open / close the settings menu : [s]
- Show this message again : [k]
- Quit the game : [ECHAP]"""

# pre-load themes
for theme in themes:
    if theme != 0:
        for opt in themes[0]:
            if not opt in themes[theme]:
                themes[theme][opt] = themes[0][opt]
        name = 'theme '+str(theme) if themes[theme]['name'] == 'theme' else themes[theme]['name']
        themes[theme]['name_rendered'] = r.font_small.render(name, True, COLOR)
        themes[theme]['numerals'] = create_numbers(themes[theme])
        themes[theme]['flag_img'] = pygame.image.load(join('asset', 'images', themes[theme]['flag'])).convert_alpha()
        themes[theme]['img'] = create_theme_preview(themes[theme])

load_theme(1) # load the main theme


# Tile class ------------------------------------------------------------------

class Tile():
    __slots__ = ('x', 'y', 'type', 'revealed', '_flaged', 'color', 'particle_nb', 'particle_color', 'neighbours')
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = None
        self.revealed = False
        self._flaged = False
        self.color = get_color(x, y, BKG1, BKG2)
        self.particle_nb = 0
        self.particle_color = PURPLE
        self.neighbours = []
    
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
        self.particle_color = RED if self.type == -1 else PURPLE
    
    def set_difficulty(self, diff):
        self.particle_nb = self.get_particles_nb(diff)
    
    def reveal(self):
        self.revealed = True
        if self.flaged:
            self.flaged = False
        self.color = get_color(self.x, self.y, BKGR1, BKGR2)
        for i in range(self.particle_nb):
            particles.append(Particle((self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2), self.particle_color))
    
    def get_particles_nb(self, diff):
        if self.type != -1:
            return 30 if diff != 4 else 20
        elif diff < 3:
            return 100
        elif diff == 3:
            return 40
        else:
            return 20
    
    def get_neighbours(self, Map, cols, rows):
        neighbours = []
        for (x, y) in ADJACENTS:
            if 0 <= self.x + x <= cols-1 and 0 <= self.y + y <= rows-1:
                neighbours.append(Map[self.y + y][self.x + x])
        return neighbours


# Particle class --------------------------------------------------------------

class Particle():
    __slots__ = ('rect', 'speed', 'color', 'image', 'cos', 'sin', 'alpha')
    def __init__(self, center, color):
        if dc.diff_nb == 3:
            m = 0.8
        elif dc.diff_nb == 4:
            m = 0.7
        else:
            m = 1
        
        width = randint(4, 10) * m
        self.speed = randint(8, 12) * m
        
        self.rect = pygame.Rect(*center, width, width)
        self.color = color
        self.image = pygame.Surface((width, width))
        self.image.fill(self.color)
        angle = radians(randint(-180, 180))
        self.cos = cos(angle)
        self.sin = sin(angle)
        self.alpha = 255
        
    def update(self, *args):
        self.rect.x += self.cos * self.speed
        self.rect.y += self.sin * self.speed
        self.speed -= 0.7
        self.alpha -= 15
        if self.speed <= 0 or self.alpha <= 0:
            return True
        return False
        
    def render(self, surf):
        self.image.set_alpha(self.alpha)
        surf.blit(self.image, self.rect)


# Difficulty drop-down menu ---------------------------------------------------

class DifficultyChooser():
    current_diff = 'medium'
    def  __init__(self):
        c = COLOR
        self.images = {
            'easy':  r.font.render('easy', True, c),
            'medium': r.font.render('medium', True, c),
            'hard': r.font.render('hard', True, c),
            'extreme': r.font.render('extreme', True, c)
            }
        self.image = pygame.Surface(WIN_SIZE, pygame.SRCALPHA)
        self.rect = self.images['extreme'].get_rect()
        self.rect.inflate_ip(32, -2)
        self.rect.centery = 17
        self.rect.left = 3
        self.expanded = False
        self.triangle_points = tuple([(self.rect.right-10, self.rect.top+11), (self.rect.right-18, self.rect.top+11), (self.rect.right-14, self.rect.top+17)])
        self.diff_nb_dict = {'easy': 1, 'medium': 2, 'hard': 3, 'extreme': 4}
        self.opt_size = self.images['extreme'].get_rect().height
        self.options_name = ['easy', 'medium', 'hard', 'extreme']
        self.options = {}
        self.set_difficulty(self.current_diff)
        self.hovered_color = list(pygame.colordict.THECOLORS['navyblue'])
        self.hovered_color[3] = 200
        self.hovered = False
    
    @property
    def diff_nb(self):
        return self.diff_nb_dict[self.current_diff]
    
    def set_difficulty(self, diff):
        global Map, rows, cols, current_mines, first_click, game_over, safe_tile
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
        Map, rows, cols, current_mines, safe_tile = set_level(self.diff_nb_dict[diff])
    
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
    
    def render(self, surface):
        self.image.fill((0, 0, 0, 0))
        if self.hovered:
            pygame.draw.rect(self.image, self.hovered_color, self.rect)
        
        self.image.blit(self.images[self.current_diff], (self.rect.x + 5, self.rect.top - 3))
        pygame.draw.rect(self.image, COLOR, self.rect, 2)
        pygame.draw.polygon(self.image, COLOR, self.triangle_points)
        
        if self.expanded:
            for opt in self.options.values():
                if opt['rect'].collidepoint(mouse_pos):
                    pygame.draw.rect(self.image, self.hovered_color, opt['rect'])
                self.image.blit(self.images[opt['name']], (self.rect.x + 5, self.rect.bottom + self.opt_size*opt['index'] - 2))
            pygame.draw.rect(self.image, COLOR, (self.rect.left, self.rect.bottom-2, self.rect.width, self.opt_size*3+4), 2)
        
        surface.blit(self.image, (0, 0))


# UI toggle button element ----------------------------------------------------

class SwitchButton():
    def __init__(self, text, center, activated=True):
        self.text_img = r.font_small.render(text, True, COLOR)
        self.img_rect = self.text_img.get_rect()
        self.rect = pygame.Rect(0, 0, 50, 25)
        self.state = activated
        self.move(center)
    
    def move(self, center):
        self.img_rect.midright = (center[0] - 5, center[1])
        self.rect.midleft = (center[0] + 5, center[1])
    
    def toggle(self):
        self.state = not self.state
    
    def update(self):
        if self.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if left_click:
                self.toggle()
                return True
        return None
    
    def render(self, surf):
        surf.blit(self.text_img, self.img_rect)
        if self.state:
            pygame.draw.circle(surf, 'green', (self.rect.right - self.rect.width/3 + 4, self.rect.centery), self.rect.height/2-2)
        else:
            pygame.draw.circle(surf, 'red', (self.rect.left + self.rect.width/3 - 3, self.rect.centery), self.rect.height/2-2)
        pygame.draw.rect(surf, COLOR, self.rect, 2, border_radius=75)


# Settings menu class ---------------------------------------------------------

class Settings():
    def __init__(self):
        self.image = pygame.Surface((350, 350))#, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(WIN_SIZE[0]/2, WIN_SIZE[1]/2))
        self.setup_ui()
        self.themes_rects = tuple([pygame.Rect(i*160 + 35, 172, 122, 122) for i in range(len(themes)-1)])
        self.sound_button = SwitchButton('sound', (self.rect.left + 240, self.rect.top + 30))
        self.safe_tile_button = SwitchButton('safe starting tile', (self.rect.left + 240, self.rect.top + 65))
        self.active = False
        self.themes_nb = len(themes)
    
    def setup_ui(self):
        self.image.fill((0, 0, 0, 140))
        self.image.blit(r.font.render('Themes :', True, COLOR), (20, 90))
        close_button_img = r.font.render('x', True, COLOR)
        self.close_rect = close_button_img.get_rect(topleft=(self.image.get_width() - 32, 10))
        self.image.blit(close_button_img, self.close_rect)
        controls_img = r.font_small.render('Controls', True, COLOR)
        self.controls_rect = controls_img.get_rect(topleft=(self.rect.left + 20, self.rect.bottom - 45))
        self.image.blit(controls_img, (20, self.rect.height - 45))
        self.image2 = pygame.Surface((350, 350), pygame.SRCALPHA)
    
    def win_adapt(self):
        self.rect.center = (WIN_SIZE[0]/2, WIN_SIZE[1]/2)
        self.controls_rect.topleft = (self.rect.left + 20, self.rect.bottom - 45)
        self.close_rect.topleft = (self.rect.right - 32, self.rect.top + 10)
        self.sound_button.move((self.rect.left + 240, self.rect.top + 30))
        self.safe_tile_button.move((self.rect.left + 240, self.rect.top + 65))
    
    def show_keys(self):
        from tkinter import messagebox
        messagebox.showinfo('Controls', controls_text)
    
    def toggle(self, state=None):
        if state is not None:
            self.active = state
        else:
            self.active = not self.active
        if not self.active:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def scroll_themes(self, scroll):
        for rect in self.themes_rects:
            rect.x += 30 * scroll
    
    def update(self):
        global show_starting_tile
        ui_hovered = False
        if self.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            if scrolling != 0:
                self.scroll_themes(scrolling)
            elif keys[pygame.K_UP]:
                self.scroll_themes(-0.5)
            elif keys[pygame.K_DOWN]:
                self.scroll_themes(0.5)
            
            if self.sound_button.update():
                toggle_sound(switched=False)
            if self.safe_tile_button.update():
                show_starting_tile = not show_starting_tile
            
            if self.close_rect.collidepoint(mouse_pos):
                ui_hovered = True
                if left_click:
                    self.toggle(False)
                    return
            
            if self.controls_rect.collidepoint(mouse_pos):
                ui_hovered = True
                if left_click:
                    self.show_keys()
            
            for i in range(self.themes_nb-1):
                if pygame.Rect(self.themes_rects[i].x + self.rect.left, self.themes_rects[i].y + self.rect.top, 120, 120).collidepoint(mouse_pos):
                    ui_hovered = True
                    if left_click:
                        load_theme(i+1)
            
            if ui_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    
    def render(self, surface):
        surface.blit(self.image, self.rect)
        
        if self.controls_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, COLOR, (self.controls_rect.x, self.controls_rect.bottom - 2, self.controls_rect.width, 2))
        
        self.image2.fill((0, 0, 0, 0))
        for i in range(1, self.themes_nb):
            self.image2.blit(themes[i]['img'], self.themes_rects[i-1])
            pygame.draw.rect(self.image2, COLOR, self.themes_rects[i-1], 2)
            blit_center(self.image2, themes[i]['name_rendered'], (self.themes_rects[i-1].centerx, self.themes_rects[i-1].top - 25))
        surface.blit(self.image2, self.rect)
        
        self.sound_button.render(surface)
        self.safe_tile_button.render(surface)
        
        pygame.draw.rect(surface, COLOR, self.rect, 3)


# Camera class ----------------------------------------------------------------

class Camera():
    __slots__ = ('area', 'zoom', 'offset', 'vel')
    def __init__(self):
        self.area = pygame.Rect(0, 0, WIN_SIZE[0], WIN_SIZE[1] - 35)
        self.zoom = 1
        self.offset = [0, 0]
        self.vel = 10
    
    def reset(self):
        self.zoom = 1
        self.area = pygame.Rect(0, 0, WIN_SIZE[0], WIN_SIZE[1] - 35)
    
    def get_hovered_tile(self):
        if self.zoom == 1:
            pos = (mouse_pos[0] // TILE_SIZE, (mouse_pos[1] - 35) // TILE_SIZE)
            for y, row in enumerate(Map):
                for x, tile in enumerate(row):
                    if (x, y) == pos:
                        return tile
        else:
            pos_x = ((mouse_pos[0] + self.area.x) / self.zoom) // TILE_SIZE
            pos_y = ((mouse_pos[1] + self.area.y - 35) / self.zoom) // TILE_SIZE
            for y, row in enumerate(Map):
                for x, tile in enumerate(row):
                    if (x, y) == (pos_x, pos_y):
                        return tile
    
    def update(self):
        if not sett.active and dc.diff_nb > 2:
            global key_timer
            if key_timer <= 0 :
                if (keys[pygame.K_EQUALS] or scrolling == 1) and self.zoom < (2 if dc.diff_nb == 4 else 1.5):
                    self.zoom += 0.5
                    key_timer = 200
                elif (keys[pygame.K_6] or scrolling == -1) and self.zoom > 1:
                    self.zoom -= 0.5
                    key_timer = 200
            
            if self.zoom != 1:
                motion = [0, 0]
                if keys[pygame.K_UP]:
                   motion[1] -= self.vel
                if keys[pygame.K_DOWN]:
                   motion[1] += self.vel
                if keys[pygame.K_LEFT]:
                    motion[0] -= self.vel
                if keys[pygame.K_RIGHT]:
                    motion[0] += self.vel
                
                self.area.x += motion[0]
                if self.area.x < 0:
                    self.area.x = 0
                elif self.area.right > WIN_SIZE[0] * self.zoom:
                    self.area.right = WIN_SIZE[0] * self.zoom
                
                self.area.y += motion[1]
                if self.area.y < 0:
                    self.area.y = 0
                elif self.area.bottom > (WIN_SIZE[1] - 35) * self.zoom:
                    self.area.bottom = (WIN_SIZE[1] - 35) * self.zoom
    
    def render(self, surface):
       if self.zoom != 1:
           surface.blit(pygame.transform.scale(display, (WIN_SIZE[0] * self.zoom, (WIN_SIZE[1] - 35) * self.zoom)), offset, area=self.area)
       else:
           surface.blit(display, offset)


# Load level functions --------------------------------------------------------

def set_level(difficulty):
    global WIN_SIZE, TILE_SIZE, win, display, settings_rect, first_click, game_over
    
    # load variables
    rows = cols = levels['map'][difficulty]
    WIN_SIZE = [levels['win'][difficulty], levels['win'][difficulty] + 35]
    win = pygame.display.set_mode(WIN_SIZE)
    display = pygame.Surface((WIN_SIZE[0], WIN_SIZE[1] - 35))
    TILE_SIZE = levels['tile'][difficulty]
    sett.win_adapt()
    settings_rect = r.settings_icon.get_rect(center=(WIN_SIZE[0]-25, 18))
    first_click = True
    game_over = False
    cam.reset()
    
    # create raw map
    Map = [[Tile(x, y) for x in range(cols)] for y in range(rows)]
    
    # place mines
    mines = 0
    max_mines = levels['mines'][difficulty]
    if 0: # debug : display all the numbers without mines
        for i  in range(1, 9):
            Map[1][i].set_type(i)
            Map[1][i].set_difficulty(difficulty)
    else:
        while mines != max_mines:
            x = randint(0, cols-1)
            y = randint(0, rows-1)
            if Map[y][x].type is None and x != 0 and y != 0:
                Map[y][x].set_type(-1)
                Map[y][x].set_difficulty(difficulty)
                mines += 1
    
    # determine tiles numbers
    for y, row in enumerate(Map):
        for x, tile in enumerate(row):
            tile.neighbours = tile.get_neighbours(Map, cols, rows)
            if tile.type is None:
                neighbours_mines = 0
                for t in tile.neighbours:
                    if t.type == -1:
                        neighbours_mines += 1
                tile.set_type(neighbours_mines)
                tile.set_difficulty(difficulty)
    
    # determine safe tile
    max_opening = ([], 0)
    visited = set()
    for y, row in enumerate(Map):
        for x, tile in enumerate(row):
            if not tile in visited and tile.type == 0:
                opening = explore_opening(tile, visited, Map, cols, rows)
                visited.update(opening[0])
                if opening[1] > max_opening[1]:
                    max_opening = opening
    safe_tile = choice(max_opening[0])
    safe_tile = pygame.Rect(safe_tile.x * TILE_SIZE, safe_tile.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    return Map, rows, cols, mines, safe_tile


def explore_opening(tile, visited, Map, cols, rows): # DFS alg part to determine the safe starting tile
    currents = [tile]
    opening = [tile]
    while currents:
        for t in currents:
            for n in t.neighbours:
                if n.type == 0 and not n in currents and not n in visited and not n in opening:
                    currents.append(n)
                    opening.append(n)
            currents.remove(t)
    return (opening, len(opening))


# Game functions --------------------------------------------------------------

def toggle_sound(key=False, switched=True):
    global sound, key_timer
    sound = not sound
    if key:
        key_timer = 300
    if switched:
        sett.sound_button.toggle()


def set_screen_shake(duration):
    global screen_shake, screen_shake_timer
    screen_shake = True
    screen_shake_timer = duration


def calculate_screen_shake_timer(num_destroyed_tiles):
    scaling_factor = min(num_destroyed_tiles / 10, 1.0)
    scaled_shake_timer = 500 * scaling_factor
    scaled_shake_timer *= uniform(0.8, 1.2)
    return round(scaled_shake_timer)


def check_all_revealed(): # check if all tiles except mines are revealed
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
        r.win_sound.play()


def GameOver():
    global game_over, final_time
    final_time = time()-start_time
    game_over = True
    if sound:
        r.exp_sound.play()
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
        elif check_all_revealed():
            Win()
    else:
        currents = [tile]
        revealed_tiles = 1
        while currents:
            for t in currents:
                for n in t.neighbours:
                    if not n in currents and n.type != -1 and not n.revealed:
                        if n.type == 0:
                            currents.append(n)
                        n.reveal()
                        revealed_tiles += 1
                currents.remove(t)
        if revealed_tiles > 4:
            set_screen_shake(calculate_screen_shake_timer(revealed_tiles))
        if check_all_revealed():
            Win()


def flag(tile):
    global first_click, start_time
    if first_click:
        first_click = False
        start_time = time()
    tile.flaged = not tile.flaged
    if sound:
        if tile.flaged:
            r.flag_sound.play()
        else:
            r.unflag_sound.play()
    if check_all_revealed():
        Win()


def chord(tile):
    flaged_neighbours = 0
    for t in tile.neighbours:
        if t.flaged:
            flaged_neighbours += 1
    if flaged_neighbours == tile.type:
        if sound:
            r.click_sound.play()
        mines = False
        for t in tile.neighbours:
            if t.type != -1:
                if not t.revealed:
                    reveal(t)
            elif not t.flaged:
                mines = True
        if mines:
            GameOver()


def reset(): # reset all with the reload button
    global Map, rows, cols, current_mines, first_click, game_over, safe_tile
    Map, rows, cols, current_mines, safe_tile = set_level(dc.diff_nb)
    if sound:
        r.refresh_sound.play()


# Game Loop -------------------------------------------------------------------

screen_shake = False
screen_shake_timer = 0
show_starting_tile = True
sound = True
particles = []
key_timer = 0

try:
    sett = Settings()
    cam = Camera()
    dc = DifficultyChooser()
    
    while True:
        dt = clock.tick(30)
        
        # process events
        keys = pygame.key.get_pressed()
        left_click = right_click = middle_click = False
        scrolling = 0
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    left_click = True
                elif e.button == 3:
                    right_click = True
                elif e.button == 2:
                    middle_click = True
            elif e.type == pygame.MOUSEWHEEL:
                if e.y < 0:
                    scrolling = -1
                elif e.y > 0:
                    scrolling = 1
            elif e.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        mouse_pos = pygame.mouse.get_pos()
        
        # update the key timer
        if key_timer > 0:
            key_timer -= dt
        
        # toggle some options with keyboard shortcuts
        if key_timer <= 0:
            if keys[pygame.K_m]:
                toggle_sound(True)
            if keys[pygame.K_t]:
                show_starting_tile = not show_starting_tile
                sett.safe_tile_button.toggle()
                key_timer = 400
        
        # calculate screen shake and determine global offset
        if screen_shake:
            screen_shake_timer -= dt
            if screen_shake_timer <= 0:
                screen_shake = False
            power = round(screen_shake_timer/12)
            offset = (randint(0, max(power, 1)) - power/2, 35 + randint(0, max(power, 1)) - power/2)
            win.fill('black')
        else:
            offset = (0, 35) # to draw the board under the menu bar
        
        # check if the menu is hovered
        ui_hovered = False
        if sett.active or menu_rect.collidepoint(mouse_pos):
            ui_hovered = True
        elif dc.expanded:
            if dc.is_hovered_exp():
                ui_hovered = True
        
        # get the hovered tile
        if not ui_hovered:
            hovered_tile = cam.get_hovered_tile()
        else:
            hovered_tile = None
        
        # loop througth the map tile
        for y, row in enumerate(Map):
            for x, tile in enumerate(row):
                hovered = hovered_tile == tile
                
                # tile actions
                if not ui_hovered and hovered and not game_over:
                    if not tile.revealed:
                        
                        # reveal a tile
                        if not tile.flaged and (left_click or keys[pygame.K_RETURN]):
                            reveal(tile)
                            if sound:
                                r.click_sound.play()
                        
                        # flag / unflag a tile
                        elif right_click or (key_timer <= 0 and keys[pygame.K_f]):
                            key_timer = 300
                            flag(tile)
                    
                    # chord on a tile
                    elif tile.type != 0 and ((left_click and right_click) or middle_click or keys[pygame.K_SPACE]):
                        if not all([(t.revealed or t.flaged) for t in tile.neighbours]):
                            chord(tile)
                
                # render ( hovered or not ) tile background
                if not ui_hovered and hovered and not (tile.revealed and (tile.type == 0 or tile.type == -1)):
                    pygame.draw.rect(display, TILE_HOVERED_COLOR, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(display, tile.color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                
                # render revealed tile image
                if tile.revealed and tile.type != 0:
                    # render mine image
                    if tile.type == -1:
                        img = r.mine_img if TILE_SIZE == 40 else pygame.transform.scale(r.mine_img, (TILE_SIZE, TILE_SIZE))
                        display.blit(img, (x*TILE_SIZE, y*TILE_SIZE))
                    # render tile numeral
                    else:
                        blit_center(display, numbers[TILE_SIZE][tile.type], (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2))
                
                # render flag on tile
                elif tile.flaged:
                    img = flag_img if TILE_SIZE == 40 else pygame.transform.scale(flag_img, (TILE_SIZE, TILE_SIZE))
                    display.blit(img, (x*TILE_SIZE, y*TILE_SIZE))
        
        # display a cross on the safe starting tile
        if first_click and show_starting_tile:
            pygame.draw.line(display, COLOR, (safe_tile.left+3, safe_tile.top+3), (safe_tile.right-3, safe_tile.bottom-3), 3)
            pygame.draw.line(display, COLOR, (safe_tile.right-3, safe_tile.top+3), (safe_tile.left+3, safe_tile.bottom-3), 3)
        
        # update and render particles
        for p in particles:
            if p.update(dt):
                particles.remove(p)
            else:
                p.render(display)
        
        # update the camera and render the game
        cam.update()
        cam.render(win)
        
        # reset menu background
        pygame.draw.rect(win, 'black', (0, 0, WIN_SIZE[1], 35))
        
        # reset the game pressing the reload button
        if ui_hovered and left_click and reload_rect.collidepoint(mouse_pos):
            reset()
        elif key_timer <= 0 and (keys[pygame.K_F5] or (keys[pygame.K_LCTRL] and keys[pygame.K_r])):
            key_timer = 500
            reset()
        
        # update and render difficulty chooser drop-down menu
        dc.update()
        dc.render(win)
        
        # update and render settings page
        if (left_click and settings_rect.collidepoint(mouse_pos)) or (keys[pygame.K_s] and key_timer <= 0):
            sett.toggle()
            key_timer = 400
        if sett.active:
            sett.update()
            sett.render(win)
        
        # render current mines
        blit_center(win, r.font.render(str(current_mines), True, COLOR), (WIN_SIZE[0]-(80 if dc.current_diff != 'easy' else 62), 17))
        
        # render game time
        if first_click:
            start_time = time()
        if not game_over:
            img = r.font.render(str(ctime(time()-start_time)[14:19]), True, COLOR)
        else:
            img = r.font.render(str(ctime(final_time)[14:19]), True, COLOR)
        
        blit_center(win, img, (WIN_SIZE[0]/2 + (52 if dc.current_diff == 'easy' else img.get_width()/2), 17))
        
        # render menu icons
        blit_center(win, r.time_icon, (WIN_SIZE[0]/2 - (6 if dc.current_diff == 'easy' else r.time_icon.get_width()/2 + 10), 17))
        blit_center(win, r.flag_icon, (WIN_SIZE[0]-(80 if dc.current_diff != 'easy' else 55) - r.flag_icon.get_width() - 20, 17))
        win.blit(r.settings_icon, settings_rect)
        win.blit(r.reload_img, reload_rect)
        
        # display controls
        if keys[pygame.K_k] and key_timer <= 0:
            sett.show_keys()
            key_timer = 500
        
        # final screen update
        pygame.display.flip()
        
except Exception as crash:
    pygame.quit()
    raise crash
