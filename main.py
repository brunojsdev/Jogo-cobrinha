<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jogo da Cobrinha - Python via Brython</title>
    
    <!-- Tailwind CSS para um visual moderno -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Brython: O interpretador de Python para o navegador -->
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@3.12.0/brython.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@3.12.0/brython_stdlib.js"></script>

    <style>
        :root {
            /* FUNDOS */
            --fundo-claro: #150136;
            --fundo-medio: #090024;
            --fundo-escuro: #040014;

            /* DESTAQUES */
            --destaque-claro: #ffdd00;
            --destaque-medio: #ffaa00;
            --destaque-escuro: #ff9900;
            --brilho-interface: #8b87ff; 

            /* BOTÕES */
            --btm-claro: #17005c;
            --btm-medio: #110042;
            --btm-escuro: #0d0033;
            --btm-claro-h: #6b4100;
            --btm-medio-h: #4d2b01;
            --btm-escuro-h: #301b00;
            
            /* BORDAS */
            --borda-clara: #5752ff;
            --borda-escura: #ffaa00;
        }

        body { 
            touch-action: none; /* Evita que a tela role ao jogar no celular */ 
            background-color: var(--fundo-escuro);
            color: var(--brilho-interface);
        }
        
        canvas { 
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.7); 
            background-color: var(--fundo-claro);
            border-color: var(--borda-clara) !important;
        }

        /* Classes Personalizadas baseadas na Paleta */
        .title-text { 
            color: var(--destaque-claro); 
            text-shadow: 0 0 10px var(--destaque-escuro); 
        }
        .score-box { 
            background-color: var(--fundo-medio); 
            border-color: var(--borda-clara); 
        }
        .score-number { 
            color: var(--destaque-claro); 
        }
        .btn-restart { 
            background-color: var(--btm-claro); 
            border: 2px solid var(--borda-escura); 
            color: var(--destaque-claro); 
        }
        .btn-restart:hover { 
            background-color: var(--btm-claro-h); 
            border-color: var(--destaque-claro); 
        }
        .btn-mobile { 
            background-color: var(--btm-medio); 
            border: 1px solid var(--borda-clara); 
            color: var(--destaque-claro);
        }
        .btn-mobile:active { 
            background-color: var(--btm-medio-h); 
        }
    </style>
</head>
<body onload="brython()" class="min-h-screen flex flex-col items-center justify-center font-sans antialiased p-4">

    <div class="max-w-md w-full flex flex-col items-center">
        <!-- Cabeçalho e Placar -->
        <div class="flex justify-between items-center w-full mb-4 px-2">
            <h1 class="text-3xl font-bold title-text tracking-wider">Snake</h1>
            <div class="text-xl font-semibold score-box px-4 py-2 rounded-lg border">
                Pontos: <span id="score-display" class="score-number font-bold text-2xl">0</span>
            </div>
        </div>

        <!-- Tela do Jogo -->
        <div class="relative w-full flex justify-center">
            <canvas id="gameCanvas" width="400" height="400" class="border-4 rounded-xl w-full max-w-[400px] aspect-square touch-none"></canvas>
            
            <!-- Botão de Reiniciar (Escondido inicialmente) -->
            <button id="restart-btn" class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 btn-restart font-bold py-3 px-6 rounded-full shadow-lg transition duration-200 hidden z-10">
                Jogar Novamente
            </button>
        </div>

        <!-- Controles para Celular (D-Pad) -->
        <div class="grid grid-cols-3 gap-3 mt-6 md:hidden w-[240px]">
            <div></div>
            <button id="btn-up" class="btn-mobile rounded-xl h-14 flex items-center justify-center shadow-lg transition-colors">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 15l7-7 7 7"></path></svg>
            </button>
            <div></div>
            <button id="btn-left" class="btn-mobile rounded-xl h-14 flex items-center justify-center shadow-lg transition-colors">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7"></path></svg>
            </button>
            <button id="btn-down" class="btn-mobile rounded-xl h-14 flex items-center justify-center shadow-lg transition-colors">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7"></path></svg>
            </button>
            <button id="btn-right" class="btn-mobile rounded-xl h-14 flex items-center justify-center shadow-lg transition-colors">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7-7"></path></svg>
            </button>
        </div>

        <p class="mt-6 text-sm text-center opacity-70 hidden md:block">Use as setinhas do teclado para jogar.</p>
        <p class="mt-6 text-sm text-center opacity-70 md:hidden">Use os botões ou deslize (swipe) direto na tela.</p>
    </div>

    <!-- LÓGICA DO JOGO EM PYTHON -->
    <script type="text/python">
        from browser import document, window, html
        import random
        import math

        # Configurações iniciais do Canvas e Jogo
        canvas = document["gameCanvas"]
        ctx = canvas.getContext("2d")

        box = 20
        canvas_size = 400
        cols = canvas_size // box
        rows = canvas_size // box

        # Variáveis globais do estado do jogo
        snake = []
        food = {}
        score = 0
        d = "RIGHT"
        game_interval = None

        def spawn_food():
            """Gera uma comida em um local aleatório que não esteja na cobra"""
            while True:
                fx = random.randint(0, cols - 1) * box
                fy = random.randint(0, rows - 1) * box
                collision = False
                for segment in snake:
                    if segment["x"] == fx and segment["y"] == fy:
                        collision = True
                        break
                if not collision:
                    return {"x": fx, "y": fy}

        def set_direction(new_dir):
            """Define a direção garantindo que a cobra não vire 180 graus no próprio corpo"""
            global d
            if new_dir == "LEFT" and d != "RIGHT": d = "LEFT"
            elif new_dir == "UP" and d != "DOWN": d = "UP"
            elif new_dir == "RIGHT" and d != "LEFT": d = "RIGHT"
            elif new_dir == "DOWN" and d != "UP": d = "DOWN"

        def keydown_handler(event):
            """Captura os eventos de teclado"""
            if event.keyCode == 37: set_direction("LEFT")
            elif event.keyCode == 38: set_direction("UP")
            elif event.keyCode == 39: set_direction("RIGHT")
            elif event.keyCode == 40: set_direction("DOWN")
            
            # Previne que a página role ao usar as setas
            if event.keyCode in [37, 38, 39, 40]:
                event.preventDefault()

        document.bind("keydown", keydown_handler)

        # Adiciona suporte a Swipe (deslizar) na tela para mobile
        touch_start_x = 0
        touch_start_y = 0

        def touchstart_handler(ev):
            global touch_start_x, touch_start_y
            if len(ev.touches) > 0:
                touch_start_x = ev.touches[0].clientX
                touch_start_y = ev.touches[0].clientY
            ev.preventDefault() # Previne a rolagem da página ao tocar na tela

        def touchend_handler(ev):
            if len(ev.changedTouches) > 0:
                touch_end_x = ev.changedTouches[0].clientX
                touch_end_y = ev.changedTouches[0].clientY
                dx = touch_end_x - touch_start_x
                dy = touch_end_y - touch_start_y

                # Verifica se o movimento foi longo o suficiente para ser considerado um swipe (30px)
                if abs(dx) > 30 or abs(dy) > 30:
                    if abs(dx) > abs(dy):
                        if dx > 0: set_direction("RIGHT")
                        else: set_direction("LEFT")
                    else:
                        if dy > 0: set_direction("DOWN")
                        else: set_direction("UP")
            ev.preventDefault()

        canvas.bind("touchstart", touchstart_handler)
        canvas.bind("touchend", touchend_handler)
        canvas.bind("touchmove", lambda ev: ev.preventDefault())

        # Configura os botões para quem joga pelo celular
        def bind_mobile_btn(btn_id, direction):
            def handler(ev):
                ev.preventDefault()
                set_direction(direction)
            if document[btn_id]:
                document[btn_id].bind("touchstart", handler)
                document[btn_id].bind("click", handler)

        bind_mobile_btn("btn-up", "UP")
        bind_mobile_btn("btn-down", "DOWN")
        bind_mobile_btn("btn-left", "LEFT")
        bind_mobile_btn("btn-right", "RIGHT")

        def game_over():
            """Lida com a tela de fim de jogo"""
            global game_interval
            window.clearInterval(game_interval)
            
            # Escurece a tela usando o fundo-escuro com transparência
            ctx.fillStyle = "rgba(4, 0, 20, 0.8)" 
            ctx.fillRect(0, 0, canvas.width, canvas.height)
            
            # Texto
            ctx.fillStyle = "#ffdd00" # destaque-claro
            ctx.font = "bold 35px sans-serif"
            ctx.textAlign = "center"
            ctx.fillText("Fim de Jogo!", canvas.width / 2, canvas.height / 2 - 20)
            
            ctx.fillStyle = "#8b87ff" # brilho-interface
            ctx.font = "20px sans-serif"
            ctx.fillText(f"Sua pontuação: {score}", canvas.width / 2, canvas.height / 2 + 20)
            
            # Mostra o botão de reiniciar HTML
            document["restart-btn"].style.display = "block"

        def init_game(ev=None):
            """Prepara o jogo para começar ou recomeçar"""
            global snake, score, d, food, game_interval
            
            # Reseta as variáveis
            snake = [{"x": 9 * box, "y": 10 * box}]
            score = 0
            d = "RIGHT"
            food = spawn_food()
            
            # Atualiza UI
            document["score-display"].text = str(score)
            document["restart-btn"].style.display = "none"
            
            # Limpa o intervalo antigo (se existir) e começa um novo
            if game_interval:
                window.clearInterval(game_interval)
            game_interval = window.setInterval(game_loop, 120) # 120ms de velocidade

        document["restart-btn"].bind("click", init_game)

        def game_loop(*args):
            """Loop principal do jogo rodando a cada frame"""
            global score, d, food, snake

            # Pinta o fundo com o fundo-claro
            ctx.fillStyle = "#150136" 
            ctx.fillRect(0, 0, canvas.width, canvas.height)

            # Desenha a Comida usando o destaque-medio
            ctx.fillStyle = "#ffaa00" 
            ctx.beginPath()
            ctx.arc(food["x"] + box/2, food["y"] + box/2, box/2 - 2, 0, 2 * math.pi)
            ctx.fill()

            # Descobre a posição atual da cabeça
            snakeX = snake[0]["x"]
            snakeY = snake[0]["y"]

            # Move a cabeça na direção atual
            if d == "LEFT": snakeX -= box
            if d == "UP": snakeY -= box
            if d == "RIGHT": snakeX += box
            if d == "DOWN": snakeY += box

            # Verifica Colisão com as Paredes
            if snakeX < 0 or snakeX >= canvas.width or snakeY < 0 or snakeY >= canvas.height:
                game_over()
                return

            # Verifica Colisão com o Próprio Corpo
            for i in range(len(snake)):
                if snakeX == snake[i]["x"] and snakeY == snake[i]["y"]:
                    game_over()
                    return

            newHead = {"x": snakeX, "y": snakeY}

            # Verifica se a Cobra comeu a comida
            if snakeX == food["x"] and snakeY == food["y"]:
                score += 1
                document["score-display"].text = str(score)
                food = spawn_food()
            else:
                # Se não comeu, remove o último pedaço do rabo (para ela andar)
                snake.pop()

            # Adiciona a nova cabeça na frente
            snake.insert(0, newHead)

            # Desenha a Cobra
            for i in range(len(snake)):
                # Cabeça com a cor de brilho-interface, corpo com borda-clara
                ctx.fillStyle = "#8b87ff" if i == 0 else "#5752ff" 
                
                # Um leve padding (espaçamento) pra ficar mais bonito
                p = 1
                ctx.fillRect(snake[i]["x"] + p, snake[i]["y"] + p, box - (p*2), box - (p*2))

        # Inicia o jogo pela primeira vez
        init_game()
    </script>
</body>
</html>
