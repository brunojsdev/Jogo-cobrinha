"""
  ==========================================================================
  ÍNDICE DO ARQUIVO (Python - Brython)
  1. CONFIGURAÇÕES E ESTADO DO JOGO
  2. MOTOR DE PIXEL ART PROCEDURAL (Sprites e Paletas)
  3. LÓGICA AUXILIAR DO JOGO (Comida, Pausa, Game Over)
  4. SISTEMA DE CONTROLES (Teclado, Touch e Mobile)
  5. CICLO DE VIDA E RENDERIZAÇÃO (Update e Start)
  ==========================================================================
"""

from browser import document, window, html
import random

# ==========================================================================
# 1. CONFIGURAÇÕES E ESTADO DO JOGO
# ==========================================================================

canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")
box = 20
snake = []
food = {}
score = 0
direction = "RIGHT"
game_loop_ref = None
is_game_over = False
is_paused = False
last_tap_time = 0
tap_count = 0
last_theme_is_light = None

# Lógica de cores dinâmicas para a cobra (HSL)
SNAKE_COLORS = []
def update_snake_colors(is_light, score_val=0):
    global SNAKE_COLORS
    base_hue = 235 if is_light else 255
    current_hue = (base_hue + score_val * 2) % 360
    SNAKE_COLORS = [f"hsl({current_hue}, 100%, {min(95, 60 + (i / 40) * 30)}%)" for i in range(200)]

update_snake_colors(False)

offscreen_canvas = html.CANVAS(width=canvas.width, height=canvas.height)
offscreen_ctx = offscreen_canvas.getContext("2d")

DECORATIVE_STARS = [
    (50, 50), (300, 80), (450, 400), (200, 350),
    (100, 450), (420, 30), (70, 320), (490, 10),
    (250, 250), (370, 370), (150, 150), (400, 200),
    (80, 400), (320, 100), (180, 480), (480, 50)
]

# ==========================================================================
# 2. MOTOR DE PIXEL ART PROCEDURAL (Sprites e Paletas)
# Define a estética espacial do fundo do jogo
# ==========================================================================

# 1. Matrizes de Sprites ( . = Transparente )
# Os números e letras representam as cores de cada pixel do planeta
SPRITE_EARTH = [
    "    222222    ",
    "  1124422233  ",
    " 111444422333 ",
    " 112244222233 ",
    "22222222442333",
    "22444224444333",
    "22444422442353",
    "22244222223553",
    " 222222233353 ",
    " 222222333333 ",
    "  2233333333  ",
    "    333333    "
]

SPRITE_SATURN = [
    "        222222        ",
    "      1122222233      ",
    "     111444444333     ",
    "  rrr111222222333rrr  ",
    " rrrr222444444333rrrr ",
    "rrrrR222222222333Rrrrr",
    "RRRRRRRRRRRRRRRRRRRRRR", # Frente do anel
    "  RRRRRRRRRRRRRRRRRR  ",
    "     333333333333     ", # Sombra projetada pelo anel
    "     222223333333     ",
    "      2233333333      ",
    "        333333        "
]

SPRITE_MOON = [
    "    222222    ",
    "  1112222233  ",
    " 114422222333 ",
    " 114422244333 ",
    "22222224444333",
    "22244222442333",
    "22444422223333",
    "22244222233353",
    " 2222224433553",
    " 222224444353 ",
    "  2233244333  ",
    "    333333    "
]

# 2. Paletas de Cores (Derivadas da sua paleta original)
PALETTES = {
    "earth": { # Baseado em Indigo Profundo e Roxo
        "1": "#312e81", # Brilho
        "2": "#1e1b4b", # Base
        "3": "#0f0c29", # Sombra
        "4": "#4c1d95", # Continentes/Textura
        "5": "#2e1065", # Sombra da Textura
    },
    "saturn": { # Baseado em Azul Slate
        "1": "#334155", # Brilho
        "2": "#1e293b", # Base
        "3": "#101620", # Sombra
        "4": "#0f172a", # Faixas de Gás
        "r": "#1e1b4b", # Anel de Trás
        "R": "#312e81", # Anel da Frente
    },
    "moon": { # Baseado em Roxo Escuro
        "1": "#6d28d9", # Brilho intenso
        "2": "#4c1d95", # Base
        "3": "#2e1065", # Sombra
        "4": "#312e81", # Crateras
        "5": "#1a1840", # Sombra das Crateras
    }
} 

# 3. Renderizador de Pixel Art
def draw_pixel_sprite(target_ctx, x, y, pixel_size, sprite, palette):
    for row_idx, row in enumerate(sprite):
        for col_idx, char in enumerate(row):
            if char != ' ': # Se não for espaço vazio (transparente)
                target_ctx.fillStyle = palette.get(char, "#000000")
                target_ctx.fillRect(x + col_idx * pixel_size, y + row_idx * pixel_size, pixel_size, pixel_size)


def draw_space_background_once():
    """Desenha o cenário de fundo estilo pixel art UMA VEZ no off-screen canvas."""
    is_light = document.body.classList.contains("light-mode")
    offscreen_ctx.fillStyle = "#fff9c4" if is_light else "#040014"
    offscreen_ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    offscreen_ctx.save()
    # Mantém a sua lógica original para misturar com o tema
    offscreen_ctx.globalAlpha = 0.2 if is_light else 0.22 

    # 1. Estrelas Distantes
    offscreen_ctx.fillStyle = "#000000" if is_light else "#ffffff"
    for sx, sy in DECORATIVE_STARS:
        offscreen_ctx.fillRect(sx, sy, 4, 4)

    # 2. Planetas em Pixel Art Detalhado (Usando o Motor de Sprites)
    # Sintaxe: (contexto, X, Y, Tamanho_do_Pixel, Sprite, Paleta)
    draw_pixel_sprite(offscreen_ctx, 350, 70, 6, SPRITE_EARTH, PALETTES["earth"])   # Planeta Terra-like (Grande)
    draw_pixel_sprite(offscreen_ctx, 160, 200, 5, SPRITE_SATURN, PALETTES["saturn"]) # Planeta Saturno-like (Médio)
    draw_pixel_sprite(offscreen_ctx, 70, 360, 4, SPRITE_MOON, PALETTES["moon"])      # Lua com Crateras (Pequeno)
    
    # Podemos reusar os sprites com paletas e tamanhos diferentes para variar!
    draw_pixel_sprite(offscreen_ctx, 410, 380, 3, SPRITE_EARTH, PALETTES["saturn"])  # Terra-like Azulada
    draw_pixel_sprite(offscreen_ctx, 280, 420, 3, SPRITE_MOON, PALETTES["earth"])    # Lua Indigo
    draw_pixel_sprite(offscreen_ctx, 380, 260, 2, SPRITE_SATURN, PALETTES["moon"])   # Mini Saturno Roxo

    # 3. Pequenas Luas Sombrias (Pixels únicos espalhados para dar profundidade)
    offscreen_ctx.fillStyle = "#334155"
    offscreen_ctx.fillRect(150, 320, 6, 6)
    offscreen_ctx.fillRect(300, 160, 4, 4)
    offscreen_ctx.fillRect(50, 100, 5, 5)
    offscreen_ctx.fillRect(450, 350, 7, 7)
    offscreen_ctx.fillRect(20, 20, 3, 3)
    offscreen_ctx.fillRect(470, 470, 5, 5)

    offscreen_ctx.restore()

# ==========================================================================
# 3. LÓGICA AUXILIAR DO JOGO (Comida, Pausa, Game Over)
# ==========================================================================

def spawn_food():
    while True:
        fx = random.randint(0, (canvas.width // box) - 1) * box
        fy = random.randint(0, (canvas.height // box) - 1) * box
        if not any(s['x'] == fx and s['y'] == fy for s in snake):
            return {"x": fx, "y": fy}

def toggle_pause():
    global is_paused
    if not is_game_over and game_loop_ref is not None:
        is_paused = not is_paused
        document["pause-ui"].style.display = "flex" if is_paused else "none"

def game_over():
    global is_game_over
    is_game_over = True
    window.clearInterval(game_loop_ref)
    document["game-over-ui"].style.display = "flex"

def set_dir(new_dir):
    global direction
    pairs = {"LEFT": "RIGHT", "RIGHT": "LEFT", "UP": "DOWN", "DOWN": "UP"}
    if new_dir != pairs.get(direction):
        direction = new_dir

# ==========================================================================
# 4. SISTEMA DE CONTROLES (Teclado, Touch e Mobile)
# ==========================================================================

def key_press(ev):
    global is_game_over, is_paused
    key_map = {37: "LEFT", 38: "UP", 39: "RIGHT", 40: "DOWN"}
    if ev.keyCode in key_map:
        ev.preventDefault()
        set_dir(key_map[ev.keyCode])
    elif ev.keyCode == 32:
        ev.preventDefault()
        toggle_pause()
    elif ev.keyCode == 13:
        ev.preventDefault()
        if is_game_over or game_loop_ref is None:
            start()

document.bind("keydown", key_press)

t_start = [0, 0]
def t_start_h(ev):
    global t_start
    t_start = [ev.touches[0].clientX, ev.touches[0].clientY]
    if ev.target.id == "gameCanvas":
        ev.preventDefault()

def t_end_h(ev):
    global last_tap_time, tap_count
    dx = ev.changedTouches[0].clientX - t_start[0]
    dy = ev.changedTouches[0].clientY - t_start[1]
    
    if abs(dx) > 25 or abs(dy) > 25:
        if abs(dx) > abs(dy):
            set_dir("RIGHT" if dx > 0 else "LEFT")
        else:
            set_dir("DOWN" if dy > 0 else "UP")
        if ev.target.id == "gameCanvas":
            ev.preventDefault()

    now = window.Date.now()
    if now - last_tap_time < 300:
        tap_count += 1
    else:
        tap_count = 1
    last_tap_time = now
    
    if tap_count == 3:
        toggle_pause()
        tap_count = 0

canvas.bind("touchstart", t_start_h)
canvas.bind("touchend", t_end_h)

def bind_btn(id, d):
    def h_start(e): 
        e.preventDefault()
        set_dir(d)
        document[id].classList.add("glow-active")
        
    def h_end(e):
        e.preventDefault()
        document[id].classList.remove("glow-active")
        
    document[id].bind("touchstart", h_start)
    document[id].bind("mousedown", h_start)
    document[id].bind("touchend", h_end)
    document[id].bind("mouseup", h_end)
    document[id].bind("mouseleave", h_end)

for b, d in [("btn-up","UP"), ("btn-down","DOWN"), ("btn-left","LEFT"), ("btn-right","RIGHT")]:
    bind_btn(b, d)

# ==========================================================================
# 5. CICLO DE VIDA E RENDERIZAÇÃO (Update e Start)
# ==========================================================================

def render_scene():
    """Desenha todos os elementos visuais baseados no estado atual."""
    is_light = document.body.classList.contains("light-mode")
    ctx.fillStyle = "#fff9c4" if is_light else "#040014"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(offscreen_canvas, 0, 0)
    
    # Desenha a comida apenas se ela existir
    if food and "x" in food:
        draw_star_food(is_light)

    # Desenha a cobra apenas se ela tiver segmentos
    if snake:
        draw_snake_elements(is_light)

def draw_star_food(is_light):
    """Desenha a comida em formato de estrela."""
    ctx.fillStyle = "#4338ca" if is_light else "#ffdd00"
    fx = food["x"] + (box / 2)
    fy = food["y"] + (box / 2)
    star_size = 4.0 

    ctx.beginPath()
    ctx.moveTo(fx, fy - star_size * 2.2)
    ctx.quadraticCurveTo(fx + star_size * 0.8, fy - star_size * 0.8, fx + star_size * 2.2, fy)
    ctx.quadraticCurveTo(fx + star_size * 0.8, fy + star_size * 0.8, fx, fy + star_size * 2.2)
    ctx.quadraticCurveTo(fx - star_size * 0.8, fy + star_size * 0.8, fx - star_size * 2.2, fy)
    ctx.quadraticCurveTo(fx - star_size * 0.8, fy - star_size * 0.8, fx, fy - star_size * 2.2)
    ctx.closePath()
    ctx.fill()

def draw_snake_elements(is_light):
    """Desenha o corpo e os olhos da cobra."""
    for i, s in enumerate(snake):
        if i == 0:
            ctx.fillStyle = "#1e1b4b" if is_light else "#4c1d95"
        else:
            ctx.fillStyle = SNAKE_COLORS[min(i, 199)]
            
        ctx.fillRect(s["x"]+1, s["y"]+1, box-2, box-2)
        
        if i == 0:
            ctx.fillStyle = "#ffdd00"
            eye_size = 4
            if direction == "RIGHT":
                ctx.fillRect(s["x"]+12, s["y"]+4, eye_size, eye_size)
                ctx.fillRect(s["x"]+12, s["y"]+12, eye_size, eye_size)
            elif direction == "LEFT":
                ctx.fillRect(s["x"]+4, s["y"]+4, eye_size, eye_size)
                ctx.fillRect(s["x"]+4, s["y"]+12, eye_size, eye_size)
            elif direction == "UP":
                ctx.fillRect(s["x"]+4, s["y"]+4, eye_size, eye_size)
                ctx.fillRect(s["x"]+12, s["y"]+4, eye_size, eye_size)
            elif direction == "DOWN":
                ctx.fillRect(s["x"]+4, s["y"]+12, eye_size, eye_size)
                ctx.fillRect(s["x"]+12, s["y"]+12, eye_size, eye_size)

def update(*args):
    global score, food, snake, is_paused, last_theme_is_light

    is_light = document.body.classList.contains("light-mode")
    if last_theme_is_light is None or is_light != last_theme_is_light:
        last_theme_is_light = is_light
        update_snake_colors(is_light, score)
        draw_space_background_once()
        
    render_scene()

    if is_paused:
        return

    head = {"x": snake[0]["x"], "y": snake[0]["y"]}
    if direction == "LEFT": head["x"] -= box
    elif direction == "UP": head["y"] -= box
    elif direction == "RIGHT": head["x"] += box
    elif direction == "DOWN": head["y"] += box

    if (head["x"] < 0 or head["x"] >= canvas.width or 
        head["y"] < 0 or head["y"] >= canvas.height or
        any(s["x"] == head["x"] and s["y"] == head["y"] for s in snake)):
        game_over()
        return

    snake.insert(0, head)
    
    if head["x"] == food["x"] and head["y"] == food["y"]:
        score += 1
        document["score-display"].text = str(score)
        update_snake_colors(is_light, score) 
        food = spawn_food()
    else:
        snake.pop()

def start(ev=None):
    global snake, score, direction, food, game_loop_ref, is_game_over, is_paused
    is_game_over = False
    is_paused = False
    mid = (canvas.width // box // 2) * box
    snake = [{"x": mid, "y": mid}, {"x": mid-box, "y": mid}]
    score = 0
    direction = "RIGHT"
    food = spawn_food()
    document["score-display"].text = "0"
    document["game-over-ui"].style.display = "none"
    document["pause-ui"].style.display = "none"
    document["start-ui"].style.display = "none"
    if game_loop_ref: window.clearInterval(game_loop_ref)
    game_loop_ref = window.setInterval(update, 115)

def on_theme_toggle(ev):
    """Garante que a tela do jogo atualize as cores imediatamente ao clicar no tema."""
    def force_refresh():
        is_light = document.body.classList.contains("light-mode")
        update_snake_colors(is_light, score)
        draw_space_background_once()
        render_scene()
    window.setTimeout(force_refresh, 10) # Pequeno atraso para o JS alternar a classe primeiro

draw_space_background_once() 
ctx.drawImage(offscreen_canvas, 0, 0)

document["theme-toggle-btn"].bind("click", on_theme_toggle)
document["start-btn"].bind("click", start)
document["restart-btn"].bind("click", start)
