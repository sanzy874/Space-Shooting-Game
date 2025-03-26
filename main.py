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
MAX_HEALTH = 5
WAVE_SIZE = 2 
ENEMY_ZIGZAG_SPEED = 6
ENEMY_ZIGZAG_RANGE = 70

# Power-up settings
POWERUP_SPAWN_RATE = 250  # 1 in 300 chance per frame
POWERUP_SIZE = (40, 40)
FIRE_RATE_DURATION = 5000  # in milliseconds
SHIELD_DURATION = 5000

# Bullet cooldown settings
default_bullet_cooldown = 500  # milliseconds
bonus_bullet_cooldown = 200

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

# Power-up images
fire_rate_img = pygame.image.load("assets/fire_rate.png")
fire_rate_img = pygame.transform.scale(fire_rate_img, POWERUP_SIZE)
shield_img = pygame.image.load("assets/shield.png")
shield_img = pygame.transform.scale(shield_img, POWERUP_SIZE)

# Player Setup
player_x, player_y = 100, HEIGHT // 2
player_rect = pygame.Rect(player_x, player_y, 70, 70)
bullets = []
score = 0
health = MAX_HEALTH
wave_count = 1

# Power-ups
powerups = []

# Bonus timers and shooting cooldown
fire_rate_bonus_end_time = 0
shield_end_time = 0
last_bullet_time = 0
bullet_cooldown = default_bullet_cooldown

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
        enemies.append({'rect': pygame.Rect(x, y, 70, 70),
                        'direction': direction,
                        'start_y': y})
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
            # If enemy passes, reduce health (unless shield is active)
            if pygame.time.get_ticks() > shield_end_time:
                health -= 1
    enemies = new_enemies

# Power-up functions
def spawn_powerup():
    p_type = random.choice(["fire_rate", "shield"])
    x = random.randint(WIDTH, WIDTH + 100)
    y = random.randint(50, HEIGHT - 50)
    rect = pygame.Rect(x, y, POWERUP_SIZE[0], POWERUP_SIZE[1])
    powerups.append({'rect': rect, 'type': p_type})

def move_powerups():
    global powerups
    for p in powerups:
        p['rect'].x -= ENEMY_SPEED
    powerups = [p for p in powerups if p['rect'].x > 0]

def draw_powerups():
    for p in powerups:
        if p['type'] == "fire_rate":
            screen.blit(fire_rate_img, (p['rect'].x, p['rect'].y))
        elif p['type'] == "shield":
            screen.blit(shield_img, (p['rect'].x, p['rect'].y))

# Collision Detection for enemies and bullets
def check_collisions():
    global bullets, enemies, score
    explosions = []
    bullets_to_remove = []
    enemies_to_remove = []
    
    for enemy in enemies:
        for bullet in bullets:
            if enemy['rect'].colliderect(bullet):
                explosions.append((enemy['rect'].x, enemy['rect'].y))
                score += 1
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

# Collision Detection for powerups
def check_powerup_collision():
    global powerups, fire_rate_bonus_end_time, shield_end_time, bullet_cooldown
    player_rect.update(player_x, player_y, 70, 70)
    collected = []
    current_time = pygame.time.get_ticks()
    for p in powerups:
        if player_rect.colliderect(p['rect']):
            if p['type'] == "fire_rate":
                fire_rate_bonus_end_time = current_time + FIRE_RATE_DURATION
                bullet_cooldown = bonus_bullet_cooldown
            elif p['type'] == "shield":
                shield_end_time = current_time + SHIELD_DURATION
            collected.append(p)
    for p in collected:
        if p in powerups:
            powerups.remove(p)

# Collision Detection for player and enemies
def check_player_collision():
    global health, enemies, score
    player_rect.update(player_x, player_y, 70, 70)
    remaining_enemies = []
    current_time = pygame.time.get_ticks()
    for enemy in enemies:
        if player_rect.colliderect(enemy['rect']):
            if current_time < shield_end_time:
                score += 1
            else:
                health -= 1
            # Enemy is removed in either case
        else:
            remaining_enemies.append(enemy)
    enemies[:] = remaining_enemies

# Draw Functions
def draw_background():
    screen.blit(background_img, (0, 0))

def draw_player(x, y):
    screen.blit(player_img, (x, y))
    # If shield is active, draw a blue overlay
    if pygame.time.get_ticks() < shield_end_time:
        shield_overlay = pygame.Surface((70, 70), pygame.SRCALPHA)
        shield_overlay.fill((0, 0, 255, 100))
        screen.blit(shield_overlay, (x, y))

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
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

def show_game_over():
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.delay(3000)

# Game Loop
running = True
spawn_wave()
while running:
    pygame.time.delay(30)
    current_time = pygame.time.get_ticks()
    if current_time > fire_rate_bonus_end_time:
        bullet_cooldown = default_bullet_cooldown

    draw_background()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # In default mode, fire on keydown events (one shot per press)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and current_time >= fire_rate_bonus_end_time:
                bullets.append(pygame.Rect(player_x + 50, player_y + 30, 30, 15))
                last_bullet_time = current_time

    keys = pygame.key.get_pressed()
    if current_time < fire_rate_bonus_end_time:
        # When fire_rate bonus is active, allow continuous shooting while holding space
        if keys[pygame.K_SPACE]:
            if current_time - last_bullet_time >= bullet_cooldown:
                bullets.append(pygame.Rect(player_x + 50, player_y + 30, 30, 15))
                last_bullet_time = current_time

    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 70:
        player_x += PLAYER_SPEED
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] and player_y < HEIGHT - 70:
        player_y += PLAYER_SPEED

    if random.randint(1, POWERUP_SPAWN_RATE) == 1:
        spawn_powerup()

    if not enemies:
        spawn_wave()

    move_bullets()
    move_enemies()
    move_powerups()
    explosions = check_collisions()
    check_powerup_collision()
    check_player_collision()

    draw_player(player_x, player_y)
    draw_bullets()
    draw_enemies()
    draw_powerups()
    draw_explosions(explosions)
    draw_score()
    draw_health()

    pygame.display.update()

    if health <= 0:
        running = False

show_game_over()
pygame.quit()
