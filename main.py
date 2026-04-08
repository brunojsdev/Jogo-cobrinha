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
    # Mapeamento de direções (Setas)
    key_map = {37: "LEFT", 38: "UP", 39: "RIGHT", 40: "DOWN"}
    if ev.keyCode in key_map:
        ev.preventDefault()
        set_dir(key_map[ev.keyCode])
    
    # Iniciar/Reiniciar com Espaço (32) ou Enter (13)
    elif ev.keyCode in [32, 13]:
        ev.preventDefault()
        if is_game_over or game_loop_ref is None:
            start()

document.bind("keydown", key_press)

# Lógica de Deslizar (Swipe Mobile)
t_start = [0, 0]
def t_start_h(ev):
    global t_start
    t_start = [ev.touches[0].clientX, ev.touches[0].clientY]
    if ev.target.id == "gameCanvas":
        ev.preventDefault()

def t_end_h(ev):
    dx = ev.changedTouches[0].clientX - t_start[0]
    dy = ev.changedTouches[0].clientY - t_start[1]
    if abs(dx) > 20 or abs(dy) > 20:
        if abs(dx) > abs(dy):
            set_dir("RIGHT" if dx > 0 else "LEFT")
        else:
            set_dir("DOWN" if dy > 0 else "UP")
    if ev.target.id == "gameCanvas":
        ev.preventDefault()

canvas.bind("touchstart", t_start_h)
canvas.bind("touchend", t_end_h)

# Configuração dos Botões Mobile da tela
def bind_btn(id, d):
    def h(e): 
        e.preventDefault()
        set_dir(d)
    document[id].bind("click", h)
    document[id].bind("touchstart", h)

for b, d in [("btn-up","UP"), ("btn-down","DOWN"), ("btn-left","LEFT"), ("btn-right","RIGHT")]:
    bind_btn(b, d)

def game_over():
    global is_game_over
    is_game_over = True
    window.clearInterval(game_loop_ref)
    
    # Efeito de Fim de Jogo (Escurece a tela e mostra texto)
    ctx.fillStyle = "rgba(4, 0, 20, 0.9)"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = "#ffdd00"
    ctx.font = "black 32px sans-serif"
    ctx.textAlign = "center"
    ctx.fillText("FIM DE JOGO", canvas.width/2, canvas.height/2)
    
    # Mostra o botão e muda o texto para REINICIAR
    document["restart-btn"].text = "Reiniciar"
    document["restart-btn"].style.display = "block"

def update(*args):
    global score, food, snake
    
    # Limpa a tela frame a frame
    ctx.fillStyle = "#150136"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    # Desenha a Comida
    ctx.fillStyle = "#ffaa00"
    ctx.beginPath()
    ctx.arc(food["x"]+10, food["y"]+10, 8, 0, math.pi*2)
    ctx.fill()

    # Move a Cabeça
    head = {"x": snake[0]["x"], "y": snake[0]["y"]}
    if direction == "LEFT": head["x"] -= box
    elif direction == "UP": head["y"] -= box
    elif direction == "RIGHT": head["x"] += box
    elif direction == "DOWN": head["y"] += box

    # Regras de Colisão (Paredes ou Corpo)
    if (head["x"] < 0 or head["x"] >= canvas.width or 
        head["y"] < 0 or head["y"] >= canvas.height or
        any(s["x"] == head["x"] and s["y"] == head["y"] for s in snake)):
        game_over()
        return

    snake.insert(0, head)
    
    # Verifica se comeu a comida
    if head["x"] == food["x"] and head["y"] == food["y"]:
        score += 1
        document["score-display"].text = str(score)
        food = spawn_food()
    else:
        snake.pop()

    # Desenha o Corpo da Cobra
    for i, s in enumerate(snake):
        ctx.fillStyle = "#8b87ff" if i == 0 else "#5752ff"
        ctx.fillRect(s["x"]+1, s["y"]+1, box-2, box-2)

def start_screen():
    # Desenha a tela inicial antes do usuário apertar Iniciar
    ctx.fillStyle = "#150136"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    document["restart-btn"].text = "Iniciar"
    document["restart-btn"].style.display = "block"

def start(ev=None):
    global snake, score, direction, food, game_loop_ref, is_game_over
    is_game_over = False
    snake = [{"x": 10*box, "y": 10*box}]
    score = 0
    direction = "RIGHT"
    food = spawn_food()
    
    document["score-display"].text = "0"
    document["restart-btn"].style.display = "none"
    
    if game_loop_ref: window.clearInterval(game_loop_ref)
    game_loop_ref = window.setInterval(update, 125)

# Liga o botão HTML à função Python
document["restart-btn"].bind("click", start)

# Chama a tela inicial quando o script carregar
start_screen()
