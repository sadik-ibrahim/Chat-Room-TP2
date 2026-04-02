# TP2 – Flet ChatRoom

Aplicação de chat em tempo real desenvolvida em Python com a framework [Flet](https://flet.dev).
Trabalho Prático 2 — Computação Móvel · UAlg LESTI 2025/26

---

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (gestor de pacotes)

Dependências (instaladas automaticamente pelo uv):

| Pacote | Versão |
|---|---|
| flet | 0.83.x |
| flet-desktop | 0.83.x |

---

## Instalação

```bash
# Clonar / extrair o projeto
cd TP2_ChatRoom

# Instalar dependências com uv
uv sync
```

---

## Como Correr

### Desktop (Windows / macOS / Linux)

```bash
uv run flet run main.py
```

### Browser — múltiplas sessões simultâneas

```bash
uv run flet run --web main.py
```

Abre dois tabs em `http://localhost:8550` para testar o chat entre utilizadores.

### Android (app nativa Flet)

```bash
uv run flet run --android main.py
```

Instala a [app Flet](https://play.google.com/store/apps/details?id=com.appveyor.flet) no telemóvel, corre o comando acima no PC e lê o QR code apresentado no terminal.

> **Nota:** o PC e o telemóvel têm de estar na mesma rede Wi-Fi.

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

---

## Estrutura do Projeto

```
TP2_ChatRoom/
├── main.py           # Código fonte completo da aplicação
├── pyproject.toml    # Dependências (uv)
├── uv.lock           # Lock file
├── assets/
│   └── uploads/      # Ficheiros enviados (limpos ao arrancar)
└── README.md
```

---

## Notas Técnicas

- Toda a lógica está num único ficheiro `main.py`, por simplicidade
- O estado global (salas, histórico, reações) é partilhado entre sessões via variáveis de módulo e PubSub
- A pasta `assets/uploads/` é limpa automaticamente ao iniciar o servidor
- Ficheiros enviados são acessíveis via HTTP no URL do servidor Flet

---

## Autor

Sadik 79440 — LESTI · UAlg · 2025/26
