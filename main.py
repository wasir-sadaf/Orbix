import pygame
import cv2
import random
import math
from pygame.math import Vector2
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

# ---------- CAMERA ----------
cap = cv2.VideoCapture(0)
tracker = HandTracker(WIDTH)

# ---------- GAME OBJECTS ----------
paddle = paddle_img.get_rect()
paddle.midbottom = (WIDTH // 2, HEIGHT - 20)
paddle_pos = float(paddle.centerx)

ball = ball_img.get_rect()
ball_pos = Vector2(WIDTH // 2, HEIGHT // 2)
ball_speed = [5.0, -5.0]
MAX_SPEED = 12.0
SPEED_INCREMENT = 0.5
ball_attached = True

ROWS, COLS = 5, 10
brick_w, brick_h = brick_img.get_size()
gap = 8
start_x = (WIDTH - (COLS * brick_w + (COLS - 1) * gap)) // 2

bricks = []

def reset_bricks():
    bricks.clear()
    for r in range(ROWS):
        for c in range(COLS):
            rect = brick_img.get_rect()
            rect.x = start_x + c * (brick_w + gap)
            rect.y = 60 + r * (brick_h + gap)
            bricks.append(rect)

reset_bricks()

# ---------- PARTICLES ----------
particles = []
shake_offset = Vector2(0, 0)
shake_frames = 0

def spawn_particles(pos):
    global shake_offset, shake_frames
    shake_frames = 5  # slight shake duration
    for _ in range(20):  # more particles
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        particles.append({
            'pos': Vector2(pos),
            'vel': Vector2(speed * math.cos(angle), speed * math.sin(angle)),
            'life': random.randint(25, 40),
            'size': 2,  # smaller particles
            'color': (0, 0, 0)
        })

# ---------- UI ----------
score = 0
lives = 5
font = pygame.font.SysFont("Calibri", 30)
title_font = pygame.font.SysFont("Calibri", 64)

score_box = pygame.Rect(12, 12, 180, 40)
life_box = pygame.Rect(WIDTH - 160, 12, 140, 40)

score_bg = pygame.Surface(score_box.size, pygame.SRCALPHA)
life_bg = pygame.Surface(life_box.size, pygame.SRCALPHA)
score_bg.fill((0, 0, 0, 120))
life_bg.fill((0, 0, 0, 120))

# ---------- GAME STATE ----------
running = True
game_over = False
pause = False
prev_fingers_up = True
game_started = False
show_menu = True
pause_menu = False

# ---------- BUTTON ----------
def draw_button(text, rect):
    pygame.draw.rect(screen, (230, 230, 230), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    txt = font.render(text, True, (0, 0, 0))
    screen.blit(txt, txt.get_rect(center=rect.center))

# ---------- MAIN LOOP ----------
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not show_menu and not game_over:
                pause_menu = not pause_menu

        # Main menu clicks
        if show_menu and event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.collidepoint(event.pos):
                show_menu = False
            elif exit_btn.collidepoint(event.pos):
                running = False

        # Pause menu clicks
        if pause_menu and event.type == pygame.MOUSEBUTTONDOWN:
            if cont_btn.collidepoint(event.pos):
                pause_menu = False
            elif restart_btn.collidepoint(event.pos):
                reset_bricks()
                ball_attached = True
                ball_pos = Vector2(WIDTH//2, HEIGHT//2)
                ball_speed = [5.0, -5.0]
                score = 0
                lives = 5
                game_started = False
                pause_menu = False
            elif exit_to_menu_btn.collidepoint(event.pos):
                show_menu = True
                pause_menu = False
                reset_bricks()
                score = 0
                lives = 5
                ball_attached = True
                ball_pos = Vector2(WIDTH//2, HEIGHT//2)
                ball_speed = [5.0, -5.0]
                game_started = False

        # Game over clicks
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if replay_btn.collidepoint(event.pos):
                show_menu = True
                game_over = False
            elif exit_btn.collidepoint(event.pos):
                running = False

    # ---------- DRAW ----------
    screen.blit(background, (0, 0))

    if show_menu:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(235)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))

        title_text = title_font.render("ORBIX", True, (0, 0, 0))
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 140)))

        tip_text = font.render(
            "Tip: Use good lighting so your hand is clearly visible",
            True, (0, 0, 0)
        )
        screen.blit(tip_text, tip_text.get_rect(center=(WIDTH // 2, 220)))

        start_btn = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
        exit_btn = pygame.Rect(WIDTH // 2 - 100, 370, 200, 50)

        draw_button("START", start_btn)
        draw_button("EXIT", exit_btn)

    else:
        # ---------- GAME CODE ----------
        if not game_over:
            ret, frame = cap.read()
            if ret:
                hand_x = tracker.get_x_if_two_fingers(frame)
                fingers_up = tracker.fingers_up(frame)

                if hand_x is None:
                    pause = True
                else:
                    pause = False
                    paddle_pos += (hand_x - paddle_pos) * 0.2
                    paddle.centerx = int(paddle_pos)
                    paddle.clamp_ip(screen.get_rect())

                if ball_attached and prev_fingers_up and fingers_up is False:
                    ball_attached = False
                    game_started = True
                    ball_speed = [5.0, -5.0]

                if fingers_up is not None:
                    prev_fingers_up = fingers_up

            # ---------- BALL ----------
            if ball_attached:
                ball_pos.x = paddle.centerx - ball.width // 2
                ball_pos.y = paddle.top - ball.height - 4
            else:
                if not pause:
                    ball_pos += Vector2(ball_speed)

                    if ball_pos.x <= 0 or ball_pos.x >= WIDTH - ball.width:
                        ball_speed[0] *= -1
                    if ball_pos.y <= 0:
                        ball_speed[1] *= -1

                    if ball.colliderect(paddle) and ball_speed[1] > 0:
                        ball_speed[1] *= -1

                    for brick in bricks[:]:
                        if ball.colliderect(brick):
                            bricks.remove(brick)
                            ball_speed[1] *= -1
                            score += 10
                            spawn_particles(brick.center)
                            for i in (0, 1):
                                if abs(ball_speed[i]) < MAX_SPEED:
                                    ball_speed[i] += SPEED_INCREMENT * (1 if ball_speed[i] > 0 else -1)
                            break

                    if ball_pos.y > HEIGHT:
                        lives -= 1
                        ball_attached = True
                        ball_speed = [5.0, -5.0]
                        if lives <= 0:
                            game_over = True

            ball.topleft = ball_pos

        # ---------- DRAW GAME ----------
        offset = (shake_offset.x, shake_offset.y)
        if shake_frames > 0:
            shake_offset.x = random.randint(-3, 3)
            shake_offset.y = random.randint(-3, 3)
            shake_frames -= 1
        else:
            shake_offset = Vector2(0, 0)

        for brick in bricks:
            screen.blit(brick_img, brick.move(offset))

        screen.blit(paddle_img, paddle.move(offset))
        screen.blit(ball_img, ball.move(offset))

        screen.blit(score_bg, score_box.topleft)
        screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)),
                    (score_box.x + 12, score_box.y + 9))

        screen.blit(life_bg, life_box.topleft)
        screen.blit(font.render(f"Lives: {lives}", True, (0, 0, 0)),
                    (life_box.x + 12, life_box.y + 9))

        # ---------- TEXT ----------
        text_y = 300
        if not game_started:
            line1 = font.render("Move paddle using two fingers", True, (0, 0, 0))
            line2 = font.render("Tap your fingers to launch the ball", True, (0, 0, 0))
            screen.blit(line1, line1.get_rect(center=(WIDTH // 2, text_y)))
            screen.blit(line2, line2.get_rect(center=(WIDTH // 2, text_y + 34)))
        elif pause:
            pause_text = font.render(
                "Hand not detected — show your hand to continue",
                True, (0, 0, 0)
            )
            screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, text_y)))

        # ---------- PARTICLES ----------
        for p in particles[:]:
            p['pos'] += p['vel']
            p['life'] -= 1
            pygame.draw.circle(screen, p['color'], (int(p['pos'].x)+offset[0], int(p['pos'].y)+offset[1]), p['size'])
            if p['life'] <= 0:
                particles.remove(p)

        # ---------- GAME OVER ----------
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(235)
            overlay.fill((255, 255, 255))
            screen.blit(overlay, (0, 0))

            screen.blit(font.render("GAME OVER", True, (0, 0, 0)),
                        (WIDTH // 2 - 80, HEIGHT // 2 - 60))

            replay_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
            exit_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
            draw_button("REPLAY", replay_btn)
            draw_button("EXIT", exit_btn)

        # ---------- PAUSE MENU ----------
        if pause_menu:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(235)
            overlay.fill((255, 255, 255))
            screen.blit(overlay, (0, 0))

            cont_btn = pygame.Rect(WIDTH // 2 - 100, 250, 200, 50)
            restart_btn = pygame.Rect(WIDTH // 2 - 100, 320, 200, 50)
            exit_to_menu_btn = pygame.Rect(WIDTH // 2 - 100, 390, 200, 50)

            draw_button("CONTINUE", cont_btn)
            draw_button("RESTART", restart_btn)
            draw_button("EXIT TO MENU", exit_to_menu_btn)

    pygame.display.flip()

cap.release()
pygame.quit()