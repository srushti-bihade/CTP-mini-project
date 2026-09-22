import pygame
import random
import time
import os
import math

pygame.init()

# ================= SOUND =================
try:
    pygame.mixer.init()
    sound_on = True
except:
    sound_on = False

# 🔊 LOAD SOUNDS (FIXED)
click = None
correct = None
wrong = None

if sound_on:
    if os.path.exists("assets/click.wav"):
        click = pygame.mixer.Sound("assets/click.wav")

    if os.path.exists("assets/correct.wav"):
        correct = pygame.mixer.Sound("assets/correct.wav")

    if os.path.exists("assets/wrong.wav"):
        wrong = pygame.mixer.Sound("assets/wrong.wav")

    if os.path.exists("assets/bg.mp3"):
        pygame.mixer.music.load("assets/bg.mp3")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

# ================= FULLSCREEN =================
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Memory Rush")

clock = pygame.time.Clock()

# ================= COLORS =================
WHITE = (255,255,255)
GREEN = (0,255,160)
RED = (255,80,80)
BLUE = (80,180,255)
YELLOW = (255,220,100)
DARK = (10,10,20)

# ================= FONTS =================
font = pygame.font.SysFont("arial", 26)
big = pygame.font.SysFont("arial", 52, bold=True)
title_font = pygame.font.SysFont("arial", 90, bold=True)

cx, cy = WIDTH//2, HEIGHT//2

# ================= SCORE =================
def load_high():
    if os.path.exists("highscore.txt"):
        return int(open("highscore.txt").read())
    return 0

def save_high(s):
    with open("highscore.txt", "w") as f:
        f.write(str(s))

high_score = load_high()
last_score = 0

# ================= GAME STATE =================
state = "home"

level = 1
score = 0
lives = 3

sequence = []
user_input = ""
phase = "idle"
timer = 0
result = False

# ================= SAFE SCORE SAVE =================
def save_last_score():
    global last_score
    last_score = score

# ================= PARTICLES =================
particles = []

for _ in range(120):
    particles.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1,3)
    ])

def update_particles():
    for p in particles:
        p[1] += p[2]
        if p[1] > HEIGHT:
            p[0] = random.randint(0, WIDTH)
            p[1] = 0

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen, (120,180,255), (int(p[0]), int(p[1])), p[2])

# ================= FLOATING NUMBERS =================
numbers = []

for _ in range(25):
    numbers.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(0,9),
        random.uniform(0.5,1.5)
    ])

def update_numbers():
    for n in numbers:
        n[1] -= n[3]
        n[0] += math.sin(time.time()*2 + n[2]) * 0.5
        if n[1] < -20:
            n[1] = HEIGHT + 20
            n[0] = random.randint(0, WIDTH)
            n[2] = random.randint(0,9)

def draw_numbers():
    t = time.time()
    for n in numbers:
        glow = int(120 + 100 * math.sin(t*2))
        text = font.render(str(n[2]), True, (0, glow, 255))
        screen.blit(text, (int(n[0]), int(n[1])))

# ================= TITLE =================
def animated_title(text, x, y):
    t = time.time()
    float_y = y + math.sin(t * 2) * 12
    glow = int(120 + 135 * (0.5 + 0.5 * math.sin(t * 3)))

    for i in range(6, 0, -1):
        glow_text = title_font.render(text, True, (0, glow, 255))
        screen.blit(glow_text, (x-i, float_y-i))
        screen.blit(glow_text, (x+i, float_y+i))

    main = title_font.render(text, True, WHITE)
    screen.blit(main, (x, float_y))

# ================= BUTTON =================
def button(text,x,y,w,h,color):
    rect = pygame.Rect(x,y,w,h)

    hover = rect.collidepoint(pygame.mouse.get_pos())
    c = tuple(min(v+40,255) for v in color) if hover else color

    pygame.draw.rect(screen,c,rect,border_radius=14)
    pygame.draw.rect(screen,(255,255,255,30),rect,1,border_radius=14)

    txt = font.render(text,True,WHITE)
    screen.blit(txt,(x+w//2-txt.get_width()//2,y+h//2-txt.get_height()//2))
    return rect

# ================= CARD =================
def card(x,y,w,h):
    rect = pygame.Rect(x,y,w,h)
    pygame.draw.rect(screen,(25,25,45),rect,border_radius=20)
    pygame.draw.rect(screen,(120,200,255),rect,2,border_radius=20)
    return rect

# ================= ROUND =================
def new_round():
    global sequence, user_input, phase, timer
    sequence = [random.randint(0,9) for _ in range(level)]
    user_input = ""
    phase = "show"
    timer = time.time()

# ================= LOOP =================
running = True

while running:

    screen.fill(DARK)

    update_particles()
    draw_particles()

    overlay = pygame.Surface((WIDTH,HEIGHT))
    overlay.set_alpha(140)
    overlay.fill((0,0,0))
    screen.blit(overlay,(0,0))

    # ================= HOME =================
    if state == "home":

        update_numbers()
        draw_numbers()

        animated_title("MEMORY RUSH", cx-300, 120)

        start_btn = button("START",cx-100,cy-60,200,50,GREEN)
        score_btn = button("SCORES",cx-100,cy+10,200,50,YELLOW)
        quit_btn = button("QUIT",cx-100,cy+80,200,50,RED)

    # ================= LEADERBOARD =================
    elif state == "leaderboard":

        screen.blit(big.render("LEADERBOARD",True,YELLOW),(cx-180,120))
        screen.blit(font.render(f"Last Score: {last_score}",True,WHITE),(cx-140,220))
        screen.blit(font.render(f"High Score: {high_score}",True,YELLOW),(cx-140,270))

        back_btn = button("BACK",cx-100,cy+100,200,50,GREEN)

    # ================= GAME =================
    elif state == "game":

        now = time.time() - timer

        time_left = max(0, int(10 - now))
        timer_color = RED if time_left <= 3 else YELLOW
        timer_text = font.render(f"TIME: {time_left}s", True, timer_color)
        screen.blit(timer_text, (WIDTH - 180, 60))

        exit_btn = button("EXIT",WIDTH-160,20,120,40,RED)

        card(20,20,300,150)
        screen.blit(font.render(f"LEVEL {level}",True,YELLOW),(40,50))
        screen.blit(font.render(f"SCORE {score}",True,GREEN),(40,90))
        screen.blit(font.render(f"LIVES {'❤'*lives}",True,RED),(40,130))

        card(cx-250,cy-120,500,260)

        title = "MEMORIZE" if phase=="show" else "ENTER" if phase=="input" else "RESULT"
        screen.blit(big.render(title,True,BLUE),(cx-90,cy-100))

        if phase == "show":
            seq = "   ".join(map(str,sequence))
            screen.blit(big.render(seq,True,WHITE),(cx-120,cy))
            if now > 0.5:
                phase = "input"
                timer = time.time()

        elif phase == "input":
            box = pygame.Rect(cx-150,cy-20,300,60)
            pygame.draw.rect(screen,(40,40,70),box,border_radius=10)
            screen.blit(big.render(user_input,True,WHITE),(cx-130,cy-15))

            if now > 10:
                lives -= 1
                result = False
                if wrong: wrong.play()
                phase = "result"
                timer = time.time()

        elif phase == "result":
            msg = "CORRECT!" if result else "WRONG!"
            col = GREEN if result else RED
            screen.blit(big.render(msg,True,col),(cx-120,cy))

            if now > 2:
                if lives <= 0:
                    save_last_score()

                    if score > high_score:
                        high_score = score
                        save_high(score)

                    state = "home"
                else:
                    if result:
                        score += level*10
                        level += 1
                        if correct: correct.play()
                    new_round()

    # ================= EVENTS =================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            save_last_score()
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state = "home"

        if event.type == pygame.MOUSEBUTTONDOWN:

            if state == "home":
                if start_btn.collidepoint(event.pos):
                    if click: click.play()
                    level,score,lives = 1,0,3
                    new_round()
                    state = "game"

                if score_btn.collidepoint(event.pos):
                    if click: click.play()
                    state = "leaderboard"

                if quit_btn.collidepoint(event.pos):
                    if click: click.play()
                    save_last_score()
                    running = False

            elif state == "leaderboard":
                if back_btn.collidepoint(event.pos):
                    if click: click.play()
                    state = "home"

            elif state == "game":
                if exit_btn.collidepoint(event.pos):
                    if click: click.play()
                    save_last_score()
                    state = "home"

        if state == "game" and phase=="input" and event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:
                try:
                    user_list = list(map(int,user_input.split()))
                    result = (user_list == sequence)
                    if not result:
                        lives -= 1
                        if wrong: wrong.play()
                except:
                    result = False
                    lives -= 1
                    if wrong: wrong.play()

                phase = "result"
                timer = time.time()

            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]

            else:
                if event.unicode.isdigit() or event.unicode==" ":
                    user_input += event.unicode

    pygame.display.update()
    clock.tick(60)

pygame.quit()