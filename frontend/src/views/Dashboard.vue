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

        <div class="hero-metrics" aria-label="Resumo da plataforma">
          <span><strong>{{ totalImoveis }}</strong> imóveis ativos</span>
          <span><strong>5</strong> regiões</span>
          <span><strong>Mapa</strong> ao vivo</span>
        </div>

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
                <select v-model="filtros.bairro" @change="aplicarFiltros">
                  <option value="">Todos os bairros de Maringá</option>
                  <option v-for="bairro in bairros" :key="bairro" :value="bairro">{{ bairro }}</option>
                </select>
              </span>
            </label>
          </div>

          <div class="compact-tools">
            <button type="button" class="advanced-toggle" @click="mostrarFiltrosAvancados = !mostrarFiltrosAvancados">
              <span>{{ mostrarFiltrosAvancados ? 'Ocultar filtros' : 'Mais filtros' }}</span>
              <strong>{{ chips.length ? chips.length + ' ativo(s)' : 'Tipo, valor, quartos' }}</strong>
            </button>

            <div v-if="chips.length" class="hero-active-chips" aria-label="Filtros ativos na busca">
              <button v-for="chip in chips" :key="chip.key" type="button" @click="removerFiltro(chip.key)">
                {{ chip.label }} ×
              </button>
            </div>
          </div>

          <Transition name="filters-slide">
            <div v-if="mostrarFiltrosAvancados" class="advanced-panel">
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
            </div>
          </Transition>

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
          <div class="map-topline-actions">
            <button type="button" @click="centralizarMapa">Centralizar mapa</button>
            <button type="button" class="btn-anunciar-mapa" @click="abrirModalAnuncio">+ Anunciar imóvel</button>
          </div>
        </div>

        <div class="map-wrapper">
          <div ref="mapEl" class="leaflet-map"></div>
          <Transition name="pin-fade">
            <div v-if="pinandoLocalizacao" class="pin-overlay">
              <span>📍 Clique no mapa para definir a localização</span>
              <button @click="cancelarPinagem">Cancelar</button>
            </div>
          </Transition>
        </div>

        <article v-if="imovelEmDestaque && !cardDestaqueFechado" class="floating-result-card">
          <img :src="imovelEmDestaque.img" :alt="imovelEmDestaque.titulo" />
          <div>
            <span :class="imovelEmDestaque.anunciante === 'pago' ? 'badge premium' : 'badge owner'">
              {{ imovelEmDestaque.anunciante === 'pago' ? 'Destaque' : 'Proprietário' }}
            </span>
            <strong>{{ formatarMoeda(imovelEmDestaque.preco) }}<small v-if="imovelEmDestaque.modalidade === 'aluguel'">/mês</small></strong>
            <p>{{ imovelEmDestaque.bairro }} · {{ imovelEmDestaque.area }}m² · {{ imovelEmDestaque.quartos }} quartos</p>
          </div>
          <button
            type="button"
            class="floating-card-close"
            aria-label="Fechar destaque do imóvel"
            @click="fecharCardDestaque"
          >
            ×
          </button>
        </article>

        <div v-else-if="!imoveisFiltrados.length" class="floating-result-card empty">
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

      <div v-if="carregandoApi" class="property-grid">
        <div v-for="n in 6" :key="`sk-${n}`" class="property-card skeleton-card" aria-hidden="true">
          <div class="skeleton-photo"></div>
          <div class="skeleton-body">
            <div class="skel-line w-50 h-22"></div>
            <div class="skel-line w-85 h-16"></div>
            <div class="skel-line w-45"></div>
            <div class="skel-specs">
              <div class="skel-chip"></div>
              <div class="skel-chip"></div>
              <div class="skel-chip"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="imoveisOrdenados.length" class="property-grid">
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
            <div class="property-photo-inner">
              <img :src="imovel.img" :alt="imovel.titulo" loading="lazy" />
            </div>
            <div class="property-photo-badges">
              <span :class="imovel.anunciante === 'pago' ? 'badge premium' : 'badge owner'">
                {{ imovel.anunciante === 'pago' ? '⭐ Destaque' : '🔑 Proprietário' }}
              </span>
              <span class="badge type-badge">{{ tipos.find(t => t.value === imovel.tipo)?.label || imovel.tipo }}</span>
            </div>
            <button
              type="button"
              class="fav-btn"
              :class="{ active: favoritos.has(imovel.id) }"
              :aria-label="favoritos.has(imovel.id) ? 'Remover dos favoritos' : 'Salvar nos favoritos'"
              @click.stop="toggleFavorito(imovel)"
            >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" :fill="favoritos.has(imovel.id) ? '#ef4444' : 'none'" :stroke="favoritos.has(imovel.id) ? '#ef4444' : 'currentColor'" stroke-width="2"/>
              </svg>
            </button>
          </div>

          <div class="property-content">
            <strong class="property-price">{{ formatarMoeda(imovel.preco) }}<small v-if="imovel.modalidade === 'aluguel'">/mês</small></strong>
            <h3>{{ imovel.titulo }}</h3>
            <p class="property-location">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" width="14" height="14"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="#6b7280"/></svg>
              {{ imovel.bairro }}, {{ imovel.cidade }}
            </p>
            <div class="property-specs">
              <span v-if="imovel.quartos > 0">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-8v7H3V5H1v15h2v-3h18v3h2v-9c0-2.21-1.79-4-4-4z" fill="currentColor"/></svg>
                {{ imovel.quartos }} {{ imovel.quartos === 1 ? 'quarto' : 'quartos' }}
              </span>
              <span>
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 6c0-.55.45-1 1-1s1 .45 1 1-.45 1-1 1-1-.45-1-1zm13 9H4V8h16v7zm0-9H9.17C8.73 4.83 7.97 4 7 4c-1.15 0-2.1.83-2.23 1.92C3.23 6.22 2 7.53 2 9v8c0 .55.45 1 1 1h1v1c0 .55.45 1 1 1s1-.45 1-1v-1h12v1c0 .55.45 1 1 1s1-.45 1-1v-1h1c.55 0 1-.45 1-1V9c0-1.65-1.35-3-3-3z" fill="currentColor"/></svg>
                {{ imovel.banheiros }} ban.
              </span>
              <span>
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M21 3L3 10.53v.98l6.84 2.65L12.48 21h.98L21 3z" fill="currentColor"/></svg>
                {{ imovel.area }}m²
              </span>
              <span v-if="imovel.vagas">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="currentColor"/></svg>
                {{ imovel.vagas }} {{ imovel.vagas === 1 ? 'vaga' : 'vagas' }}
              </span>
            </div>
            <div class="property-actions">
              <button type="button" class="map-btn" @click.stop="selecionarImovel(imovel)">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" width="15" height="15"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z" fill="currentColor"/></svg>
                Ver no mapa
              </button>
              <button type="button" class="contact" @click.stop="contatar(imovel)">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" width="15" height="15"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" fill="currentColor"/></svg>
                Tenho interesse
              </button>
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
  <!-- Modal de anúncio com pinagem de localização -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modalAnuncio" class="anuncio-overlay" @click.self="fecharModalAnuncio">
        <div class="anuncio-modal">
          <div class="anuncio-header">
            <div>
              <h2>Anunciar imóvel</h2>
              <p>Preencha os dados e marque a localização no mapa</p>
            </div>
            <button class="anuncio-close" @click="fecharModalAnuncio">×</button>
          </div>

          <div class="anuncio-fields">
            <!-- Modalidade -->
            <div class="anuncio-tabs">
              <button :class="{ active: novoImovelForm.modalidade === 'aluguel' }" @click="novoImovelForm.modalidade = 'aluguel'">Aluguel</button>
              <button :class="{ active: novoImovelForm.modalidade === 'venda' }" @click="novoImovelForm.modalidade = 'venda'">Venda</button>
            </div>

            <!-- Título -->
            <label class="anuncio-field full">
              <span>Título do anúncio *</span>
              <input v-model="novoImovelForm.titulo" type="text" placeholder="Ex: Apartamento 3 quartos com suíte" />
            </label>

            <!-- Tipo + Preço -->
            <label class="anuncio-field">
              <span>Tipo</span>
              <select v-model="novoImovelForm.tipo">
                <option value="apartamento">Apartamento</option>
                <option value="casa">Casa</option>
                <option value="terreno">Terreno</option>
                <option value="comercial">Comercial</option>
                <option value="rural">Rural</option>
              </select>
            </label>

            <label class="anuncio-field">
              <span>Preço (R$) *</span>
              <input v-model.number="novoImovelForm.preco" type="number" min="0" placeholder="Ex: 2500" />
            </label>

            <!-- Quartos + Banheiros + Área + Vagas -->
            <label class="anuncio-field">
              <span>Quartos</span>
              <select v-model.number="novoImovelForm.quartos">
                <option v-for="n in [0,1,2,3,4,5]" :key="n" :value="n">{{ n === 0 ? 'Sem quarto' : n }}</option>
              </select>
            </label>

            <label class="anuncio-field">
              <span>Banheiros</span>
              <select v-model.number="novoImovelForm.banheiros">
                <option v-for="n in [1,2,3,4,5]" :key="n" :value="n">{{ n }}</option>
              </select>
            </label>

            <label class="anuncio-field">
              <span>Área (m²)</span>
              <input v-model.number="novoImovelForm.area" type="number" min="0" placeholder="Ex: 85" />
            </label>

            <label class="anuncio-field">
              <span>Vagas</span>
              <select v-model.number="novoImovelForm.vagas">
                <option v-for="n in [0,1,2,3,4]" :key="n" :value="n">{{ n }}</option>
              </select>
            </label>

            <!-- Bairro -->
            <label class="anuncio-field full">
              <span>Bairro *</span>
              <select v-model="novoImovelForm.bairro">
                <option value="">Selecione o bairro</option>
                <option v-for="b in bairros" :key="b" :value="b">{{ b }}</option>
              </select>
            </label>

            <!-- Localização no mapa -->
            <div class="anuncio-field full">
              <span class="anuncio-field-label">Localização no mapa</span>
              <div class="localizacao-box">
                <div v-if="novoImovelForm.lat && novoImovelForm.lng" class="localizacao-ok">
                  📍 {{ novoImovelForm.lat.toFixed(5) }}, {{ novoImovelForm.lng.toFixed(5) }}
                  <button class="btn-repin" @click="ativarPinagem">Alterar</button>
                </div>
                <div v-else class="localizacao-vazia">
                  <span v-if="novoImovelForm.bairro">Bairro selecionado: o mapa voou para lá. Clique em "Marcar no mapa" para definir a posição exata.</span>
                  <span v-else>Selecione um bairro primeiro, depois marque a localização.</span>
                  <button class="btn-pin" :disabled="!novoImovelForm.bairro" @click="ativarPinagem">📍 Marcar no mapa</button>
                </div>
              </div>
            </div>
          </div>

          <div class="anuncio-footer">
            <button class="btn-cancel" @click="fecharModalAnuncio">Cancelar</button>
            <button
              class="btn-publicar"
              :disabled="!novoImovelForm.titulo || !novoImovelForm.preco || !novoImovelForm.bairro"
              @click="confirmarNovoImovel"
            >
              Publicar anúncio
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { BAIRROS_MARINGA } from '@/data/bairrosMaringa'
import { useKmlStore, getKmlCentroid } from '@/composables/useKmlStore'

const mapEl = ref(null)
const map = ref(null)
const markersLayer = ref(null)
const kmlLayerGroup = ref(null)
const pinMarker = ref(null)
const mapResizeObserver = ref(null)
const selectedId = ref(null)

const { kmlLayers } = useKmlStore()

// ─── Imóveis locais (criados via modal, salvos em localStorage) ───────────────
const LOCAL_KEY = 'geohouse_imoveis_locais'
const imoveisLocais = ref((() => { try { return JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]') } catch { return [] } })())

function persistirLocais() {
  localStorage.setItem(LOCAL_KEY, JSON.stringify(imoveisLocais.value))
}

// ─── Modal de anúncio ────────────────────────────────────────────────────────
const modalAnuncio = ref(false)
const pinandoLocalizacao = ref(false)

const novoImovelForm = reactive({
  titulo: '', tipo: 'apartamento', modalidade: 'aluguel',
  preco: null, quartos: 1, banheiros: 1, area: null, vagas: 0,
  bairro: '', cidade: 'Maringá', lat: null, lng: null,
})

function resetForm() {
  Object.assign(novoImovelForm, {
    titulo: '', tipo: 'apartamento', modalidade: 'aluguel',
    preco: null, quartos: 1, banheiros: 1, area: null, vagas: 0,
    bairro: '', cidade: 'Maringá', lat: null, lng: null,
  })
  if (pinMarker.value) { pinMarker.value.remove(); pinMarker.value = null }
}

function abrirModalAnuncio() {
  resetForm()
  if (filtros.bairro) novoImovelForm.bairro = filtros.bairro
  modalAnuncio.value = true
}

function fecharModalAnuncio() {
  modalAnuncio.value = false
  pinandoLocalizacao.value = false
  if (pinMarker.value) { pinMarker.value.remove(); pinMarker.value = null }
}

function ativarPinagem() {
  modalAnuncio.value = false
  pinandoLocalizacao.value = true
}

function cancelarPinagem() {
  pinandoLocalizacao.value = false
  modalAnuncio.value = true
}

function confirmarNovoImovel() {
  if (!novoImovelForm.titulo || !novoImovelForm.preco || !novoImovelForm.bairro) return

  // Posição: coordenadas pinadas ou centroide do KML
  let { lat, lng } = novoImovelForm
  if (!lat || !lng) {
    const c = getKmlCentroid(novoImovelForm.bairro, kmlLayers.value)
    if (c) {
      lat = c.lat + (Math.random() - 0.5) * 0.002
      lng = c.lng + (Math.random() - 0.5) * 0.002
    }
  }

  const imovel = {
    id: `local_${Date.now()}`,
    titulo: novoImovelForm.titulo,
    tipo: novoImovelForm.tipo,
    modalidade: novoImovelForm.modalidade,
    zona: '',
    anunciante: 'proprietario',
    preco: Number(novoImovelForm.preco),
    quartos: Number(novoImovelForm.quartos),
    banheiros: Number(novoImovelForm.banheiros),
    area: Number(novoImovelForm.area) || 0,
    vagas: Number(novoImovelForm.vagas),
    bairro: novoImovelForm.bairro,
    cidade: novoImovelForm.cidade,
    lat, lng,
    pinned: !!(novoImovelForm.lat && novoImovelForm.lng), // localização definida manualmente no mapa
    img: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=70',
  }

  imoveisLocais.value = [...imoveisLocais.value, imovel]
  persistirLocais()
  fecharModalAnuncio()
  renderMarkers()
}
const ordenacao = ref('relevancia')
const mostrarFiltrosAvancados = ref(false)
const favoritos = ref(new Set())
const cardDestaqueFechado = ref(false)

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

const API_URL = import.meta.env.VITE_API_URL || ''

const filtros = reactive({
  modalidade: 'aluguel',
  cidade: 'Maringá',
  busca: '',
  bairro: '',
  tipo: '',
  zona: '',
  anunciante: '',
  precoMax: null,
  quartos: 0,
})

const imoveis = ref([])
const bairros = ref([...BAIRROS_MARINGA])
const totalImoveis = ref(0)
const carregandoApi = ref(false)

async function carregarBairros() {
  try {
    const resposta = await fetch(`${API_URL}/api/bairros`)

    if (!resposta.ok) {
      throw new Error('Não foi possível carregar os bairros pela API.')
    }

    const dados = await resposta.json()

    if (Array.isArray(dados) && dados.length > 0) {
      bairros.value = dados
    } else {
      bairros.value = [...BAIRROS_MARINGA]
    }
  } catch (erro) {
    console.warn('Usando lista local de bairros de Maringá:', erro)
    bairros.value = [...BAIRROS_MARINGA]
  }
}

async function carregarImoveis() {
  carregandoApi.value = true

  const params = new URLSearchParams()
  params.set('modalidade', filtros.modalidade)
  if (filtros.cidade) params.set('cidade', filtros.cidade)
  if (filtros.busca) params.set('busca', filtros.busca)
  if (filtros.bairro) params.set('bairro', filtros.bairro)
  if (filtros.tipo) params.set('tipo', filtros.tipo)
  if (filtros.zona) params.set('zona', filtros.zona)
  if (filtros.anunciante) params.set('anunciante', filtros.anunciante)
  if (filtros.precoMax) params.set('preco_max', filtros.precoMax)
  if (filtros.quartos) params.set('quartos', filtros.quartos)

  try {
    const resposta = await fetch(`${API_URL}/api/imoveis?${params.toString()}`)

    if (!resposta.ok) {
      throw new Error('Não foi possível carregar os imóveis pela API.')
    }

    imoveis.value = await resposta.json()
    totalImoveis.value = imoveis.value.length
    renderMarkers()
  } catch (erro) {
    console.error('Erro ao carregar imóveis:', erro)
    imoveis.value = []
    totalImoveis.value = 0
    renderMarkers()
  } finally {
    carregandoApi.value = false
  }
}

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

const todosImoveis = computed(() => [...imoveis.value, ...imoveisLocais.value])

const imoveisFiltrados = computed(() => {
  const cidade = filtros.cidade.trim().toLowerCase()
  const termo = filtros.busca.trim().toLowerCase()
  const bairroSelecionado = filtros.bairro.trim().toLowerCase()

  return todosImoveis.value.filter((imovel) => {
    const texto = [imovel.titulo, imovel.bairro, imovel.cidade].join(' ').toLowerCase()
    const cidadeOk = !cidade || imovel.cidade.toLowerCase().includes(cidade)
    const termoOk = !termo || texto.includes(termo)
    const bairroOk = !bairroSelecionado || imovel.bairro.toLowerCase() === bairroSelecionado

    return imovel.modalidade === filtros.modalidade
      && cidadeOk
      && termoOk
      && bairroOk
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
  if (filtros.bairro) list.push({ key: 'bairro', label: filtros.bairro })
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
  cardDestaqueFechado.value = false
  carregarImoveis()
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
  filtros.bairro = ''
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

// Scatter determinístico: mesmo ID → mesmo offset, não embaralha a cada render
function kmlScatter(id) {
  const n = parseInt(String(id).replace(/\D/g, '') || '1', 10)
  const angle = (n * 137.508 * Math.PI) / 180 // ângulo de ouro
  const radius = 0.0004 + (n % 6) * 0.00025
  return { dlat: radius * Math.cos(angle), dlng: radius * Math.sin(angle) }
}

function resolverPosicao(imovel) {
  // 1. Localização pinada pelo usuário no mapa → sempre exata
  if (imovel.pinned && imovel.lat && imovel.lng) {
    return { lat: imovel.lat, lng: imovel.lng }
  }

  // 2. KML carregado para o bairro → centroide + scatter determinístico
  if (imovel.bairro) {
    const c = getKmlCentroid(imovel.bairro, kmlLayers.value)
    if (c) {
      const { dlat, dlng } = kmlScatter(imovel.id)
      return { lat: c.lat + dlat, lng: c.lng + dlng }
    }
  }

  // 3. Fallback: coordenadas do backend/locais
  if (imovel.lat && imovel.lng) return { lat: imovel.lat, lng: imovel.lng }

  return null
}

function renderMarkers() {
  if (!map.value || !markersLayer.value) return

  markersLayer.value.clearLayers()
  const posicoes = []

  imoveisFiltrados.value.forEach((imovel) => {
    const pos = resolverPosicao(imovel)
    if (!pos) return

    const marker = L.marker([pos.lat, pos.lng], {
      icon: markerIcon(imovel, selectedId.value === imovel.id),
    })
      .bindPopup(popupHtml(imovel), { closeButton: false, minWidth: 240 })
      .on('click', () => selecionarImovel(imovel, false))

    marker.geoId = imovel.id
    markersLayer.value.addLayer(marker)
    posicoes.push([pos.lat, pos.lng])
  })

  nextTick(() => {
    map.value?.invalidateSize()

    const kmlAtivo = filtros.bairro &&
      kmlLayers.value.some((l) => l.bairro.toLowerCase() === filtros.bairro.toLowerCase())
    if (kmlAtivo) return

    if (posicoes.length) {
      map.value.fitBounds(L.latLngBounds(posicoes).pad(0.25), { maxZoom: 14, animate: true })
    } else {
      map.value?.setView(MARINGA_CENTER, 12)
    }
  })
}

function selecionarImovel(imovel, abrirPopup = true) {
  selectedId.value = imovel.id
  cardDestaqueFechado.value = false
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
  cardDestaqueFechado.value = false
  renderMarkers()
}

function selecionarBairroKml(bairro) {
  // Toggle: clicar no bairro já ativo limpa o filtro
  filtros.bairro = filtros.bairro.toLowerCase() === bairro.toLowerCase() ? '' : bairro
  selectedId.value = null
  cardDestaqueFechado.value = false
  carregarImoveis()
}

function renderKmlLayers() {
  if (!map.value || !kmlLayerGroup.value) return
  kmlLayerGroup.value.clearLayers()

  const bairroAtivo = filtros.bairro.trim().toLowerCase()

  kmlLayers.value.forEach((layer) => {
    const isAtivo = bairroAtivo && layer.bairro.toLowerCase() === bairroAtivo

    const geoLayer = L.geoJSON(layer.geoJSON, {
      style: () => ({
        color: isAtivo ? '#0077b6' : '#00b4d8',
        weight: isAtivo ? 3 : 1.5,
        opacity: isAtivo ? 1 : 0.55,
        fillOpacity: isAtivo ? 0.18 : 0,
        fillColor: '#00b4d8',
      }),
      onEachFeature(_, featureLayer) {
        featureLayer.on({
          click() { selecionarBairroKml(layer.bairro) },
          mouseover(e) {
            if (!isAtivo) e.target.setStyle({ fillOpacity: 0.1, opacity: 0.9 })
          },
          mouseout(e) {
            if (!isAtivo) e.target.setStyle({ fillOpacity: 0, opacity: 0.55 })
          },
        })
      },
    })

    geoLayer.bindTooltip(layer.bairro, {
      permanent: false,
      direction: 'center',
      className: 'kml-tooltip',
    })

    kmlLayerGroup.value.addLayer(geoLayer)

    if (isAtivo) {
      nextTick(() => {
        try { map.value?.fitBounds(geoLayer.getBounds().pad(0.12), { maxZoom: 15, animate: true }) }
        catch (_) { /* polígono inválido */ }
      })
    }
  })
}

function fecharCardDestaque() {
  cardDestaqueFechado.value = true
  selectedId.value = null
  markersLayer.value?.eachLayer((marker) => {
    const item = imoveis.value.find((imovelItem) => imovelItem.id === marker.geoId)
    if (item) marker.setIcon(markerIcon(item, false))
  })
}

function toggleFavorito(imovel) {
  const novos = new Set(favoritos.value)
  if (novos.has(imovel.id)) novos.delete(imovel.id)
  else novos.add(imovel.id)
  favoritos.value = novos
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
  L.tileLayer(`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`, {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: 'abc',
    maxZoom: 19,
  }).addTo(map.value)

  markersLayer.value = L.layerGroup().addTo(map.value)
  kmlLayerGroup.value = L.layerGroup().addTo(map.value)
  carregarBairros()
  carregarImoveis()
  renderKmlLayers()

  // Click no mapa durante modo de pinagem de localização
  map.value.on('click', (e) => {
    if (!pinandoLocalizacao.value) return
    novoImovelForm.lat = e.latlng.lat
    novoImovelForm.lng = e.latlng.lng
    if (pinMarker.value) pinMarker.value.remove()
    pinMarker.value = L.marker([e.latlng.lat, e.latlng.lng], {
      icon: L.divIcon({
        className: '',
        html: '<div class="pin-icon">📍</div>',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
      }),
    }).addTo(map.value)
    pinandoLocalizacao.value = false
    modalAnuncio.value = true
  })

  const atualizarTamanhoMapa = () => map.value?.invalidateSize()
  setTimeout(atualizarTamanhoMapa, 250)
  setTimeout(atualizarTamanhoMapa, 800)

  mapResizeObserver.value = new ResizeObserver(atualizarTamanhoMapa)
  if (mapEl.value) mapResizeObserver.value.observe(mapEl.value)
})

onUnmounted(() => {
  mapResizeObserver.value?.disconnect()
  map.value?.remove()
})

watch(
  () => [
    filtros.modalidade,
    filtros.cidade,
    filtros.busca,
    filtros.bairro,
    filtros.tipo,
    filtros.zona,
    filtros.anunciante,
    filtros.precoMax,
    filtros.quartos,
  ],
  () => carregarImoveis(),
)

watch(() => filtros.bairro, () => renderKmlLayers())
watch(kmlLayers, () => renderKmlLayers(), { deep: true })

// Ao selecionar bairro no formulário de anúncio: voa para o KML e preenche coords padrão
watch(() => novoImovelForm.bairro, (bairro) => {
  if (!bairro || !map.value) return
  const c = getKmlCentroid(bairro, kmlLayers.value)
  if (c) {
    novoImovelForm.lat = null  // reseta para forçar nova pinagem se quiser
    novoImovelForm.lng = null
    if (pinMarker.value) { pinMarker.value.remove(); pinMarker.value = null }
    map.value.flyTo([c.lat, c.lng], 15, { duration: 0.7 })
  }
})
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
  --geo-surface: rgba(255, 255, 255, .94);
  --geo-radius: 18px;
  min-height: 100vh;
  background:
    linear-gradient(180deg, rgba(202, 240, 248, .7) 0%, rgba(255, 255, 255, .96) 42%, #ffffff 100%);
  color: var(--geo-text);
  font-family: Inter, 'DM Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.landing-hero {
  width: min(100%, var(--layout-max, 1400px));
  margin: 0 auto;
  padding: clamp(20px, 3vw, 36px) var(--layout-gutter, clamp(16px, 3vw, 40px));
  display: grid;
  grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
  gap: clamp(20px, 2.5vw, 32px);
  align-items: stretch;
  background:
    linear-gradient(135deg, rgba(202, 240, 248, .9), rgba(255, 255, 255, .96));
}

.hero-search-card {
  position: sticky;
  top: 86px;
  z-index: 2;
  align-self: start;
  width: 100%;
  background: var(--geo-surface);
  border: 1px solid rgba(219, 228, 239, .9);
  border-radius: var(--geo-radius);
  padding: clamp(16px, 2vw, 26px);
  box-shadow: 0 20px 54px rgba(3, 4, 94, .12);
  backdrop-filter: blur(18px);
}

.intent-tabs {
  display: inline-grid;
  grid-template-columns: 1fr 1fr;
  width: min(100%, 360px);
  padding: 4px;
  margin-bottom: 20px;
  background: #eeeeF1;
  border-radius: 999px;
}

.intent-tabs button,
.intent-tabs a {
  border: 0;
  min-height: 42px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  color: #111827;
  background: transparent;
  font-size: .88rem;
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
  max-width: 440px;
  margin: 0;
  color: #020617;
  font-size: clamp(2rem, 3vw, 2.85rem);
  line-height: 1.04;
  letter-spacing: 0;
  font-weight: 950;
}

.hero-text {
  max-width: 470px;
  margin: 12px 0 14px;
  color: #4b5563;
  font-size: clamp(.92rem, 1.1vw, 1rem);
  line-height: 1.52;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 0 0 16px;
}

.hero-metrics span {
  min-height: 58px;
  display: grid;
  align-content: center;
  gap: 2px;
  border: 1px solid rgba(0, 180, 216, .22);
  border-radius: 12px;
  padding: 8px 10px;
  background: rgba(202, 240, 248, .32);
  color: var(--geo-muted);
  font-size: .78rem;
  font-weight: 800;
}

.hero-metrics strong {
  color: var(--geo-primary);
  font-size: 1rem;
  font-weight: 950;
}

.search-form {
  display: grid;
  gap: 12px;
}

.operation-tabs {
  display: flex;
  gap: 22px;
  border-bottom: 1px solid var(--geo-line);
}

.operation-tabs button {
  position: relative;
  border: 0;
  padding: 0 0 10px;
  background: transparent;
  color: #374151;
  font-size: .96rem;
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
  min-height: 66px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1.5px solid var(--geo-line);
  border-radius: 12px;
  background: #ffffff;
  transition: border-color .18s ease, box-shadow .18s ease;
}

.big-field:focus-within,
.select-field:focus-within {
  border-color: var(--geo-cyan);
  box-shadow: 0 0 0 4px rgba(0, 180, 216, .12);
}

.field-icon {
  width: 24px;
  color: #111827;
  font-size: 1.22rem;
  line-height: 1;
}

.field-copy {
  flex: 1;
  display: grid;
  gap: 5px;
}

.field-copy strong,
.select-field span {
  color: #111827;
  font-size: .82rem;
  font-weight: 900;
}

.field-copy input,
.field-copy select,
.select-field select {
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: #374151;
  font-size: .94rem;
  font-weight: 600;
}

.field-copy input::placeholder {
  color: #6b7280;
}

.advanced-panel {
  display: grid;
  gap: 12px;
}

.secondary-fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.select-field {
  min-height: 64px;
  display: grid;
  gap: 6px;
  padding: 11px 12px;
  border: 1.5px solid var(--geo-line);
  border-radius: 12px;
  background: #ffffff;
}

.compact-tools {
  display: grid;
  gap: 10px;
}

.advanced-toggle {
  width: 100%;
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid #d7e6f4;
  border-radius: 12px;
  padding: 0 14px;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
  color: var(--geo-primary);
  font-weight: 950;
  cursor: pointer;
}

.advanced-toggle strong {
  color: #64748b;
  font-size: .82rem;
  font-weight: 850;
}

.hero-active-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-active-chips button {
  border: 1px solid rgba(0, 180, 216, .35);
  border-radius: 999px;
  padding: 7px 10px;
  background: rgba(202, 240, 248, .5);
  color: var(--geo-primary);
  font-size: .8rem;
  font-weight: 850;
  cursor: pointer;
}

.filters-slide-enter-active,
.filters-slide-leave-active {
  overflow: hidden;
  transition: max-height .22s ease, opacity .18s ease, transform .18s ease;
}

.filters-slide-enter-from,
.filters-slide-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-4px);
}

.filters-slide-enter-to,
.filters-slide-leave-from {
  max-height: 360px;
  opacity: 1;
  transform: translateY(0);
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
  padding: 8px 11px;
  background: #f7fbff;
  color: var(--geo-primary);
  font-size: .84rem;
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
  gap: 12px;
  margin-top: 2px;
}

.clear-button {
  border: 0;
  background: transparent;
  color: #4b5563;
  font-weight: 900;
  cursor: pointer;
}

.search-button {
  min-height: 48px;
  min-width: 168px;
  border: 0;
  border-radius: 999px;
  background: #111827;
  color: #ffffff;
  font-size: .94rem;
  font-weight: 950;
  box-shadow: 0 14px 30px rgba(17, 24, 39, .22);
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
  display: flex;
  flex-direction: column;
  min-height: clamp(480px, 68vh, 680px);
  height: 100%;
  border-radius: var(--geo-radius);
  overflow: hidden;
  background: #ffffff;
  border: 1px solid rgba(219, 228, 239, .92);
  box-shadow: 0 24px 72px rgba(3, 4, 94, .16);
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
  border-radius: 14px;
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

.map-topline-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.map-topline button {
  border: 0;
  border-radius: 999px;
  padding: 10px 14px;
  background: #f3f6fb;
  color: #111827;
  font-weight: 900;
  cursor: pointer;
  white-space: nowrap;
}

.btn-anunciar-mapa {
  background: #03045e !important;
  color: #ffffff !important;
  transition: background .15s;
}

.btn-anunciar-mapa:hover { background: #0077b6 !important; }

/* map-wrapper para o overlay de pinagem */
.map-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.leaflet-map {
  flex: 1;
  width: 100%;
  min-height: 400px;
  min-width: 0;
  z-index: 1;
}

/* Pin overlay */
.pin-overlay {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 800;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #03045e;
  color: #fff;
  padding: 12px 20px;
  border-radius: 999px;
  font-size: .88rem;
  font-weight: 700;
  box-shadow: 0 8px 28px rgba(3, 4, 94, .35);
  white-space: nowrap;
  pointer-events: auto;
}

.pin-overlay button {
  background: rgba(255,255,255,.18) !important;
  color: #fff !important;
  border: 1px solid rgba(255,255,255,.3) !important;
  padding: 6px 14px !important;
  border-radius: 999px !important;
  font-size: .82rem !important;
}

.pin-fade-enter-active, .pin-fade-leave-active { transition: opacity .2s, transform .2s; }
.pin-fade-enter-from, .pin-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(10px); }

/* Modal de anúncio */
.anuncio-overlay {
  position: fixed;
  inset: 0;
  background: rgba(3, 4, 94, .55);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.anuncio-modal {
  background: #fff;
  border-radius: 20px;
  width: min(100%, 580px);
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 32px 80px rgba(3, 4, 94, .25);
  display: flex;
  flex-direction: column;
}

.anuncio-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 0;
}

.anuncio-header h2 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #03045e;
  margin: 0 0 4px;
}

.anuncio-header p {
  font-size: .8rem;
  color: #5f6f89;
  margin: 0;
}

.anuncio-close {
  background: #f1f5f9;
  border: 0;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  font-size: 1.1rem;
  cursor: pointer;
  color: #475569;
  flex-shrink: 0;
  display: grid;
  place-items: center;
}

.anuncio-fields {
  padding: 20px 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.anuncio-tabs {
  grid-column: span 2;
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 4px;
}

.anuncio-tabs button {
  flex: 1;
  padding: 9px;
  border: 0;
  border-radius: 8px;
  font-size: .85rem;
  font-weight: 700;
  cursor: pointer;
  background: transparent;
  color: #5f6f89;
  transition: background .15s, color .15s;
}

.anuncio-tabs button.active {
  background: #fff;
  color: #03045e;
  box-shadow: 0 1px 6px rgba(0,0,0,.1);
}

.anuncio-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.anuncio-field.full { grid-column: span 2; }

.anuncio-field span,
.anuncio-field-label {
  font-size: .75rem;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: .04em;
  display: block;
  margin-bottom: 2px;
}

.anuncio-field input,
.anuncio-field select {
  padding: 10px 12px;
  border: 1.5px solid #dbe4ef;
  border-radius: 10px;
  font-size: .9rem;
  outline: none;
  background: #f8fafc;
  transition: border-color .15s;
  width: 100%;
  box-sizing: border-box;
}

.anuncio-field input:focus,
.anuncio-field select:focus { border-color: #0077b6; background: #fff; }

/* Localização box */
.localizacao-box {
  border: 1.5px solid #dbe4ef;
  border-radius: 10px;
  padding: 14px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.localizacao-ok {
  font-size: .85rem;
  color: #0077b6;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
}

.localizacao-vazia {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: .82rem;
  color: #5f6f89;
}

.btn-pin, .btn-repin {
  border: 1.5px solid #0077b6;
  background: #fff;
  color: #0077b6;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: .82rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background .15s, color .15s;
}

.btn-pin:hover:not(:disabled),
.btn-repin:hover { background: #0077b6; color: #fff; }

.btn-pin:disabled { opacity: .4; cursor: not-allowed; }

/* Footer */
.anuncio-footer {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 11px 22px;
  border: 1.5px solid #dbe4ef;
  background: #fff;
  border-radius: 10px;
  font-size: .9rem;
  cursor: pointer;
  color: #5f6f89;
}

.btn-publicar {
  padding: 11px 28px;
  background: #03045e;
  color: #fff;
  border: 0;
  border-radius: 10px;
  font-size: .9rem;
  font-weight: 700;
  cursor: pointer;
  transition: background .15s;
}

.btn-publicar:hover:not(:disabled) { background: #0077b6; }
.btn-publicar:disabled { opacity: .4; cursor: not-allowed; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity .2s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

/* Pin icon no mapa */
:global(.pin-icon) {
  font-size: 28px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,.4));
}

:deep(.leaflet-tile-pane) {
  filter: none;
}

.floating-result-card {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: 20px;
  z-index: 450;
  display: grid;
  grid-template-columns: 112px 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, .96);
  box-shadow: 0 18px 48px rgba(15, 23, 42, .18);
  backdrop-filter: blur(16px);
}

.floating-card-close {
  align-self: start;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 999px;
  background: #f3f6fb;
  color: #475569;
  font-size: 1.35rem;
  line-height: 1;
  font-weight: 400;
  cursor: pointer;
  transition: background .16s ease, color .16s ease;
}

.floating-card-close:hover {
  background: #e2e8f0;
  color: #111827;
}

.floating-result-card.empty {
  display: block;
  color: #4b5563;
  font-weight: 900;
}

.floating-result-card img {
  width: 112px;
  height: 86px;
  border-radius: 10px;
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
  width: min(100%, var(--layout-max, 1400px));
  margin: 0 auto;
  padding: clamp(28px, 4vw, 40px) var(--layout-gutter, clamp(16px, 3vw, 40px)) clamp(48px, 6vw, 68px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.section-header h2 {
  margin: 0;
  color: #111827;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  letter-spacing: 0;
  line-height: 1.04;
}

.section-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
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
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
  gap: clamp(16px, 2vw, 24px);
  align-items: stretch;
}

.property-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  border: 1px solid rgba(219, 228, 239, .95);
  border-radius: var(--geo-radius);
  background: #ffffff;
  box-shadow: 0 12px 34px rgba(3, 4, 94, .08);
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
  aspect-ratio: 16 / 10;
  height: auto;
  background: #e5edf7;
  overflow: hidden;
}

.property-photo-inner {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.property-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform .38s ease;
}

.property-card:hover .property-photo img {
  transform: scale(1.05);
}

.property-photo-badges {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.badge.type-badge {
  background: rgba(255, 255, 255, .92);
  color: #111827;
  border: 1px solid rgba(0,0,0,.08);
  backdrop-filter: blur(6px);
}

.fav-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, .92);
  backdrop-filter: blur(6px);
  color: #6b7280;
  cursor: pointer;
  transition: background .16s ease, color .16s ease, transform .16s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,.15);
}

.fav-btn svg {
  width: 18px;
  height: 18px;
}

.fav-btn:hover {
  color: #ef4444;
  transform: scale(1.12);
  background: #fff;
}

.fav-btn.active {
  color: #ef4444;
}



.property-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 18px;
}

.property-price {
  display: block;
  color: #111827;
  font-size: 1.3rem;
  font-weight: 950;
}

.property-content h3 {
  min-height: 42px;
  margin: 9px 0 7px;
  color: #111827;
  font-size: 1.05rem;
  line-height: 1.28;
}

.property-location {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0 0 14px;
  color: #64748b;
  font-weight: 700;
  font-size: .88rem;
}

.property-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  border-top: 1px solid #f1f5f9;
  padding-top: 12px;
}

.property-specs span {
  display: flex;
  align-items: center;
  gap: 5px;
  border-radius: 999px;
  padding: 6px 10px;
  background: #f4f8fc;
  color: #374151;
  font-size: .82rem;
  font-weight: 850;
}

.property-specs svg {
  width: 14px;
  height: 14px;
  color: var(--geo-blue);
  flex-shrink: 0;
}

.property-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 14px;
}

.map-btn {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 40px;
  padding: 0 14px;
  border: 1.5px solid var(--geo-line);
  border-radius: 999px;
  background: transparent;
  color: #374151;
  font-size: .84rem;
  font-weight: 900;
  cursor: pointer;
  transition: border-color .16s ease, background .16s ease;
  white-space: nowrap;
}

.map-btn:hover {
  border-color: var(--geo-cyan);
  background: rgba(202, 240, 248, .25);
}

.property-actions .contact {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 40px;
  border: 0;
  border-radius: 999px;
  background: #25d366;
  color: #ffffff;
  font-size: .88rem;
  font-weight: 950;
  cursor: pointer;
  transition: background .16s ease, transform .16s ease;
  white-space: nowrap;
}

.property-actions .contact:hover {
  background: #1ebe5d;
  transform: translateY(-1px);
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
  }

  .hero-search-card {
    position: static;
    max-width: none;
  }

  .map-showcase {
    min-height: clamp(420px, 56vh, 560px);
  }

  .property-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .landing-hero,
  .results-section {
    padding-left: var(--layout-gutter, 16px);
    padding-right: var(--layout-gutter, 16px);
  }

  .primary-fields {
    gap: 10px;
  }

  .hero-search-card {
    max-width: none;
    border-radius: 20px;
    padding: 16px;
  }

  .hero-search-card h1 {
    font-size: clamp(1.72rem, 8vw, 2.28rem);
    letter-spacing: -.045em;
  }

  .hero-kicker {
    margin-bottom: 7px;
    font-size: .68rem;
  }

  .hero-text {
    margin: 10px 0 14px;
    font-size: .88rem;
    line-height: 1.45;
  }

  .intent-tabs {
    width: 100%;
    margin-bottom: 14px;
  }

  .intent-tabs button,
  .intent-tabs a {
    min-height: 38px;
    font-size: .78rem;
  }

  .big-field {
    min-height: 58px;
    padding: 9px 11px;
  }

  .secondary-fields {
    grid-template-columns: repeat(2, minmax(0, 1fr));
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
    grid-template-columns: 82px 1fr auto;
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
@media (max-width: 520px) {
  .landing-hero {
    padding-top: 12px;
    padding-bottom: 22px;
  }

  .hero-search-card {
    box-shadow: 0 16px 38px rgba(3, 4, 94, .11);
  }

  .operation-tabs {
    gap: 18px;
  }

  .operation-tabs button {
    font-size: .88rem;
    padding-bottom: 8px;
  }

  .primary-fields {
    gap: 9px;
  }

  .field-icon {
    width: 20px;
    font-size: 1.04rem;
  }

  .field-copy strong,
  .select-field span {
    font-size: .76rem;
  }

  .field-copy input,
  .select-field select {
    font-size: .86rem;
  }

  .secondary-fields {
    grid-template-columns: 1fr;
  }

  .select-field {
    min-height: 58px;
    padding: 9px 11px;
  }

  .advanced-toggle {
    min-height: 42px;
    padding: 0 12px;
    font-size: .84rem;
  }

  .advanced-toggle strong {
    font-size: .74rem;
  }

  .quick-filters,
  .hero-active-chips,
  .active-chips {
    gap: 7px;
  }

  .quick-filters button,
  .hero-active-chips button,
  .active-chips button {
    padding: 7px 9px;
    font-size: .76rem;
  }

  .form-footer {
    gap: 8px;
  }

  .clear-button {
    min-height: 38px;
  }

  .search-button {
    min-height: 44px;
  }
}

/* ── Skeleton Loading ─────────────────────────────── */
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

.skeleton-card {
  pointer-events: none;
  cursor: default;
}

.skeleton-photo {
  aspect-ratio: 16 / 10;
  background: linear-gradient(90deg, #e8eef5 25%, #f4f7fb 50%, #e8eef5 75%);
  background-size: 800px 100%;
  animation: shimmer 1.6s infinite linear;
}

.skeleton-body {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skel-line {
  height: 12px;
  border-radius: 99px;
  background: linear-gradient(90deg, #e8eef5 25%, #f4f7fb 50%, #e8eef5 75%);
  background-size: 800px 100%;
  animation: shimmer 1.6s infinite linear;
  width: 70%;
}

.skel-line.w-50 { width: 50%; }
.skel-line.w-85 { width: 85%; }
.skel-line.w-45 { width: 45%; }
.skel-line.h-22 { height: 22px; }
.skel-line.h-16 { height: 16px; }

.skel-specs {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.skel-chip {
  height: 28px;
  width: 72px;
  border-radius: 99px;
  background: linear-gradient(90deg, #e8eef5 25%, #f4f7fb 50%, #e8eef5 75%);
  background-size: 800px 100%;
  animation: shimmer 1.6s infinite linear;
}

</style>