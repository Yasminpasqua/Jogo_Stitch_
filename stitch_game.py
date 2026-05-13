import pygame, sys, math, random
pygame.init()

W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Stitch: Ohana Adventure")
clock = pygame.time.Clock()
FPS = 60

# ── FONTS ──────────────────────────────────────────────────────────────────────
F_TITLE = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
F_BIG   = pygame.font.SysFont("Comic Sans MS", 28, bold=True)
F_MID   = pygame.font.SysFont("Comic Sans MS", 20, bold=True)
F_SM    = pygame.font.SysFont("Comic Sans MS", 15)
F_XS    = pygame.font.SysFont("Comic Sans MS", 12)

# ── STITCH PALETTE ─────────────────────────────────────────────────────────────
SM   = (88,  112, 175)   # main fur
SD   = (52,  70,  132)   # dark shadow
SL   = (132, 157, 210)   # light highlight
SBL  = (218, 228, 248)   # belly (almost white)
SEA  = (215, 136, 152)   # ear pink
SNO  = (28,  28,  44)    # nose
SEY  = (10,  10,  18)    # eye black
STH  = (250, 253, 255)   # teeth white
STG  = (225, 92,  116)   # tongue
SMI  = (162, 62,  80)    # mouth interior
SCL  = (14,  14,  22)    # claws
SPW  = (46,  56,  108)   # paws/feet

# ── GENERAL ────────────────────────────────────────────────────────────────────
WHITE  = (255,255,255); BLACK = (0,0,0); RED = (220,50,50)
GOLD   = (255,210,0);   PINK  = (255,105,180); TEAL = (0,180,180)
ORANGE = (255,140,0);   YELLOW= (255,215,0);   LIME = (140,220,0)

# ── ENVIRONMENT ────────────────────────────────────────────────────────────────
GANTU_C=(85,88,105); JUMBA_C=(118,58,158); PLEK_C=(55,158,55)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def grad_fill(surf, c1, c2, rect=None):
    if rect is None: rect = (0, 0, surf.get_width(), surf.get_height())
    x, y, rw, rh = rect
    for i in range(rh):
        t = i / max(1, rh-1)
        col = tuple(int(c1[k]+(c2[k]-c1[k])*t) for k in range(3))
        pygame.draw.line(surf, col, (x, y+i), (x+rw, y+i))

def alpha_circle(surf, color, pos, r, a):
    s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color[:3], a), (r, r), r)
    surf.blit(s, (pos[0]-r, pos[1]-r))

_BG_CACHE = {}
def _load_bg(name):
    if name not in _BG_CACHE:
        base_dir = _os.path.dirname(_os.path.abspath(__file__))
        possible_paths = [
            _os.path.join(base_dir, 'imagens', name),
            _os.path.join(base_dir, 'images', name),
            _os.path.join(base_dir, 'inicial', 'imagens', name),
            _os.path.join(base_dir, 'inicial', 'images', name),
        ]
        
        found = False
        for path in possible_paths:
            if _os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    _BG_CACHE[name] = pygame.transform.smoothscale(img, (W, H))
                    found = True
                    break
                except: continue
        
        if not found:
            # If we were looking for a specific background, maybe try the other common names
            if name == 'bg_beach.png' and 'fundo.png' not in _BG_CACHE:
                return _load_bg('fundo.png')
            _BG_CACHE[name] = False
            
    return _BG_CACHE[name]

def rrect(surf, color, rect, rad=10, alpha=None):
    if alpha:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color[:3], alpha), (0,0,rect[2],rect[3]), border_radius=rad)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=rad)

# ═══════════════════════════════════════════════════════════════════════════════
# STITCH SPRITE – Real PNG image with animation
# ═══════════════════════════════════════════════════════════════════════════════
import os as _os

_STITCH_ORIG  = None   # original loaded Surface
_STITCH_CACHE = {}     # (w,h) -> scaled Surface

def _load_stitch():
    global _STITCH_ORIG
    if _STITCH_ORIG is None:
        base_dir = _os.path.dirname(_os.path.abspath(__file__))
        possible_paths = [
            _os.path.join(base_dir, 'stitch.png'),
            _os.path.join(base_dir, 'imagens', 'stitch.png'),
            _os.path.join(base_dir, 'images', 'stitch.png'),
            _os.path.join(base_dir, 'inicial', 'imagens', 'stitch.png'),
            _os.path.join(base_dir, 'inicial', 'images', 'stitch.png'),
        ]
        
        for path in possible_paths:
            if _os.path.exists(path):
                try:
                    _STITCH_ORIG = pygame.image.load(path).convert_alpha()
                    break
                except:
                    continue
        
        if _STITCH_ORIG is None:
            # Create a small dummy surface if image is missing to prevent crash
            _STITCH_ORIG = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(_STITCH_ORIG, (0, 0, 255), (50, 50), 40)
            
    return _STITCH_ORIG


_GAMEOVER_IMG = None
def _load_gameover():
    global _GAMEOVER_IMG
    if _GAMEOVER_IMG is None:
        # Check multiple possible paths based on user structure
        base_dir = _os.path.dirname(_os.path.abspath(__file__))
        possible_paths = [
            _os.path.join(base_dir, 'imagens', 'gameover.png'),
            _os.path.join(base_dir, 'images', 'gameover.png'),
            _os.path.join(base_dir, 'inicial', 'imagens', 'gameover.png'),
            _os.path.join(base_dir, 'inicial', 'images', 'gameover.png'),
        ]
        
        for path in possible_paths:
            if _os.path.exists(path):
                try:
                    _GAMEOVER_IMG = pygame.image.load(path).convert_alpha()
                    return _GAMEOVER_IMG
                except:
                    continue
        _GAMEOVER_IMG = False
    return _GAMEOVER_IMG

_OBJ_CACHE = {}
def _load_obj_img(name):
    if name not in _OBJ_CACHE:
        base_dir = _os.path.dirname(_os.path.abspath(__file__))
        possible_paths = [
            _os.path.join(base_dir, 'imagens', name),
            _os.path.join(base_dir, 'images', name),
            _os.path.join(base_dir, 'inicial', 'imagens', name),
            _os.path.join(base_dir, 'inicial', 'images', name),
        ]
        for path in possible_paths:
            if _os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Scale to a standard size for objects (approx 50-60px height)
                    target_h = 60
                    ratio = img.get_width() / img.get_height()
                    _OBJ_CACHE[name] = pygame.transform.smoothscale(img, (int(target_h * ratio), target_h))
                    return _OBJ_CACHE[name]
                except: continue
        _OBJ_CACHE[name] = False
    return _OBJ_CACHE[name]

def _scaled_stitch(w, h):
    key = (w, h)
    if key not in _STITCH_CACHE:
        _STITCH_CACHE[key] = pygame.transform.smoothscale(_load_stitch(), (w, h))
    return _STITCH_CACHE[key]

def draw_stitch(surf, cx, by, scale=1.0, moving=False, direction=1, frame=0, jumping=False):
    """Draw the real Stitch PNG with walk-bob, tilt and flip animations."""
    t = frame
    base_h = int(138 * scale)
    base_w = int(base_h * 1122 / 1687)

    # ── ANIMATION ──────────────────────────────────────────────────────────────
    if jumping:
        bob_y = -int(6 * scale)
        tilt  = -10 * (1 if direction >= 0 else -1)
        sx, sy = 1.08, 0.93
    elif moving:
        ph    = math.sin(t * 0.22)
        bob_y = int(abs(ph) * -5 * scale)
        tilt  = ph * 7 * direction
        sx, sy = 1.0, 1.0
    else:
        br    = math.sin(t * 0.06)
        bob_y = int(br * 2.5 * scale)
        tilt  = br * 3
        sx, sy = 1.0, 1.0

    img = _scaled_stitch(base_w, base_h)
    if sx != 1.0 or sy != 1.0:
        img = pygame.transform.smoothscale(img, (int(base_w*sx), int(base_h*sy)))
    if abs(tilt) > 0.5:
        img = pygame.transform.rotate(img, -tilt)
    if direction < 0:
        img = pygame.transform.flip(img, True, False)

    iw, ih = img.get_size()
    sh = pygame.Surface((int(iw * 0.72), 12), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 40), (0, 0, int(iw * 0.72), 12))
    surf.blit(sh, (cx - int(iw * 0.36), by - 6))
    surf.blit(img, (cx - iw // 2, by - ih + bob_y))

# ═══════════════════════════════════════════════════════════════════════════════
# COLLECTIBLE OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_hula(surf, cx, cy, anim):
    img = _load_obj_img('hula.png')
    if img:
        iw, ih = img.get_size()
        surf.blit(img, (cx - iw // 2, cy - ih))
    else:
        # Fallback procedural
        for i in range(7):
            a = math.radians(-60 + i*20)
            pygame.draw.ellipse(surf, (50,160,30), (cx-5+int(math.sin(a)*12), cy, 10, 20))
        pygame.draw.circle(surf, YELLOW, (cx, cy-10), 5)
    lbl = F_XS.render("Saia de Hula", True, WHITE)
    surf.blit(lbl, (cx-lbl.get_width()//2, cy+28))

def draw_ragdoll(surf, cx, cy):
    img = _load_obj_img('xepa.png')
    if img:
        iw, ih = img.get_size()
        surf.blit(img, (cx - iw // 2, cy - ih))
    else:
        # Fallback procedural
        pygame.draw.circle(surf, (255,220,180), (cx, cy-8), 12)
        pygame.draw.rect(surf, RED, (cx-8, cy, 16, 20))
    lbl = F_XS.render("Boneca Xepa", True, WHITE)
    surf.blit(lbl, (cx-lbl.get_width()//2, cy+26))


def draw_surfboard(surf, cx, cy):
    img = _load_obj_img('prancha.png')
    if img:
        iw, ih = img.get_size()
        surf.blit(img, (cx - iw // 2, cy - ih))
    else:
        pygame.draw.ellipse(surf, (220,90,40), (cx-9, cy-22, 18, 44))
        pygame.draw.ellipse(surf, YELLOW, (cx-5, cy-12, 10, 24))
    lbl = F_XS.render("Prancha", True, WHITE)
    surf.blit(lbl, (cx-lbl.get_width()//2, cy+26))

def draw_ukelele(surf, cx, cy):
    img = _load_obj_img('ukulele.png')
    if img:
        iw, ih = img.get_size()
        surf.blit(img, (cx - iw // 2, cy - ih))
    else:
        pygame.draw.ellipse(surf, ORANGE, (cx-11, cy-12, 22, 26))
        pygame.draw.rect(surf, (160,80,20), (cx-2, cy-32, 4, 24))
    lbl = F_XS.render("Ukulelê", True, WHITE)
    surf.blit(lbl, (cx-lbl.get_width()//2, cy+20))

# ═══════════════════════════════════════════════════════════════════════════════
# ENEMIES
# ═══════════════════════════════════════════════════════════════════════════════
def draw_gantu(surf, cx, by, frame=0):
    bob = int(math.sin(frame*0.14)*3)
    body_cy = by - int(45)
    head_cy = by - int(80) + bob
    # body
    pygame.draw.ellipse(surf, (55,58,75), (cx-22+2, body_cy-27+2, 44, 54))
    pygame.draw.ellipse(surf, GANTU_C,   (cx-22, body_cy-27, 44, 54))
    pygame.draw.rect(surf, (40,40,65), (cx-16, body_cy-14, 32, 28))
    # head
    pygame.draw.ellipse(surf, (55,58,75), (cx-26+2, head_cy-18+2, 52, 36))
    pygame.draw.ellipse(surf, GANTU_C,   (cx-26, head_cy-18, 52, 36))
    # eyes
    for ex in [cx-9, cx+9]:
        pygame.draw.circle(surf, RED,        (ex, head_cy-2+bob), 5)
        pygame.draw.circle(surf, (255,80,80),(ex, head_cy-2+bob), 3)
    # arms
    pygame.draw.ellipse(surf, GANTU_C, (cx-38, body_cy-22+bob, 18,34))
    pygame.draw.ellipse(surf, GANTU_C, (cx+20, body_cy-22+bob, 18,34))
    lbl = F_XS.render("Gantu !", True, (255,80,80))
    surf.blit(lbl, (cx-lbl.get_width()//2, by+4))

def draw_jumba(surf, cx, by, frame=0):
    bob = int(math.sin(frame*0.17+1)*3)
    body_cy = by - int(44)
    head_cy = by - int(78) + bob
    pygame.draw.ellipse(surf, (80,35,115), (cx-24+2, body_cy-26+2, 48,52))
    pygame.draw.ellipse(surf, JUMBA_C,    (cx-24, body_cy-26, 48,52))
    pygame.draw.ellipse(surf, (80,35,115),(cx-22+2, head_cy-20+2, 44,40))
    pygame.draw.ellipse(surf, JUMBA_C,   (cx-22, head_cy-20, 44,40))
    pygame.draw.rect(surf, WHITE, (cx-14, body_cy-16, 28,30))
    for ox,oy in [(-11,-8),(11,-8),(-6,4),(6,4)]:
        pygame.draw.circle(surf, YELLOW, (cx+ox, head_cy+oy+bob), 4)
        pygame.draw.circle(surf, BLACK,  (cx+ox, head_cy+oy+bob), 2)
    pygame.draw.ellipse(surf, JUMBA_C,(cx-36, body_cy-18+bob, 16,28))
    pygame.draw.ellipse(surf, JUMBA_C,(cx+20, body_cy-18+bob, 16,28))
    lbl = F_XS.render("Jumba !", True, YELLOW)
    surf.blit(lbl, (cx-lbl.get_width()//2, by+4))

def draw_pleakley(surf, cx, by, frame=0):
    bob = int(math.sin(frame*0.19+2)*4)
    body_cy = by - int(38)
    head_cy = by - int(66) + bob
    pygame.draw.ellipse(surf, (30,108,30),(cx-11+2, body_cy-22+2, 22,44))
    pygame.draw.ellipse(surf, PLEK_C,    (cx-11, body_cy-22, 22,44))
    pygame.draw.circle(surf, (30,108,30),(cx+2, head_cy+2), 15)
    pygame.draw.circle(surf, PLEK_C,    (cx, head_cy), 15)
    pygame.draw.circle(surf, (240,240,80),(cx, head_cy), 8)
    pygame.draw.circle(surf, BLACK, (cx, head_cy), 4)
    pygame.draw.circle(surf, WHITE, (cx+2, head_cy-3), 2)
    for i,a in enumerate([-30,0,30]):
        rad = math.radians(a-90)
        ax = cx+int(math.cos(rad)*14); ay = head_cy+int(math.sin(rad)*14)-6
        pygame.draw.line(surf, PLEK_C,(cx, head_cy-15+bob),(ax,ay),2)
        pygame.draw.circle(surf, PINK,(ax,ay),3)
    for i in range(3):
        px = cx-8+i*8
        pygame.draw.line(surf, PLEK_C,(px,body_cy+22+bob),(px-2+i*2,body_cy+36+bob),2)
    lbl = F_XS.render("Pleakley !", True, LIME)
    surf.blit(lbl, (cx-lbl.get_width()//2, by+4))

# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUNDS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_hawaii(surf, t=0):
    bg = _load_bg('fundo.png')
    if not bg: bg = _load_bg('bg_beach.png')
    
    if bg:
        surf.blit(bg, (0, 0))

    else:
        grad_fill(surf, (135, 206, 235), (255, 255, 255))
        pygame.draw.rect(surf, (240, 215, 168), (0, H-120, W, 120))


    # Improved Platforms - Tropical Wood Style
    plats = [pygame.Rect(90,H-195,165,18),pygame.Rect(310,H-255,145,18),
             pygame.Rect(525,H-215,165,18),pygame.Rect(725,H-280,140,18)]
    for p in plats:
        # Subtle outer glow for visibility
        for g in range(4, 0, -1):
            alpha_circle(surf, (255, 210, 0), (p.centerx, p.centery), p.width//2 + g*2, 20)
        
        # Main platform body (Dark tropical wood)
        rrect(surf, (110, 70, 30), p, 8)
        # Top highlight (Polished wood)
        pygame.draw.rect(surf, (160, 110, 60), (p.x, p.y, p.w, 6), border_radius=8)
        # Decorative flowers
        for fx in range(p.x+15, p.right-15, 25):
            pygame.draw.circle(surf, PINK, (fx, p.y+2), 4)
            pygame.draw.circle(surf, YELLOW, (fx, p.y+2), 1.5)
    return plats

def draw_space(surf, stars, t=0):
    # Deep space gradient
    grad_fill(surf,(8,5,22),(18,10,50))
    # Stars twinkling
    for (sx,sy,sb,sz) in stars:
        b = int(sb + math.sin(t*0.003+sx)*35); b=max(80,min(255,b))
        pygame.draw.circle(surf,(b,b,int(b*0.78)),(sx,sy),sz)
    # Nebulae
    for nx,ny,nc in [(180,160,(100,20,180)),(500,120,(20,80,200)),(760,200,(180,30,100))]:
        for dr in range(50,0,-10):
            alpha_circle(surf,nc,(nx,ny),dr,8)
    # Ringed planet
    pygame.draw.circle(surf,(200,100,50),(700,100),62)
    pygame.draw.circle(surf,(220,135,80),(700,100),54)
    pygame.draw.ellipse(surf,(155,80,35),(628,90,144,20))
    pygame.draw.ellipse(surf,(0,0,0,0),(636,92,128,16)) # ring gap illusion
    pygame.draw.ellipse(surf,(155,80,35,180),(636,94,128,12))
    # Floor
    grad_fill(surf,(25,35,85),(12,18,50),(0,H-58,W,58))
    pygame.draw.rect(surf,(0,210,210),(0,H-62,W,5))
    for gx in range(0,W,40):
        pygame.draw.line(surf,(35,55,130),(gx,H-58),(gx+20,H),1)
    # Platforms
    plats = [pygame.Rect(75,H-175,175,16),pygame.Rect(305,H-240,150,16),
             pygame.Rect(510,H-198,170,16),pygame.Rect(718,H-268,148,16)]
    for p in plats:
        pygame.draw.rect(surf,(40,52,95),p,border_radius=6)
        pygame.draw.rect(surf,(0,200,200),(p.x,p.y,p.w,6),border_radius=6)
        for lx in range(p.x+16,p.right-16,28):
            ph2 = (t*0.004+lx*0.05)%(2*math.pi)
            lc = (0,255,200) if math.sin(ph2)>0 else (0,80,80)
            pygame.draw.circle(surf,lc,(lx,p.y+2),3)
    return plats

# ═══════════════════════════════════════════════════════════════════════════════
# HUD
# ═══════════════════════════════════════════════════════════════════════════════
def draw_hud(surf, lives, level, clue):
    # Glass bar
    rrect(surf,(20,20,80),(0,0,W,56),0,200)
    pygame.draw.line(surf,(100,120,255),(0,56),(W,56),2)
    # Hearts
    for i in range(lives):
        hx = 14 + i*40
        pygame.draw.circle(surf,(220,20,60),(hx+8,12),9)
        pygame.draw.circle(surf,(220,20,60),(hx+24,12),9)
        pygame.draw.polygon(surf,(220,20,60),[(hx+2,18),(hx+16,30),(hx+30,18)])
        pygame.draw.circle(surf,(255,90,110),(hx+10,11),5)
    # Level badge
    rrect(surf,(60,40,160),(W//2-50,4,100,24),12,200)
    lt = F_SM.render(f"Fase  {level}", True, GOLD)
    surf.blit(lt,(W//2-lt.get_width()//2, 8))
    # Clue
    rrect(surf,(0,0,60),(0,56,W,26),0,180)
    pygame.draw.line(surf,(80,100,200),(0,82),(W,82),1)
    ct = F_SM.render(f"💡  {clue}", True, (220,240,255))
    surf.blit(ct,(W//2-ct.get_width()//2, 60))

def draw_overlay(surf, title, sub="", col=GOLD):
    s2 = pygame.Surface((W,H),pygame.SRCALPHA)
    s2.fill((0,0,25,210)); surf.blit(s2,(0,0))
    t1 = F_BIG.render(title, True, col)
    surf.blit(t1,(W//2-t1.get_width()//2, H//2-60))
    if sub:
        t2 = F_MID.render(sub, True, WHITE)
        surf.blit(t2,(W//2-t2.get_width()//2, H//2))
    t3 = F_SM.render("Pressione ENTER para continuar", True,(160,180,255))
    surf.blit(t3,(W//2-t3.get_width()//2, H//2+55))

def draw_title(surf, frame):
    grad_fill(surf,(10,30,100),(5,10,40))
    for i in range(80):
        random.seed(i)
        sx=random.randint(0,W); sy=random.randint(0,H-100)
        b=int(140+math.sin(frame*0.004+i)*80); b=max(80,min(255,b))
        pygame.draw.circle(surf,(b,b,int(b*0.75)),(sx,sy),random.randint(1,2))
    # animated waves
    for w2 in range(5):
        wpts=[]
        for x in range(0,W+10,10):
            y=H-100+int(math.sin((x+frame*2+w2*50)*0.022)*18)
            wpts.append((x,y))
        wpts+=[(W,H),(0,H)]
        ws=pygame.Surface((W,H),pygame.SRCALPHA)
        pygame.draw.polygon(ws,(*TEAL[:2],180,50+w2*18),wpts) if len(wpts)>2 else None
        surf.blit(ws,(0,0))
    # Stitch big
    draw_stitch(surf, W//2, 370, scale=2.2, moving=False, frame=frame)
    # Title text with shadow
    tl = F_TITLE.render("STITCH: OHANA ADVENTURE", True, BLACK)
    surf.blit(tl,(W//2-tl.get_width()//2+3, 33))
    tl = F_TITLE.render("STITCH: OHANA ADVENTURE", True, GOLD)
    surf.blit(tl,(W//2-tl.get_width()//2, 30))
    sub2 = F_MID.render("Experiência 626 – Missão Ohana!", True,(200,230,255))
    surf.blit(sub2,(W//2-sub2.get_width()//2, 80))
    # Controls panel
    rrect(surf,(20,20,80),(W//2-230,H-150,460,100),14,200)
    for i,line in enumerate(["← → / A D  Mover     ESPAÇO / ↑  Pular",
                              "Encontre o objeto da DICA para avançar!",
                              "Evite os inimigos você tem  ♥ 3 vidas"]):
        ls = F_SM.render(line, True,(210,230,255))
        surf.blit(ls,(W//2-ls.get_width()//2, H-142+i*28))
    pulse = 0.5+0.5*math.sin(frame*0.05)
    sc = F_MID.render("▶  ENTER para jogar  ◀", True,(int(180+75*pulse),int(220+35*pulse),255))
    surf.blit(sc,(W//2-sc.get_width()//2, H-168))

def draw_win(surf, frame):
    grad_fill(surf,(5,30,80),(2,12,35))
    random.seed(0)
    for _ in range(70):
        cx2=random.randint(0,W); cy2=(random.randint(0,H)+frame*2)%H
        pygame.draw.circle(surf,random.choice([GOLD,PINK,TEAL,LIME,ORANGE]),(cx2,cy2),random.randint(4,9))
    draw_stitch(surf, W//2, H//2+60, scale=2.0, moving=True, frame=frame)
    t2=F_BIG.render("🎉  VOCÊ VENCEU!  🎉",True,GOLD)
    surf.blit(t2,(W//2-t2.get_width()//2,55))
    s2=F_MID.render("Stitch encontrou sua Ohana! 💙",True,WHITE)
    surf.blit(s2,(W//2-s2.get_width()//2,100))
    m=F_SM.render("ENTER  jogar de novo  -  ESC sair",True,(180,210,255))
    surf.blit(m,(W//2-m.get_width()//2,H-55))

def draw_gameover(surf, frame):
    go_img = _load_gameover()
    if go_img:
        # Beautiful animated Game Over screen with custom art
        grad_fill(surf, (30, 0, 0), (10, 0, 0)) # Darker red background
        
        # Calculate animation
        bob = math.sin(frame * 0.05) * 12
        pulse = 1.0 + math.sin(frame * 0.04) * 0.03
        
        # Scale and center
        iw, ih = go_img.get_size()
        # Scale to fit screen while maintaining aspect ratio
        fit_scale = min(W * 0.8 / iw, H * 0.7 / ih) * pulse
        nw, nh = int(iw * fit_scale), int(ih * fit_scale)
        
        scaled_img = pygame.transform.smoothscale(go_img, (nw, nh))
        
        # Draw with shadow
        shadow_off = 8
        shadow = pygame.Surface((nw, nh), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        surf.blit(shadow, (W//2 - nw//2 + shadow_off, H//2 - nh//2 + shadow_off + bob))
        
        # Draw main image
        surf.blit(scaled_img, (W//2 - nw//2, H//2 - nh//2 + bob))
        
    else:
        # Fallback to original drawing if image not found
        grad_fill(surf,(50,5,5),(15,2,2))
        draw_stitch(surf, W//2, H//2+40, scale=1.8, frame=frame)
        t2=F_BIG.render("💔 GAME OVER 💔",True,(255,60,60))
        surf.blit(t2,(W//2-t2.get_width()//2,55))
        s2=F_MID.render("Gantu capturou o Stitch…",True,(255,150,150))
        surf.blit(s2,(W//2-s2.get_width()//2,100))
    
    # Common UI elements
    m=F_SM.render("ENTER  tentar de novo  -  ESC  sair",True,(220,180,180))
    surf.blit(m,(W//2-m.get_width()//2,H-55))

# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLES
# ═══════════════════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, color):
        self.x=float(x); self.y=float(y); self.color=color
        a=random.uniform(0,2*math.pi); sp=random.uniform(2,6)
        self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp-3
        self.life=random.randint(25,50); self.r=random.randint(3,7)
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.2; self.life-=1
    def draw(self, surf):
        alpha_circle(surf, self.color, (int(self.x),int(self.y)), self.r, int(self.life*5))

# ═══════════════════════════════════════════════════════════════════════════════
# GAME OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════
class Player:
    def __init__(self):
        self.x=80.0; self.y=float(H-60); self.vx=0.0; self.vy=0.0
        self.on_ground=False; self.lives=3; self.inv=0; self.frame=0
        self.moving=False; self.facing=1; self.jumping=False

    def rect(self):
        return pygame.Rect(int(self.x)-22, int(self.y)-88, 44, 88)

    def update(self, platforms):
        keys=pygame.key.get_pressed()
        sp=4.8
        if   keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx=-sp; self.facing=-1; self.moving=True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx= sp; self.facing= 1; self.moving=True
        else: self.vx*=0.75; self.moving=False
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy=-15; self.on_ground=False
        self.vy+=0.65; self.x+=self.vx; self.y+=self.vy
        self.x=max(22,min(W-22,self.x))
        self.on_ground=False; self.jumping=self.vy<0
        if self.y>=H-60: self.y=float(H-60); self.vy=0; self.on_ground=True
        r=self.rect()
        for p in platforms:
            if r.colliderect(p) and self.vy>=0 and (r.bottom-self.vy)<=p.top+8:
                self.y=float(p.top); self.vy=0; self.on_ground=True
        if self.inv>0: self.inv-=1
        self.frame+=1

    def draw(self, surf):
        if self.inv>0 and (self.frame//4)%2==0: return
        draw_stitch(surf, int(self.x), int(self.y), scale=1.06,
                    moving=self.moving, direction=self.facing,
                    frame=self.frame, jumping=self.jumping)

    def hurt(self):
        if self.inv==0: self.lives-=1; self.inv=90


class Obj:
    def __init__(self, x, y, kind, correct):
        self.x=float(x); self.y=float(y); self.kind=kind
        self.correct=correct; self.collected=False; self.anim=0

    def rect(self): return pygame.Rect(int(self.x)-22,int(self.y)-52,44,52)

    def update(self): self.anim+=1

    def draw(self, surf):
        if self.collected: return
        pulse=abs(math.sin(self.anim*0.06))
        col=GOLD if self.correct else (200,200,200)
        alpha_circle(surf,col,(int(self.x),int(self.y)-26),int(22+pulse*8),60)
        fy=self.y+math.sin(self.anim*0.07)*5
        if   self.kind=='hula':      draw_hula(surf,int(self.x),int(fy),self.anim)
        elif self.kind=='ragdoll':   draw_ragdoll(surf,int(self.x),int(fy))
        elif self.kind=='surfboard': draw_surfboard(surf,int(self.x),int(fy))
        elif self.kind=='ukelele':   draw_ukelele(surf,int(self.x),int(fy))


class Enemy:
    SPEEDS={'gantu':1.8,'jumba':1.3,'pleakley':2.5}
    def __init__(self,x,y,kind,dir=1):
        self.x=float(x); self.y=float(y); self.kind=kind; self.dir=dir
        self.speed=self.SPEEDS[kind]; self.frame=0
    def rect(self): return pygame.Rect(int(self.x)-24,int(self.y)-78,48,78)
    def update(self,lb,rb):
        self.x+=self.speed*self.dir
        if self.x<lb or self.x>rb: self.dir*=-1
        self.frame+=1
    def draw(self,surf):
        if   self.kind=='gantu':    draw_gantu(surf,int(self.x),int(self.y),self.frame)
        elif self.kind=='jumba':    draw_jumba(surf,int(self.x),int(self.y),self.frame)
        elif self.kind=='pleakley': draw_pleakley(surf,int(self.x),int(self.y),self.frame)

# ═══════════════════════════════════════════════════════════════════════════════
# LEVEL CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
def build_level(lvl):
    if lvl==1:
        clue="Qual dança havaiana Lilo adora praticar? Ache o objeto!"
        objs=[Obj(165,H-210,'surfboard',False),
              Obj(385,H-272,'hula',True),
              Obj(605,H-232,'ukelele',False)]
        enes=[Enemy(280,H-60,'gantu',1),Enemy(560,H-60,'pleakley',-1)]
    else:
        clue="Qual é o brinquedo favorito de Lilo? Encontre-o!"
        objs=[Obj(150,H-192,'ukelele',False),
              Obj(380,H-258,'surfboard',False),
              Obj(608,H-214,'ragdoll',True)]
        enes=[Enemy(250,H-60,'jumba',1),Enemy(480,H-60,'gantu',-1),Enemy(730,H-60,'pleakley',1)]
    return clue,objs,enes

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    random.seed(99)
    stars=[(random.randint(0,W),random.randint(0,H-80),random.randint(100,200),random.randint(1,2))
           for _ in range(130)]
    state='title'; level=1; frame=0
    player=Player(); clue,objs,enes=build_level(1)
    particles=[]; wrong_timer=0

    while True:
        clock.tick(FPS); frame+=1
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if state=='title' and ev.key==pygame.K_RETURN:
                    state='play'; level=1; player=Player()
                    clue,objs,enes=build_level(1); particles=[]
                elif state=='levelup' and ev.key==pygame.K_RETURN:
                    level=2; player=Player()
                    clue,objs,enes=build_level(2); particles=[]; state='play'
                elif state in ('win','gameover') and ev.key==pygame.K_RETURN:
                    state='title'

        # ── SCREENS ──────────────────────────────────────────────────────────
        if state=='title':    draw_title(screen,frame); pygame.display.flip(); continue
        if state=='win':      draw_win(screen,frame);   pygame.display.flip(); continue
        if state=='gameover': draw_gameover(screen,frame); pygame.display.flip(); continue
        if state=='levelup':
            plats = draw_hawaii(screen,frame) if level==1 else draw_space(screen,stars,frame)
            draw_overlay(screen,"🌟 FASE 1 CONCLUÍDA!","Saia de Hula encontrada! Próxima: Espaço! 🚀",GOLD)
            pygame.display.flip(); continue

        # ── PLAY ─────────────────────────────────────────────────────────────
        if level==1: plats=draw_hawaii(screen,frame)
        else:        plats=draw_space(screen,stars,frame)

        # Update & draw objects
        for obj in objs: obj.update(); obj.draw(screen)
        # Update & draw enemies
        for en in enes:
            en.update(28, W-28); en.draw(screen)
            if player.rect().colliderect(en.rect()):
                player.hurt()
                if player.lives<=0: state='gameover'

        # Player
        player.update(plats); player.draw(screen)

        # Collect check
        for obj in objs:
            if not obj.collected and player.rect().colliderect(obj.rect()):
                obj.collected=True
                for _ in range(22):
                    particles.append(Particle(obj.x,obj.y-26,GOLD if obj.correct else (200,80,80)))
                if obj.correct:
                    state='levelup' if level==1 else 'win'
                else:
                    player.hurt(); wrong_timer=80
                    if player.lives<=0: state='gameover'

        # Particles
        for p in particles[:]:
            p.update(); p.draw(screen)
            if p.life<=0: particles.remove(p)

        # HUD
        draw_hud(screen, player.lives, level, clue)

        # Wrong object message
        if wrong_timer>0:
            wrong_timer-=1
            ms=F_MID.render("❌  Objeto errado! Tome cuidado!", True, (255,80,80))
            rrect(screen,(50,0,0),(W//2-ms.get_width()//2-10,H//2-20,ms.get_width()+20,36),8,180)
            screen.blit(ms,(W//2-ms.get_width()//2,H//2-16))

        pygame.display.flip()

if __name__=='__main__':
    main()
