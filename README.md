# Flet ChatRoom — TP2

Aplicação de chat em tempo real desenvolvida em Python com [Flet](https://flet.dev), a correr nativamente em desktop, web e mobile.
Trabalho Prático 2 — Computação Móvel · UAlg LESTI 2025/26

[![Live Demo](https://img.shields.io/badge/live%20demo-railway-blueviolet?style=flat-square)](https://chat-room-tp2-production.up.railway.app)
[![Python](https://img.shields.io/badge/python-3.11-blue?style=flat-square)](https://python.org)
[![Flet](https://img.shields.io/badge/flet-0.83.x-purple?style=flat-square)](https://flet.dev)

---

## Funcionalidades

### Objetivo 1 — Base
- Entrar no chat com nome de utilizador
- Enviar e receber mensagens em tempo real (PubSub)
- Mensagem de entrada visível a todos

### Objetivo 2 — Extra
- **Salas de chat** — criar e trocar entre salas independentes
- **Mensagens privadas** — conversa direta entre dois utilizadores
- **Partilha de ficheiros** — imagens (inline), vídeos e documentos (abrem no player do sistema)
- **Editar / Eliminar** mensagens próprias (premir e manter)
- **Reações por emoji** — 6 emojis com contagem de utilizadores distintos

### Objetivo 3 — Funcionalidades Personalizadas

#### Feature 1 — Pré-visualização de Vídeos YouTube

Ao enviar uma mensagem que contenha um link do YouTube, a aplicação deteta automaticamente o URL e apresenta a miniatura do vídeo diretamente na conversa, sem necessidade de sair da app. O utilizador vê a thumbnail em tamanho reduzido inline na mensagem; ao tocar nela, o vídeo abre no YouTube para reprodução.

A extração do identificador do vídeo é feita com lógica simples em Python: para URLs com o parâmetro `v=` (formato `youtube.com/watch?v=ID`), o ID é obtido fazendo split em `=` e em `&`; para URLs curtos `youtu.be/ID` e para lives (`youtu.be/live/ID`), o ID é o último segmento do caminho. Esta lógica está encapsulada na função `extract_youtube_id`, reutilizada em todas as mensagens.

A miniatura é carregada a partir da API pública do YouTube (`img.youtube.com/vi/{id}/hqdefault.jpg`), não requerendo chave de API nem autenticação. A funcionalidade é completamente passiva — o utilizador escreve o link normalmente e a pré-visualização aparece de forma automática.

#### Feature 2 — Contador de Mensagens Não Lidas

Quando o utilizador está numa sala ou conversa e chegam mensagens noutras salas, a sidebar apresenta um badge circular vermelho com o número de mensagens não lidas, semelhante ao comportamento do WhatsApp ou Telegram. O contador incrementa a cada mensagem recebida numa sala inativa e é reposto a zero automaticamente quando o utilizador navega para essa sala.

A implementação é feita com uma estrutura `dict[str, int]` por sessão que mapeia cada sala ao número de mensagens não lidas. O badge é um `ft.Container` circular (fundo vermelho, texto branco) que fica invisível quando o contador é zero, evitando ruído visual desnecessário. O controlo é atualizado em tempo real via `update()` sempre que chega uma nova mensagem fora da sala ativa.

Esta funcionalidade melhora significativamente a usabilidade em contextos com múltiplas salas ativas em simultâneo, permitindo ao utilizador saber de imediato onde há atividade nova sem ter de navegar manualmente por todas as salas.

### Objetivo 4 — Deploy e Personalização Visual
- **Favicon personalizado** — ícone FC (indigo) no tab do browser
- **Loading animation** — ícone personalizado no ecrã de carregamento
- **Deploy** — aplicação publicada em [Railway](https://railway.app)

---

## Stack

| | |
|---|---|
| Framework | [Flet](https://flet.dev) — Flutter UI from Python |
| Language | Python 3.11 |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| Deploy | [Railway](https://railway.app) |

---

## Instalação

```bash
# Instalar dependências (requer uv)
uv sync
```

> Se não tiver o `uv` instalado: `pip install uv`

---

## Como Correr

| Plataforma | Comando |
|---|---|
| Desktop | `uv run flet run main.py` |
| Web | `uv run flet run --web main.py` |
| Android | `uv run flet run --android main.py` |

> **Android:** instala a [app Flet](https://play.google.com/store/apps/details?id=com.appveyor.flet) no telemóvel, corre o comando no PC e lê o QR code. O PC e o telemóvel têm de estar na mesma rede Wi-Fi.

---

## Estrutura

```
TP2_ChatRoom/
├── main.py           # Código fonte completo da aplicação
├── pyproject.toml    # Dependências (uv)
├── uv.lock
├── assets/
│   ├── favicon.png              # Ícone no tab do browser
│   ├── icon.png                 # Ícone da app
│   ├── icons/
│   │   ├── loading-animation.png  # Ecrã de carregamento
│   │   └── Icon-192.png
│   └── uploads/                 # Ficheiros enviados (limpos ao arrancar)
└── README.md
```

---

## Notas Técnicas

- Toda a lógica está num único ficheiro `main.py`, por simplicidade
- O estado global (salas, histórico, reações) é partilhado entre sessões via variáveis de módulo e PubSub
- A pasta `assets/uploads/` é limpa automaticamente ao iniciar o servidor
- Ficheiros enviados são acessíveis via HTTP no URL do servidor Flet
- Deploy em Railway com `host="0.0.0.0"` e porta dinâmica via `$PORT`

---

## Autor

Sadik 79440 — LESTI · UAlg · 2025/26
