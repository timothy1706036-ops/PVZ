from pygame import *
from random import randint

back = (200, 255, 255)
win_height = 500
win_width = 700
background = transform.scale(image.load("Background.png"), (800, 600))

window = display.set_mode((win_width, win_height))
window.fill(back)
window.blit(background, (0, 0))
clock = time.Clock()

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
    def update(self):
        self.rect.x -= 1
        if self.rect.x < 0:
            self.rect.x = win_width

class Bullet(GameSprite):
    def fire(self):
        pea = Pea("pea.png", self.rect.x, self.rect.y, 20, 20)
        peas.add(pea)

class Pea(GameSprite):
    def update(self):
        self.rect.x += 1
        if self.rect.x > win_width:
            self.kill()


david = Bullet("David.png", 500, 200, 80, 80)
dora = GameSprite("Dora.png", 300, 200, 80, 80)
snow_pea = Pea("Snow_pea.png", 400, 200, 80, 80)

peas = sprite.Group()
zombies = sprite.Group()
zombie_min = 1
zombie_max = 5
for i in range(randint(zombie_min, zombie_max)):
    zombie = Zombie("Zombie.png", randint(700, 800), randint(100, 400), 80, 80)
    zombies.add(zombie)

game_over = False

wait_pea = 0
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    window.blit(background, (0, 0))
    zombies.draw(window)
    zombies.update()
    david.reset()
    dora.reset()
    snow_pea.reset()
    peas.draw(window)
    peas.update()

    if wait_pea == 0:
        david.fire()
        wait_pea = 30
    else:
        wait_pea -= 1





    display.update()
    clock.tick(60)