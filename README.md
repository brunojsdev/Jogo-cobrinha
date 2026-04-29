# 🐍 Jogo da Cobrinha - Python/Brython

Uma reinterpretação moderna e temática do clássico "Jogo da Cobrinha", desenvolvida utilizando **Python** nativo no navegador através da engine **Brython**. O projeto apresenta uma estética baseada em exploração espacial com renderização de pixel art procedimental e suporte completo a temas.

## 🚀 Diferencial Tecnológico: Brython

Diferente da maioria dos jogos casuais para web que utilizam JavaScript, este projeto foi escrito em **Python 3**. A engine Brython permite que a lógica de jogo, manipulação do DOM e renderização no HTML5 Canvas sejam feitas inteiramente com sintaxe Python, unindo a legibilidade da linguagem com o alcance da web.

## ✨ Funcionalidades

- **Lógica de Jogo em Python:** Processamento de colisões, movimento e crescimento da cobra via scripts Python.
- **Motor de Pixel Art Procedural:** O fundo do jogo (planetas, luas e estrelas) é gerado dinamicamente no Canvas, utilizando matrizes de sprites definidas no código.
- **Sistema de Temas Dinâmico:** Alternância entre Modo Escuro (Espaço Profundo) e Modo Claro (Nebulosa), com atualização em tempo real das cores da interface e dos elementos do Canvas.
- **Controles Híbridos:** Suporte total para teclado (Setas/Enter/Espaço) e controles touch responsivos para dispositivos móveis.
- **Cores Adaptativas:** A cor da cobra muda dinamicamente (sistema HSL) conforme o jogador consome itens e aumenta sua pontuação.

## 🎨 Identidade Visual

- **Paleta Dark:** Tons de roxo profundo (`#040014`) e amarelo neon (`#ffdd00`).
- **Paleta Light:** Tons quentes de laranja e amarelo, mantendo o contraste e legibilidade.
- **Sprites:** Planetas e estrelas desenhados pixel a pixel via código, garantindo leveza e um visual retrô consistente.

## 🛠️ Tecnologias Utilizadas

- **Python 3 / Brython:** Motor principal da lógica de negócio.
- **HTML5 Canvas API:** Renderização gráfica de alta performance.
- **Tailwind CSS:** Estruturação da interface e componentes de UI.
- **Lucide Icons:** Ícones vetoriais para controles e botões.

## 📂 Estrutura de Arquivos

```bash
/
├── index.html      # Estrutura da UI, estilos CSS e carregamento do Brython
├── main.py         # Lógica do jogo, renderização e motor de sprites
├── img/            # Assets estáticos (favicon)
└── README.md       # Documentação do projeto
```

## ⚙️ Como Executar o Projeto

Como o Brython processa os arquivos `.py` via requisições assíncronas, recomenda-se abrir o projeto através de um servidor local para evitar restrições de CORS:

1.  Com o Python instalado, execute na pasta do projeto:
    ```bash
    python -m http.server
    ```
2.  Acesse `http://localhost:8000` no seu navegador.

---

### 📝 Notas de Versão (V2)

- Adicionado sistema de `render_scene` para atualização de tema pré-jogo.
- Implementado `offscreen_canvas` para otimização do fundo estático.
- Refatoração de variáveis para evitar conflitos de shadowing no VS Code.

Desenvolvido por **Bruno J. Silveira** | Acesse meu Portfólio
