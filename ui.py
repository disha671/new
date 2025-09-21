import pygame
from settings import *

# Constants for layout
MENU_WIDTH = 400
MENU_HEIGHT = 200
SWITCH_HEIGHT = 400
STATS_WIDTH = 250
STATS_HEIGHT = 80
FONT_SIZE = 30

class UI:
    def __init__(self, monster, player_monsters, simple_surfs, get_input):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.left = WINDOW_WIDTH / 2 - 100
        self.top = WINDOW_WIDTH / 2 + 50
        self.monster = monster
        self.simple_surfs = simple_surfs
        self.get_input = get_input

        # Control
        self.general_options = ["attack", "heal", "switch", "escape"]
        self.general_index = {"col": 0, "row": 0}
        self.attack_index = {"col": 0, "row": 0}
        self.state = "general"
        self.rows, self.cols = 2, 2
        self.visible_monsters = 4
        self.player_monsters = player_monsters
        self.available_monsters = [m for m in self.player_monsters if m != self.monster and m.health > 0]
        self.switch_index = 0

    def input(self):
        keys = pygame.key.get_just_pressed()
        if self.state == "general":
            self.general_index["row"] = (self.general_index["row"] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.general_index["col"] = (self.general_index["col"] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) % self.cols
            if keys[pygame.K_SPACE]:
                self.state = self.general_options[self.general_index["col"] + self.general_index["row"] * self.cols]

        elif self.state == 'attack':
            self.attack_index["row"] = (self.attack_index["row"] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.attack_index["col"] = (self.attack_index["col"] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) % self.cols
            if keys[pygame.K_SPACE]:
                i = self.attack_index["col"] + self.attack_index["row"] * self.cols
                if i < len(self.monster.abilities):
                    attack = self.monster.abilities[i]
                    self.get_input(self.state, attack)
                    self.state = "general"

        elif self.state == 'switch':
            if self.available_monsters:
                self.switch_index = (self.switch_index + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % len(self.available_monsters)
                if keys[pygame.K_SPACE]:
                    self.get_input(self.state, self.available_monsters[self.switch_index])
                    self.state = "general"

        elif self.state == "heal":
            self.get_input("heal")
            self.state = "general"

        elif self.state == "escape":
            self.get_input('escape')

        if keys[pygame.K_ESCAPE]:
            self.state = "general"
            self.general_index = {"col": 0, "row": 0}
            self.attack_index = {"col": 0, "row": 0}
            self.switch_index = 0

    def quad_select(self, index, options):
        rect = pygame.FRect(self.left + 40, self.top + 60, MENU_WIDTH, MENU_HEIGHT)
        pygame.draw.rect(self.display_surface, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], rect, 4, 4)

        for col in range(self.cols):
            for row in range(self.rows):
                x = rect.left + rect.width / (self.cols * 2) + (rect.width / self.cols) * col
                y = rect.top + rect.height / (self.rows * 2) + (rect.height / self.rows) * row
                i = col + self.cols * row
                if i < len(options):
                    color = COLORS["gray"] if col == index['col'] and row == index["row"] else COLORS["black"]
                    text_surf = self.font.render(options[i], True, color)
                    text_rect = text_surf.get_frect(center=(x, y))
                    self.display_surface.blit(text_surf, text_rect)

    def switch(self):
        rect = pygame.FRect(self.left + 40, self.top - 140, MENU_WIDTH, SWITCH_HEIGHT)
        pygame.draw.rect(self.display_surface, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], rect, 4, 4)

        v_offset = 0 if self.switch_index < self.visible_monsters else -(self.switch_index - self.visible_monsters + 1) * rect.height / self.visible_monsters
        for i, monster in enumerate(self.available_monsters):
            x = rect.centerx
            y = rect.top + rect.height / (self.visible_monsters * 2) + rect.height / self.visible_monsters * i + v_offset
            color = COLORS["gray"] if i == self.switch_index else COLORS["black"]
            name = monster.name
            simple_surf = self.simple_surfs.get(name)
            if simple_surf:
                simple_rect = simple_surf.get_frect(center=(x - 100, y))
                text_surf = self.font.render(name, True, color)
                text_rect = text_surf.get_frect(midleft=(x, y))
                if rect.collidepoint(text_rect.center):
                    self.display_surface.blit(text_surf, text_rect)
                    self.display_surface.blit(simple_surf, simple_rect)

    def stats(self):
        rect = pygame.FRect(self.left, self.top, STATS_WIDTH, STATS_HEIGHT)
        pygame.draw.rect(self.display_surface, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], rect, 4, 4)

        name_surf = self.font.render(self.monster.name, True, COLORS['black'])
        name_rect = name_surf.get_frect(topleft=rect.topleft + pygame.Vector2(rect.width * 0.05, 12))
        self.display_surface.blit(name_surf, name_rect)

        health_rect = pygame.FRect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
        pygame.draw.rect(self.display_surface, COLORS["gray"], health_rect)
        self.draw_bar(health_rect, self.monster.health, self.monster.max_health)

    def draw_bar(self, rect, value, max_value):
        value = min(value, max_value)
        ratio = rect.width / max_value
        progress_rect = pygame.FRect(rect.topleft, (value * ratio, rect.height))
        pygame.draw.rect(self.display_surface, COLORS["red"], progress_rect)

    def update(self):
        self.input()
        self.available_monsters = [m for m in self.player_monsters if m != self.monster and m.health > 0]

    def draw(self):
        match self.state:
            case 'general': self.quad_select(self.general_index, self.general_options)
            case 'attack': self.quad_select(self.attack_index, self.monster.abilities)
            case 'switch': self.switch()
        if self.state != "switch":
            self.stats()

class OpponentUI:
    def __init__(self, monster):
        self.display_surface = pygame.display.get_surface()
        self.monster = monster
        self.font = pygame.font.Font(None, FONT_SIZE)

    def draw(self):
        rect = pygame.FRect((0, 0), (STATS_WIDTH, STATS_HEIGHT)).move_to(midleft=(500, self.monster.rect.centery))
        pygame.draw.rect(self.display_surface, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], rect, 4, 4)

        name_surf = self.font.render(self.monster.name, True, COLORS["black"])
        name_rect = name_surf.get_frect(topleft=pygame.Vector2(rect.width * 0.05, 12))
        self.display_surface.blit(name_surf, name_rect)

        health_rect = pygame.FRect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
        pygame.draw.rect(self.display_surface, COLORS["gray"], health_rect)
        value = min(self.monster.health, self.monster.max_health)
        ratio = health_rect.width / self.monster.max_health
        progress_rect = pygame.FRect(health_rect.topleft, (value * ratio, health_rect.height))
        pygame.draw.rect(self.display_surface, COLORS["red"], progress_rect)
