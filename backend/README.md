# GeoHouse - Backend

API do GeoHouse, feita em **FastAPI**. Conecta no banco **MariaDB** hospedado
no servidor `141.11.72.90`.

Esta pasta (`backend/`) roda **separada** do frontend (`frontend/`), mas as duas
vivem no mesmo repositorio (commitadas juntas).

## Rodar localmente (dentro de backend/)
```bash
py -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- API:    http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/api/health

As credenciais do banco vem do arquivo [.env](.env).

## Deploy (Render)
Web Service Python. Veja [render.yaml](render.yaml).
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Depois do deploy, defina `ALLOWED_ORIGINS` com a URL do front para liberar o
CORS, ex: `["https://geohouse-web.onrender.com"]`.

## Endpoints principais
- `GET /api/health`    - status da API e do banco
- `GET /api/bairros`   - lista de bairros
- `GET /api/imoveis`   - lista de imoveis (com filtros)
- `POST /api/login`    - autenticacao (devolve id, nome, email, tipo)
- `POST /api/cadastro` - cria usuario (proprietario | corretor | cliente)

### Papeis (coluna `usuarios.tipo` no banco)
`admin` | `corretor` | `proprietario` | `cliente`. O cadastro pelo site so
permite `proprietario`, `corretor` e `cliente`; `admin` e criado direto no
banco (veja `seed_usuarios.py`).
