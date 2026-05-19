import pygame, sys, math, random
import os as _os

pygame.init()

W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Stitch: Labirinto Ohana")
clock = pygame.time.Clock()
FPS = 60

# ── FONTS ──────────────────────────────────────────────────────────────────────
F_TITLE = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
F_BIG   = pygame.font.SysFont("Comic Sans MS", 28, bold=True)
F_MID   = pygame.font.SysFont("Comic Sans MS", 20, bold=True)
F_SM    = pygame.font.SysFont("Comic Sans MS", 15)

# ── PHASES ─────────────────────────────────────────────────────────────────────
PHASES = [
    {"id": 1, "obj": "hula",      "clue": "Encontre a Saia de Hula escondida!"},
    {"id": 2, "obj": "xepa",      "clue": "Ache a Boneca Xepa, cuidado com os inimigos!"},
    {"id": 3, "obj": "ukulele",   "clue": "O Jumba perdeu o Ukulele no labirinto!"},
    {"id": 4, "obj": "prancha", "clue": "Pegue a Prancha e escape!"}
]

# ── COLORS ────────────────────────────────────────────────────────────────────
WHITE  = (255,255,255); BLACK = (0,0,0); RED = (220,50,50)
GOLD   = (255,210,0);   LIME = (140,220,0)
WALL_C = (30, 50, 150); DOT_C = (255, 200, 150)

TILE = 30
COLS = W // TILE
ROWS = H // TILE

# ═══════════════════════════════════════════════════════════════════════════════
# ASSETS
# ═══════════════════════════════════════════════════════════════════════════════
IMG_CACHE = {}

def get_img(name, target_size=None):
    if (name, target_size) in IMG_CACHE:
        return IMG_CACHE[(name, target_size)]
        
    base_dir = _os.path.dirname(_os.path.abspath(__file__))
    path = _os.path.join(base_dir, 'inicial', 'imagens', name)
    
    if not _os.path.exists(path):
        s = pygame.Surface(target_size if target_size else (TILE, TILE), pygame.SRCALPHA)
        IMG_CACHE[(name, target_size)] = s
        return s
        
    try:
        img = pygame.image.load(path).convert_alpha()
        if target_size:
            img = pygame.transform.smoothscale(img, target_size)
        IMG_CACHE[(name, target_size)] = img
        return img
    except:
        s = pygame.Surface(target_size if target_size else (TILE, TILE), pygame.SRCALPHA)
        IMG_CACHE[(name, target_size)] = s
        return s

# ═══════════════════════════════════════════════════════════════════════════════
# MAZE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

MAZE_MAP = [
    "##############################",
    "#............##............#O#",
    "#.####.#####.##.#####.####.#.#",
    "#O####.#####.##.#####.####.#.#",
    "#..........................#.#",
    "#.####.##.########.##.####.#.#",
    "#......##....##....##......#.#",
    "######.##### ## #####.######.#",
    "     #.#####    #####.#     .#",
    "######.##   E E E  ##.######.#",
    "#      ## ######## ##      #.#",
    "######.## ######## ##.######.#",
    "     #.##          ##.#     .#",
    "######.## ######## ##.######.#",
    "#............##............#.#",
    "#.####.#####.##.#####.####.#.#",
    "#O..##.......S........##..O#.#",
    "###.##.##.########.##.##.###.#",
    "#......##..........##......#.#",
    "##############################"
]

class PacPlayer:
    def __init__(self, cx, cy):
        self.x = cx * TILE + TILE//2
        self.y = cy * TILE + TILE//2
        self.speed = 3
        self.dx = 0; self.dy = 0
        self.frame = 0
        self.lives = 3
        self.facing = 'right'

    def rect(self):
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

    def update(self, walls):
        keys = pygame.key.get_pressed()
        self.dx = 0; self.dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.dx = -self.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.dx = self.speed
        elif keys[pygame.K_UP] or keys[pygame.K_w]: self.dy = -self.speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: self.dy = self.speed

        if self.dx != 0 or self.dy != 0:
            if not self.check_collision(self.dx, self.dy, walls):
                self.x += self.dx
                self.y += self.dy
                self.frame += 1
                if self.dx > 0: self.facing = 'right'
                elif self.dx < 0: self.facing = 'left'
            else:
                # Corner sliding logic to prevent getting stuck
                if self.dx != 0:
                    if not self.check_collision(self.dx, -self.speed, walls): self.y -= self.speed
                    elif not self.check_collision(self.dx, self.speed, walls): self.y += self.speed
                elif self.dy != 0:
                    if not self.check_collision(-self.speed, self.dy, walls): self.x -= self.speed
                    elif not self.check_collision(self.speed, self.dy, walls): self.x += self.speed

        # Wrap around screen
        if self.x < 0: self.x = W
        if self.x > W: self.x = 0

    def check_collision(self, dx, dy, walls):
        rect = pygame.Rect(self.x + dx - 10, self.y + dy - 10, 20, 20)
        for w in walls:
            if rect.colliderect(w): return True
        return False

    def draw(self, surf):
        img = get_img('stitch.png', (TILE+10, TILE+10))
        if self.facing == 'left': img = pygame.transform.flip(img, True, False)
        
        bob = math.sin(self.frame * 0.4) * 3 if (self.dx!=0 or self.dy!=0) else 0
        surf.blit(img, (self.x - TILE//2 - 5, self.y - TILE//2 - 5 + bob))

class Ghost:
    def __init__(self, cx, cy, kind):
        self.x = cx * TILE + TILE//2
        self.y = cy * TILE + TILE//2
        self.speed = 2
        self.dx = self.speed; self.dy = 0
        self.kind = kind
        self.frame = 0
        self.start_x = self.x
        self.start_y = self.y

    def rect(self):
        return pygame.Rect(self.x - 12, self.y - 14, 24, 28)

    def update(self, walls):
        self.frame += 1
        
        # Sync dx/dy to current speed
        if self.dx > 0: self.dx = self.speed
        elif self.dx < 0: self.dx = -self.speed
        if self.dy > 0: self.dy = self.speed
        elif self.dy < 0: self.dy = -self.speed

        # Try to move
        if not self.check_collision(self.dx, self.dy, walls):
            self.x += self.dx
            self.y += self.dy
            
            # Randomly turn if roughly aligned with grid
            if int(self.x) % TILE in (14, 15, 16) and int(self.y) % TILE in (14, 15, 16):
                if random.random() < 0.05: # 5% chance to try turning
                    possible = []
                    for ddx, ddy in [(self.speed,0), (-self.speed,0), (0,self.speed), (0,-self.speed)]:
                        if not self.check_collision(ddx, ddy, walls):
                            possible.append((ddx, ddy))
                    if possible:
                        self.dx, self.dy = random.choice(possible)
        else:
            # Hit a wall, must pick a new direction
            possible = []
            for ddx, ddy in [(self.speed,0), (-self.speed,0), (0,self.speed), (0,-self.speed)]:
                if not self.check_collision(ddx, ddy, walls):
                    possible.append((ddx, ddy))
            if possible:
                # snap to grid center to prevent clipping
                self.x = (int(self.x) // TILE) * TILE + TILE//2
                self.y = (int(self.y) // TILE) * TILE + TILE//2
                self.dx, self.dy = random.choice(possible)
            else:
                self.dx = -self.dx
                self.dy = -self.dy

        # Wrap
        if self.x < 0: self.x = W
        if self.x > W: self.x = 0

    def check_collision(self, dx, dy, walls):
        rect = pygame.Rect(self.x + dx - 10, self.y + dy - 10, 20, 20)
        for w in walls:
            if rect.colliderect(w): return True
        return False

    def draw(self, surf):
        bob = math.sin(self.frame * 0.2) * 3
        c = RED if self.kind == 'gantu' else (118,58,158) if self.kind == 'jumba' else (55,158,55)
        pygame.draw.ellipse(surf, c, (self.x - 12, self.y - 12 + bob, 24, 28))
        pygame.draw.circle(surf, WHITE, (self.x-5, self.y-5+bob), 4)
        pygame.draw.circle(surf, WHITE, (self.x+5, self.y-5+bob), 4)

class BigObject:
    def __init__(self, cx, cy, kind, is_correct):
        self.x = cx * TILE + TILE//2
        self.y = cy * TILE + TILE//2
        self.kind = kind
        self.is_correct = is_correct
        self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        self.frame = random.randint(0, 100)

    def draw(self, surf):
        self.frame += 1
        bob = math.sin(self.frame * 0.1) * 4
        img = get_img(f"{self.kind}.png", (40, 40))
        
        # Glow effect
        if self.is_correct:
            pygame.draw.circle(surf, (255, 215, 0, 100), (self.x, self.y+bob), 20)
            
        surf.blit(img, (self.x - 20, self.y - 20 + bob))

class GameLevel:
    def __init__(self, level):
        self.walls = []
        self.dots = []
        self.objects = []
        self.enemies = []
        self.player_start = (0,0)
        self.level = level
        self.score = 0
        
        self.build()
        
    def build(self):
        phase_info = PHASES[min(self.level-1, len(PHASES)-1)]
        correct_kind = phase_info['obj']
        
        # Possible decoys
        all_decoys = ['hula', 'xepa', 'ukulele', 'prancha']
        decoys = [d for d in all_decoys if d != correct_kind]
        
        obj_spots = []
        ghost_names = ['gantu', 'jumba', 'pleakley']
        g_idx = 0
        
        for row in range(ROWS):
            for col in range(COLS):
                char = MAZE_MAP[row][col]
                x = col * TILE
                y = row * TILE
                
                if char == '#':
                    self.walls.append(pygame.Rect(x, y, TILE, TILE))
                elif char == '.':
                    self.dots.append(pygame.Rect(x + TILE//2 - 2, y + TILE//2 - 2, 4, 4))
                elif char == 'S':
                    self.player_start = (col, row)
                elif char == 'E':
                    if g_idx < len(ghost_names):
                        self.enemies.append(Ghost(col, row, ghost_names[g_idx]))
                        g_idx += 1
                elif char == 'O':
                    obj_spots.append((col, row))

        # Assign correct and fake objects to 'O' spots randomly
        random.shuffle(obj_spots)
        for i, spot in enumerate(obj_spots):
            if i == 0:
                self.objects.append(BigObject(spot[0], spot[1], correct_kind, True))
            else:
                self.objects.append(BigObject(spot[0], spot[1], random.choice(decoys), False))

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER MENUS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_ui(surf, state, found_obj, score, lives, level, clue):
    if state == 'title':
        surf.fill((10,30,100))
        img = get_img('stitch.png', (200, 200))
        surf.blit(img, (W//2 - 100, 150))
        tl = F_TITLE.render("STITCH: LABIRINTO PAC-MAN", True, GOLD)
        surf.blit(tl, (W//2-tl.get_width()//2, 80))
        sc = F_MID.render("▶ ENTER para jogar ◀", True, WHITE)
        surf.blit(sc, (W//2-sc.get_width()//2, 400))
        
    elif state == 'gameover':
        img = get_img('gameover.png', (W, H))
        surf.blit(img, (0, 0))
        tl = F_TITLE.render("GAME OVER", True, RED)
        surf.blit(tl, (W//2-tl.get_width()//2, 100))
        m = F_SM.render("Pressione ENTER para tentar novamente", True, WHITE)
        surf.blit(m, (W//2-m.get_width()//2, H-50))
        
    elif state == 'win':
        surf.fill((5,30,80))
        img = get_img('stitch.png', (300, 300))
        surf.blit(img, (W//2 - 150, 200))
        tl = F_TITLE.render("VOCÊ ZEROU O LABIRINTO!", True, GOLD)
        surf.blit(tl, (W//2-tl.get_width()//2, 100))
        m = F_SM.render("Pressione ENTER para jogar novamente", True, WHITE)
        surf.blit(m, (W//2-m.get_width()//2, H-50))
        
    elif state == 'found':
        surf.fill((20,100,50))
        img = get_img(f"{found_obj}.png", (150, 150))
        surf.blit(img, (W//2 - 75, 100))
        tl = F_TITLE.render("OBJETO ENCONTRADO!", True, GOLD)
        surf.blit(tl, (W//2-tl.get_width()//2, 300))
        t2 = F_MID.render(f"Você pegou: {found_obj.title()}", True, WHITE)
        surf.blit(t2, (W//2-t2.get_width()//2, 400))
        t3 = F_SM.render("Pressione ENTER para próxima fase", True, LIME)
        surf.blit(t3, (W//2-t3.get_width()//2, 500))

    elif state == 'play':
        # HUD bar at the top or bottom
        pygame.draw.rect(surf, (0,0,0,150), (0, 0, W, 40))
        for i in range(lives):
            pygame.draw.circle(surf, RED, (30 + i*25, 20), 8)
        sc = F_SM.render(f"Score: {score}", True, WHITE)
        surf.blit(sc, (120, 10))
        cl = F_SM.render(f"Missão {level}: {clue}", True, GOLD)
        surf.blit(cl, (300, 10))

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    state = 'title'
    level_num = 1
    total_score = 0
    player = None
    lvl = None
    flash_timer = 0
    flash_msg = ""
    found_obj = ""
    
    def reset_positions():
        player.x = lvl.player_start[0]*TILE + TILE//2
        player.y = lvl.player_start[1]*TILE + TILE//2
        player.dx = 0; player.dy = 0
        for e in lvl.enemies:
            e.x = e.start_x; e.y = e.start_y
    
    while True:
        clock.tick(FPS)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                
                if state == 'title' and ev.key == pygame.K_RETURN:
                    state = 'play'; level_num = 1; total_score = 0
                    lvl = GameLevel(level_num)
                    player = PacPlayer(*lvl.player_start)
                    
                elif state in ('win', 'gameover') and ev.key == pygame.K_RETURN:
                    state = 'title'
                    
                elif state == 'found' and ev.key == pygame.K_RETURN:
                    state = 'play'
                    level_num += 1
                    if level_num > len(PHASES):
                        state = 'win'
                    else:
                        lvl = GameLevel(level_num)
                        # Carry over lives and score
                        old_lives = player.lives
                        player = PacPlayer(*lvl.player_start)
                        player.lives = old_lives
                        
        if state in ('title', 'gameover', 'win', 'found'):
            draw_ui(screen, state, found_obj, 0, 0, 0, "")
            pygame.display.flip(); continue

        # PLAY STATE
        # Draw background and walls
        screen.fill(BLACK)
        for w in lvl.walls:
            pygame.draw.rect(screen, WALL_C, w, border_radius=4)
            pygame.draw.rect(screen, (50, 100, 200), w, 2, border_radius=4)
            
        # Draw Dots
        for d in lvl.dots:
            pygame.draw.rect(screen, DOT_C, d)
            
        # Update and Draw Objects
        for o in lvl.objects:
            o.draw(screen)
            if player.rect().colliderect(o.rect):
                if o.is_correct:
                    state = 'found'
                    found_obj = o.kind
                    total_score += 1000
                else:
                    player.lives -= 1
                    flash_timer = 30
                    flash_msg = "Objeto Falso! Perdeu 1 vida!"
                    lvl.objects.remove(o)
                    if player.lives <= 0: state = 'gameover'
                    else: reset_positions()

        # Update and Draw Enemies
        for e in lvl.enemies:
            # Increase enemy speed slightly based on level
            e.speed = 2 + (level_num * 0.5)
            e.update(lvl.walls)
            e.draw(screen)
            if player.rect().colliderect(e.rect()):
                player.lives -= 1
                flash_timer = 30
                flash_msg = "Pego por um Inimigo!"
                if player.lives <= 0: state = 'gameover'
                else: reset_positions()

        # Update and Draw Player
        player.update(lvl.walls)
        player.draw(screen)
        
        # Check Dot collisions
        p_rect = player.rect()
        new_dots = []
        for d in lvl.dots:
            if p_rect.colliderect(d):
                total_score += 10
            else:
                new_dots.append(d)
        lvl.dots = new_dots

        # UI & Effects
        draw_ui(screen, state, "", total_score, player.lives, level_num, PHASES[level_num-1]['clue'])
        
        if flash_timer > 0:
            flash_timer -= 1
            sf = pygame.Surface((W,H), pygame.SRCALPHA)
            sf.fill((255,0,0,flash_timer*5)); screen.blit(sf,(0,0))
            if flash_msg:
                fm = F_BIG.render(flash_msg, True, WHITE)
                screen.blit(fm, (W//2-fm.get_width()//2, H//2))

        pygame.display.flip()

if __name__ == '__main__':
    main()
