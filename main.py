from browser import document, window, html, storage
import random
import math

# --- CONFIGURAÇÕES DO JOGO ---
canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")
box = 25 # Grade 20x20 num canvas de 500px

store = storage.localStorage

# --- ESTADO GLOBAL ---
snake = []
food = {}
score = 0
direction = "RIGHT"
game_loop = None
is_running = False

def update_ui_ranking():
    """Atualiza a lista de recordes na tela"""
    last = store.get("snake_last_score", "0")
    document["last-score"].text = last
    
    try:
        top_scores = window.JSON.parse(store.get("snake_top_scores", "[]"))
    except:
        top_scores = []
        
    rank_elements = document.select(".rank-val")
    for i in range(3):
        if i < len(top_scores):
            rank_elements[i].text = str(top_scores[i])
        else:
            rank_elements[i].text = "---"

def save_score(final_score):
    """Salva no LocalStorage do navegador"""
    store["snake_last_score"] = str(final_score)
    try:
        top_scores = window.JSON.parse(store.get("snake_top_scores", "[]"))
    except:
        top_scores = []
        
    top_scores.append(final_score)
    top_scores = sorted(list(set(top_scores)), reverse=True)[:3]
    store["snake_top_scores"] = window.JSON.stringify(top_scores)
    update_ui_ranking()

def spawn_food():
    cols = (canvas.width // box) - 1
    rows = (canvas.height // box) - 1
    while True:
        fx = random.randint(0, cols) * box
        fy = random.randint(0, rows) * box
        if not any(s['x'] == fx and s['y'] == fy for s in snake):
            return {"x": fx, "y": fy}

def set_direction(new_dir):
    global direction
    forbidden = {"LEFT": "RIGHT", "RIGHT": "LEFT", "UP": "DOWN", "DOWN": "UP"}
    if new_dir != forbidden.get(direction):
        direction = new_dir

# --- INPUTS ---

def key_handler(ev):
    global is_running
    key_map = {37: "LEFT", 38: "UP", 39: "RIGHT", 40: "DOWN"}
    if ev.keyCode in key_map:
        ev.preventDefault()
        set_direction(key_map[ev.keyCode])
    if ev.keyCode in [13, 32]: # Enter ou Espaço
        ev.preventDefault()
        if not is_running:
            start_game()

document.bind("keydown", key_handler)

# Swipe Mobile
touch_start = [0, 0]
def ts_h(ev):
    global touch_start
    touch_start = [ev.touches[0].clientX, ev.touches[0].clientY]
    ev.preventDefault()

def te_h(ev):
    dx = ev.changedTouches[0].clientX - touch_start[0]
    dy = ev.changedTouches[0].clientY - touch_start[1]
    if abs(dx) > 30 or abs(dy) > 30:
        if abs(dx) > abs(dy):
            set_direction("RIGHT" if dx > 0 else "LEFT")
        else:
            set_direction("DOWN" if dy > 0 else "UP")
    ev.preventDefault()

canvas.bind("touchstart", ts_h)
canvas.bind("touchend", te_h)

# --- LOOP PRINCIPAL ---

def main_loop(*args):
    global score, food, snake
    ctx.fillStyle = "#150136"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    # Comida
    ctx.fillStyle = "#ffaa00"
    ctx.beginPath()
    ctx.arc(food["x"] + box/2, food["y"] + box/2, box/2.5, 0, math.pi*2)
    ctx.fill()

    nx, ny = snake[0]["x"], snake[0]["y"]
    if direction == "LEFT": nx -= box
    elif direction == "UP": ny -= box
    elif direction == "RIGHT": nx += box
    elif direction == "DOWN": ny += box

    # Colisões
    if (nx < 0 or nx >= canvas.width or ny < 0 or ny >= canvas.height or
        any(s["x"] == nx and s["y"] == ny for s in snake)):
        game_over()
        return

    new_head = {"x": nx, "y": ny}
    snake.insert(0, new_head)

    if nx == food["x"] and ny == food["y"]:
        score += 1
        document["score-display"].text = str(score)
        food = spawn_food()
    else:
        snake.pop()

    # Desenha Cobra
    for i, s in enumerate(snake):
        ctx.fillStyle = "#8b87ff" if i == 0 else "#5752ff"
        ctx.fillRect(s["x"]+1, s["y"]+1, box-2, box-2)

def game_over():
    global is_running
    is_running = False
    window.clearInterval(game_loop)
    save_score(score)
    ctx.fillStyle = "rgba(4, 0, 20, 0.85)"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = "#ffdd00"
    ctx.font = "bold 40px sans-serif"
    ctx.textAlign = "center"
    ctx.fillText("FIM DE JOGO", canvas.width/2, canvas.height/2)
    document["overlay"].style.display = "flex"

def start_game(ev=None):
    global snake, score, direction, food, game_loop, is_running
    is_running = True
    snake = [{"x": 10*box, "y": 10*box}, {"x": 9*box, "y": 10*box}]
    score, direction, food = 0, "RIGHT", spawn_food()
    document["score-display"].text = "0"
    document["overlay"].style.display = "none"
    if game_loop: window.clearInterval(game_loop)
    game_loop = window.setInterval(main_loop, 100)

# Bindings
document["restart-btn"].bind("click", start_game)

def bind_mobile(id, d):
    def h(e): e.preventDefault(); set_direction(d)
    document[id].bind("touchstart", h)
    document[id].bind("mousedown", h)

for b, d in [("btn-up","UP"), ("btn-down","DOWN"), ("btn-left","LEFT"), ("btn-right","RIGHT")]:
    bind_mobile(b, d)

update_ui_ranking()
