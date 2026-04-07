"""
SNAKE.PY - Lógica Avançada com Ranking Persistente
"""
from browser import document, window, html, storage
import random
import math

# --- CONFIGURAÇÕES DO AMBIENTE ---
canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")
box = 25  # Grid um pouco maior para o canvas de 500px

# LocalStorage para salvar recordes
local_storage = storage.localStorage

# --- VARIÁVEIS DE ESTADO ---
snake = []
food = {}
score = 0
direction = "RIGHT"
game_loop_ref = None
is_playing = False

# --- SISTEMA DE PONTUAÇÃO E RANKING ---

def update_ranking_ui():
    """Atualiza os textos de recordes na interface HTML"""
    # Última pontuação
    last = local_storage.get("snake_last_score", "0")
    document["last-score"].text = last
    
    # Top 3
    high_scores = window.JSON.parse(local_storage.get("snake_top_scores", "[]"))
    # Garante que temos pelo menos 3 entradas para exibir
    while len(high_scores) < 3:
        high_scores.append(0)
    
    container = document["high-scores"]
    container.clear()
    
    colors = ["text-yellow-400", "text-gray-300", "text-orange-400"]
    for i in range(3):
        item = html.DIV(Class="flex justify-between")
        item <= html.SPAN(f"{i+1}º")
        item <= html.SPAN(str(high_scores[i]), Class=colors[i])
        container <= item

def save_score(current_score):
    """Salva a pontuação atual e atualiza o Top 3"""
    # Salva como última partida
    local_storage["snake_last_score"] = str(current_score)
    
    # Atualiza Top 3
    high_scores = window.JSON.parse(local_storage.get("snake_top_scores", "[]"))
    high_scores.append(current_score)
    # Remove duplicatas, ordena do maior para o menor e pega os 3 primeiros
    high_scores = sorted(list(set(high_scores)), reverse=True)[:3]
    local_storage["snake_top_scores"] = window.JSON.stringify(high_scores)
    
    update_ranking_ui()

# --- MECÂNICA DO JOGO ---

def spawn_food():
    cols = (canvas.width // box) - 1
    rows = (canvas.height // box) - 1
    while True:
        fx = random.randint(0, cols) * box
        fy = random.randint(0, rows) * box
        if not any(s['x'] == fx and s['y'] == fy for s in snake):
            return {"x": fx, "y": fy}

def set_dir(new_dir):
    global direction
    opposite = {"LEFT": "RIGHT", "RIGHT": "LEFT", "UP": "DOWN", "DOWN": "UP"}
    if new_dir != opposite.get(direction):
        direction = new_dir

# --- INPUTS ---

def input_handler(ev):
    """Controla teclado e comandos de início"""
    global is_playing
    
    # Setas para direção
    key_map = {37: "LEFT", 38: "UP", 39: "RIGHT", 40: "DOWN"}
    if ev.keyCode in key_map:
        ev.preventDefault()
        set_dir(key_map[ev.keyCode])
    
    # Enter (13) ou Espaço (32) para iniciar
    if ev.keyCode in [13, 32]:
        ev.preventDefault()
        if not is_playing:
            start_game()

document.bind("keydown", input_handler)

# Mobile Swipe
t_start = [0, 0]
def ts_h(ev):
    global t_start
    t_start = [ev.touches[0].clientX, ev.touches[0].clientY]
    ev.preventDefault()

def te_h(ev):
    dx = ev.changedTouches[0].clientX - t_start[0]
    dy = ev.changedTouches[0].clientY - t_start[1]
    if abs(dx) > 30 or abs(dy) > 30:
        if abs(dx) > abs(dy): set_dir("RIGHT" if dx > 0 else "LEFT")
        else: set_dir("DOWN" if dy > 0 else "UP")
    ev.preventDefault()

canvas.bind("touchstart", ts_h)
canvas.bind("touchend", te_h)

def bind_btn(id, d):
    def h(e): e.preventDefault(); set_dir(d)
    document[id].bind("touchstart", h)
    document[id].bind("click", h)

for b, d in [("btn-up","UP"), ("btn-down","DOWN"), ("btn-left","LEFT"), ("btn-right","RIGHT")]:
    bind_btn(b, d)

# --- CORE ---

def game_over():
    global is_playing
    is_playing = False
    window.clearInterval(game_loop_ref)
    
    save_score(score)
    
    # Overlay visual
    ctx.fillStyle = "rgba(4, 0, 20, 0.9)"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    ctx.fillStyle = "#ffdd00"
    ctx.font = "900 40px sans-serif"
    ctx.textAlign = "center"
    ctx.fillText("VOCÊ BATEU!", canvas.width/2, canvas.height/2 - 10)
    
    document["start-overlay"].style.display = "flex"
    document["restart-btn"].text = "TENTAR DE NOVO"

def update(*args):
    global score, food, snake
    
    # Desenha fundo
    ctx.fillStyle = "#150136"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    # Desenha Comida com efeito de brilho
    ctx.shadowBlur = 15
    ctx.shadowColor = "#ffaa00"
    ctx.fillStyle = "#ffaa00"
    ctx.beginPath()
    ctx.arc(food["x"]+box/2, food["y"]+box/2, box/3, 0, math.pi*2)
    ctx.fill()
    ctx.shadowBlur = 0 # Reseta brilho para o corpo

    # Movimento
    head = {"x": snake[0]["x"], "y": snake[0]["y"]}
    if direction == "LEFT": head["x"] -= box
    elif direction == "UP": head["y"] -= box
    elif direction == "RIGHT": head["x"] += box
    elif direction == "DOWN": head["y"] += box

    # Colisões
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

    # Render cobra
    for i, s in enumerate(snake):
        # Gradiente de cor do brilho até o azul
        ctx.fillStyle = "#8b87ff" if i == 0 else "#5752ff"
        # Cantos levemente arredondados simulados
        ctx.fillRect(s["x"]+1, s["y"]+1, box-2, box-2)

def start_game(ev=None):
    global snake, score, direction, food, game_loop_ref, is_playing
    
    is_playing = True
    snake = [{"x": 10*box, "y": 10*box}, {"x": 9*box, "y": 10*box}]
    score = 0
    direction = "RIGHT"
    food = spawn_food()
    
    document["score-display"].text = "0"
    document["start-overlay"].style.display = "none"
    
    if game_loop_ref: window.clearInterval(game_loop_ref)
    game_loop_ref = window.setInterval(update, 100) # Velocidade 100ms para ser mais desafiador

# Inicialização
document["restart-btn"].bind("click", start_game)
update_ranking_ui() # Carrega recordes salvos
