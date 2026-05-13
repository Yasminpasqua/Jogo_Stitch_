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

# ── PHASES ─────────────────────────────────────────────────────────────────────
PHASES = [
    {"id": 1, "obj": "hula",      "clue": "Encontre a Saia de Hula escondida na Casa!"},
    {"id": 2, "obj": "xepa",      "clue": "Procure a Boneca Xepa no Quarto da Lilo!"},
    {"id": 3, "obj": "ukulele",   "clue": "O Jumba sumiu com o Ukulele! Procure na Garagem!"},
    {"id": 4, "obj": "surfboard", "clue": "Hora de surfar! Ache a Prancha na Praia!"}
]

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
                    if name == 'casa_ext.png':
                        _OBJ_CACHE[name] = pygame.transform.smoothscale(img, (220, 200))
                    elif name in ['casa_int.png', 'casa_kitchen.png', 'casa_bedroom.png']:
                        _OBJ_CACHE[name] = pygame.transform.smoothscale(img, (W, H))
                    else:
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

def draw_stitch_cam(surf, cx, by, cam_x=0, scale=1.0, moving=False, direction=1, frame=0, jumping=False):
    draw_stitch(surf, cx - cam_x, by, scale, moving, direction, frame, jumping)

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
def draw_hawaii(surf, t=0, offset_x=0):
    bg = _load_bg('fundo.png')
    if bg:
        surf.blit(bg, (offset_x, 0))
    else:
        grad_fill(surf, (135, 206, 235), (255, 255, 255))
        pygame.draw.rect(surf, (238, 214, 175), (offset_x, H-60, W, 60))
    return [pygame.Rect(offset_x, H-60, W, 60)]

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
def draw_hud(surf, lives, level, clue, score=0, msg=""):
    # Bottom Shadow Gradient
    for i in range(80):
        alpha = int((i/80.0) * 120)
        pygame.draw.line(surf, (0,0,0,alpha), (0, H-i), (W, H-i))
    
    # HUD Bar Top
    rrect(surf,(10,15,35),(10,10,W-20,46),15,180)
    pygame.draw.rect(surf,(100,150,255),(10,10,W-20,46),2,border_radius=15)

    for i in range(lives):
        hx=30+i*35
        pygame.draw.circle(surf,(220,20,60),(hx+8,25),8)
        pygame.draw.circle(surf,(220,20,60),(hx+20,25),8)
        pygame.draw.polygon(surf,(220,20,60),[(hx+2,30),(hx+14,40),(hx+26,30)])
    
    lt=F_MID.render(f"Objetivo {level}",True,GOLD)
    surf.blit(lt,(W//2-lt.get_width()//2,18))
    
    sc=F_MID.render(f"⭐ {score}",True,GOLD)
    surf.blit(sc,(W-sc.get_width()-35,18))
    
    # Interaction Key Prompt (Small floating 'E')
    if msg:
        tw = F_SM.render("E", True, BLACK)
        bx, by = W//2 - 15, H-120
        pygame.draw.circle(surf, GOLD, (bx+15, by+15), 18)
        pygame.draw.circle(surf, WHITE, (bx+15, by+15), 15)
        surf.blit(tw, (bx+15-tw.get_width()//2, by+15-tw.get_height()//2))
        
        lw = F_SM.render(msg, True, WHITE)
        surf.blit(lw, (W//2-lw.get_width()//2, H-80))

def draw_dialog(surf, text, name="Lilo"):
    # RPG Style Dialog Box
    dh = 120
    rrect(surf, (10, 10, 30), (50, H-dh-20, W-100, dh), 15, 230)
    pygame.draw.rect(surf, (100, 150, 255), (50, H-dh-20, W-100, dh), 3, border_radius=15)
    
    # Name Tag
    rrect(surf, GOLD, (70, H-dh-35, 100, 30), 8)
    nt = F_SM.render(name, True, BLACK)
    surf.blit(nt, (120-nt.get_width()//2, H-dh-30))
    
    # Text wrapping
    words = text.split()
    lines = []
    curr = ""
    for w in words:
        if len(curr + w) < 65: curr += w + " "
        else: lines.append(curr); curr = w + " "
    lines.append(curr)
    
    for i, l in enumerate(lines[:3]):
        tt = F_MID.render(l.strip(), True, WHITE)
        surf.blit(tt, (80, H-dh+5+i*30))
    
    prompt = F_XS.render("Pressione ESPAÇO para continuar", True, (150, 180, 255))
    surf.blit(prompt, (W-100-prompt.get_width(), H-45))

def draw_house_ext(surf, x, y):
    img = _load_obj_img('casa_ext.png')
    if img:
        surf.blit(img, (x, y - img.get_height()))
    else:
        # Fallback if image fails
        rrect(surf, (150, 100, 50), (x, y-120, 160, 120), 5)
        pygame.draw.polygon(surf, (100, 50, 20), [(x-20, y-120), (x+80, y-180), (x+180, y-120)])

def draw_interior(surf, room_type='casa_int.png', offset_x=0):
    img = _load_obj_img(room_type)
    if img:
        surf.blit(img, (offset_x, 0))
    else:
        pygame.draw.rect(surf, (80, 60, 40), (offset_x, 0, W, H))

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
        self.target_interact = None


    def rect(self):
        return pygame.Rect(int(self.x)-22, int(self.y)-88, 44, 88)

    def update(self, platforms, room_width=W):
        keys=pygame.key.get_pressed()
        sp=4.8
        if   keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx=-sp; self.facing=-1; self.moving=True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx= sp; self.facing= 1; self.moving=True
        else: self.vx*=0.75; self.moving=False

        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy=-15; self.on_ground=False
        self.vy+=0.65; self.x+=self.vx; self.y+=self.vy
        self.x=max(22,min(room_width-22,self.x))
        self.on_ground=False; self.jumping=self.vy<0
        if self.y>=H-60: self.y=float(H-60); self.vy=0; self.on_ground=True
        r=self.rect()
        for p in platforms:
            if r.colliderect(p) and self.vy>=0 and (r.bottom-self.vy)<=p.top+8:
                self.y=float(p.top); self.vy=0; self.on_ground=True
        if self.inv>0: self.inv-=1
        self.frame+=1

    def draw(self, surf, cam_x=0):
        if self.inv>0 and (self.frame//4)%2==0: return
        draw_stitch(surf, int(self.x - cam_x), int(self.y), scale=1.06,
                    moving=self.moving, direction=self.facing,
                    frame=self.frame, jumping=self.jumping)

    def hurt(self):
        if self.inv==0: 
            self.lives-=1; self.inv=90

class InteractivePoint:
    def __init__(self, x, y, label, action='inspect', hidden_obj=None):
        self.rect = pygame.Rect(x-40, y-100, 80, 100)
        self.x = x; self.y = y
        self.label = label
        self.action = action
        self.hidden_obj = hidden_obj

    def draw(self, surf, cam_x=0):
        pass # Hidden points are now just for portals or simple inspection




class Obj:
    def __init__(self, x, y, kind, correct):
        self.x=float(x); self.y=float(y); self.kind=kind
        self.correct=correct; self.collected=False; self.anim=0

    def rect(self): return pygame.Rect(int(self.x)-22,int(self.y)-52,44,52)

    def update(self): self.anim+=1

    def draw(self, surf, cam_x=0):
        if self.collected: return
        pulse=abs(math.sin(self.anim*0.06))
        col=GOLD if self.correct else (200,200,200)
        alpha_circle(surf,col,(int(self.x-cam_x),int(self.y)-26),int(15+pulse*5),40)
        fy=self.y+math.sin(self.anim*0.07)*5
        if   self.kind=='hula':      draw_hula(surf,int(self.x-cam_x),int(fy),self.anim)
        elif self.kind=='ragdoll' or self.kind=='xepa': draw_ragdoll(surf,int(self.x-cam_x),int(fy))
        elif self.kind=='surfboard' or self.kind=='prancha': draw_surfboard(surf,int(self.x-cam_x),int(fy))
        elif self.kind=='ukelele' or self.kind=='ukulele':   draw_ukelele(surf,int(self.x-cam_x),int(fy))
        lbl = F_XS.render(self.kind.title(), True, WHITE)
        surf.blit(lbl, (self.x - cam_x - lbl.get_width()//2, fy - 80))

class Enemy:
    SPEEDS={'gantu':1.5,'jumba':1.0,'pleakley':2.2}
    CHASE_SPEEDS={'gantu':2.2,'jumba':1.8,'pleakley':2.8}
    
    def __init__(self,x,y,kind,dir=1):
        self.x=float(x); self.y=float(y); self.kind=kind; self.dir=dir
        self.speed=self.SPEEDS[kind]; self.frame=0
        self.state = 'patrol' # 'patrol' or 'chase'
        self.detect_range = 140
        self.detect_timer = 0 # Countdown before chasing



    def rect(self): return pygame.Rect(int(self.x)-24,int(self.y)-78,48,78)
    
    def update(self,lb,rb, player_x=None):
        can_see = player_x and abs(self.x - player_x) < self.detect_range
        
        if can_see:
            self.detect_timer = min(30, self.detect_timer + 1)
        else:
            self.detect_timer = max(0, self.detect_timer - 1)

        if self.detect_timer >= 20: # Must see for ~20 frames
            self.state = 'chase'
            self.dir = 1 if player_x > self.x else -1
            self.speed = self.CHASE_SPEEDS[self.kind]
        else:
            self.state = 'patrol'
            self.speed = self.SPEEDS[self.kind]

        self.x+=self.speed*self.dir
        if self.state == 'patrol':
            if self.x<lb or self.x>rb: self.dir*=-1
        self.frame+=1


    def draw(self, surf, cam_x=0):
        if self.state == 'chase':
            alpha = int(155 + 100 * math.sin(self.frame * 0.2))
            pygame.draw.circle(surf, (255, 0, 0, alpha), (int(self.x-cam_x), int(self.y-100)), 12)
            lbl = F_XS.render("!", True, WHITE)
            surf.blit(lbl, (self.x-cam_x-lbl.get_width()//2, self.y-108))
        elif self.detect_timer > 0:
            # Yellow warning meter
            pygame.draw.circle(surf, YELLOW, (int(self.x-cam_x), int(self.y-100)), int(4 + self.detect_timer//3))

        if   self.kind=='gantu':    draw_gantu(surf,int(self.x-cam_x),int(self.y),self.frame)

        elif self.kind=='jumba':    draw_jumba(surf,int(self.x-cam_x),int(self.y),self.frame)
        elif self.kind=='pleakley': draw_pleakley(surf,int(self.x-cam_x),int(self.y),self.frame)

# ── ROOM SYSTEM ────────────────────────────────────────────────────────────────
class Portal:
    def __init__(self, x, y, w, h, target_room, target_pos, label="ENTRAR"):
        self.rect = pygame.Rect(x, y, w, h)
        self.target_room = target_room
        self.target_pos = target_pos
        self.label = label

class Room:
    def __init__(self, name, bg_type, objects, enemies, portals, platforms, interactives=[], width=W):
        self.name = name
        self.bg_type = bg_type
        self.objects = objects
        self.enemies = enemies
        self.portals = portals
        self.platforms = platforms
        self.interactives = interactives
        self.width = width

def build_adventure():
    rooms = {
        'island': Room('Ilha Tropical', 'hawaii', [], 
                     [Enemy(550, H-60, 'gantu', 1), Enemy(1100, H-60, 'pleakley', -1)], 
                     [Portal(320, H-150, 100, 150, 'house_entrance', (100, H-100), "ENTRAR NA CASA")],
                     [pygame.Rect(600,H-195,165,18)],
                     interactives=[],
                     width=W*2),
        
        'house_entrance': Room('Sala da Lilo', ['casa_int.png'], 
                      [Obj(400, H-60, 'hula', True), Obj(150, H-60, 'ragdoll', False), Obj(700, H-60, 'ukelele', False)], 
                      [], 
                      [Portal(10, 0, 80, H, 'island', (320, H-100), "SAIR"),
                       Portal(W-90, 0, 80, H, 'house_kitchen', (100, H-100), "COZINHA")],
                      [pygame.Rect(350, H-160, 200, 18), pygame.Rect(100, H-220, 150, 18), 
                       pygame.Rect(600, H-250, 200, 18)],
                      interactives=[],
                      width=W),

        'house_kitchen': Room('Cozinha', ['casa_kitchen.png'], 
                      [Obj(700, H-60, 'ukelele', True), Obj(300, H-180, 'hula', False), Obj(100, H-60, 'prancha', False)], 
                      [], 
                      [Portal(10, 0, 80, H, 'house_entrance', (W-150, H-100), "SALA"),
                       Portal(W-90, 0, 80, H, 'house_bedroom', (100, H-100), "QUARTO")],
                      [pygame.Rect(300, H-180, 250, 20), pygame.Rect(650, H-250, 150, 18),
                       pygame.Rect(0, H-200, 180, 18)],
                      interactives=[],
                      width=W),
                      
        'house_bedroom': Room('Quarto da Lilo', ['casa_bedroom.png'], 
                      [Obj(300, H-220, 'xepa', True), Obj(600, H-60, 'ragdoll', False), Obj(150, H-60, 'hula', False)], 
                      [], 
                      [Portal(10, 0, 80, H, 'house_kitchen', (W-150, H-100), "COZINHA")],
                      [pygame.Rect(200, H-220, 200, 20), pygame.Rect(500, H-150, 180, 18),
                       pygame.Rect(750, H-280, 150, 18)],
                      interactives=[],
                      width=W),
    }
    return rooms

def main():
    random.seed(99)
    state='title'; frame=0; score=0
    player=Player()
    rooms = build_adventure()
    current_room_key = 'island'
    level = 1
    clue = PHASES[level-1]["clue"]
    particles=[]; flash_timer=0; flash_col=(255,0,0)
    dialog_text = ""; dialog_active = False
    cam_x = 0

    while True:
        dt=clock.tick(FPS); frame+=1
        room = rooms[current_room_key]
        hud_msg = ""
        
        target_cam_x = player.x - W//2
        target_cam_x = max(0, min(target_cam_x, room.width - W))
        cam_x += (target_cam_x - cam_x) * 0.1

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if state=='title' and ev.key==pygame.K_RETURN:
                    state='play'; score=0
                    dialog_text = "Stitch! Encontre os objetos da Ohana. Nem tudo é o que parece ser!"
                    dialog_active = True
                elif state in('win','gameover') and ev.key==pygame.K_RETURN:
                    state='title'; player=Player(); level=1; current_room_key='island'
                
                if dialog_active and ev.key==pygame.K_SPACE:
                    dialog_active = False
                
                if state=='play' and not dialog_active and ev.key==pygame.K_e:
                    for p in room.portals:
                        if player.rect().colliderect(p.rect):
                            current_room_key = p.target_room
                            player.x, player.y = p.target_pos
                            cam_x = player.x - W//2
                            break

        if state=='title':    draw_title(screen,frame); pygame.display.flip(); continue
        if state=='win':      draw_win(screen,frame);   pygame.display.flip(); continue
        if state=='gameover': draw_gameover(screen,frame); pygame.display.flip(); continue

        if room.bg_type == 'hawaii': 
            for i in range(2): 
                draw_hawaii(screen, frame, offset_x=i*W - cam_x)
            draw_house_ext(screen, 320 - cam_x, H-60)
        else:
            for i, bg in enumerate(room.bg_type):
                draw_interior(screen, bg, offset_x=i*W - cam_x)
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.rect(s, (30, 20, 0, 40), (0, 0, W, H))
            screen.blit(s, (0,0))

        for p in room.portals:
            if player.rect().colliderect(p.rect):
                hud_msg = p.label

        for obj in room.objects[:]:
            obj.update(); obj.draw(screen, cam_x)
            if not obj.collected and player.rect().colliderect(obj.rect()):
                if obj.kind == PHASES[level-1]["obj"]:
                    obj.collected = True
                    score += 500
                    level += 1
                    flash_timer = 30
                    if level > len(PHASES):
                        state = 'win'
                    else:
                        if level == 2: current_room_key = 'house_bedroom'; player.x, player.y = 100, H-100
                        elif level == 3: current_room_key = 'house_kitchen'; player.x, player.y = 100, H-100
                        elif level == 4: current_room_key = 'island'; player.x, player.y = 80, H-60
                        
                        cam_x = player.x - W//2
                        dialog_text = f"MUITO BEM! Você achou! Próxima missão: {PHASES[level-1]['clue']}"
                        dialog_active = True
                        clue = PHASES[level-1]["clue"]
                else:
                    dialog_text = f"Humm... {obj.kind.title()} não é o que estamos procurando. Continue tentando!"
                    dialog_active = True
                    player.x -= player.facing * 50

        for en in room.enemies:
            en.update(50, room.width-50, player_x=player.x); en.draw(screen, cam_x)
            if player.rect().colliderect(en.rect()):
                player.hurt()
                if player.lives<=0: state='gameover'

        if not dialog_active:
            player.update(room.platforms, room_width=room.width)
        player.draw(screen, cam_x)

        if flash_timer>0:
            flash_timer-=1
            sf=pygame.Surface((W,H),pygame.SRCALPHA)
            sf.fill((255,215,0,flash_timer*8)); screen.blit(sf,(0,0))

        draw_hud(screen, player.lives, level, clue, score, hud_msg)
        if dialog_active: draw_dialog(screen, dialog_text, "Lilo")
        pygame.display.flip()

if __name__=='__main__':
    main()


