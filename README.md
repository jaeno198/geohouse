# GeoHouse

Plataforma de imóveis de Maringá (PR) com mapa de bairros. O repositório tem
**duas pastas independentes, commitadas juntas**:

```
geohouse/
├── frontend/   → app Vue (Vite)        — http://127.0.0.1:5173
└── backend/    → API FastAPI (uvicorn) — http://127.0.0.1:8000
```

Cada parte roda separada, no seu próprio terminal. O banco MariaDB fica no
servidor `141.11.72.90` (credenciais em `backend/.env`).

- **Como rodar:** veja [COMO_RODAR.md](COMO_RODAR.md)
- **Deploy (Render):** veja [DEPLOY.md](DEPLOY.md) e [render.yaml](render.yaml)

## Papéis de usuário (coluna `usuarios.tipo` no banco)

`admin` · `corretor` · `proprietario` · `cliente`

- Login (`POST /api/login`) devolve o papel; o frontend roteia por ele.
- Cadastro pelo site (`POST /api/cadastro`) cria `proprietario`, `corretor` ou
  `cliente`. O `admin` é criado direto no banco (`backend/seed_usuarios.py`).
- O painel `/admin` é liberado apenas para o papel `admin`.
