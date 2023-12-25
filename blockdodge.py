# Import the pygame module
import pygame

# random
import random

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_r,
    K_w,
    K_a,
    K_s,
    K_d,
)
from pygame.sprite import Group

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

LIVE_COLOR = (0, 0, 128)
DEAD_COLOR = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

class HUD(pygame.sprite.Sprite):
    def __init__(self):
        super(HUD, self).__init__()

    def blit_text(self):
        font = pygame.font.Font('freesansbold.ttf', 24)
        self.text = ["Move with arrowkeys or WASD", "Press R to restart", "ESC to quit", "", f"Highscore: {player.highscore}", f"Score: {player.score}"]
        y = 0
        for line in self.text:
            surf = font.render(line, True, BLACK)
            screen.blit(surf, (0, y))
            y += 24


# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(LIVE_COLOR)
        self.rect = self.surf.get_rect(center = (25, SCREEN_HEIGHT/2))
        self.speed = 5
        self.alive: bool = True
        self.score = 0
        self.highscore = 0

    def dies(self):
        self.alive = False
        self.surf.fill(DEAD_COLOR)
    def revive(self):
        self.alive = True
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.surf.fill(LIVE_COLOR)
        self.rect.center = (25, SCREEN_HEIGHT/2)

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if self.alive:
            if pressed_keys[K_UP] or pressed_keys[K_w]:
                if self.rect.top > self.speed:
                    self.rect.move_ip(0, -self.speed)
            if pressed_keys[K_DOWN] or pressed_keys[K_s]:
                if self.rect.bottom < SCREEN_HEIGHT - self.speed:
                    self.rect.move_ip(0, self.speed)
            if pressed_keys[K_LEFT] or pressed_keys[K_a]:
                if self.rect.left > self.speed:
                   self.rect.move_ip(-self.speed, 0)
            if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
               if self.rect.right < SCREEN_WIDTH - self.speed:
                    self.rect.move_ip(self.speed, 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super(Coin, self).__init__()
        self.surf = pygame.Surface((20, 20))
        self.surf.fill(WHITE)
        pygame.draw.circle(self.surf, GOLD, (10, 10), 10)
        self.rect = self.surf.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

    def place(self):
        margin = 100
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin) 
        self.rect.center = (x, y)

    def collect(self):
        if player.alive:
            player.score += 10
            self.place()
            # print(f"Player Score: {player.score}")

# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.size = random.randint(1, 3)
        self.speed = 6 - self.size
        self.surf = pygame.Surface((10 * self.size, 5 * self.size))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

def reset():
    for entity in enemies:
        entity.kill()
    coin.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    player.revive()
    pygame.time.set_timer(ADDENEMY, 250)


# Initialize pygame
pygame.init()
# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Block Dodge')

# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

# Instantiate player. Right now, this is just a rectangle.
player = Player()
coin = Coin()
hud = HUD()

# Create groups to hold enemy sprites and all sprites
# - enemies is used for collision detection and position updates
# - all_sprites is used for rendering
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(coin)

# Variable to keep the main loop running
running = True
while running:
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_r:
                reset()
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False

        # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy and add it to sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

    # Get the set of keys pressed and check for user input
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    # Update enemy position
    enemies.update()

    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Check if any enemies have collided with the player
    if pygame.sprite.spritecollideany(player, enemies):
        player.dies()
        pygame.time.set_timer(ADDENEMY, 0)

    if pygame.sprite.collide_rect(player, coin):
        coin.collect()

    # Draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    hud.blit_text()

    # Update the display
    pygame.display.flip()

    # Ensure program maintains a rate of 30 frames per second
    clock.tick(60)