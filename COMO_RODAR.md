# Como rodar o GeoHouse (frontend e backend separados)

O projeto tem **duas pastas independentes**, commitadas juntas neste repositório:

```
geohouse/
├── frontend/   → app Vue (Vite)        — porta 5173
└── backend/    → API FastAPI (uvicorn) — porta 8000
```

Cada parte roda no seu próprio terminal. O banco de dados MariaDB continua no
servidor `141.11.72.90` e é lido do arquivo `backend/.env` (sem credencial fixa
no código).

---

## 1. Backend (API)

Em um terminal, dentro de `backend/`:

```bash
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

- API:    http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/api/health  → mostra se o banco está conectado

> Se o banco estiver fora do ar, a API ainda responde `/api/imoveis` com dados
> locais de demonstração (fallback), para o site não quebrar.

### Usuários de teste (papéis no banco)

Para criar/atualizar os 4 usuários de exemplo (um por papel):

```bash
.\.venv\Scripts\python.exe seed_usuarios.py
```

| Papel (usuarios.tipo) | Login (e-mail)              | Senha        |
|-----------------------|-----------------------------|--------------|
| admin                 | admin@geohouse.com          | Admin@123    |
| corretor              | corretor@geohouse.com       | Corretor@123 |
| proprietario          | proprietario@geohouse.com   | Prop@123     |
| cliente               | cliente@geohouse.com        | Cliente@123  |

O painel `/admin` é liberado **apenas para o papel `admin`** (não há mais senha
fixa no código — o acesso vem da role do usuário logado, vinda do banco).

---

## 2. Frontend (site)

Em **outro** terminal, dentro de `frontend/`:

```bash
cd frontend
npm install        # só na primeira vez
npm run dev
```

- Site: http://127.0.0.1:5173

Em desenvolvimento, o Vite faz proxy de `/api` para `http://127.0.0.1:8000`
(veja `frontend/vite.config.js`), então não precisa configurar nada.
Em produção, defina `VITE_API_URL` com a URL pública do backend.

---

## Rotas da API

```txt
GET  /api/health                              status da API e do banco
GET  /api/bairros                             lista de bairros
GET  /api/imoveis                             lista de imóveis (com filtros)
GET  /api/imoveis?bairro=Zona%2001
GET  /api/imoveis?modalidade=aluguel&bairro=Centro
POST /api/login        { email, senha }       autenticação → { id, nome, email, tipo }
POST /api/cadastro     { nome, email, senha, tipo, telefone?, creci? }   cria usuário
```

`tipo` no cadastro aceita `proprietario`, `corretor` ou `cliente`
(o papel `admin` é criado direto no banco, nunca pelo site).

## Banco de dados (backend/.env)

```env
DB_HOST=141.11.72.90
DB_PORT=3306
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
```
