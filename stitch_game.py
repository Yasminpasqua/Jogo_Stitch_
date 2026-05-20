import pygame, sys, math, random
import os as _os

pygame.init()

HUD_H = 50
W, H  = 900, 600 + HUD_H
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Stitch: Labirinto Ohana")
clock = pygame.time.Clock()
FPS = 60

# ── FONTS ──────────────────────────────────────────────────────────────────────
F_TITLE = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
F_BIG   = pygame.font.SysFont("Comic Sans MS", 28, bold=True)
F_MID   = pygame.font.SysFont("Comic Sans MS", 20, bold=True)
F_SM    = pygame.font.SysFont("Comic Sans MS", 15)
F_Q     = pygame.font.SysFont("Comic Sans MS", 18, bold=True)

# ── PHASES (perguntas trivia sobre o filme) ────────────────────────────────────
PHASES = [
    {"id": 1, "obj": "hula",    "clue": "Qual roupa Lilo usa na apresentação de dança?"},
    {"id": 2, "obj": "xepa",    "clue": "Qual o nome da boneca de pano da Lilo?"},
    {"id": 3, "obj": "ukulele", "clue": "Qual instrumento Stitch aprende a tocar?"},
    {"id": 4, "obj": "prancha", "clue": "Com o que Nani e David surfam no mar?"},
    {"id": 5, "obj": "saida",   "clue": "Nível Assustador! Encontre a SAÍDA no escuro!"}
]

# ── COLORS ────────────────────────────────────────────────────────────────────
WHITE  = (255,255,255); BLACK = (0,0,0); RED = (220,50,50)
GOLD   = (255,210,0);   LIME = (140,220,0)
WALL_C = (30, 50, 150); DOT_C = (255, 200, 150)

TILE = 30
COLS = W // TILE
ROWS = 20  # linhas fixas do mapa

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
# AUDIO
# ═══════════════════════════════════════════════════════════════════════════════
AUDIO_CACHE = {}

def play_audio(name):
    base_dir = _os.path.dirname(_os.path.abspath(__file__))
    path = _os.path.join(base_dir, 'inicial', 'audios', name)
    if _os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print("Erro ao tocar áudio:", e)
    else:
        print("Áudio não encontrado:", path)

# ═══════════════════════════════════════════════════════════════════════════════
# MAZE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════
MAZE_MAP = [
    "##############################",
    "#............##............#O#",
    "#.####.#####.##.#####.####.#.#",
    "#O####.#####.##.#####.####.#.#",
    "#.............................#",
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
    "#......##..........##........#",
    "##############################"
]

# ═══════════════════════════════════════════════════════════════════════════════
# PLAYER (com animação de caminhada realista)
# ═══════════════════════════════════════════════════════════════════════════════
class PacPlayer:
    def __init__(self, cx, cy):
        self.x = cx * TILE + TILE//2
        self.y = cy * TILE + TILE//2 + HUD_H
        self.speed = 3
        self.dx = 0; self.dy = 0
        self.frame = 0
        self.anim_timer = 0.0
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
                self.anim_timer += 0.25
                if self.dx > 0: self.facing = 'right'
                elif self.dx < 0: self.facing = 'left'
            else:
                if self.dx != 0:
                    if not self.check_collision(self.dx, -self.speed, walls): self.y -= self.speed
                    elif not self.check_collision(self.dx, self.speed, walls): self.y += self.speed
                elif self.dy != 0:
                    if not self.check_collision(-self.speed, self.dy, walls): self.x -= self.speed
                    elif not self.check_collision(self.speed, self.dy, walls): self.x += self.speed

        if self.x < 0: self.x = W
        if self.x > W: self.x = 0

    def check_collision(self, dx, dy, walls):
        rect = pygame.Rect(self.x + dx - 10, self.y + dy - 10, 20, 20)
        for w in walls:
            if rect.colliderect(w): return True
        return False

    def draw(self, surf):
        sz = (TILE + 10, TILE + 10)
        base_img = get_img('stitch.png', sz)
        if self.facing == 'left':
            base_img = pygame.transform.flip(base_img, True, False)

        moving = (self.dx != 0 or self.dy != 0)

        if moving:
            # ── Ciclo de caminhada realista ──
            # Fase do passo (0 a 2*PI = 1 passo completo)
            t = self.anim_timer
            step_phase = t % (2 * math.pi)

            # 1) Bounce vertical — sobe no meio do passo, desce no contato
            #    abs(sin) dá dois "contatos" por ciclo
            bounce = -abs(math.sin(step_phase)) * 4

            # 2) Waddle — balanço lateral como o Stitch anda no filme
            waddle_angle = math.sin(step_phase) * 8

            # 3) Squash & Stretch — achata no contato, estica no ar
            contact = abs(math.cos(step_phase))  # 1 = contato, 0 = ar
            stretch_y = 1.0 + contact * 0.08      # até 1.08x mais alto
            squash_x  = 1.0 - contact * 0.06      # até 0.94x mais largo

            # Aplicar squash/stretch redimensionando
            new_w = max(1, int(sz[0] * squash_x))
            new_h = max(1, int(sz[1] * stretch_y))
            img = pygame.transform.smoothscale(base_img, (new_w, new_h))

            # Aplicar waddle (rotação)
            img = pygame.transform.rotate(img, waddle_angle)

            # Posicionar centralizado com bounce
            r = img.get_rect(center=(self.x, self.y + bounce))
            surf.blit(img, r)
        else:
            # Parado — idle com respiração suave
            breath = math.sin(self.frame * 0.05) * 1.5
            r = base_img.get_rect(center=(self.x, self.y + breath))
            surf.blit(base_img, r)

# ═══════════════════════════════════════════════════════════════════════════════
# GHOST (Gantu persegue, Jumba e Pleakley aleatórios)
# ═══════════════════════════════════════════════════════════════════════════════
class Ghost:
    def __init__(self, cx, cy, kind):
        self.x = cx * TILE + TILE//2
        self.y = cy * TILE + TILE//2 + HUD_H
        self.speed = 2
        self.dx = self.speed; self.dy = 0
        self.kind = kind
        self.frame = 0
        self.start_x = self.x
        self.start_y = self.y

    def rect(self):
        return pygame.Rect(self.x - 12, self.y - 14, 24, 28)

    def update(self, walls, player_pos=None):
        self.frame += 1
        if self.speed == 0:
            return

        # Sync dx/dy to current speed
        if self.dx > 0: self.dx = self.speed
        elif self.dx < 0: self.dx = -self.speed
        if self.dy > 0: self.dy = self.speed
        elif self.dy < 0: self.dy = -self.speed

        is_chaser = (self.kind == 'gantu' and player_pos is not None)

        cx = int(self.x) % TILE
        cy = int(self.y - HUD_H) % TILE

        # Se estiver no centro do tile (margem de erro para garantir)
        if 14 <= cx <= 16 and 14 <= cy <= 16:
            # Alinha perfeitamente ao centro para evitar travamentos
            grid_x = int(self.x) // TILE
            grid_y = int(self.y - HUD_H) // TILE
            self.x = grid_x * TILE + TILE//2
            self.y = grid_y * TILE + TILE//2 + HUD_H

            def is_open(test_dx, test_dy):
                step_x = (test_dx / self.speed) * TILE
                step_y = (test_dy / self.speed) * TILE
                return not self.check_collision(step_x, step_y, walls)

            possible = []
            all_dirs = [(self.speed, 0), (-self.speed, 0), (0, self.speed), (0, -self.speed)]
            opp_dir = (-self.dx, -self.dy)

            for ddx, ddy in all_dirs:
                if (ddx, ddy) == opp_dir:
                    continue  # Fantasma não dá meia-volta (regra do Pac-Man)
                if is_open(ddx, ddy):
                    possible.append((ddx, ddy))

            if not possible:
                # Beco sem saída: única opção é dar meia-volta
                if is_open(opp_dir[0], opp_dir[1]):
                    possible.append(opp_dir)

            if possible:
                if len(possible) > 1:
                    # Interseção: decide o caminho
                    if is_chaser:
                        px, py = player_pos
                        scored = []
                        for ddx, ddy in possible:
                            # Avalia a distância a partir do PRÓXIMO tile
                            next_x = self.x + (ddx / self.speed) * TILE
                            next_y = self.y + (ddy / self.speed) * TILE
                            dist = math.hypot(next_x - px, next_y - py)
                            scored.append((dist, ddx, ddy))
                        
                        scored.sort(key=lambda t: t[0])
                        # 90% das vezes escolhe o melhor caminho, 10% aleatório para não prender
                        if random.random() < 0.90:
                            self.dx, self.dy = scored[0][1], scored[0][2]
                        else:
                            _, ddx, ddy = random.choice(scored)
                            self.dx, self.dy = ddx, ddy
                    else:
                        self.dx, self.dy = random.choice(possible)
                else:
                    # Apenas um caminho livre (curva ou reta)
                    self.dx, self.dy = possible[0]
            else:
                self.dx = 0
                self.dy = 0

        # Movimenta se não for bater (segurança adicional)
        if not self.check_collision(self.dx, self.dy, walls):
            self.x += self.dx
            self.y += self.dy
        else:
            # Fallback caso bata numa parede por erro de arredondamento
            self.dx = -self.dx
            self.dy = -self.dy
            self.x += self.dx
            self.y += self.dy

        # Wrap na tela (túneis)
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

# ═══════════════════════════════════════════════════════════════════════════════
# OBJECTS (sem glow)
# ═══════════════════════════════════════════════════════════════════════════════
class BigObject:
    def __init__(self, cx, cy, kind, is_correct):
        self.x = cx * TILE + TILE//2
        self.y = cy * TILE + TILE//2 + HUD_H
        self.kind = kind
        self.is_correct = is_correct
        self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        self.frame = random.randint(0, 100)

    def draw(self, surf):
        self.frame += 1
        bob = math.sin(self.frame * 0.1) * 4
        if self.kind == 'saida':
            r = pygame.Rect(self.x - 20, self.y - 20 + bob, 40, 40)
            pygame.draw.rect(surf, (150, 50, 200), r, border_radius=8)
            pygame.draw.rect(surf, WHITE, r, 2, border_radius=8)
            t = F_SM.render("SAÍDA", True, WHITE)
            surf.blit(t, (self.x - t.get_width()//2, self.y - 10 + bob))
        else:
            img = get_img(f"{self.kind}.png", (40, 40))
            surf.blit(img, (self.x - 20, self.y - 20 + bob))

# ═══════════════════════════════════════════════════════════════════════════════
# LEVEL BUILDER
# ═══════════════════════════════════════════════════════════════════════════════
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
        empty_spots = []

        for row in range(ROWS):
            for col in range(COLS):
                char = MAZE_MAP[row][col]
                x = col * TILE
                y = row * TILE + HUD_H

                if char == '#':
                    self.walls.append(pygame.Rect(x, y, TILE, TILE))
                elif char == '.':
                    self.dots.append(pygame.Rect(x + TILE//2 - 2, y + TILE//2 - 2, 4, 4))
                    empty_spots.append((col, row))
                elif char == 'S':
                    self.player_start = (col, row)
                elif char == 'E':
                    if self.level == 5:
                        pass # Na fase 5, espalhamos os fantasmas aleatoriamente depois
                    elif g_idx < len(ghost_names):
                        self.enemies.append(Ghost(col, row, ghost_names[g_idx]))
                        g_idx += 1
                elif char == 'O':
                    obj_spots.append((col, row))

        if self.level == 5:
            fixed_traps = [(1, 14), (14, 18), (28, 14), (8, 4), (21, 4), (1, 6), (14, 1)]
            for i, (c, r) in enumerate(fixed_traps):
                g = Ghost(c, r, 'gantu')
                g.jumpscare_img = 'susto1' if i % 2 == 0 else 'susto2'
                self.enemies.append(g)

        # Assign correct and fake objects to 'O' spots randomly
        random.shuffle(obj_spots)
        if self.level == 5:
            # Phase 5: Only exit, no decoys
            self.objects.append(BigObject(obj_spots[0][0], obj_spots[0][1], 'saida', True))
        else:
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
        img = get_img('introlabirinto.png', (W, H))
        surf.blit(img, (0, 0))

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
        tl = F_TITLE.render("RESPOSTA CERTA!", True, GOLD)
        surf.blit(tl, (W//2-tl.get_width()//2, 300))
        t2 = F_MID.render(f"Você pegou: {found_obj.title()}", True, WHITE)
        surf.blit(t2, (W//2-t2.get_width()//2, 400))
        t3 = F_SM.render("Pressione ENTER para próxima fase", True, LIME)
        surf.blit(t3, (W//2-t3.get_width()//2, 500))

    elif state == 'play':
        # HUD bar — fundo escuro acima do labirinto
        pygame.draw.rect(surf, (10, 15, 60), (0, 0, W, HUD_H))
        pygame.draw.line(surf, (50, 100, 200), (0, HUD_H-1), (W, HUD_H-1), 2)

        # Lives
        for i in range(lives):
            pygame.draw.circle(surf, RED, (20 + i*22, 14), 7)

        # Score
        sc = F_SM.render(f"Score: {score}", True, WHITE)
        surf.blit(sc, (90, 6))

        # Trivia question — destaque com fundo
        q_text = f"Fase {level}: {clue}"
        cl = F_Q.render(q_text, True, GOLD)
        qx = W//2 - cl.get_width()//2
        pygame.draw.rect(surf, (20, 30, 90), (qx - 10, 26, cl.get_width() + 20, 22), border_radius=6)
        surf.blit(cl, (qx, 26))

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
    jumpscare_img = ""
    found_obj = ""

    def reset_positions():
        player.x = lvl.player_start[0]*TILE + TILE//2
        player.y = lvl.player_start[1]*TILE + TILE//2 + HUD_H
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
                        old_lives = player.lives
                        player = PacPlayer(*lvl.player_start)
                        player.lives = old_lives

        if state in ('title', 'gameover', 'win', 'found'):
            draw_ui(screen, state, found_obj, 0, 0, 0, "")
            pygame.display.flip(); continue

        # ── PLAY STATE ─────────────────────────────────────────────────────────
        screen.fill(BLACK)

        # Walls
        for w in lvl.walls:
            pygame.draw.rect(screen, WALL_C, w, border_radius=4)
            pygame.draw.rect(screen, (50, 100, 200), w, 2, border_radius=4)

        # Dots
        for d in lvl.dots:
            pygame.draw.rect(screen, DOT_C, d)

        # Objects
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
                    flash_msg = "Resposta Errada! Perdeu 1 vida!"
                    lvl.objects.remove(o)
                    if player.lives <= 0: state = 'gameover'
                    else: reset_positions()

        # Enemies — pass player position so Gantu can chase
        player_pos = (player.x, player.y)
        for e in lvl.enemies:
            if level_num == 5:
                e.speed = 0 # Monstros são armadilhas estáticas
            else:
                e.speed = 2 + (level_num * 0.5)
            if flash_timer == 0:
                e.update(lvl.walls, player_pos)
            if level_num != 5:
                e.draw(screen)
            if player.rect().colliderect(e.rect()) and flash_timer == 0:
                player.lives -= 1
                if level_num == 5:
                    flash_timer = 60 # 1 segundo de jumpscare
                    flash_msg = ""
                    jumpscare_img = getattr(e, 'jumpscare_img', 'susto1')
                    play_audio('susto.mp3')
                else:
                    flash_timer = 30
                    flash_msg = "Pego por um Inimigo!"
                    jumpscare_img = ""
                reset_positions()

        # Player
        if flash_timer == 0:
            player.update(lvl.walls)
        player.draw(screen)

        # Dot collisions
        p_rect = player.rect()
        new_dots = []
        for d in lvl.dots:
            if p_rect.colliderect(d):
                total_score += 10
            else:
                new_dots.append(d)
        lvl.dots = new_dots

        # Se for a fase 5, desenhar escuridão com luz no Stitch
        if level_num == 5:
            dark = pygame.Surface((W, H))
            dark.fill((0, 0, 0))
            # Usar magenta como cor de recorte para criar o buraco de luz menor
            pygame.draw.circle(dark, (255, 0, 255), (int(player.x), int(player.y)), 40)
            dark.set_colorkey((255, 0, 255))
            screen.blit(dark, (0, 0))

        # UI & Effects
        draw_ui(screen, state, "", total_score, player.lives, level_num,
                PHASES[level_num-1]['clue'])

        if flash_timer > 0:
            flash_timer -= 1
            if jumpscare_img and level_num == 5:
                big_img = get_img(f"{jumpscare_img}.png", (W, H))
                screen.blit(big_img, (0, 0))
            else:
                sf = pygame.Surface((W,H), pygame.SRCALPHA)
                sf.fill((255,0,0,flash_timer*5)); screen.blit(sf,(0,0))
                if flash_msg:
                    fm = F_BIG.render(flash_msg, True, WHITE)
                    screen.blit(fm, (W//2-fm.get_width()//2, H//2))
            
            # Checar gameover só depois que o susto/flash acabar
            if flash_timer == 0 and player.lives <= 0:
                state = 'gameover'

        pygame.display.flip()

if __name__ == '__main__':
    main()
