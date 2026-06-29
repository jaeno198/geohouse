from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import unicodedata

try:
    import bcrypt
    _BCRYPT_OK = True
except Exception:  # noqa: BLE001
    _BCRYPT_OK = False

# Conexao com o banco (credenciais vindas do .env). Se as dependencias do
# banco nao estiverem disponiveis, a API continua funcionando com os dados
# locais de demonstracao definidos mais abaixo.
try:
    from database import db_status, query, db_config
    _DB_OK = True
    _DB_ERR = None
except Exception as _exc:  # noqa: BLE001
    _DB_OK = False
    _DB_ERR = f"{type(_exc).__name__}: {_exc}"

    def db_status():
        return False, f"modulo 'database' indisponivel: {_DB_ERR}"

app = FastAPI(title="GeoHouse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalizar(texto: str) -> str:
    texto = texto or ""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
    return texto.lower().strip()

# Lista baseada no Anexo II - Descrição dos bairros por região, da Prefeitura de Maringá.
# Mantida como base didática para alimentar o filtro do frontend.
BAIRROS_MARINGA = sorted(set([
    "Centro", "Zona 01", "Zona 02", "Zona 03", "Zona 04", "Zona 05", "Zona 06", "Zona 07", "Zona 08",
    "Zona 09", "Zona 10", "Zona 12", "Zona 13", "Zona 14", "Zona 15", "Zona 17", "Zona 18", "Zona 20",
    "Zona 22", "Zona 23", "Zona 25", "Zona 26", "Zona 27", "Zona 28", "Zona 35", "Zona 38", "Zona 39",
    "Parque Residencial Anchieta", "Jardim Acema", "Jardim Carolina", "Jardim Castor", "Jardim Ipiranga",
    "Jardim Universitário", "Loteamento Alto da Boa Vista", "Residencial Moreschi", "Zona Armazém", "Zona Industrial",
    "Jardim Canadá", "Loteamento Marega", "Jardim Monte Belo", "Vila Progresso", "Vila Morangueira",
    "Vila Morangueira Ampliação", "Bom Jardim", "Conjunto Habitacional Requião", "Conjunto Habitacional Itatiaia",
    "Conjunto Residencial Guaiapó", "Conjunto Residencial Karina", "Jardim América", "Jardim Atlanta", "Jardim da Glória",
    "Jardim Nova América", "Jardim Paulista", "Parque Industrial I", "Parque Industrial II", "Parque Residencial Ibirapuera",
    "Parque Residencial Regente", "Chácara Morangueira", "Jardim Campos Elíseos", "Jardim Colina Verde",
    "Jardim Dourado", "Jardim Novo Oásis", "Jardim Oásis", "Jardim Pinheiros", "Jardim Santa Alice",
    "Jardim Tupinambá", "Jardim Virgínia", "Loteamento Batel", "Loteamento Grajaú", "Parque Residencial Patrícia",
    "Parque Residencial Tuiuti", "Jardim São Francisco", "Vila Esperança", "Vila Santo Antônio", "Jardim Diamante",
    "Jardim Oriental", "Portal das Torres", "Condomínio Ana Rosa", "Condomínio Cidade Campo", "Recanto Kakogawa",
    "Jardim Alvorada", "Jardim Imperial", "Parque Residencial Cidade Nova", "Cidade Jardim", "Jardim do Sol",
    "Vila Nevada", "Miosótis", "Jardim Vitória", "Parque das Bandeiras", "Parque das Palmeiras", "Parque Residencial Quebec",
    "Residencial Copacabana", "Copacabana II", "Loteamento Jardim Baeza", "Jardim Dias", "Jardim Kakogawa",
    "Jardim Licce", "Jardim Tóquio", "Parque Avenida", "Parque Grevíleas", "Parque Residencial Eldorado",
    "Chácaras Alvorada", "Jardim Andrade", "Jardim Novo Alvorada", "Jardim Santa Clara", "Loteamento Ebenezer",
    "Loteamento Sumaré", "Parque Industrial Duzentos", "Condomínio Country Village", "Condomínio Monte Alto",
    "Condomínio Santa Maria", "Condomínio Santa Marina", "Condomínio Bela Vista", "Jardim Novo Paulista", "Jardim Monte Sinai",
    "Jardim Monte Sião", "Jardins de Monet Residence", "Conjunto Habitacional Planalto", "Central Park", "Cidade Industrial",
    "Jardim Campo Belo", "Jardim Guairacá", "Jardim Kosmos", "Jardim Olímpico", "Jardim Ouro Cola", "Jardim Três Lagoas",
    "Moradia Atenas", "Parque Hortência", "Parque Residencial Andréa", "Jardim Solimões", "Residencial Pimenta",
    "Residencial Arezzo", "Giardino San Marco", "Jardim Noroeste", "Jardim Continental", "Cidade Universitária",
    "Jardim Los Angeles", "Jardim Lucianópolis", "Jardim Mandacaru", "Jardim Maravilha", "Jardim Monte Carlo",
    "Jardim São Jorge", "Jardim Seminário", "Núcleo Social Papa João XXIII", "Vila Santa Isabel", "Vila Vardelina",
    "Jardim Império do Sol", "Jardim Monte Rei", "Jardim Paris", "Jardim Alto Alegre", "Jardim Primavera",
    "Jardim São Pedro", "Jardim Golden", "Jardim Belo Horizonte", "Jardim Marajoara", "Jardim do Índio",
    "Jardim Azaléia", "Jardim Gabriella", "Jardim Guaporé", "Jardim Parque Horto", "Jardim San Remo",
    "Parque Residencial Rio Branco", "Jardim Ivemar", "Chácaras Estilos", "Jardim Aurora", "Jardim Califórnia",
    "Jardim do Carmo", "Jardim dos Pássaros", "Jardim Everest", "Jardim Indaiá", "Jardim Montreal",
    "Jardim São Miguel", "Jardim Santa Cruz", "Borba Gato", "Jardim Alzira", "Jardim Espanha",
    "Jardim Iguaçu", "Jardim Santa Rosa", "Jardim Veredas", "Jardim Verônica", "Portal de Maringá",
    "Jardim Europa", "Distrito Industrial II", "Jardim Nilza", "Parque dos Cerealistas", "Jardim das Estações",
    "Jardim Industrial", "Parque Industrial Sul", "Parque Itaipu", "Jardim Barcelona", "Jardim Castanheira",
    "Conjunto Residencial Planville", "Jardim Brasil", "Jardim Brasília", "Jardim Imperador", "Jardim Petrópolis",
    "Jardim Pilar", "Jardim Real", "Jardim Rebouças", "Jardim Santa Helena", "Jardim Tropical",
    "Parque das Laranjeiras", "Jardim Campos", "Jardim São Domingos", "Jardim Colombo", "Chácaras Centenário",
    "Jardim Munique", "Jardim Santa Mônica", "Jardim Santa Rita", "Jardim Vila Rica", "Vila Cristino",
    "Vila Bosque", "Vila Cleópatra", "Vila Nova", "Jardim Cerro Azul", "Jardim Itapuã", "Jardim Novo Horizonte",
    "Jardim Social", "Vila Emília", "Jardim Guararapes", "Vila Cafelândia", "Vila Ipiranga",
    "Jardim Alamar", "Jardim Betty", "Jardim das Nações", "Jardim Higienópolis", "Jardim Itália",
    "Jardim Laudicéia", "Jardim São Conrado", "Jardim Universo", "Jardim Botânico", "Recanto dos Magnatas",
    "Cidade Monções", "Jardim Michelângelo", "Jardim Gambini", "Jardim Portugal", "Jardim Atami",
    "Jardim São Clemente", "Jardim São Basílio", "Jardim Ipanema", "Jardim São Paulo", "Jardim das Flores",
    "Santa Felicidade", "Parque Tarumã", "Residencial Dolores Duran", "Residencial Tarumã", "Jardim Paraíso",
    "Jardim Internorte", "Chácaras Assaí", "Chácaras Paulista", "Jardim Tabaetê", "Loteamento Malbec",
    "Vila Marumby", "Jardim Dom Pedro Peres", "Jardim Aclimação", "Jardim Fregadolli", "Parque da Gávea",
    "Parque Lagoa Dourada", "Jardim Leblon", "Galeão", "Distrito Floriano", "Vila Regina", "Vila Ruth",
    "Centro Cívico", "Jardim Bertioga", "Jardim Valparaíso", "Jardim Freitas", "Eurogarden",
    "Chácaras Aeroporto", "Jardim Araucária", "Jardim São Silvestre", "Alto das Grevíleas", "Loteamento Madrid",
    "Prolar", "Jardim Catedral", "Cidade Alta", "Parque Industrial Cidade de Maringá"
]))

IMOVEIS = [
    {"id": 1, "titulo": "Apartamento mobiliado próximo ao centro", "tipo": "apartamento", "modalidade": "aluguel", "zona": "centro", "anunciante": "pago", "preco": 2350, "quartos": 2, "banheiros": 2, "area": 72, "vagas": 1, "bairro": "Zona 01", "cidade": "Maringá PR", "lat": -23.4214, "lng": -51.9341, "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&q=80"},
    {"id": 2, "titulo": "Studio moderno com lazer completo", "tipo": "apartamento", "modalidade": "aluguel", "zona": "centro", "anunciante": "pago", "preco": 1850, "quartos": 1, "banheiros": 1, "area": 42, "vagas": 1, "bairro": "Centro", "cidade": "Maringá PR", "lat": -23.4252, "lng": -51.9388, "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=900&q=80"},
    {"id": 3, "titulo": "Casa para locação com churrasqueira", "tipo": "casa", "modalidade": "aluguel", "zona": "leste", "anunciante": "proprietario", "preco": 2800, "quartos": 3, "banheiros": 2, "area": 155, "vagas": 2, "bairro": "Borba Gato", "cidade": "Maringá PR", "lat": -23.4279, "lng": -51.9025, "img": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=900&q=80"},
    {"id": 4, "titulo": "Sala comercial em avenida movimentada", "tipo": "comercial", "modalidade": "aluguel", "zona": "centro", "anunciante": "pago", "preco": 3600, "quartos": 0, "banheiros": 1, "area": 86, "vagas": 2, "bairro": "Zona 04", "cidade": "Maringá PR", "lat": -23.4181, "lng": -51.9278, "img": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=900&q=80"},
    {"id": 5, "titulo": "Apartamento alto padrão na Zona 01", "tipo": "apartamento", "modalidade": "venda", "zona": "centro", "anunciante": "pago", "preco": 720000, "quartos": 3, "banheiros": 2, "area": 118, "vagas": 2, "bairro": "Zona 01", "cidade": "Maringá PR", "lat": -23.4211, "lng": -51.9324, "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&q=80"},
    {"id": 6, "titulo": "Casa térrea com piscina", "tipo": "casa", "modalidade": "venda", "zona": "sul", "anunciante": "pago", "preco": 890000, "quartos": 4, "banheiros": 3, "area": 260, "vagas": 2, "bairro": "Jardim Novo Horizonte", "cidade": "Maringá PR", "lat": -23.4446, "lng": -51.9255, "img": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=900&q=80"},
    {"id": 7, "titulo": "Casa geminada pronta para morar", "tipo": "casa", "modalidade": "venda", "zona": "norte", "anunciante": "proprietario", "preco": 335000, "quartos": 2, "banheiros": 1, "area": 92, "vagas": 1, "bairro": "Jardim Alvorada", "cidade": "Maringá PR", "lat": -23.3928, "lng": -51.9490, "img": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900&q=80"},
    {"id": 8, "titulo": "Terreno 300m² em bairro consolidado", "tipo": "terreno", "modalidade": "venda", "zona": "oeste", "anunciante": "proprietario", "preco": 185000, "quartos": 0, "banheiros": 0, "area": 300, "vagas": 0, "bairro": "Jardim Universo", "cidade": "Maringá PR", "lat": -23.4246, "lng": -51.9774, "img": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=80"},
    {"id": 9, "titulo": "Chácara com área verde", "tipo": "rural", "modalidade": "venda", "zona": "sul", "anunciante": "pago", "preco": 1180000, "quartos": 3, "banheiros": 2, "area": 5000, "vagas": 4, "bairro": "Saída para Paiçandu", "cidade": "Maringá PR", "lat": -23.4750, "lng": -51.9503, "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=900&q=80"},

    # Imóveis fictícios adicionados manualmente para demonstração do filtro por bairro no mapa.
    {"id": 10, "titulo": "Apartamento compacto na Zona 07", "tipo": "apartamento", "modalidade": "aluguel", "zona": "norte", "anunciante": "pago", "preco": 1700, "quartos": 1, "banheiros": 1, "area": 45, "vagas": 1, "bairro": "Zona 07", "cidade": "Maringá PR", "lat": -23.4102, "lng": -51.9398, "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=900&q=80"},
    {"id": 11, "titulo": "Sobrado no Jardim Aclimação", "tipo": "casa", "modalidade": "venda", "zona": "sul", "anunciante": "proprietario", "preco": 650000, "quartos": 3, "banheiros": 3, "area": 180, "vagas": 2, "bairro": "Jardim Aclimação", "cidade": "Maringá PR", "lat": -23.4524, "lng": -51.9445, "img": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900&q=80"},
    {"id": 12, "titulo": "Casa familiar no Jardim Alvorada", "tipo": "casa", "modalidade": "aluguel", "zona": "norte", "anunciante": "pago", "preco": 2400, "quartos": 3, "banheiros": 2, "area": 140, "vagas": 2, "bairro": "Jardim Alvorada", "cidade": "Maringá PR", "lat": -23.3908, "lng": -51.9482, "img": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=900&q=80"},
    {"id": 13, "titulo": "Apartamento próximo à UEM", "tipo": "apartamento", "modalidade": "aluguel", "zona": "norte", "anunciante": "pago", "preco": 2100, "quartos": 2, "banheiros": 1, "area": 64, "vagas": 1, "bairro": "Jardim Universitário", "cidade": "Maringá PR", "lat": -23.4068, "lng": -51.9391, "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&q=80"},
    {"id": 14, "titulo": "Casa no Jardim Paris", "tipo": "casa", "modalidade": "venda", "zona": "norte", "anunciante": "proprietario", "preco": 420000, "quartos": 3, "banheiros": 2, "area": 125, "vagas": 2, "bairro": "Jardim Paris", "cidade": "Maringá PR", "lat": -23.3759, "lng": -51.9195, "img": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=900&q=80"},
    {"id": 15, "titulo": "Terreno no Jardim Imperial", "tipo": "terreno", "modalidade": "venda", "zona": "norte", "anunciante": "pago", "preco": 230000, "quartos": 0, "banheiros": 0, "area": 300, "vagas": 0, "bairro": "Jardim Imperial", "cidade": "Maringá PR", "lat": -23.3858, "lng": -51.9411, "img": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=80"},
    {"id": 16, "titulo": "Apartamento no Jardim Novo Horizonte", "tipo": "apartamento", "modalidade": "aluguel", "zona": "sul", "anunciante": "pago", "preco": 2600, "quartos": 3, "banheiros": 2, "area": 86, "vagas": 1, "bairro": "Jardim Novo Horizonte", "cidade": "Maringá PR", "lat": -23.4442, "lng": -51.9276, "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&q=80"},
    {"id": 17, "titulo": "Casa ampla no Jardim Iguaçu", "tipo": "casa", "modalidade": "venda", "zona": "oeste", "anunciante": "proprietario", "preco": 510000, "quartos": 3, "banheiros": 2, "area": 160, "vagas": 2, "bairro": "Jardim Iguaçu", "cidade": "Maringá PR", "lat": -23.4377, "lng": -51.9721, "img": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=900&q=80"},
    {"id": 18, "titulo": "Studio no Centro", "tipo": "apartamento", "modalidade": "aluguel", "zona": "centro", "anunciante": "pago", "preco": 1550, "quartos": 1, "banheiros": 1, "area": 35, "vagas": 0, "bairro": "Centro", "cidade": "Maringá PR", "lat": -23.4247, "lng": -51.9366, "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=900&q=80"},
    {"id": 19, "titulo": "Comercial na Zona 05", "tipo": "comercial", "modalidade": "aluguel", "zona": "centro", "anunciante": "pago", "preco": 4800, "quartos": 0, "banheiros": 2, "area": 120, "vagas": 3, "bairro": "Zona 05", "cidade": "Maringá PR", "lat": -23.4322, "lng": -51.9344, "img": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=900&q=80"},
    {"id": 20, "titulo": "Apartamento na Vila Morangueira", "tipo": "apartamento", "modalidade": "venda", "zona": "norte", "anunciante": "pago", "preco": 380000, "quartos": 2, "banheiros": 2, "area": 74, "vagas": 1, "bairro": "Vila Morangueira", "cidade": "Maringá PR", "lat": -23.4028, "lng": -51.9273, "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&q=80"},
    {"id": 21, "titulo": "Casa no Jardim Europa", "tipo": "casa", "modalidade": "venda", "zona": "oeste", "anunciante": "proprietario", "preco": 590000, "quartos": 3, "banheiros": 2, "area": 170, "vagas": 2, "bairro": "Jardim Europa", "cidade": "Maringá PR", "lat": -23.4358, "lng": -51.9848, "img": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=900&q=80"},
    {"id": 22, "titulo": "Apartamento no Jardim Canadá", "tipo": "apartamento", "modalidade": "aluguel", "zona": "leste", "anunciante": "pago", "preco": 2200, "quartos": 2, "banheiros": 2, "area": 70, "vagas": 1, "bairro": "Jardim Canadá", "cidade": "Maringá PR", "lat": -23.4112, "lng": -51.9158, "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&q=80"},
    {"id": 23, "titulo": "Casa no Parque das Laranjeiras", "tipo": "casa", "modalidade": "aluguel", "zona": "leste", "anunciante": "pago", "preco": 2500, "quartos": 3, "banheiros": 2, "area": 150, "vagas": 2, "bairro": "Parque das Laranjeiras", "cidade": "Maringá PR", "lat": -23.4248, "lng": -51.8857, "img": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900&q=80"},
    {"id": 24, "titulo": "Terreno no Jardim São Silvestre", "tipo": "terreno", "modalidade": "venda", "zona": "sul", "anunciante": "proprietario", "preco": 210000, "quartos": 0, "banheiros": 0, "area": 250, "vagas": 0, "bairro": "Jardim São Silvestre", "cidade": "Maringá PR", "lat": -23.4644, "lng": -51.9572, "img": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=80"},
    {"id": 25, "titulo": "Apartamento no Jardim Botânico", "tipo": "apartamento", "modalidade": "venda", "zona": "sul", "anunciante": "pago", "preco": 470000, "quartos": 2, "banheiros": 2, "area": 82, "vagas": 2, "bairro": "Jardim Botânico", "cidade": "Maringá PR", "lat": -23.4545, "lng": -51.9185, "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=900&q=80"},
    {"id": 26, "titulo": "Casa no Jardim Tóquio", "tipo": "casa", "modalidade": "venda", "zona": "oeste", "anunciante": "pago", "preco": 540000, "quartos": 3, "banheiros": 2, "area": 155, "vagas": 2, "bairro": "Jardim Tóquio", "cidade": "Maringá PR", "lat": -23.4143, "lng": -51.9689, "img": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=900&q=80"},
    {"id": 27, "titulo": "Casa no Jardim Mandacaru", "tipo": "casa", "modalidade": "aluguel", "zona": "norte", "anunciante": "proprietario", "preco": 2300, "quartos": 3, "banheiros": 1, "area": 130, "vagas": 2, "bairro": "Jardim Mandacaru", "cidade": "Maringá PR", "lat": -23.3936, "lng": -51.9282, "img": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=900&q=80"},
    {"id": 28, "titulo": "Apartamento na Zona 03", "tipo": "apartamento", "modalidade": "aluguel", "zona": "centro", "anunciante": "pago", "preco": 1900, "quartos": 2, "banheiros": 1, "area": 62, "vagas": 1, "bairro": "Zona 03", "cidade": "Maringá PR", "lat": -23.4321, "lng": -51.9228, "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&q=80"},
    {"id": 29, "titulo": "Sobrado no Jardim América", "tipo": "casa", "modalidade": "venda", "zona": "norte", "anunciante": "pago", "preco": 610000, "quartos": 3, "banheiros": 3, "area": 190, "vagas": 2, "bairro": "Jardim América", "cidade": "Maringá PR", "lat": -23.3899, "lng": -51.9217, "img": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900&q=80"},
    {"id": 30, "titulo": "Apartamento no Eurogarden", "tipo": "apartamento", "modalidade": "venda", "zona": "sul", "anunciante": "pago", "preco": 760000, "quartos": 3, "banheiros": 2, "area": 105, "vagas": 2, "bairro": "Eurogarden", "cidade": "Maringá PR", "lat": -23.4487, "lng": -51.9495, "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&q=80"},
]

# SQL que traduz as colunas do banco para o formato que o frontend consome
# (tipo, modalidade, preco, area, vagas, lat, lng, img, ...).
SQL_IMOVEIS = """
SELECT
    i.id,
    i.titulo,
    LOWER(COALESCE(cat.slug, '')) AS tipo,
    i.tipo_negocio AS modalidade,
    LOWER(COALESCE(i.zona, '')) AS zona,
    LOWER(COALESCE(i.anunciante, '')) AS anunciante,
    CASE WHEN i.tipo_negocio = 'aluguel'
         THEN COALESCE(i.preco_aluguel, i.preco)
         ELSE COALESCE(i.preco, i.preco_aluguel) END AS preco,
    COALESCE(i.quartos, 0) AS quartos,
    COALESCE(i.banheiros, 0) AS banheiros,
    COALESCE(i.area_construida, i.area_total, 0) AS area,
    COALESCE(i.vagas_garagem, 0) AS vagas,
    i.bairro,
    TRIM(CONCAT(COALESCE(i.cidade, ''), ' ', COALESCE(i.estado, ''))) AS cidade,
    i.latitude AS lat,
    i.longitude AS lng,
    (SELECT f.url FROM fotos_imovel f
        WHERE f.imovel_id = i.id
        ORDER BY f.capa DESC, f.ordem ASC
        LIMIT 1) AS img
FROM imoveis i
LEFT JOIN categorias cat ON cat.id = i.categoria_id
WHERE i.status = 'ativo'
ORDER BY i.id
"""

_IMG_PADRAO = "https://via.placeholder.com/900x600?text=Sem+foto"


def carregar_imoveis() -> list:
    """Busca os imoveis no banco; em caso de falha usa a lista local."""
    if _DB_OK:
        try:
            linhas = query(SQL_IMOVEIS)
            for r in linhas:
                r["preco"] = float(r["preco"]) if r["preco"] is not None else 0
                r["area"] = float(r["area"]) if r["area"] is not None else 0
                r["lat"] = float(r["lat"]) if r["lat"] is not None else None
                r["lng"] = float(r["lng"]) if r["lng"] is not None else None
                r["img"] = r["img"] or _IMG_PADRAO
            if linhas:
                return linhas
        except Exception as exc:  # noqa: BLE001
            print("[main] Falha ao consultar imoveis no banco, usando dados locais:", exc)
    return IMOVEIS


class LoginInput(BaseModel):
    email: str
    senha: str


@app.post("/api/login")
def login(dados: LoginInput):
    """Autentica pelo banco e devolve os dados do usuario + papel (role)."""
    if not _DB_OK or not _BCRYPT_OK:
        raise HTTPException(status_code=503, detail="Autenticacao indisponivel no momento.")

    email = (dados.email or "").strip().lower()
    linhas = query(
        "SELECT id, nome, email, senha_hash, tipo, ativo FROM usuarios WHERE LOWER(email) = %s LIMIT 1",
        (email,),
    )
    if not linhas:
        raise HTTPException(status_code=401, detail="E-mail ou senha invalidos.")

    user = linhas[0]
    if not user.get("ativo"):
        raise HTTPException(status_code=403, detail="Usuario inativo.")

    senha_ok = bcrypt.checkpw(
        dados.senha.encode("utf-8"), (user["senha_hash"] or "").encode("utf-8")
    )
    if not senha_ok:
        raise HTTPException(status_code=401, detail="E-mail ou senha invalidos.")

    return {
        "id": user["id"],
        "nome": user["nome"],
        "email": user["email"],
        "tipo": user["tipo"],  # admin | corretor | proprietario | cliente
    }


@app.get("/api/health")
def health():
    ok, erro = db_status()
    return {
        "api": "online",
        "banco": "conectado" if ok else "indisponivel",
        "erro": erro,
    }


@app.get("/api/bairros")
def listar_bairros():
    return BAIRROS_MARINGA

@app.get("/api/imoveis")
def listar_imoveis(
    modalidade: Optional[str] = None,
    bairro: Optional[str] = None,
    cidade: Optional[str] = None,
    busca: Optional[str] = None,
    tipo: Optional[str] = None,
    zona: Optional[str] = None,
    anunciante: Optional[str] = None,
    preco_max: Optional[float] = Query(default=None),
    quartos: Optional[int] = Query(default=None),
):
    resultado = carregar_imoveis()
    if modalidade:
        resultado = [i for i in resultado if normalizar(i["modalidade"]) == normalizar(modalidade)]
    if bairro:
        resultado = [i for i in resultado if normalizar(i["bairro"]) == normalizar(bairro)]
    if cidade:
        resultado = [i for i in resultado if normalizar(cidade) in normalizar(i["cidade"])]
    if busca:
        termo = normalizar(busca)
        resultado = [i for i in resultado if termo in normalizar(" ".join([i["titulo"], i["bairro"], i["cidade"]]))]
    if tipo:
        resultado = [i for i in resultado if normalizar(i["tipo"]) == normalizar(tipo)]
    if zona:
        resultado = [i for i in resultado if normalizar(i["zona"]) == normalizar(zona)]
    if anunciante:
        resultado = [i for i in resultado if normalizar(i["anunciante"]) == normalizar(anunciante)]
    if preco_max:
        resultado = [i for i in resultado if i["preco"] <= preco_max]
    if quartos:
        resultado = [i for i in resultado if i["quartos"] >= quartos]
    return resultado
