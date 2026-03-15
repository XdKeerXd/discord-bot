import pygame
import random
import sys
import math

pygame.init()
pygame.mixer.init()

# ── Window ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 700, 500
HUD_HEIGHT = 50
GRID = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT + HUD_HEIGHT))
pygame.display.set_caption("🐍 Snake")
clock = pygame.time.Clock()

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = (10,  12,  20)
GRID_COLOR  = (18,  22,  36)
HEAD_COLOR  = (50,  220, 120)
BODY_COLOR  = (30,  170,  80)
TAIL_COLOR  = (20,  100,  50)
FOOD_COLOR  = (255,  80,  80)
FOOD_SHINE  = (255, 180, 160)
GOLD        = (255, 200,  50)
WHITE       = (235, 240, 250)
GRAY        = (120, 130, 150)
DARK_GRAY   = ( 40,  45,  60)
PANEL_BG    = ( 18,  22,  38)
ACCENT      = ( 50, 220, 120)
RED_SOFT    = (220,  70,  70)
BLUE_SOFT   = ( 80, 160, 230)

# ── Fonts ────────────────────────────────────────────────────────────────────
font_large  = pygame.font.SysFont("consolas", 52, bold=True)
font_med    = pygame.font.SysFont("consolas", 30, bold=True)
font_small  = pygame.font.SysFont("consolas", 20)
font_tiny   = pygame.font.SysFont("consolas", 16)

# ── Settings defaults ────────────────────────────────────────────────────────
settings = {
    "speed":       10,       # FPS / tick speed
    "walls":       True,     # die on wall collision
    "show_grid":   True,
    "theme":       "green",  # green / blue / gold
}

THEMES = {
    "green": (HEAD_COLOR, BODY_COLOR, TAIL_COLOR),
    "blue":  ((80, 180, 255), (40, 110, 200), (20, 60, 130)),
    "gold":  ((255, 210, 60), (200, 150, 30), (130, 90, 10)),
}

SPEEDS = {"Slow": 7, "Normal": 10, "Fast": 15, "Insane": 22}

high_score = 0


# ── Helpers ──────────────────────────────────────────────────────────────────
def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def draw_rounded_rect(surf, color, rect, radius=10, alpha=255):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))

def draw_text(surf, text, font, color, cx, cy, shadow=True):
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        surf.blit(sh, sh.get_rect(center=(cx + 2, cy + 2)))
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))

def draw_grid():
    if not settings["show_grid"]:
        return
    for x in range(0, WIDTH, GRID):
        pygame.draw.line(screen, GRID_COLOR, (x, HUD_HEIGHT), (x, HEIGHT + HUD_HEIGHT))
    for y in range(HUD_HEIGHT, HEIGHT + HUD_HEIGHT, GRID):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def random_food(snake):
    while True:
        fx = random.randrange(0, WIDTH // GRID) * GRID
        fy = random.randrange(0, HEIGHT // GRID) * GRID + HUD_HEIGHT
        if [fx, fy] not in snake:
            return fx, fy

def draw_hud(score, length):
    pygame.draw.rect(screen, PANEL_BG, (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)
    draw_text(screen, f"SCORE  {score}", font_small, ACCENT,    90, HUD_HEIGHT // 2)
    draw_text(screen, f"LENGTH {length}", font_small, GRAY,    270, HUD_HEIGHT // 2)
    draw_text(screen, f"BEST   {high_score}", font_small, GOLD, 450, HUD_HEIGHT // 2)
    spd = [k for k, v in SPEEDS.items() if v == settings["speed"]]
    spd_label = spd[0] if spd else str(settings["speed"])
    draw_text(screen, spd_label, font_small, BLUE_SOFT, 630, HUD_HEIGHT // 2)

def draw_snake_body(snake, tick):
    head_c, body_c, tail_c = THEMES[settings["theme"]]
    n = len(snake)
    for i, seg in enumerate(snake):
        t = i / max(n - 1, 1)
        color = lerp_color(tail_c, body_c, t)
        if i == n - 1:
            color = head_c
        rx, ry = seg[0], seg[1]
        # body segment with slight rounding
        r = pygame.Rect(rx + 1, ry + 1, GRID - 2, GRID - 2)
        pygame.draw.rect(screen, color, r, border_radius=4)
        # shine on head
        if i == n - 1:
            pygame.draw.rect(screen, lerp_color(color, WHITE, 0.4),
                             (rx + 3, ry + 3, GRID // 3, GRID // 4), border_radius=2)

def draw_food(fx, fy, tick):
    pulse = 0.5 + 0.5 * math.sin(tick * 0.12)
    r = int(GRID // 2 - 1 + pulse * 2)
    cx, cy = fx + GRID // 2, fy + GRID // 2
    # glow
    glow = pygame.Surface((GRID * 2, GRID * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*FOOD_COLOR, 40), (GRID, GRID), GRID)
    screen.blit(glow, (cx - GRID, cy - GRID))
    pygame.draw.circle(screen, FOOD_COLOR, (cx, cy), r)
    pygame.draw.circle(screen, FOOD_SHINE, (cx - 2, cy - 2), max(2, r // 3))

def draw_overlay(title, subtitle, options, selected):
    """Reusable overlay panel."""
    overlay = pygame.Surface((WIDTH, HEIGHT + HUD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    pw, ph = 420, 80 + len(options) * 58 + 20
    px = (WIDTH - pw) // 2
    py = (HEIGHT + HUD_HEIGHT - ph) // 2

    draw_rounded_rect(screen, PANEL_BG, (px, py, pw, ph), radius=18, alpha=230)
    pygame.draw.rect(screen, DARK_GRAY, (px, py, pw, ph), 2, border_radius=18)

    draw_text(screen, title,    font_med,   ACCENT, WIDTH // 2, py + 38)
    if subtitle:
        draw_text(screen, subtitle, font_tiny,  GRAY,   WIDTH // 2, py + 62)

    for i, (label, _) in enumerate(options):
        oy = py + 80 + i * 58 + 20
        if i == selected:
            draw_rounded_rect(screen, ACCENT, (px + 20, oy - 18, pw - 40, 42), radius=8)
            draw_text(screen, label, font_small, BG, WIDTH // 2, oy + 3, shadow=False)
        else:
            draw_text(screen, label, font_small, WHITE, WIDTH // 2, oy + 3)


# ── Screens ──────────────────────────────────────────────────────────────────
def screen_main_menu():
    options = [
        ("▶  Play", "play"),
        ("⚙  Settings", "settings"),
        ("✕  Quit", "quit"),
    ]
    sel = 0
    tick = 0
    while True:
        screen.fill(BG)
        draw_grid()
        tick += 1

        # animated title snake decoration
        for i in range(8):
            bx = WIDTH // 2 - 80 + i * 20
            by = 100 + int(math.sin(tick * 0.05 + i * 0.5) * 6)
            head_c, body_c, _ = THEMES[settings["theme"]]
            color = head_c if i == 7 else lerp_color(body_c, head_c, i / 7)
            pygame.draw.rect(screen, color, (bx, by, 18, 18), border_radius=4)

        draw_text(screen, "SNAKE", font_large, ACCENT, WIDTH // 2, 160)
        draw_text(screen, "Use ↑↓ to navigate  •  ENTER to select", font_tiny, GRAY, WIDTH // 2, 210)

        draw_overlay("", None, options, sel)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return options[sel][1]


def screen_settings():
    speed_keys = list(SPEEDS.keys())
    theme_keys = list(THEMES.keys())

    def speed_label():
        for k, v in SPEEDS.items():
            if v == settings["speed"]:
                return k
        return "Custom"

    items = [
        lambda: f"Speed:      {speed_label()}",
        lambda: f"Walls:      {'ON' if settings['walls'] else 'OFF'}",
        lambda: f"Grid:       {'ON' if settings['show_grid'] else 'OFF'}",
        lambda: f"Theme:      {settings['theme'].capitalize()}",
        lambda: "← Back",
    ]
    sel = 0
    while True:
        screen.fill(BG)
        draw_grid()
        options = [(fn(), None) for fn in items]
        draw_overlay("SETTINGS", "◀ ▶ to change  •  ENTER to select", options, sel)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if sel == 4:
                        return
                elif event.key == pygame.K_LEFT:
                    if sel == 0:
                        idx = speed_keys.index(speed_label()) if speed_label() in speed_keys else 0
                        settings["speed"] = SPEEDS[speed_keys[(idx - 1) % len(speed_keys)]]
                    elif sel == 1:
                        settings["walls"] = not settings["walls"]
                    elif sel == 2:
                        settings["show_grid"] = not settings["show_grid"]
                    elif sel == 3:
                        idx = theme_keys.index(settings["theme"])
                        settings["theme"] = theme_keys[(idx - 1) % len(theme_keys)]
                elif event.key == pygame.K_RIGHT:
                    if sel == 0:
                        idx = speed_keys.index(speed_label()) if speed_label() in speed_keys else 0
                        settings["speed"] = SPEEDS[speed_keys[(idx + 1) % len(speed_keys)]]
                    elif sel == 1:
                        settings["walls"] = not settings["walls"]
                    elif sel == 2:
                        settings["show_grid"] = not settings["show_grid"]
                    elif sel == 3:
                        idx = theme_keys.index(settings["theme"])
                        settings["theme"] = theme_keys[(idx + 1) % len(theme_keys)]
                elif event.key == pygame.K_ESCAPE:
                    return


def screen_game_over(score, length):
    options = [("▶  Play Again", "play"), ("⌂  Main Menu", "menu"), ("✕  Quit", "quit")]
    sel = 0
    while True:
        screen.fill(BG)
        draw_grid()
        subtitle = f"Score: {score}   Length: {length}"
        draw_overlay("GAME OVER", subtitle, options, sel)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return options[sel][1]


# ── Core gameplay ─────────────────────────────────────────────────────────────
def play_game():
    global high_score

    x = (WIDTH // GRID // 2) * GRID
    y = (HEIGHT // GRID // 2) * GRID + HUD_HEIGHT
    dx, dy = GRID, 0

    snake = [[x - i * GRID, y] for i in range(3)]
    score = 0
    tick  = 0

    fx, fy = random_food(snake)

    # bonus food
    bonus_active  = False
    bonus_pos     = None
    bonus_timer   = 0
    bonus_counter = 0   # eat N normal foods to spawn bonus

    paused = False

    while True:
        clock.tick(settings["speed"])
        tick += 1

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_p:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT  and dx == 0:
                        dx, dy = -GRID, 0
                    elif event.key == pygame.K_RIGHT and dx == 0:
                        dx, dy =  GRID, 0
                    elif event.key == pygame.K_UP    and dy == 0:
                        dx, dy = 0, -GRID
                    elif event.key == pygame.K_DOWN  and dy == 0:
                        dx, dy = 0,  GRID

        if paused:
            draw_text(screen, "PAUSED  (P to resume)", font_med, ACCENT,
                      WIDTH // 2, (HEIGHT + HUD_HEIGHT) // 2)
            pygame.display.flip()
            continue

        # ── Move ──
        head = [snake[-1][0] + dx, snake[-1][1] + dy]

        # Wall logic
        if settings["walls"]:
            if (head[0] < 0 or head[0] >= WIDTH or
                    head[1] < HUD_HEIGHT or head[1] >= HEIGHT + HUD_HEIGHT):
                if score > high_score:
                    high_score = score
                return screen_game_over(score, len(snake))
        else:
            head[0] %= WIDTH
            head[1] = ((head[1] - HUD_HEIGHT) % HEIGHT) + HUD_HEIGHT

        # Self collision
        if head in snake[1:]:
            if score > high_score:
                high_score = score
            return screen_game_over(score, len(snake))

        snake.append(head)

        ate = False

        # Normal food
        if head[0] == fx and head[1] == fy:
            score += 10
            ate = True
            bonus_counter += 1
            fx, fy = random_food(snake)
            if bonus_counter >= 5 and not bonus_active:
                bonus_pos   = random_food(snake)
                bonus_active = True
                bonus_timer  = settings["speed"] * 8  # 8 seconds

        # Bonus food (golden apple)
        if bonus_active:
            bonus_timer -= 1
            if head[0] == bonus_pos[0] and head[1] == bonus_pos[1]:
                score += 50
                ate = True
                bonus_active  = False
                bonus_counter = 0
            elif bonus_timer <= 0:
                bonus_active  = False
                bonus_counter = 0

        if not ate:
            snake.pop(0)

        # ── Draw ──
        screen.fill(BG)
        draw_grid()
        draw_food(fx, fy, tick)

        if bonus_active:
            # pulsing gold bonus food
            pulse = 0.5 + 0.5 * math.sin(tick * 0.25)
            r = int(GRID // 2 + pulse * 3)
            cx, cy = bonus_pos[0] + GRID // 2, bonus_pos[1] + GRID // 2
            glow = pygame.Surface((GRID * 3, GRID * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*GOLD, 60), (GRID + GRID // 2, GRID + GRID // 2), GRID + 4)
            screen.blit(glow, (cx - GRID - GRID // 2, cy - GRID - GRID // 2))
            pygame.draw.circle(screen, GOLD, (cx, cy), r)
            pygame.draw.circle(screen, WHITE, (cx - 2, cy - 2), max(2, r // 3))
            # timer bar
            bar_w = int((bonus_timer / (settings["speed"] * 8)) * 100)
            pygame.draw.rect(screen, DARK_GRAY, (bonus_pos[0] - 10, bonus_pos[1] - 10, 100, 6), border_radius=3)
            pygame.draw.rect(screen, GOLD,      (bonus_pos[0] - 10, bonus_pos[1] - 10, bar_w, 6), border_radius=3)

        draw_snake_body(snake, tick)
        draw_hud(score, len(snake))

        # "PAUSED" hint in corner
        draw_text(screen, "P=Pause  ESC=Menu", font_tiny, DARK_GRAY, 100, HUD_HEIGHT // 2)

        pygame.display.flip()


# ── Main loop ────────────────────────────────────────────────────────────────
def main():
    while True:
        action = screen_main_menu()
        if action == "quit":
            pygame.quit(); sys.exit()
        elif action == "settings":
            screen_settings()
        elif action == "play":
            result = play_game()
            if result == "menu":
                continue


if __name__ == "__main__":
    main()
