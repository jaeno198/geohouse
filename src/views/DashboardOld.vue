<template>
  <div class="dashboard-page">
    <section class="landing-hero" aria-labelledby="titulo-busca-imoveis">
      <div class="hero-search-card">
        <div class="intent-tabs" aria-label="Escolha a finalidade">
          <button type="button" class="active">Buscar Imóveis</button>
          <router-link to="/cadastro?tipo=anunciante">Anunciar Imóvel</router-link>
        </div>

        <p class="hero-kicker">Portal imobiliário inteligente</p>
        <h1 id="titulo-busca-imoveis">Encontre um imóvel para chamar de seu</h1>
        <p class="hero-text">
          Busque por cidade, bairro, preço e características. O mapa é atualizado automaticamente conforme os filtros mudam.
        </p>

        <form class="search-form" @submit.prevent="buscarImoveis" aria-label="Formulário de busca de imóveis">
          <div class="operation-tabs" aria-label="Tipo de negociação">
            <button
              v-for="modalidade in modalidades"
              :key="modalidade.value"
              type="button"
              :class="{ active: filtros.modalidade === modalidade.value }"
              @click="alterarModalidade(modalidade.value)"
            >
              {{ modalidade.label }}
            </button>
          </div>

          <div class="primary-fields">
            <label class="big-field">
              <span class="field-icon">⌖</span>
              <span class="field-copy">
                <strong>Cidade</strong>
                <input v-model="filtros.cidade" type="search" placeholder="Busque por cidade" @input="aplicarFiltros" />
              </span>
            </label>

            <label class="big-field">
              <span class="field-icon">⌂</span>
              <span class="field-copy">
                <strong>Bairro</strong>
                <input v-model="filtros.busca" type="search" placeholder="Busque por bairro, rua ou condomínio" @input="aplicarFiltros" />
              </span>
            </label>
          </div>

          <div class="secondary-fields">
            <label class="select-field">
              <span>Tipo</span>
              <select v-model="filtros.tipo" @change="aplicarFiltros">
                <option value="">Todos os tipos</option>
                <option v-for="tipo in tipos" :key="tipo.value" :value="tipo.value">{{ tipo.label }}</option>
              </select>
            </label>

            <label class="select-field">
              <span>Valor até</span>
              <select v-model.number="filtros.precoMax" @change="aplicarFiltros">
                <option :value="null">Escolha o valor</option>
                <option v-for="opcao in opcoesPreco" :key="opcao.value" :value="opcao.value">{{ opcao.label }}</option>
              </select>
            </label>

            <label class="select-field">
              <span>Quartos</span>
              <select v-model.number="filtros.quartos" @change="aplicarFiltros">
                <option :value="0">Nº de quartos</option>
                <option :value="1">1 ou mais</option>
                <option :value="2">2 ou mais</option>
                <option :value="3">3 ou mais</option>
                <option :value="4">4 ou mais</option>
              </select>
            </label>

            <label class="select-field">
              <span>Anunciante</span>
              <select v-model="filtros.anunciante" @change="aplicarFiltros">
                <option value="">Todos</option>
                <option value="pago">Anunciante pago</option>
                <option value="proprietario">Proprietário comum</option>
              </select>
            </label>
          </div>

          <div class="quick-filters" aria-label="Filtros rápidos">
            <button type="button" :class="{ active: filtros.anunciante === 'proprietario' }" @click="alternarAnunciante('proprietario')">
              Direto com proprietário
            </button>
            <button type="button" :class="{ active: filtros.anunciante === 'pago' }" @click="alternarAnunciante('pago')">
              Imóveis em destaque
            </button>
            <button type="button" :class="{ active: filtros.zona === 'centro' }" @click="alternarZona('centro')">
              Região central
            </button>
          </div>

          <div class="form-footer">
            <button type="button" class="clear-button" @click="limparFiltros">Limpar filtros</button>
            <button type="submit" class="search-button">Buscar imóveis</button>
          </div>
        </form>
      </div>

      <aside class="map-showcase" aria-label="Mapa interativo com imóveis filtrados">
        <div class="map-topline">
          <div>
            <strong>{{ imoveisFiltrados.length }} imóveis encontrados</strong>
            <span>{{ resumoBusca }}</span>
          </div>
          <button type="button" @click="centralizarMapa">Centralizar mapa</button>
        </div>

        <div ref="mapEl" class="leaflet-map"></div>

        <article v-if="imovelEmDestaque" class="floating-result-card">
          <img :src="imovelEmDestaque.img" :alt="imovelEmDestaque.titulo" />
          <div>
            <span :class="imovelEmDestaque.anunciante === 'pago' ? 'badge premium' : 'badge owner'">
              {{ imovelEmDestaque.anunciante === 'pago' ? 'Destaque' : 'Proprietário' }}
            </span>
            <strong>{{ formatarMoeda(imovelEmDestaque.preco) }}<small v-if="imovelEmDestaque.modalidade === 'aluguel'">/mês</small></strong>
            <p>{{ imovelEmDestaque.bairro }} · {{ imovelEmDestaque.area }}m² · {{ imovelEmDestaque.quartos }} quartos</p>
          </div>
        </article>

        <div v-else class="floating-result-card empty">
          Nenhum imóvel encontrado para os filtros atuais.
        </div>
      </aside>
    </section>

    <section id="imoveis" class="results-section" aria-labelledby="titulo-resultados">
      <div class="section-header">
        <div>
          <p class="section-kicker">Imóveis disponíveis</p>
          <h2 id="titulo-resultados">Resultados próximos da sua busca</h2>
        </div>
        <div class="section-actions">
          <select v-model="filtros.zona" @change="aplicarFiltros" aria-label="Filtrar por região">
            <option value="">Toda Maringá</option>
            <option v-for="zona in zonas" :key="zona.value" :value="zona.value">{{ zona.label }}</option>
          </select>
          <select v-model="ordenacao" aria-label="Ordenar imóveis">
            <option value="relevancia">Mais relevantes</option>
            <option value="menorPreco">Menor preço</option>
            <option value="maiorPreco">Maior preço</option>
            <option value="maiorArea">Maior área</option>
          </select>
        </div>
      </div>

      <div v-if="chips.length" class="active-chips" aria-label="Filtros ativos">
        <button v-for="chip in chips" :key="chip.key" type="button" @click="removerFiltro(chip.key)">
          {{ chip.label }} ×
        </button>
      </div>

      <div v-if="imoveisOrdenados.length" class="property-grid">
        <article
          v-for="imovel in imoveisOrdenados"
          :key="imovel.id"
          class="property-card"
          :class="{ selected: selectedId === imovel.id }"
          @mouseenter="destacarMarker(imovel.id)"
          @mouseleave="destacarMarker(null)"
          @click="selecionarImovel(imovel)"
        >
          <div class="property-photo">
            <img :src="imovel.img" :alt="imovel.titulo" loading="lazy" />
            <span :class="imovel.anunciante === 'pago' ? 'badge premium' : 'badge owner'">
              {{ imovel.anunciante === 'pago' ? 'Anúncio em destaque' : 'Direto com proprietário' }}
            </span>
          </div>

          <div class="property-content">
            <strong class="property-price">{{ formatarMoeda(imovel.preco) }}<small v-if="imovel.modalidade === 'aluguel'">/mês</small></strong>
            <h3>{{ imovel.titulo }}</h3>
            <p>{{ imovel.bairro }} · {{ imovel.cidade }}</p>
            <div class="property-specs">
              <span>{{ imovel.quartos }} quartos</span>
              <span>{{ imovel.banheiros }} banheiros</span>
              <span>{{ imovel.area }}m²</span>
              <span v-if="imovel.vagas">{{ imovel.vagas }} vagas</span>
            </div>
            <div class="property-actions">
              <button type="button" @click.stop="selecionarImovel(imovel)">Ver no mapa</button>
              <button type="button" class="contact" @click.stop="contatar(imovel)">Tenho interesse</button>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="empty-state">
        <strong>Nenhum imóvel encontrado</strong>
        <p>Tente remover algum filtro ou pesquisar por outra região.</p>
        <button type="button" @click="limparFiltros">Limpar filtros</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const mapEl = ref(null)
const map = ref(null)
const markersLayer = ref(null)
const selectedId = ref(null)
const ordenacao = ref('relevancia')

const MARINGA_CENTER = [-23.4205, -51.9331]

const modalidades = [
  { value: 'aluguel', label: 'Alugar' },
  { value: 'venda', label: 'Comprar' },
]

const tipos = [
  { value: 'apartamento', label: 'Apartamento' },
  { value: 'casa', label: 'Casa' },
  { value: 'terreno', label: 'Terreno' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'rural', label: 'Rural' },
]

const zonas = [
  { value: 'centro', label: 'Centro' },
  { value: 'norte', label: 'Zona Norte' },
  { value: 'sul', label: 'Zona Sul' },
  { value: 'leste', label: 'Zona Leste' },
  { value: 'oeste', label: 'Zona Oeste' },
]

const filtros = reactive({
  modalidade: 'aluguel',
  cidade: 'Maringá',
  busca: '',
  tipo: '',
  zona: '',
  anunciante: '',
  precoMax: null,
  quartos: 0,
})

const imoveis = ref([
  { id: 1, titulo: 'Apartamento mobiliado próximo ao centro', tipo: 'apartamento', modalidade: 'aluguel', zona: 'centro', anunciante: 'pago', preco: 2350, quartos: 2, banheiros: 2, area: 72, vagas: 1, bairro: 'Zona 01', cidade: 'Maringá PR', lat: -23.4214, lng: -51.9341, img: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&q=80' },
  { id: 2, titulo: 'Studio moderno com lazer completo', tipo: 'apartamento', modalidade: 'aluguel', zona: 'centro', anunciante: 'pago', preco: 1850, quartos: 1, banheiros: 1, area: 42, vagas: 1, bairro: 'Centro', cidade: 'Maringá PR', lat: -23.4252, lng: -51.9388, img: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=900&q=80' },
  { id: 3, titulo: 'Casa para locação com churrasqueira', tipo: 'casa', modalidade: 'aluguel', zona: 'leste', anunciante: 'proprietario', preco: 2800, quartos: 3, banheiros: 2, area: 155, vagas: 2, bairro: 'Borba Gato', cidade: 'Maringá PR', lat: -23.4279, lng: -51.9025, img: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=900&q=80' },
  { id: 4, titulo: 'Sala comercial em avenida movimentada', tipo: 'comercial', modalidade: 'aluguel', zona: 'centro', anunciante: 'pago', preco: 3600, quartos: 0, banheiros: 1, area: 86, vagas: 2, bairro: 'Zona 04', cidade: 'Maringá PR', lat: -23.4181, lng: -51.9278, img: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=900&q=80' },
  { id: 5, titulo: 'Apartamento alto padrão na Zona 01', tipo: 'apartamento', modalidade: 'venda', zona: 'centro', anunciante: 'pago', preco: 720000, quartos: 3, banheiros: 2, area: 118, vagas: 2, bairro: 'Zona 01', cidade: 'Maringá PR', lat: -23.4211, lng: -51.9324, img: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&q=80' },
  { id: 6, titulo: 'Casa térrea com piscina', tipo: 'casa', modalidade: 'venda', zona: 'sul', anunciante: 'pago', preco: 890000, quartos: 4, banheiros: 3, area: 260, vagas: 2, bairro: 'Jardim Novo Horizonte', cidade: 'Maringá PR', lat: -23.4446, lng: -51.9255, img: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=900&q=80' },
  { id: 7, titulo: 'Casa geminada pronta para morar', tipo: 'casa', modalidade: 'venda', zona: 'norte', anunciante: 'proprietario', preco: 335000, quartos: 2, banheiros: 1, area: 92, vagas: 1, bairro: 'Jardim Alvorada', cidade: 'Maringá PR', lat: -23.3928, lng: -51.9490, img: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900&q=80' },
  { id: 8, titulo: 'Terreno 300m² em bairro consolidado', tipo: 'terreno', modalidade: 'venda', zona: 'oeste', anunciante: 'proprietario', preco: 185000, quartos: 0, banheiros: 0, area: 300, vagas: 0, bairro: 'Jardim Universo', cidade: 'Maringá PR', lat: -23.4246, lng: -51.9774, img: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=80' },
  { id: 9, titulo: 'Chácara com área verde', tipo: 'rural', modalidade: 'venda', zona: 'sul', anunciante: 'pago', preco: 1180000, quartos: 3, banheiros: 2, area: 5000, vagas: 4, bairro: 'Saída para Paiçandu', cidade: 'Maringá PR', lat: -23.4750, lng: -51.9503, img: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=900&q=80' },
])

const opcoesPreco = computed(() => {
  if (filtros.modalidade === 'aluguel') {
    return [
      { value: 1500, label: 'Até R$ 1.500/mês' },
      { value: 2500, label: 'Até R$ 2.500/mês' },
      { value: 3500, label: 'Até R$ 3.500/mês' },
      { value: 5000, label: 'Até R$ 5.000/mês' },
    ]
  }
  return [
    { value: 250000, label: 'Até R$ 250 mil' },
    { value: 500000, label: 'Até R$ 500 mil' },
    { value: 800000, label: 'Até R$ 800 mil' },
    { value: 1200000, label: 'Até R$ 1,2 milhão' },
  ]
})

const imoveisFiltrados = computed(() => {
  const cidade = filtros.cidade.trim().toLowerCase()
  const termo = filtros.busca.trim().toLowerCase()

  return imoveis.value.filter((imovel) => {
    const texto = [imovel.titulo, imovel.bairro, imovel.cidade].join(' ').toLowerCase()
    const cidadeOk = !cidade || imovel.cidade.toLowerCase().includes(cidade)
    const termoOk = !termo || texto.includes(termo)

    return imovel.modalidade === filtros.modalidade
      && cidadeOk
      && termoOk
      && (!filtros.tipo || imovel.tipo === filtros.tipo)
      && (!filtros.zona || imovel.zona === filtros.zona)
      && (!filtros.anunciante || imovel.anunciante === filtros.anunciante)
      && (!filtros.precoMax || imovel.preco <= filtros.precoMax)
      && (!filtros.quartos || imovel.quartos >= filtros.quartos)
  })
})

const imoveisOrdenados = computed(() => {
  const lista = [...imoveisFiltrados.value]
  if (ordenacao.value === 'menorPreco') return lista.sort((a, b) => a.preco - b.preco)
  if (ordenacao.value === 'maiorPreco') return lista.sort((a, b) => b.preco - a.preco)
  if (ordenacao.value === 'maiorArea') return lista.sort((a, b) => b.area - a.area)
  return lista.sort((a, b) => Number(b.anunciante === 'pago') - Number(a.anunciante === 'pago'))
})

const imovelEmDestaque = computed(() => {
  return imoveisFiltrados.value.find((imovel) => imovel.id === selectedId.value) || imoveisOrdenados.value[0] || null
})

const resumoBusca = computed(() => {
  const acao = filtros.modalidade === 'aluguel' ? 'para alugar' : 'à venda'
  const zona = zonas.find((item) => item.value === filtros.zona)?.label || 'Toda Maringá'
  return `${zona} · imóveis ${acao}`
})

const chips = computed(() => {
  const list = []
  if (filtros.cidade && filtros.cidade.toLowerCase() !== 'maringá') list.push({ key: 'cidade', label: filtros.cidade })
  if (filtros.busca) list.push({ key: 'busca', label: filtros.busca })
  if (filtros.tipo) list.push({ key: 'tipo', label: tipos.find((item) => item.value === filtros.tipo)?.label })
  if (filtros.zona) list.push({ key: 'zona', label: zonas.find((item) => item.value === filtros.zona)?.label })
  if (filtros.anunciante) list.push({ key: 'anunciante', label: filtros.anunciante === 'pago' ? 'Anunciante pago' : 'Proprietário comum' })
  if (filtros.precoMax) list.push({ key: 'precoMax', label: `Até ${formatarMoeda(filtros.precoMax)}` })
  if (filtros.quartos) list.push({ key: 'quartos', label: `${filtros.quartos}+ quartos` })
  return list.filter((chip) => chip.label)
})

function alterarModalidade(value) {
  filtros.modalidade = value
  filtros.precoMax = null
  aplicarFiltros()
}

function alternarAnunciante(value) {
  filtros.anunciante = filtros.anunciante === value ? '' : value
  aplicarFiltros()
}

function alternarZona(value) {
  filtros.zona = filtros.zona === value ? '' : value
  aplicarFiltros()
}

function aplicarFiltros() {
  selectedId.value = null
  renderMarkers()
}

function buscarImoveis() {
  aplicarFiltros()
  document.querySelector('#imoveis')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function removerFiltro(key) {
  if (key === 'precoMax') filtros.precoMax = null
  else if (key === 'quartos') filtros.quartos = 0
  else if (key === 'cidade') filtros.cidade = 'Maringá'
  else filtros[key] = ''
  aplicarFiltros()
}

function limparFiltros() {
  filtros.cidade = 'Maringá'
  filtros.busca = ''
  filtros.tipo = ''
  filtros.zona = ''
  filtros.anunciante = ''
  filtros.precoMax = null
  filtros.quartos = 0
  aplicarFiltros()
}

function formatarMoeda(valor) {
  return valor.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  })
}

function formatarPrecoCurto(valor) {
  if (valor >= 1000000) return `${(valor / 1000000).toFixed(1).replace('.', ',')} mi`
  if (valor >= 1000) return `${Math.round(valor / 1000)} mil`
  return valor.toLocaleString('pt-BR')
}

function markerIcon(imovel, active = false) {
  const premium = imovel.anunciante === 'pago'
  const color = premium ? '#03045e' : '#00b4d8'
  return L.divIcon({
    className: 'geo-marker-wrapper',
    html: `<button class="price-marker ${premium ? 'premium' : 'owner'} ${active ? 'active' : ''}" style="--marker-color:${color}">R$ ${formatarPrecoCurto(imovel.preco)}</button>`,
    iconSize: [96, 40],
    iconAnchor: [48, 40],
    popupAnchor: [0, -36],
  })
}

function popupHtml(imovel) {
  return `
    <article class="map-popup-card">
      <img src="${imovel.img}" alt="${imovel.titulo}" />
      <div>
        <strong>${formatarMoeda(imovel.preco)}${imovel.modalidade === 'aluguel' ? '/mês' : ''}</strong>
        <p>${imovel.titulo}</p>
        <span>${imovel.bairro} · ${imovel.area}m² · ${imovel.quartos} quartos</span>
      </div>
    </article>
  `
}

function renderMarkers() {
  if (!map.value || !markersLayer.value) return

  markersLayer.value.clearLayers()

  imoveisFiltrados.value.forEach((imovel) => {
    const marker = L.marker([imovel.lat, imovel.lng], {
      icon: markerIcon(imovel, selectedId.value === imovel.id),
    })
      .bindPopup(popupHtml(imovel), { closeButton: false, minWidth: 240 })
      .on('click', () => selecionarImovel(imovel, false))

    marker.geoId = imovel.id
    markersLayer.value.addLayer(marker)
  })

  nextTick(() => {
    map.value?.invalidateSize()
    if (imoveisFiltrados.value.length) {
      const bounds = L.latLngBounds(imoveisFiltrados.value.map((imovel) => [imovel.lat, imovel.lng]))
      map.value.fitBounds(bounds.pad(0.25), { maxZoom: 14, animate: true })
    } else {
      map.value?.setView(MARINGA_CENTER, 12)
    }
  })
}

function selecionarImovel(imovel, abrirPopup = true) {
  selectedId.value = imovel.id
  if (!map.value) return

  map.value.flyTo([imovel.lat, imovel.lng], 15, { duration: 0.8 })

  nextTick(() => {
    markersLayer.value?.eachLayer((marker) => {
      const item = imoveis.value.find((imovelItem) => imovelItem.id === marker.geoId)
      const ativo = marker.geoId === imovel.id
      if (item) marker.setIcon(markerIcon(item, ativo))
      if (ativo && abrirPopup) marker.openPopup()
    })
  })
}

function destacarMarker(id) {
  selectedId.value = id
  markersLayer.value?.eachLayer((marker) => {
    const item = imoveis.value.find((imovel) => imovel.id === marker.geoId)
    if (item) marker.setIcon(markerIcon(item, id === marker.geoId))
  })
}

function centralizarMapa() {
  selectedId.value = null
  renderMarkers()
}

function contatar(imovel) {
  const msg = encodeURIComponent(`Olá! Vi o imóvel "${imovel.titulo}" no GeoHouse e tenho interesse.`)
  window.open(`https://wa.me/5544999999999?text=${msg}`, '_blank')
}

onMounted(() => {
  map.value = L.map(mapEl.value, {
    zoomControl: false,
    scrollWheelZoom: true,
  }).setView(MARINGA_CENTER, 12)

  L.control.zoom({ position: 'bottomright' }).addTo(map.value)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 19,
  }).addTo(map.value)

  markersLayer.value = L.layerGroup().addTo(map.value)
  renderMarkers()
  setTimeout(() => map.value?.invalidateSize(), 250)
})

onUnmounted(() => {
  map.value?.remove()
})

watch(
  () => [
    filtros.modalidade,
    filtros.cidade,
    filtros.busca,
    filtros.tipo,
    filtros.zona,
    filtros.anunciante,
    filtros.precoMax,
    filtros.quartos,
  ],
  () => renderMarkers(),
)
</script>

<style scoped>
.dashboard-page {
  --geo-primary: var(--azul-royal, #03045e);
  --geo-blue: var(--azul-corporativo, #0077b6);
  --geo-cyan: var(--ceu-tecnologico, #00b4d8);
  --geo-soft: var(--brisa-suave, #caf0f8);
  --geo-text: #111827;
  --geo-muted: #5f6f89;
  --geo-line: #dbe4ef;
  min-height: 100vh;
  background: linear-gradient(180deg, #f6fbff 0%, #ffffff 58%);
  color: var(--geo-text);
  font-family: Inter, 'DM Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.landing-hero {
  width: min(100%, 1760px);
  min-height: calc(100vh - 142px);
  margin: 0 auto;
  padding: clamp(24px, 4vw, 56px) clamp(18px, 4vw, 68px);
  display: grid;
  grid-template-columns: minmax(390px, 640px) minmax(520px, 1fr);
  gap: clamp(22px, 4vw, 46px);
  align-items: center;
  background:
    radial-gradient(circle at 18% 18%, rgba(202, 240, 248, .78), transparent 35%),
    linear-gradient(135deg, rgba(202, 240, 248, .88), rgba(255, 255, 255, .94));
}

.hero-search-card {
  position: relative;
  z-index: 2;
  background: #ffffff;
  border: 1px solid rgba(219, 228, 239, .9);
  border-radius: 28px;
  padding: clamp(24px, 3.2vw, 42px);
  box-shadow: 0 30px 80px rgba(3, 4, 94, .13);
}

.intent-tabs {
  display: inline-grid;
  grid-template-columns: 1fr 1fr;
  min-width: min(100%, 430px);
  padding: 5px;
  margin-bottom: 30px;
  background: #eeeeF1;
  border-radius: 999px;
}

.intent-tabs button,
.intent-tabs a {
  border: 0;
  min-height: 54px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  color: #111827;
  background: transparent;
  font-weight: 900;
  text-decoration: none;
  cursor: pointer;
}

.intent-tabs .active {
  background: #ffffff;
  box-shadow: 0 2px 10px rgba(17, 24, 39, .08);
}

.hero-kicker,
.section-kicker {
  margin: 0 0 10px;
  color: var(--geo-blue);
  font-size: .78rem;
  font-weight: 900;
  letter-spacing: .09em;
  text-transform: uppercase;
}

.hero-search-card h1 {
  max-width: 540px;
  margin: 0;
  color: #020617;
  font-size: clamp(2.45rem, 4vw, 4.1rem);
  line-height: .98;
  letter-spacing: -.065em;
  font-weight: 950;
}

.hero-text {
  max-width: 550px;
  margin: 22px 0 24px;
  color: #4b5563;
  font-size: clamp(1rem, 1.3vw, 1.18rem);
  line-height: 1.62;
}

.search-form {
  display: grid;
  gap: 16px;
}

.operation-tabs {
  display: flex;
  gap: 28px;
  border-bottom: 1px solid var(--geo-line);
}

.operation-tabs button {
  position: relative;
  border: 0;
  padding: 0 0 14px;
  background: transparent;
  color: #374151;
  font-size: 1.04rem;
  font-weight: 900;
  cursor: pointer;
}

.operation-tabs button.active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 3px;
  background: var(--geo-primary);
  border-radius: 999px;
}

.primary-fields {
  display: grid;
  gap: 12px;
}

.big-field {
  min-height: 94px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
  border: 1.5px solid var(--geo-line);
  border-radius: 14px;
  background: #ffffff;
  transition: border-color .18s ease, box-shadow .18s ease;
}

.big-field:focus-within,
.select-field:focus-within {
  border-color: var(--geo-cyan);
  box-shadow: 0 0 0 4px rgba(0, 180, 216, .12);
}

.field-icon {
  width: 30px;
  color: #111827;
  font-size: 1.55rem;
  line-height: 1;
}

.field-copy {
  flex: 1;
  display: grid;
  gap: 8px;
}

.field-copy strong,
.select-field span {
  color: #111827;
  font-size: .96rem;
  font-weight: 900;
}

.field-copy input,
.select-field select {
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: #374151;
  font-size: 1.02rem;
  font-weight: 600;
}

.field-copy input::placeholder {
  color: #6b7280;
}

.secondary-fields {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.select-field {
  min-height: 82px;
  display: grid;
  gap: 10px;
  padding: 14px 16px;
  border: 1.5px solid var(--geo-line);
  border-radius: 14px;
  background: #ffffff;
}

.quick-filters,
.active-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-filters button,
.active-chips button {
  border: 1px solid #d7e6f4;
  border-radius: 999px;
  padding: 10px 14px;
  background: #f7fbff;
  color: var(--geo-primary);
  font-weight: 850;
  cursor: pointer;
}

.quick-filters button.active,
.active-chips button {
  border-color: rgba(0, 180, 216, .35);
  background: rgba(202, 240, 248, .55);
}

.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 4px;
}

.clear-button {
  border: 0;
  background: transparent;
  color: #4b5563;
  font-weight: 900;
  cursor: pointer;
}

.search-button {
  min-height: 54px;
  min-width: 190px;
  border: 0;
  border-radius: 999px;
  background: #111827;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 950;
  box-shadow: 0 16px 35px rgba(17, 24, 39, .24);
  cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease;
}

.search-button:hover,
.property-card:hover,
.property-card.selected {
  transform: translateY(-2px);
}

.map-showcase {
  position: relative;
  min-height: min(680px, calc(100vh - 205px));
  border-radius: 30px;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid rgba(219, 228, 239, .92);
  box-shadow: 0 30px 90px rgba(3, 4, 94, .18);
}

.map-topline {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  z-index: 450;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, .94);
  box-shadow: 0 12px 35px rgba(15, 23, 42, .12);
  backdrop-filter: blur(16px);
}

.map-topline strong {
  display: block;
  color: #111827;
  font-weight: 950;
}

.map-topline span {
  display: block;
  margin-top: 2px;
  color: var(--geo-muted);
  font-size: .9rem;
  font-weight: 700;
}

.map-topline button {
  border: 0;
  border-radius: 999px;
  padding: 10px 14px;
  background: #f3f6fb;
  color: #111827;
  font-weight: 900;
  cursor: pointer;
}

.leaflet-map {
  width: 100%;
  height: 100%;
  min-height: inherit;
  z-index: 1;
}

.floating-result-card {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: 20px;
  z-index: 450;
  display: grid;
  grid-template-columns: 112px 1fr;
  gap: 14px;
  align-items: center;
  padding: 12px;
  border-radius: 22px;
  background: rgba(255, 255, 255, .96);
  box-shadow: 0 18px 48px rgba(15, 23, 42, .18);
  backdrop-filter: blur(16px);
}

.floating-result-card.empty {
  display: block;
  color: #4b5563;
  font-weight: 900;
}

.floating-result-card img {
  width: 112px;
  height: 86px;
  border-radius: 16px;
  object-fit: cover;
}

.badge {
  display: inline-flex;
  width: fit-content;
  margin-bottom: 7px;
  border-radius: 999px;
  padding: 5px 9px;
  color: #ffffff;
  font-size: .72rem;
  font-weight: 950;
}

.badge.premium {
  background: var(--geo-primary);
}

.badge.owner {
  background: var(--geo-cyan);
}

.floating-result-card strong {
  display: block;
  color: #111827;
  font-size: 1.12rem;
  font-weight: 950;
}

.floating-result-card small,
.property-price small {
  color: #6b7280;
  font-size: .82rem;
  margin-left: 3px;
}

.floating-result-card p {
  margin: 5px 0 0;
  color: #4b5563;
  font-weight: 700;
}

.results-section {
  width: min(100%, 1760px);
  margin: 0 auto;
  padding: 44px clamp(18px, 4vw, 68px) 72px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-end;
  margin-bottom: 18px;
}

.section-header h2 {
  margin: 0;
  color: #111827;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  letter-spacing: -.04em;
  line-height: 1.04;
}

.section-actions {
  display: flex;
  gap: 10px;
}

.section-actions select {
  min-height: 44px;
  border: 1px solid var(--geo-line);
  border-radius: 12px;
  background: #ffffff;
  color: #111827;
  padding: 0 14px;
  font-weight: 850;
}

.active-chips {
  margin-bottom: 20px;
}

.property-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px;
}

.property-card {
  overflow: hidden;
  border: 1px solid rgba(219, 228, 239, .95);
  border-radius: 24px;
  background: #ffffff;
  box-shadow: 0 14px 45px rgba(3, 4, 94, .08);
  cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.property-card:hover,
.property-card.selected {
  border-color: rgba(0, 180, 216, .55);
  box-shadow: 0 22px 55px rgba(0, 119, 182, .14);
}

.property-photo {
  position: relative;
  height: 230px;
  background: #e5edf7;
}

.property-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.property-photo .badge {
  position: absolute;
  left: 14px;
  top: 14px;
}

.property-content {
  padding: 18px;
}

.property-price {
  display: block;
  color: #111827;
  font-size: 1.3rem;
  font-weight: 950;
}

.property-content h3 {
  min-height: 46px;
  margin: 9px 0 7px;
  color: #111827;
  font-size: 1.05rem;
  line-height: 1.28;
}

.property-content p {
  margin: 0 0 14px;
  color: #64748b;
  font-weight: 700;
}

.property-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.property-specs span {
  border-radius: 999px;
  padding: 7px 10px;
  background: #f4f8fc;
  color: #374151;
  font-size: .82rem;
  font-weight: 850;
}

.property-actions {
  display: flex;
  gap: 10px;
  margin-top: 18px;
}

.property-actions button {
  flex: 1;
  min-height: 42px;
  border: 0;
  border-radius: 999px;
  background: #f1f6fb;
  color: #111827;
  font-weight: 950;
  cursor: pointer;
}

.property-actions .contact {
  background: var(--geo-primary);
  color: #ffffff;
}

.empty-state {
  padding: 60px 20px;
  border: 1px dashed #cbd5e1;
  border-radius: 24px;
  text-align: center;
  background: #ffffff;
}

.empty-state strong {
  display: block;
  color: #111827;
  font-size: 1.3rem;
}

.empty-state p {
  color: #64748b;
}

.empty-state button {
  border: 0;
  border-radius: 999px;
  padding: 12px 18px;
  background: #111827;
  color: #ffffff;
  font-weight: 950;
  cursor: pointer;
}

:deep(.price-marker) {
  position: relative;
  border: 0;
  border-radius: 999px;
  padding: 8px 12px;
  background: var(--marker-color);
  color: #ffffff;
  font-size: 12px;
  font-weight: 950;
  white-space: nowrap;
  box-shadow: 0 10px 28px rgba(3, 4, 94, .25);
  cursor: pointer;
  transition: transform .16s ease, box-shadow .16s ease;
}

:deep(.price-marker::after) {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -5px;
  width: 10px;
  height: 10px;
  background: var(--marker-color);
  transform: translateX(-50%) rotate(45deg);
}

:deep(.price-marker.active) {
  transform: scale(1.12);
  box-shadow: 0 14px 32px rgba(3, 4, 94, .35);
}

:deep(.leaflet-control-zoom) {
  border: 0;
  box-shadow: 0 10px 28px rgba(15, 23, 42, .16);
}

:deep(.leaflet-control-zoom a) {
  color: #111827;
  border: 0;
}

:deep(.leaflet-popup-content-wrapper) {
  overflow: hidden;
  border-radius: 18px;
  box-shadow: 0 22px 60px rgba(15, 23, 42, .25);
}

:deep(.leaflet-popup-content) {
  margin: 0;
}

:deep(.map-popup-card) {
  width: 240px;
  background: #ffffff;
}

:deep(.map-popup-card img) {
  width: 100%;
  height: 112px;
  object-fit: cover;
  display: block;
}

:deep(.map-popup-card div) {
  padding: 11px 13px 13px;
}

:deep(.map-popup-card strong) {
  display: block;
  color: #111827;
  font-size: 1rem;
  font-weight: 950;
}

:deep(.map-popup-card p) {
  margin: 5px 0;
  color: #1f2937;
  font-weight: 850;
}

:deep(.map-popup-card span) {
  color: #64748b;
  font-size: .83rem;
  font-weight: 700;
}

@media (max-width: 1280px) {
  .landing-hero {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .map-showcase {
    min-height: 520px;
  }

  .property-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .landing-hero,
  .results-section {
    padding-left: 14px;
    padding-right: 14px;
  }

  .hero-search-card {
    border-radius: 22px;
  }

  .intent-tabs {
    min-width: 100%;
  }

  .secondary-fields {
    grid-template-columns: 1fr;
  }

  .form-footer,
  .section-header,
  .section-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .search-button {
    width: 100%;
  }

  .map-showcase {
    min-height: 460px;
    border-radius: 22px;
  }

  .map-topline {
    align-items: flex-start;
    flex-direction: column;
  }

  .floating-result-card {
    grid-template-columns: 82px 1fr;
  }

  .floating-result-card img {
    width: 82px;
    height: 72px;
  }

  .property-grid {
    grid-template-columns: 1fr;
  }

  .property-photo {
    height: 210px;
  }
}
</style>
