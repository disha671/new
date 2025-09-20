import pygame
import random
import sys
import os

# ==========================
#  LOGIN & REGISTER SYSTEM
# ==========================

USER_FILE = "users.txt"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    users = {}
    with open(USER_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) == 7:
                username, password, wins, losses = parts
                users[username] = {"password": password, "wins": int(wins), "losses": int(losses)}
    return users

def save_users(users):
    with open(USER_FILE, "w") as f:
        for username, data in users.items():
            f.write(f"{username}:{data['password']}:{data['wins']}:{data['losses']}\n")

class InputBox:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (200, 200, 200)
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, (0, 0, 0))
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (50, 100, 255) if self.active else (200, 200, 200)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, (0, 0, 0))

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text

def login_register(screen, font, WIDTH, HEIGHT):
    username_box = InputBox(300, 200, 300, 50, font)
    password_box = InputBox(300, 260, 300, 50, font)
    message = ""
    mode = "login"
    users = load_users()

    def draw_text(text, x, y, color=(0, 0, 0), center=False):
        txt_surface = font.render(text, True, color)
        if center:
            screen.blit(txt_surface, (x - txt_surface.get_width() // 2, y))
        else:
            screen.blit(txt_surface, (x, y))

    while True:
        screen.fill((255, 255, 255))
        draw_text(f"{mode.capitalize()} Page", WIDTH//2, 100, (50, 100, 255), center=True)
        draw_text("Username: ", 100, 210)
        draw_text("Password: ", 100, 270)

        username_box.draw(screen)
        password_box.draw(screen)

        draw_text("Press ENTER to submit", WIDTH//2, 400, (0, 0, 0), center=True)
        draw_text("Press TAB to switch Login/Register", WIDTH//2, 440, (0, 0, 0), center=True)
        draw_text(message, WIDTH//2, 500, (200, 0, 0), center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            username_box.handle_event(event)
            password_box.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    mode = "register" if mode == "login" else "login"
                    message = ""
                if event.key == pygame.K_RETURN:
                    username = username_box.get_text()
                    password = password_box.get_text()
                    if username == "" or password == "":
                        message = "Fields cannot be empty!"
                    elif mode == "login":
                        if username in users and users[username]["password"] == password:
                            return username, users  # success
                        else:
                            message = "Invalid username or password!"
                    elif mode == "register":
                        if username in users:
                            message = "Username already exists!"
                        else:
                            users[username] = {"password": password, "wins": 0, "losses": 0}
                            save_users(users)
                            message = "Registered successfully! Press TAB for Login."

        pygame.display.flip()

# ==========================
#  GAME SECTION
# ==========================

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Pokémon Battle")

WHITE = (255, 255, 255)
BLUE = (0, 0, 200)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

player_size = 50
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5

player_img = pygame.image.load("player.png")
monster_img = pygame.image.load("monster1.png")
player_img = pygame.transform.scale(player_img, (60, 60))
monster_img = pygame.transform.scale(monster_img, (120, 120))

in_battle = False
monster_hp = 100
player_hp = 100
battle_message = ""
show_leaderboard = False
show_home = True  # NEW: Start from home

def draw_text(text, x, y, color=BLACK, center=False):
    txt_surface = font.render(text, True, color)
    if center:
        screen.blit(txt_surface, (x - txt_surface.get_width() // 2, y))
    else:
        screen.blit(txt_surface, (x, y))

def draw_bar(x, y, hp, max_hp, color):
    bar_width = 200
    bar_height = 20
    ratio = max(hp, 0) / max_hp
    pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
    pygame.draw.rect(screen, color, (x, y, bar_width * ratio, bar_height))

def draw_button(text, x, y, w, h, mouse_pos, click, color=(0, 150, 255), hover_color=(0, 200, 200)):
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    txt_surface = font.render(text, True, (0, 0, 0))
    screen.blit(txt_surface, (x + (w - txt_surface.get_width()) // 2, y + (h - txt_surface.get_height()) // 2))
    return False

def start_battle():
    global in_battle, monster_hp, player_hp, battle_message
    in_battle = True
    monster_hp = 100
    player_hp = 100
    battle_message = "A wild monster appeared!"

def battle_turn():
    global monster_hp, player_hp, battle_message, users, current_user
    player_attack = random.randint(10, 30)
    monster_attack = random.randint(5, 25)

    monster_hp -= player_attack
    if monster_hp <= 0:
        battle_message = f"You dealt {player_attack} damage! Monster fainted!"
        users[current_user]["wins"] += 1
        save_users(users)
        return

    player_hp -= monster_attack
    if player_hp <= 0:
        battle_message = f"Monster hit {monster_attack} damage! You fainted!"
        users[current_user]["losses"] += 1
        save_users(users)
        return

    battle_message = f"You hit {player_attack}, Monster hit {monster_attack}!"

def draw_leaderboard(users):
    screen.fill((230, 230, 255))
    draw_text("🏆 Leaderboard 🏆", WIDTH // 2, 50, BLUE, center=True)

    sorted_users = sorted(users.items(), key=lambda x: x[1]["wins"], reverse=True)

    y_offset = 120
    for i, (username, data) in enumerate(sorted_users[:10], start=1):
        draw_text(f"{i}. {username} - Wins: {data['wins']} | Losses: {data['losses']}", WIDTH//2, y_offset, BLACK, center=True)
        y_offset += 40

    draw_text("Press ESC to return", WIDTH//2, HEIGHT - 60, RED, center=True)

# Run login/register first
current_user, users = login_register(screen, font, WIDTH, HEIGHT)

# ==========================
#  MAIN GAME LOOP
# ==========================
running = True
while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if show_home:
        # Home Screen
        draw_text(f"Welcome, {current_user}!", WIDTH // 2, 100, BLUE, center=True)
        draw_text(f"Wins: {users[current_user]['wins']}   Losses: {users[current_user]['losses']}", WIDTH // 2, 150, BLACK, center=True)

        if draw_button("▶ START GAME", WIDTH//2 - 100, 250, 200, 60, mouse_pos, click):
            show_home = False  # go to explore mode

        if draw_button("🏆 LEADERBOARD", WIDTH//2 - 100, 350, 200, 60, mouse_pos, click):
            show_leaderboard = True
            show_home = False

        if draw_button("❌ QUIT", WIDTH//2 - 100, 450, 200, 60, mouse_pos, click, color=(200,0,0), hover_color=(255,0,0)):
            running = False

    elif show_leaderboard:
        draw_leaderboard(users)
        if keys[pygame.K_ESCAPE]:
            show_leaderboard = False
            show_home = True

    elif not in_battle:
        if keys[pygame.K_LEFT]: player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]: player_pos[0] += player_speed
        if keys[pygame.K_UP]: player_pos[1] -= player_speed
        if keys[pygame.K_DOWN]: player_pos[1] += player_speed

        player_pos[0] = max(0, min(WIDTH - player_size, player_pos[0]))
        player_pos[1] = max(0, min(HEIGHT - player_size, player_pos[1]))
        

        if random.randint(0, 100) < 2:
            start_battle()

        screen.blit(player_img, player_pos)
        draw_text("Explore to find monsters!", 20, 20, GREEN)
        draw_text("Press ESC to return Home", 20, 60, RED)

        if keys[pygame.K_ESCAPE]:
            show_home = True

    else:
        screen.fill((150, 180, 255))

        monster_x = WIDTH // 2 - 150
        monster_y = HEIGHT // 2 - 180
        screen.blit(monster_img, (monster_x, monster_y))

        player_x = WIDTH // 2 - 30
        player_y = HEIGHT // 2 + 120
        screen.blit(player_img, (player_x, player_y))

        draw_text("Monster HP", 50, 50, RED)
        draw_bar(200, 50, monster_hp, 100, RED)

        draw_text("Your HP", 50, 100, BLUE)
        draw_bar(200, 100, player_hp, 100, BLUE)

        draw_text(battle_message, WIDTH // 2, HEIGHT // 2, YELLOW, center=True)

        if player_hp > 0 and monster_hp > 0:
            draw_text("Press SPACE to attack!", WIDTH // 2, HEIGHT - 80, GREEN, center=True)

        if keys[pygame.K_SPACE] and player_hp > 0 and monster_hp > 0:
            battle_turn()
            pygame.time.wait(500)

        if monster_hp <= 0:
            draw_text("You WON! 🎉 (Press R to restart)", WIDTH // 2, HEIGHT - 50, GREEN, center=True)
        elif player_hp <= 0:
            draw_text("You LOST 💀 (Press R to restart)", WIDTH // 2, HEIGHT - 50, RED, center=True)

        if keys[pygame.K_r] and (monster_hp <= 0 or player_hp <= 0):
            in_battle = False

    pygame.display.flip()
    clock.tick(30)
    # Load tile map
map_img = pygame.image.load("map.png").convert()
map_width, map_height = map_img.get_size()

# Camera position (for scrolling if map > screen size)
camera_x, camera_y = 0, 0


pygame.quit()
sys.exit()
