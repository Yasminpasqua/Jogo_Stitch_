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
    {"id": 4, "obj": "prancha", "clue": "Com o que Nani e David surfam no mar?"}
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
SPRITE_BG_CACHE = {}

def remove_background(surf, tolerance=40):
    """Remove a cor de fundo usando numpy.
    Detecta o fundo por amostragem da borda completa e usa flood-fill."""
    import numpy as np
    from collections import deque
    surf = surf.convert_alpha()
    w, h = surf.get_size()
    if w == 0 or h == 0:
        return surf

    # Amostra TODA a borda (1 pixel de espessura) para detectar a cor de fundo mais comum
    rgb = pygame.surfarray.pixels3d(surf)
    border_pixels = []
    # Bordas horizontais (topo e base)
    for x in range(0, w, max(1, w//30)):
        border_pixels.append(tuple(rgb[x, 0, :3]))
        border_pixels.append(tuple(rgb[x, h-1, :3]))
    # Bordas verticais (esquerda e direita)
    for y in range(0, h, max(1, h//30)):
        border_pixels.append(tuple(rgb[0, y, :3]))
        border_pixels.append(tuple(rgb[w-1, y, :3]))

    # Agrupa por faixas de 30 para encontrar a cor dominante na borda
    from collections import Counter
    def quantize(c): return (c[0]//30*30, c[1]//30*30, c[2]//30*30)
    counted = Counter(quantize(p) for p in border_pixels)
    bg_q = counted.most_common(1)[0][0]
    br, bg_g, bb = int(bg_q[0] + 15), int(bg_q[1] + 15), int(bg_q[2] + 15)

    # Máscara booleana: pixels parecidos com o fundo
    mask = (
        (np.abs(rgb[:, :, 0].astype(np.int32) - br)  <= tolerance) &
        (np.abs(rgb[:, :, 1].astype(np.int32) - bg_g) <= tolerance) &
        (np.abs(rgb[:, :, 2].astype(np.int32) - bb)  <= tolerance)
    )
    del rgb  # libera lock

    # Flood-fill iniciando de TODOS os pixels da borda que batem com o fundo
    flood = np.zeros((w, h), dtype=bool)
    q = deque()

    def seed(x, y):
        if 0 <= x < w and 0 <= y < h and mask[x, y] and not flood[x, y]:
            flood[x, y] = True
            q.append((x, y))

    for x in range(w):
        seed(x, 0); seed(x, h-1)
    for y in range(h):
        seed(0, y); seed(w-1, y)

    while q:
        px, py = q.popleft()
        for nx, ny in ((px+1,py),(px-1,py),(px,py+1),(px,py-1)):
            if 0 <= nx < w and 0 <= ny < h and not flood[nx,ny] and mask[nx,ny]:
                flood[nx, ny] = True
                q.append((nx, ny))

    # Aplica transparência nos pixels de fundo
    new_surf = surf.copy()
    alpha = pygame.surfarray.pixels_alpha(new_surf)
    alpha[flood] = 0
    del alpha
    return new_surf


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


def get_sprite_sheet(name):
    """Carrega um sprite sheet sem processamento (apenas cache raw)."""
    if name in SPRITE_BG_CACHE:
        return SPRITE_BG_CACHE[name]
    base_dir = _os.path.dirname(_os.path.abspath(__file__))
    path = _os.path.join(base_dir, 'inicial', 'imagens', name)
    if not _os.path.exists(path):
        SPRITE_BG_CACHE[name] = None
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        SPRITE_BG_CACHE[name] = img
        return img
    except:
        SPRITE_BG_CACHE[name] = None
        return None

FRAME_CACHE = {}

def get_frame_nobg(sheet, rect, tolerance=45):
    """Recorta um frame do sheet e remove o fundo. Resultado é cacheado."""
    key = (id(sheet), rect.x, rect.y, rect.w, rect.h)
    if key in FRAME_CACHE:
        return FRAME_CACHE[key]
    frame = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    frame.blit(sheet, (0, 0), rect)
    result = remove_background(frame, tolerance)
    FRAME_CACHE[key] = result
    return result


def preload_enemy_sprites():
    """Pré-carrega todos os frames dos inimigos antes do jogo começar.
    Exibe uma tela de loading enquanto processa."""

    TOTAL_FRAMES = 20  # 8 Gantu + 6 Jumba + 6 Pleakley
    done = [0]

    # Carrega imagem de fundo do loading
    bg_loading = get_img('iniciando.png', (W, H))

    def show_loading(progress):
        """progress: float de 0.0 a 1.0"""
        # Fundo
        screen.blit(bg_loading, (0, 0))

        # Overlay escuro semitransparente no centro para destacar o texto
        overlay = pygame.Surface((W, 180), pygame.SRCALPHA)
        overlay.fill((5, 8, 30, 180))
        screen.blit(overlay, (0, H//2 - 60))

        # Título "Iniciando o jogo"
        titulo = F_BIG.render("Iniciando o jogo", True, WHITE)
        screen.blit(titulo, (W//2 - titulo.get_width()//2, H//2 - 42))

        # Barra de progresso
        bar_w = int(W * 0.55)
        bar_h = 22
        bar_x = W//2 - bar_w//2
        bar_y = H//2 + 10

        # Fundo da barra
        pygame.draw.rect(screen, (20, 25, 70), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), border_radius=12)
        pygame.draw.rect(screen, (35, 45, 110), (bar_x, bar_y, bar_w, bar_h), border_radius=10)

        # Preenchimento dourado
        fill_w = max(0, int(bar_w * progress))
        if fill_w > 0:
            pygame.draw.rect(screen, (200, 150, 0), (bar_x, bar_y, fill_w, bar_h), border_radius=10)
            pygame.draw.rect(screen, GOLD,          (bar_x, bar_y, fill_w, bar_h // 2), border_radius=10)

        # Borda da barra
        pygame.draw.rect(screen, GOLD, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)

        # Percentual
        pct = F_SM.render(f"{int(progress * 100)}%", True, WHITE)
        screen.blit(pct, (W//2 - pct.get_width()//2, bar_y + bar_h + 8))

        pygame.display.flip()
        # Processa eventos do SO para não travar (não coloca na fila)
        pygame.event.pump()

    show_loading(0.0)

    # ── Gantu (sprint1.png): 8 frames em grid 2×4, fundo branco, sem header ──
    sheet1 = get_sprite_sheet('sprint1.png')
    if sheet1:
        sw, sh = sheet1.get_size()
        fw = sw // 2
        fh = sh // 4
        for idx in range(8):
            col = idx % 2
            row = idx // 2
            rect = pygame.Rect(col * fw, row * fh, fw, fh)
            get_frame_nobg(sheet1, rect, tolerance=30)
            done[0] += 1
            show_loading(done[0] / TOTAL_FRAMES)

    # ── Jumba (sprint2.png): linhas 0 e 2 (3+3 frames, linha 1 é irregular) ──
    sheet2 = get_sprite_sheet('sprint2.png')
    if sheet2:
        sw, sh = sheet2.get_size()
        fw = sw // 3
        fh = sh // 3
        for pos in range(6):
            if pos < 3:
                col, row = pos, 0
            else:
                col, row = pos - 3, 2
            rect = pygame.Rect(col * fw, row * fh, fw, fh)
            get_frame_nobg(sheet2, rect, tolerance=30)
            done[0] += 1
            show_loading(done[0] / TOTAL_FRAMES)

    # ── Pleakley (sprint3.png): 6 frames em 1 linha ──
    sheet3 = get_sprite_sheet('sprint3.png')
    if sheet3:
        sw, sh = sheet3.get_size()
        fw = sw // 6
        for idx in range(6):
            rect = pygame.Rect(idx * fw, 0, fw, sh)
            get_frame_nobg(sheet3, rect, tolerance=30)
            done[0] += 1
            show_loading(done[0] / TOTAL_FRAMES)

    # Mostra 100% por meio segundo usando loop de eventos (não bloqueia)
    show_loading(1.0)
    t_end = pygame.time.get_ticks() + 500
    while pygame.time.get_ticks() < t_end:
        show_loading(1.0)
        pygame.time.delay(30)

    # Limpa TODOS os eventos acumulados durante o loading
    pygame.event.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# MAZE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════
MAZE_MAP = [
    "##############################",
    "#............##............#O#",
    "#.####.#####.##.#####.####.#.#",
    "#O####.#####.##.#####.####.#.#",
    "#............................#",
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
            t = self.anim_timer
            step_phase = t % (2 * math.pi)
            bounce = -abs(math.sin(step_phase)) * 4
            waddle_angle = math.sin(step_phase) * 8
            contact = abs(math.cos(step_phase))
            stretch_y = 1.0 + contact * 0.08
            squash_x  = 1.0 - contact * 0.06
            new_w = max(1, int(sz[0] * squash_x))
            new_h = max(1, int(sz[1] * stretch_y))
            img = pygame.transform.smoothscale(base_img, (new_w, new_h))
            img = pygame.transform.rotate(img, waddle_angle)
            r = img.get_rect(center=(self.x, self.y + bounce))
            surf.blit(img, r)
        else:
            breath = math.sin(self.frame * 0.05) * 1.5
            r = base_img.get_rect(center=(self.x, self.y + breath))
            surf.blit(base_img, r)

# ═══════════════════════════════════════════════════════════════════════════════
# GHOST (Gantu persegue, Jumba e Pleakley aleatórios)
# ═══════════════════════════════════════════════════════════════════════════════
class Ghost:
    def __init__(self, cx, cy, kind):
        self.x = float(cx * TILE + TILE//2)
        self.y = float(cy * TILE + TILE//2 + HUD_H)
        self.speed = 2
        self.dx = self.speed; self.dy = 0
        self.kind = kind
        self.frame = 0
        self.start_x = self.x
        self.start_y = self.y

    def rect(self):
        return pygame.Rect(self.x - 12, self.y - 14, 24, 28)

    def update(self, walls, player_pos=None, other_enemies=None):
        self.frame += 1

        # Normaliza velocidade
        if   self.dx > 0: self.dx =  self.speed
        elif self.dx < 0: self.dx = -self.speed
        if   self.dy > 0: self.dy =  self.speed
        elif self.dy < 0: self.dy = -self.speed

        is_chaser = (self.kind == 'gantu' and player_pos is not None)

        # Posição dentro do tile (0 a TILE-1)
        cx = int(self.x) % TILE
        cy = int(self.y - HUD_H) % TILE

        # Só toma decisão no centro do tile (janela de 3px)
        if 14 <= cx <= 16 and 14 <= cy <= 16:
            grid_x = int(self.x) // TILE
            grid_y = int(self.y - HUD_H) // TILE
            self.x = float(grid_x * TILE + TILE // 2)
            self.y = float(grid_y * TILE + TILE // 2 + HUD_H)

            def is_open(test_dx, test_dy):
                step_x = (test_dx / self.speed) * TILE
                step_y = (test_dy / self.speed) * TILE
                return not self.check_collision(step_x, step_y, walls, other_enemies)

            all_dirs = [(self.speed, 0), (-self.speed, 0), (0, self.speed), (0, -self.speed)]
            opp_dir  = (-self.dx, -self.dy)

            possible = [d for d in all_dirs if d != opp_dir and is_open(d[0], d[1])]

            if not possible:
                if is_open(opp_dir[0], opp_dir[1]):
                    possible = [opp_dir]

            if possible:
                if len(possible) == 1:
                    self.dx, self.dy = possible[0]
                elif is_chaser:
                    px, py = player_pos
                    scored = []
                    for ddx, ddy in possible:
                        nx = self.x + (ddx / self.speed) * TILE
                        ny = self.y + (ddy / self.speed) * TILE
                        scored.append((math.hypot(nx - px, ny - py), ddx, ddy))
                    scored.sort()
                    if random.random() < 0.90:
                        self.dx, self.dy = scored[0][1], scored[0][2]
                    else:
                        _, ddx, ddy = random.choice(scored)
                        self.dx, self.dy = ddx, ddy
                else:
                    self.dx, self.dy = random.choice(possible)
            else:
                # Sem saída: reverte
                self.dx = -self.dx
                self.dy = -self.dy

        # Move somente se não bater na parede nem em outro inimigo
        if not self.check_collision(self.dx, self.dy, walls, other_enemies):
            self.x += self.dx
            self.y += self.dy
        elif other_enemies and self.check_collision(self.dx, self.dy, [], other_enemies):
            # Se trombou de frente com outro inimigo no meio do caminho, inverte para se soltar
            self.dx = -self.dx
            self.dy = -self.dy

        # Wrap horizontal (túneis)
        if self.x < 0:       self.x = float(W)
        elif self.x > float(W): self.x = 0.0

    def check_collision(self, dx, dy, walls, other_enemies=None):
        rect = pygame.Rect(self.x + dx - 10, self.y + dy - 10, 20, 20)
        for w in walls:
            if rect.colliderect(w): return True
        if other_enemies:
            for other in other_enemies:
                if rect.colliderect(other.rect()): return True
        return False


    def _get_sprite_frame(self):
        """Extrai o frame correto do sprite sheet com remoção de fundo por frame."""
        if self.kind == 'gantu':
            # sprint1.png: 8 frames em grid 2 colunas x 4 linhas
            # Topo tem título de ~10% da altura; ignorar
            sheet = get_sprite_sheet('sprint1.png')
            if sheet is None: return None
            sw, sh = sheet.get_size()
            # Grid 2×4, fundo branco, sem header
            fw = sw // 2
            fh = sh // 4
            idx = (self.frame // 6) % 8
            col = idx % 2
            row = idx // 2
            rect = pygame.Rect(col * fw, row * fh, fw, fh)
            return get_frame_nobg(sheet, rect, tolerance=30)

        elif self.kind == 'jumba':
            # sprint2.png: linhas 0 e 2 têm 3 cols cada (linha 1 tem 4 - irregular)
            sheet = get_sprite_sheet('sprint2.png')
            if sheet is None: return None
            sw, sh = sheet.get_size()
            fw = sw // 3
            fh = sh // 3
            # Alterna entre linha 0 (idx 0-2) e linha 2 (idx 3-5)
            pos = (self.frame // 8) % 6
            if pos < 3:
                col, row = pos, 0
            else:
                col, row = pos - 3, 2
            rect = pygame.Rect(col * fw, row * fh, fw, fh)
            return get_frame_nobg(sheet, rect, tolerance=30)

        else:  # pleakley
            # sprint3.png: 6 frames em 1 linha, fundo branco
            sheet = get_sprite_sheet('sprint3.png')
            if sheet is None: return None
            sw, sh = sheet.get_size()
            fw = sw // 6
            idx = (self.frame // 7) % 6
            rect = pygame.Rect(idx * fw, 0, fw, sh)
            return get_frame_nobg(sheet, rect, tolerance=30)

    def draw(self, surf):
        bob = math.sin(self.frame * 0.15) * 2
        frame_surf = self._get_sprite_frame()

        if frame_surf is not None:
            target_w, target_h = 55, 55
            scaled = pygame.transform.smoothscale(frame_surf, (target_w, target_h))
            # Espelha se indo para a esquerda
            if self.dx < 0:
                scaled = pygame.transform.flip(scaled, True, False)
            r = scaled.get_rect(center=(int(self.x), int(self.y + bob)))
            surf.blit(scaled, r)
        else:
            # Fallback: elipse colorida caso o sprite não carregue
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

        for row in range(ROWS):
            for col in range(COLS):
                char = MAZE_MAP[row][col]
                x = col * TILE
                y = row * TILE + HUD_H

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
    found_obj = ""

    # Pré-carrega todos os frames dos inimigos (evita travamento no início)
    preload_enemy_sprites()
    pygame.event.clear()  # descarta eventos acumulados durante o loading

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
            other_enemies = [o for o in lvl.enemies if o != e]
            e.speed = 2 + (level_num - 1) * 0.3
            e.update(lvl.walls, player_pos, other_enemies)
            e.draw(screen)
            if player.rect().colliderect(e.rect()):
                player.lives -= 1
                flash_timer = 30
                flash_msg = "Pego por um Inimigo!"
                if player.lives <= 0: state = 'gameover'
                else: reset_positions()

        # Player
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

        # UI & Effects
        draw_ui(screen, state, "", total_score, player.lives, level_num,
                PHASES[level_num-1]['clue'])

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
