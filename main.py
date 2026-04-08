from browser import document, window, html
import random
import math

canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")
box = 20
snake = []
food = {}
score = 0
direction = "RIGHT"
game_loop_ref = None
is_game_over = False

def spawn_food():
    while True:
        fx = random.randint(0, (canvas.width // box) - 1) * box
        fy = random.randint(0, (canvas.height // box) - 1) * box
        if not any(s['x'] == fx and s['y'] == fy for s in snake):
            return {"x": fx, "y": fy}

def set_dir(new_dir):
    global direction
    pairs = {"LEFT": "RIGHT", "RIGHT": "LEFT", "UP": "DOWN", "DOWN": "UP"}
    if new_dir != pairs.get(direction):
        direction = new_dir

def key_press(ev):
    global is_game_over
    key_map = {37: "LEFT", 38: "UP", 39: "RIGHT", 40: "DOWN"}
    if ev.keyCode in key_map:
        ev.preventDefault()
        set_dir(key_map[ev.keyCode])
    elif ev.keyCode in [32, 13]:
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
    dx = ev.changedTouches[0].clientX - t_start[0]
    dy = ev.changedTouches[0].clientY - t_start[1]
    if abs(dx) > 25 or abs(dy) > 25:
        if abs(dx) > abs(dy):
            set_dir("RIGHT" if dx > 0 else "LEFT")
        else:
            set_dir("DOWN" if dy > 0 else "UP")
    if ev.target.id == "gameCanvas":
        ev.preventDefault()

canvas.bind("touchstart", t_start_h)
canvas.bind("touchend", t_end_h)

def bind_btn(id, d):
    # Funções para adicionar e remover o efeito visual de clique (glow)
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

def game_over():
    global is_game_over
    is_game_over = True
    window.clearInterval(game_loop_ref)
    document["game-over-ui"].style.display = "flex"

def update(*args):
    global score, food, snake
    ctx.fillStyle = "#150136"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    # Food
    ctx.fillStyle = "#ffaa00"
    ctx.shadowBlur = 12
    ctx.shadowColor = "#ff9900"
    ctx.beginPath()
    ctx.arc(food["x"]+(box/2), food["y"]+(box/2), 8, 0, math.pi*2)
    ctx.fill()
    ctx.shadowBlur = 0

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
        food = spawn_food()
    else:
        snake.pop()

    # Renderização da Cobra com Gradiente
    snake_len = len(snake)
    for i, s in enumerate(snake):
        if i == 0:
            # Cabeça: Roxo Escuro Profundo
            ctx.fillStyle = "#4c1d95"
        else:
            # Corpo: Gradiente dinâmico baseado na posição
            lightness = 60 + (i / snake_len) * 25
            ctx.fillStyle = f"hsl(255, 100%, {lightness}%)"
            
        ctx.fillRect(s["x"]+1, s["y"]+1, box-2, box-2)
        
        # Olhos Amarelos na Cabeça
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

def start(ev=None):
    global snake, score, direction, food, game_loop_ref, is_game_over
    is_game_over = False
    mid = (canvas.width // box // 2) * box
    snake = [{"x": mid, "y": mid}, {"x": mid-box, "y": mid}]
    score = 0
    direction = "RIGHT"
    food = spawn_food()
    document["score-display"].text = "0"
    document["game-over-ui"].style.display = "none"
    if game_loop_ref: window.clearInterval(game_loop_ref)
    game_loop_ref = window.setInterval(update, 100)

document["restart-btn"].bind("click", start)
start()
