# GeoHouse com API Python + filtro por bairro no mapa

## Como rodar o projeto (Windows / Mac / Linux)

O projeto tem:
- **Frontend**: Vue + Vite (porta `5173`)
- **Backend**: FastAPI (Uvicorn) (porta `8000`)

### Rodar backend (API)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

No Windows:

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Rodar frontend (Vue)

Em outro terminal:

```bash
npm install
npm run dev:frontend
```

### Rodar os dois juntos (recomendado)

Se você já instalou as dependências:

```bash
npm run dev:full
```

Primeira vez (ou depois de limpar o ambiente):

```bash
npm install
npm run setup:api
npm run dev:full
```

### Acessos

- **Frontend**: `http://127.0.0.1:5173/`
- **Backend**: `http://127.0.0.1:8000/`

## Rotas da API

```txt
GET http://127.0.0.1:8000/api/bairros
GET http://127.0.0.1:8000/api/imoveis
GET http://127.0.0.1:8000/api/imoveis?bairro=Zona%2001
GET http://127.0.0.1:8000/api/imoveis?modalidade=aluguel&bairro=Centro
```

O Vue busca os bairros na API e atualiza os marcadores do Leaflet conforme o bairro selecionado.

## Estilos de mapa compatíveis (Leaflet Tile Layers)

O mapa está configurado em `src/views/Dashboard.vue` com `L.tileLayer(...)`.

### Por que aparecem quadrados brancos/cinza?

Isso acontece quando o **tile não carrega**. Causas comuns:

- `subdomains` errado (ex.: OSM com `'abcd'` — o correto é `'abc'`)
- `maxZoom` acima do limite do provedor
- URL com padrão errado (Esri usa `{z}/{y}/{x}`, não `{z}/{x}/{y}`)
- Usar `{r}` em URL que não suporta (só CARTO usa `{r}`)

### Tabela rápida (configuração segura)

| Provedor | subdomains | maxZoom | Risco de quadrados |
|----------|------------|---------|---------------------|
| **CARTO** | `'abcd'` | `20` | Baixo (recomendado) |
| **OpenStreetMap** | `'abc'` | `19` | Baixo (se configurar certo) |
| **Esri** | omitir | `19` | Baixo |
| **OpenTopoMap** | `'abc'` | `17` | Baixo |

---

### CARTO (sem API key) — recomendado

Usa `{z}/{x}/{y}{r}` e `subdomains: 'abcd'`.

| Estilo | URL |
|--------|-----|
| **Light (padrão do projeto)** | `https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png` |
| **Light (sem labels)** | `https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png` |
| **Voyager** | `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png` |
| **Voyager (sem labels)** | `https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png` |
| **Dark** | `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png` |
| **Dark (sem labels)** | `https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png` |

```js
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
  subdomains: 'abcd',
  maxZoom: 20,
}).addTo(map.value)
```

---

### OpenStreetMap (sem API key)

Usa `{z}/{x}/{y}` **sem** `{r}`. Subdomínios: **`'abc'`** (não use `'abcd'`).

| Estilo | URL |
|--------|-----|
| **OSM padrão** | `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` |
| **OSM Humanitarian (HOT)** | `https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png` |

```js
L.tileLayer(`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`, {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  subdomains: 'abc',
  maxZoom: 19,
}).addTo(map.value)
```

---

### Esri (sem API key)

Usa `{z}/{y}/{x}` (ordem diferente). **Não** use `subdomains`.

| Estilo | URL |
|--------|-----|
| **World Street Map** | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}` |
| **World Imagery (satélite)** | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}` |
| **World Topo** | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}` |
| **World Light Gray** | `https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}` |

```js
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Tiles &copy; Esri',
  maxZoom: 19,
}).addTo(map.value)
```

---

### OpenTopoMap (sem API key)

Bom para mapas com relevo. Subdomínios: `'abc'`, `maxZoom: 17`.

| Estilo | URL |
|--------|-----|
| **OpenTopoMap** | `https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png` |

```js
L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
  subdomains: 'abc',
  maxZoom: 17,
}).addTo(map.value)
```

---

### O que evitar

| Erro | Problema |
|------|----------|
| OSM + `subdomains: 'abcd'` | Subdomínio `d` não existe → quadrados brancos |
| OSM + `maxZoom: 20` | Tiles acima de 19 podem falhar |
| Esri com `{z}/{x}/{y}` | Ordem errada → mapa quebrado |
| CARTO sem `{r}` na URL | URL incompleta em telas retina |
| Misturar URL de um provedor com config de outro | Attribution/subdomains incompatíveis |

### Dica extra no projeto

Após trocar o estilo ou redimensionar o mapa, chame `map.invalidateSize()` para evitar áreas sem tile no layout flex do dashboard.

