"""
Lógica do Jogo da Cobrinha em Python puro (usando Brython)
Desenvolvedor: [Seu Nome]
Data: 2024
"""
from browser import document, window, html
import random
import math

# --- CONFIGURAÇÕES DO AMBIENTE ---
canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")
box = 20  # Tamanho de cada quadrado (grade) do jogo

# --- VARIÁVEIS DE ESTADO (MEMÓRIA DO JOGO) ---
snake = []          # Lista de dicionários [{'x': 0, 'y': 0}, ...]
food = {}           # Posição da comida {'x': 0, 'y': 0}
score = 0           # Pontuação atual
direction = "RIGHT" # Direção inicial
game_loop_ref = None # Referência do intervalo do jogo (timer)

# --- FUNÇÕES DE LÓGICA ---

def spawn_food():
    """Gera uma posição aleatória para a comida dentro do grid do Canvas"""
    while True:
        # Calcula colunas/linhas disponíveis
        cols = (canvas.width // box) - 1
        rows = (canvas.height // box) - 1
        
        fx = random.randint(0, cols) * box
        fy = random.randint(0, rows) * box
        
        # Garante que a comida não nasça em cima do corpo da cobra
        if not any(s['x'] == fx and s['y'] == fy for s in snake):
            return {"x": fx, "y": fy}

def set_dir(new_dir):
    """Atualiza a direção, impedindo que a cobra volte no sentido oposto"""
    global direction
    opposite = {"LEFT": "RIGHT", "RIGHT": "LEFT", "UP": "DOWN", "DOWN": "UP"}
    if new_dir != opposite.get(direction):
        direction = new_dir

# --- TRATAMENTO DE ENTRADAS (INPUTS) ---

def key_press_handler(ev):
    """Captura as setas do teclado"""
    key_map = {37: "LEFT", 38: "UP", 39: "RIGHT", 40: "DOWN"}
    if ev.keyCode in key_map:
        ev.preventDefault() # Impede que a seta role a página
        set_dir(key_map[ev.keyCode])

document.bind("keydown", key_press_handler)

# Lógica de Swipe (Deslizar o dedo no mobile)
t_start = [0, 0] # Coordenadas X e Y do início do toque

def touch_start_handler(ev):
    global t_start
    t_start = [ev.touches[0].clientX, ev.touches[0].clientY]
    ev.preventDefault()

def touch_end_handler(ev):
    # Calcula a diferença entre onde começou e terminou o toque
    dx = ev.changedTouches[0].clientX - t_start[0]
    dy = ev.changedTouches[0].clientY - t_start[1]
    
    # Sensibilidade do swipe: mínimo 30 pixels de movimento
    if abs(dx) > 30 or abs(dy) > 30:
        if abs(dx) > abs(dy): # Movimento horizontal predominante
            set_dir("RIGHT" if dx > 0 else "LEFT")
        else: # Movimento vertical predominante
            set_dir("DOWN" if dy > 0 else "UP")
    ev.preventDefault()

canvas.bind("touchstart", touch_start_handler)
canvas.bind("touchend", touch_end_handler)

# Conectar botões da interface aos comandos Python
def bind_button(id, d):
    def action(e): 
        e.preventDefault()
        set_dir(d)
    document[id].bind("touchstart", action)
    document[id].bind("click", action)

for b_id, d_name in [("btn-up","UP"), ("btn-down","DOWN"), ("btn-left","LEFT"), ("btn-right","RIGHT")]:
    bind_button(b_id, d_name)

# --- MECÂNICAS DE JOGO ---

def game_over():
    """Para o jogo e exibe a tela de derrota"""
    window.clearInterval(game_loop_ref)
    
    # Escurece a tela e exibe mensagem
    ctx.fillStyle = "rgba(4, 0, 20, 0.85)" # fundo-escuro semi-transparente
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    ctx.fillStyle = "#ffdd00" # destaque-claro
    ctx.font = "bold 30px sans-serif"
    ctx.textAlign = "center"
    ctx.fillText("FIM DE JOGO!", canvas.width/2, canvas.height/2 - 10)
    
    # Exibe o botão de reiniciar que estava oculto no HTML
    document["restart-btn"].style.display = "block"

def main_update(*args):
    """Esta função roda a cada quadro (tick) do jogo"""
    global score, food, snake
    
    # 1. Limpar o quadro anterior
    ctx.fillStyle = "#150136" # fundo-claro
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    # 2. Desenhar a Comida (Destaque Médio Amarelo)
    ctx.fillStyle = "#ffaa00"
    ctx.beginPath()
    ctx.arc(food["x"]+10, food["y"]+10, 8, 0, math.pi*2)
    ctx.fill()

    # 3. Calcular a nova posição da cabeça
    curr_head = {"x": snake[0]["x"], "y": snake[0]["y"]}
    if direction == "LEFT": curr_head["x"] -= box
    elif direction == "UP": curr_head["y"] -= box
    elif direction == "RIGHT": curr_head["x"] += box
    elif direction == "DOWN": curr_head["y"] += box

    # 4. Verificar Colisões (Paredes ou Próprio Corpo)
    if (curr_head["x"] < 0 or curr_head["x"] >= canvas.width or 
        curr_head["y"] < 0 or curr_head["y"] >= canvas.height or
        any(s["x"] == curr_head["x"] and s["y"] == curr_head["y"] for s in snake)):
        game_over()
        return

    # 5. Mover a cobra
    snake.insert(0, curr_head) # Adiciona nova cabeça

    # Verifica se comeu a comida
    if curr_head["x"] == food["x"] and curr_head["y"] == food["y"]:
        score += 1
        document["score-display"].text = str(score)
        food = spawn_food()
    else:
        snake.pop() # Remove o último pedaço (rabo) para manter o tamanho

    # 6. Renderizar a Cobra (Cores Neón)
    for i, segment in enumerate(snake):
        # A cabeça tem uma cor de destaque maior
        ctx.fillStyle = "#8b87ff" if i == 0 else "#5752ff"
        ctx.fillRect(segment["x"]+1, segment["y"]+1, box-2, box-2)

def start_game(ev=None):
    """Inicia ou Reinicia o estado inicial do jogo"""
    global snake, score, direction, food, game_loop_ref
    
    # Reset de variáveis
    snake = [{"x": 10*box, "y": 10*box}]
    score = 0
    direction = "RIGHT"
    food = spawn_food()
    
    # Atualiza a Interface
    document["score-display"].text = "0"
    document["restart-btn"].style.display = "none"
    
    # Controla o loop do jogo (Executa a cada 120ms)
    if game_loop_ref: 
        window.clearInterval(game_loop_ref)
    game_loop_ref = window.setInterval(main_update, 120)

# Início imediato ao carregar a página
document["restart-btn"].bind("click", start_game)
start_game()
