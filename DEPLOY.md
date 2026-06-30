# Como publicar (deploy) o GeoHouse no Render

Este repositorio tem **2 pastas** (`backend/` e `frontend/`) que viram **2
servicos separados** no Render. O **banco continua no servidor `141.11.72.90`**
(nada muda nele).

## 1. Criar os servicos
1. Acesse https://dashboard.render.com e faca login (pode entrar com o GitHub).
2. Clique em **New > Blueprint**.
3. Conecte o repositorio **`jaeno198/geohouse`**.
4. O Render le o arquivo [`render.yaml`](render.yaml) e cria os 2 servicos
   (cada um aponta para a sua pasta via `rootDir`):
   - `geohouse-api`  -> o backend  (pasta `backend/`)
   - `geohouse-web`  -> o frontend (pasta `frontend/`)
5. Clique em **Apply** e aguarde o primeiro build.

## 2. Conectar front e back (passo obrigatorio)
Depois do primeiro deploy, cada servico ganha uma URL publica. Voce precisa
dizer um pro outro:

1. Copie a URL do **backend** (ex: `https://geohouse-api.onrender.com`).
2. No servico **geohouse-web** > *Environment* > defina:
   - `VITE_API_URL = https://geohouse-api.onrender.com`
3. Copie a URL do **frontend** (ex: `https://geohouse-web.onrender.com`).
4. No servico **geohouse-api** > *Environment* > defina:
   - `ALLOWED_ORIGINS = ["https://geohouse-web.onrender.com"]`
5. Em cada servico, clique em **Manual Deploy > Deploy latest commit** para
   aplicar as variaveis.

Pronto: o site online passa a falar com a API, que fala com o banco no 141.

## Observacoes
- **Plano free do Render dorme** apos ~15 min sem acesso; a primeira visita
  depois disso demora alguns segundos pra "acordar". Normal para demonstracao.
- O frontend ja esta preparado: usa `VITE_API_URL` quando definido e cai no
  proxy local (`/api`) quando rodando na sua maquina.
- O CORS do backend libera automaticamente dominios `*.onrender.com`,
  `*.vercel.app` e `*.netlify.app`, alem do que estiver em `ALLOWED_ORIGINS`.
