import pygame
from pygame import *
from random import randint
import time as duration

init()
win_height = 500
win_width = 700
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load("Background.png"), (win_width, win_height))
clock = pygame.time.Clock()
start_time = duration.time()

f = font.SysFont("arial", 22, True)

# ---------- ukuran petak di lawn ----------
grid_x = 130
grid_y = 130
cell_w = 60
cell_h = 70
cols = 6
rows = 5
zombie_step = 4     # zombie maju 1 pixel tiap 4 frame (makin besar = makin lambat)


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Zombie(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y):
        super().__init__(player_image, player_x, player_y, size_x, size_y)
        self.step = 0
        self.health = 100

    def update(self):
        # jalan cuma kalau di depannya kosong (kalau ada tanaman, dia berhenti makan)
        if len(sprite.spritecollide(self, plants, False)) == 0:
            self.step += 1
            if self.step >= zombie_step:
                self.step = 0
                self.rect.x -= 1


class Pea(GameSprite):
    def update(self):
        self.rect.x += 5
        if self.rect.x > win_width:
            self.kill()


class Plant(GameSprite):
    def __init__(self, card, x, y, cell):
        super().__init__(card["image"], x, y, 55, 55)
        self.card = card
        self.cell = cell
        self.wait = card["rate"]
        self.health = 100

    def update(self):
        self.wait -= 1
        if self.wait <= 0:
            self.wait = self.card["rate"]
            if self.card["name"] == "Dora":
                global sun
                sun += 25
            else:
                peas.add(Pea("pea.png", self.rect.x + 40, self.rect.y + 15, 20, 20))


# ---------- kartu (seed bank) ----------
# cost = harga sun, rate = jeda nembak, cool = jeda kartu bisa dipakai lagi
cards = [
    {"name": "Dora", "image": "Dora.png", "cost": 50, "rate": 300, "cool": 300, "wait": 0},
    {"name": "David", "image": "David.png", "cost": 100, "rate": 60, "cool": 420, "wait": 0},
    {"name": "Snow", "image": "Snow_pea.png", "cost": 175, "rate": 90, "cool": 600, "wait": 0},
]
card_rects = []
for i in range(len(cards)):
    card_rects.append(Rect(100 + i * 70, 15, 60, 70))
    cards[i]["pic"] = transform.scale(image.load(cards[i]["image"]), (50, 50))

plants = sprite.Group()
peas = sprite.Group()
zombies = sprite.Group()
field = {}          # {(col, row): Plant}  -> isi petak
selected = -1       # kartu yang lagi dipegang, -1 = kosong
sun = 50
sun_wait = 300
zombie_wait = 300
game_over = False

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

        if e.type == MOUSEBUTTONDOWN and not game_over:
            mx, my = e.pos
            col = (mx - grid_x) // cell_w
            row = (my - grid_y) // cell_h

            if my < 90:
                # klik kartu -> pilih
                for i in range(len(cards)):
                    if card_rects[i].collidepoint(mx, my):
                        if sun >= cards[i]["cost"] and cards[i]["wait"] == 0:
                            selected = i

            elif 0 <= col < cols and 0 <= row < rows:
                if e.button == 3:
                    # klik kanan = cabut tanaman
                    if (col, row) in field:
                        field.pop((col, row)).kill()
                elif selected >= 0 and (col, row) not in field:
                    # klik kiri = tanam di petak kosong
                    card = cards[selected]
                    p = Plant(card, grid_x + col * cell_w, grid_y + row * cell_h, (col, row))
                    plants.add(p)
                    field[(col, row)] = p
                    sun -= card["cost"]
                    card["wait"] = card["cool"]
                    selected = -1

    window.blit(background, (0, 0))

    if not game_over:
        # sun jatuh sendiri pelan-pelan
        sun_wait -= 1
        current_time = duration.time()
        timer = 300 - (current_time - start_time)
        if sun_wait <= 0:
            sun_wait = 300
            sun += 25

        # zombie muncul berkala
        zombie_wait -= 1
        if zombie_wait <= 0:
            zombie_wait = 300
            zombies.add(Zombie("Zombie.png", win_width, grid_y + randint(0, rows - 1) * cell_h, 55, 70))

        # cooldown kartu
        for card in cards:
            if card["wait"] > 0:
                card["wait"] -= 1

        plants.update()
        peas.update()
        zombies.update()

        # pea kena zombie -> dua-duanya hilang
        # sprite.groupcollide(peas, zombies, True, False)
        for z in zombies:
            for p in sprite.spritecollide(z, peas, True):
                z.health -= 20
                if z.health <= 0:
                    z.kill()

        # zombie makan tanaman, atau nyampe rumah -> kalah
        for z in zombies:
            for p in sprite.spritecollide(z, plants, False):
                p.health -= 1
                if p.health <= 0:
                    field.pop(p.cell, None)
                    p.kill()
            if z.rect.x < grid_x - 40:
                game_over = True

    plants.draw(window)
    peas.draw(window)
    zombies.draw(window)

    # ---------- gambar seed bank ----------
    draw.rect(window, (120, 80, 40), (10, 8, 90 + len(cards) * 70, 84))
    window.blit(f.render("Sun", True, (255, 255, 0)), (25, 20))
    window.blit(f.render(str(sun), True, (255, 255, 0)), (25, 50))
    remaining = max(0, int(timer))
    minutes = remaining // 60000
    seconds = (remaining % 60000) // 1000
    window.blit(f.render(f"Time: {int(timer)}", True, (255, 255, 255)), (25, 80))
    for i in range(len(cards)):
        r = card_rects[i]
        draw.rect(window, (210, 190, 140), r)
        window.blit(cards[i]["pic"], (r.x + 5, r.y + 2))
        window.blit(f.render(str(cards[i]["cost"]), True, (0, 0, 0)), (r.x + 8, r.y + 48))
        if cards[i]["wait"] > 0 or sun < cards[i]["cost"]:
            dark = Surface((r.w, r.h))
            dark.set_alpha(150)
            window.blit(dark, (r.x, r.y))
        if selected == i:
            draw.rect(window, (255, 255, 0), r, 3)

    if game_over:
        window.blit(f.render("ZOMBIES ATE YOUR BRAINS!", True, (255, 0, 0)), (180, 240))

    display.update()
    clock.tick(60)
