from pygame import *

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

zombie = GameSprite("Zombie.png", 100, 200, 80, 80)
david = GameSprite("David.png", 500, 200, 80, 80)
dora = GameSprite("Dora.png", 300, 200, 80, 80)
snow_pea = GameSprite("Snowe pea.png", 400, 200, 80, 80)

game_over = False

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    window.blit(background, (0, 0))
    zombie.reset()
    david.reset()
    dora.reset()
    snow_pea.reset()
    display.update()
    clock.tick(60)