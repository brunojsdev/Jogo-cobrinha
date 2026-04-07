from browser import document, window, html
import random
import math

# Inicialização do Canvas
canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")
box = 20

# Estado Global do Jogo
snake = []
food = {}
score = 0
direction = "RIGHT"
game_loop_ref = None

def spawn_food():
    """Gera comida em posição aleatória"""
    while True:
        fx = random.randint(0, (canvas.width // box) - 1) * box
        fy = random.randint(0, (canvas.height // box) - 1) * box
        if not any(s['x'] == fx and s['y'] == fy for s in snake):
            return {"x": fx, "y": fy}

def set_dir(new_dir):
    """Muda a direção evitando inversão de 180 graus"""
    global direction
    pairs = {"LEFT": "RIGHT", "RIGHT": "LEFT", "UP": "DOWN", "DOWN": "UP"}
    if new_dir != pairs.get(direction):
        direction = new_dir

# --- Listeners de Entrada ---

def key_press(ev):
    map = {37: "LEFT", 38: "UP", 39: "RIGHT", 40: "DOWN"}
    if ev.keyCode in map:
        ev.preventDefault()
        set_dir(map[ev.keyCode])

document.bind("keydown", key_press)

# Lógica de Swipe para Mobile
t_start = [0, 0]

def t_start_h(ev):
    global t_start
    t_start = [ev.touches[0].clientX, ev.touches[0].clientY]
    ev.preventDefault()

def t_end_h(ev):
    dx = ev.changedTouches[0].clientX - t_start[0]
    dy = ev.changedTouches[0].clientY - t_start[1]
    if abs(dx) > 30 or abs(dy) > 30:
        if abs(dx) > abs(dy):
            set_dir("RIGHT" if dx > 0 else "LEFT")
        else:
            set_dir("DOWN" if dy > 0 else "UP")
    ev.preventDefault()

canvas.bind("touchstart", t_start_h)
canvas.bind("touchend", t_end_h)

# Botões Virtuais
def bind_btn(id, d):
    def h(e): 
        e.preventDefault()
        set_dir(d)
    document[id].bind("touchstart", h)
    document[id].bind("click", h)

for b, d in [("btn-up","UP"), ("btn-down","DOWN"), ("btn-left","LEFT"), ("btn-right","RIGHT")]:
    bind_btn(b, d)

# --- Loop Principal e Mecânicas ---

def game_over():
    window.clearInterval(game_loop_ref)
    # Efeito visual de Game Over
    ctx.fillStyle = "rgba(4, 0, 20, 0.85)"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = "#ffdd00"
    ctx.font = "bold 30px sans-serif"
    ctx.textAlign = "center"
    ctx.fillText("GAME OVER", canvas.width/2, canvas.height/2 - 10)
    document["restart-btn"].style.display = "block"

def update(*args):
    global score, food, snake
    
    # Limpa o fundo
    ctx.fillStyle = "#150136"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    # Desenha Comida
    ctx.fillStyle = "#ffaa00"
    ctx.beginPath()
    ctx.arc(food["x"]+10, food["y"]+10, 8, 0, math.pi*2)
    ctx.fill()

    # Cálculo do Movimento
    head = {"x": snake[0]["x"], "y": snake[0]["y"]}
    if direction == "LEFT": head["x"] -= box
    elif direction == "UP": head["y"] -= box
    elif direction == "RIGHT": head["x"] += box
    elif direction == "DOWN": head["y"] += box

    # Verificação de Colisões
    if (head["x"] < 0 or head["x"] >= canvas.width or 
        head["y"] < 0 or head["y"] >= canvas.height or
        any(s["x"] == head["x"] and s["y"] == head["y"] for s in snake)):
        game_over()
        return

    snake.insert(0, head)

    # Lógica de Comer
    if head["x"] == food["x"] and head["y"] == food["y"]:
        score += 1
        document["score-display"].text = str(score)
        food = spawn_food()
    else:
        snake.pop()

    # Renderização da Cobra
    for i, s in enumerate(snake):
        ctx.fillStyle = "#8b87ff" if i == 0 else "#5752ff"
        ctx.fillRect(s["x"]+1, s["y"]+1, box-2, box-2)

def start(ev=None):
    global snake, score, direction, food, game_loop_ref
    snake = [{"x": 10*box, "y": 10*box}]
    score = 0
    direction = "RIGHT"
    food = spawn_food()
    document["score-display"].text = "0"
    document["restart-btn"].style.display = "none"
    if game_loop_ref: 
        window.clearInterval(game_loop_ref)
    game_loop_ref = window.setInterval(update, 120)

# Inicialização
document["restart-btn"].bind("click", start)
start()
