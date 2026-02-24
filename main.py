import pygame
import cv2
from utils.hand_tracker import HandTracker

# ---------- INIT ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbix")
clock = pygame.time.Clock()

# ---------- LOAD ASSETS ----------
background = pygame.image.load("assets/background.png").convert()
ball_img = pygame.image.load("assets/ball.png").convert_alpha()
paddle_img = pygame.image.load("assets/paddle.png").convert_alpha()
brick_img = pygame.image.load("assets/brick.png").convert_alpha()

ball_radius = ball_img.get_width() // 2

# ---------- CAMERA ----------
cap = cv2.VideoCapture(0)
tracker = HandTracker(WIDTH)

# ---------- GAME OBJECTS ----------

# Paddle
paddle = paddle_img.get_rect()
paddle.midbottom = (WIDTH // 2, HEIGHT - 20)

# Ball
ball = ball_img.get_rect()
ball.center = (WIDTH // 2, HEIGHT // 2)
ball_speed = [5, -5]

# Bricks
bricks = []
ROWS, COLS = 5, 10
brick_w, brick_h = brick_img.get_size()
gap = 8
start_x = (WIDTH - (COLS * brick_w + (COLS - 1) * gap)) // 2

for r in range(ROWS):
    for c in range(COLS):
        rect = brick_img.get_rect()
        rect.x = start_x + c * (brick_w + gap)
        rect.y = 60 + r * (brick_h + gap)
        bricks.append(rect)

# Score
score = 0
font = pygame.font.SysFont(None, 28)

# ---------- GAME LOOP ----------
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Hand tracking
    ret, frame = cap.read()
    if ret:
        hand_x = tracker.get_x_if_two_fingers(frame)
        if hand_x is not None:
            paddle.centerx = hand_x
            paddle.clamp_ip(screen.get_rect())

    # Ball movement
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Wall collision
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed[0] *= -1
    if ball.top <= 0:
        ball_speed[1] *= -1

    # Paddle collision
    if ball.colliderect(paddle) and ball_speed[1] > 0:
        ball_speed[1] *= -1

    # Brick collision
    for brick in bricks[:]:
        if ball.colliderect(brick):
            bricks.remove(brick)
            ball_speed[1] *= -1
            score += 10
            break

    # Ball lost
    if ball.top > HEIGHT:
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed = [5, -5]

    # ---------- DRAW ----------
    screen.blit(background, (0, 0))
    screen.blit(paddle_img, paddle)
    screen.blit(ball_img, ball)

    for brick in bricks:
        screen.blit(brick_img, brick)

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

# ---------- CLEANUP ----------
cap.release()
pygame.quit()