import pygame
import random

# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 2
WHITE = (255, 255, 255)
MAX_HEALTH = 3
WAVE_SIZE = 5
ENEMY_ZIGZAG_SPEED = 3
ENEMY_ZIGZAG_RANGE = 50

# Create Game Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load Assets
background_img = pygame.image.load("assets/background.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

player_img = pygame.image.load("assets/player.png")
player_img = pygame.transform.scale(player_img, (70, 70))

enemy_img = pygame.image.load("assets/enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (70, 70))

bullet_img = pygame.image.load("assets/bullet.png")
bullet_img = pygame.transform.scale(bullet_img, (30, 15))

explosion_img = pygame.image.load("assets/explosion.png")
explosion_img = pygame.transform.scale(explosion_img, (70, 70))

# Player Setup
player_x, player_y = 100, HEIGHT // 2
bullets = []
score = 0
health = MAX_HEALTH
wave_count = 1

def draw_health():
    font = pygame.font.Font(None, 36)
    health_text = font.render(f"Health: {health}", True, (255, 0, 0))
    screen.blit(health_text, (WIDTH - 150, 10))

# Enemy Setup
enemies = []

def spawn_wave():
    global wave_count
    for _ in range(WAVE_SIZE * wave_count):
        x = random.randint(WIDTH, WIDTH + 100)
        y = random.randint(50, HEIGHT - 50)
        direction = random.choice([-1, 1])
        enemies.append({'rect': pygame.Rect(x, y, 70, 70), 'direction': direction, 'start_y': y})
    wave_count += 1

def draw_enemies():
    for enemy in enemies:
        screen.blit(enemy_img, (enemy['rect'].x, enemy['rect'].y))

def move_enemies():
    global health, enemies
    new_enemies = []
    for enemy in enemies:
        enemy['rect'].x -= ENEMY_SPEED
        enemy['rect'].y += enemy['direction'] * ENEMY_ZIGZAG_SPEED
        
        # Reverse direction if enemy moves beyond zig-zag range
        if abs(enemy['rect'].y - enemy['start_y']) > ENEMY_ZIGZAG_RANGE:
            enemy['direction'] *= -1
        
        if enemy['rect'].x > 0:
            new_enemies.append(enemy)
        else:
            health -= 1  # Reduce health if enemy reaches the left side
    enemies = new_enemies

# Collision Detection
def check_collisions():
    global bullets, enemies, score
    explosions = []
    bullets_to_remove = []
    enemies_to_remove = []
    
    for enemy in enemies:
        for bullet in bullets:
            if enemy['rect'].colliderect(bullet):
                explosions.append((enemy['rect'].x, enemy['rect'].y))
                score += 10
                bullets_to_remove.append(bullet)
                enemies_to_remove.append(enemy)
                break
    
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
    
    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)
    
    return explosions

# Draw Functions
def draw_background():
    screen.blit(background_img, (0, 0))

def draw_player(x, y):
    screen.blit(player_img, (x, y))

def draw_bullets():
    for bullet in bullets:
        screen.blit(bullet_img, (bullet.x, bullet.y))

def move_bullets():
    for bullet in bullets:
        bullet.x += BULLET_SPEED
    
    bullets[:] = [bullet for bullet in bullets if bullet.x < WIDTH]

def draw_explosions(explosions):
    for x, y in explosions:
        screen.blit(explosion_img, (x, y))

def draw_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # Changed to white
    screen.blit(score_text, (10, 10))

# Game Loop
running = True
spawn_wave()
while running:
    pygame.time.delay(30)
    draw_background()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player_x + 50, player_y + 30, 30, 15))
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 70:
        player_x += PLAYER_SPEED
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] and player_y < HEIGHT - 70:
        player_y += PLAYER_SPEED
    
    if not enemies:
        spawn_wave()
    
    move_bullets()
    move_enemies()
    explosions = check_collisions()
    
    draw_player(player_x, player_y)
    draw_bullets()
    draw_enemies()
    draw_explosions(explosions)
    draw_score()
    draw_health()
    
    pygame.display.update()
    
    if health <= 0:
        running = False

pygame.quit()
