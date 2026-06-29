# Como rodar o GeoHouse (backend + frontend + banco juntos)

Agora tudo sobe com **um comando só**, pelo `app.py`. O banco de dados é lido
do arquivo `.env` (não há credencial fixa no código).

## 1. Instalar dependências (só na primeira vez)

Frontend (Node):

```bash
npm install
```

Backend (Python) — o `.venv` já está pronto neste projeto, mas se precisar recriar:

```bash
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

## 2. Rodar tudo junto

```bash
.\.venv\Scripts\python.exe app.py
```

O `app.py` faz tudo:

- lê o `.env` e testa a conexão com o banco;
- sobe o **backend** (FastAPI/uvicorn) em http://127.0.0.1:8000;
- sobe o **frontend** (Vite/Vue) em http://127.0.0.1:5173;
- com **Ctrl + C** derruba os dois ao mesmo tempo.

A saída deve mostrar:

```txt
Conexao : OK (banco conectado)
Frontend: http://127.0.0.1:5173
Backend : http://127.0.0.1:8000
```

Senha admin do site: `geohouse2025`

## Banco de dados (.env)

As credenciais ficam em `.env`:

```env
DB_HOST=...
DB_PORT=3306
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
```

Se o banco estiver fora do ar, a API continua respondendo com dados locais de
demonstração (fallback), para o site não quebrar.

## Rotas da API

```txt
http://127.0.0.1:8000/api/health          -> status da API e do banco
http://127.0.0.1:8000/api/bairros
http://127.0.0.1:8000/api/imoveis
http://127.0.0.1:8000/api/imoveis?bairro=Zona%2001
http://127.0.0.1:8000/api/imoveis?modalidade=aluguel&bairro=Centro
```

## Rodar separado (opcional)

Se quiser rodar cada parte isolada:

```bash
npm run dev:api        # só o backend
npm run dev:frontend   # só o frontend
npm run dev:full       # os dois via concurrently
```
