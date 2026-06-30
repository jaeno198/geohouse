<template>
  <div class="perfil-page">

    <div class="perfil-inner">

      <!-- SIDEBAR -->
      <aside class="sidebar">
        <div class="perfil-avatar">
          <div class="avatar-circle">{{ iniciais }}</div>
          <div>
            <h3>{{ usuario.nome || 'Usuário' }}</h3>
            <span class="tipo-badge" :class="usuario.tipo">
              <i :class="usuario.tipo === 'corretor' ? 'fas fa-building' : 'fas fa-user'"></i>
              {{ usuario.tipo === 'corretor' ? 'Corretor' : 'Proprietário' }}
            </span>
          </div>
        </div>

        <nav class="perfil-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="nav-item"
            :class="{ active: abaAtiva === tab.key }"
            @click="abaAtiva = tab.key"
          >
            <i :class="tab.icon"></i>
            {{ tab.label }}
            <span v-if="tab.badge" class="nav-badge">{{ tab.badge }}</span>
          </button>
        </nav>

        <!-- Plano / Upgrade -->
        <div v-if="usuario.tipo === 'proprietario'" class="upgrade-card">
          <div class="upgrade-icon"><i class="fas fa-rocket"></i></div>
          <h4>Mais destaque para seu imóvel</h4>
          <p>Anuncie com prioridade e receba mais contatos de interessados.</p>
          <button class="btn-upgrade" type="button">Ver planos</button>
        </div>

        <div v-else class="plan-card">
          <span>Plano atual</span>
          <strong>Anunciante pago</strong>
          <p>Seus imóveis podem receber destaque nas buscas.</p>
        </div>
      </aside>

      <!-- CONTENT -->
      <main class="perfil-content">

        <!-- ABA: Dados -->
        <section v-if="abaAtiva === 'dados'" class="content-section">
          <div class="section-header">
            <h2>Meus Dados</h2>
            <p>Suas informações são exibidas para compradores nos anúncios.</p>
          </div>

          <form @submit.prevent="salvar" class="dados-form">
            <div class="form-row">
              <div class="field-group">
                <label>Nome completo</label>
                <div class="input-wrap">
                  <i class="fas fa-user"></i>
                  <input v-model="usuario.nome" type="text" required />
                </div>
              </div>
              <div class="field-group" v-if="usuario.tipo === 'corretor'">
                <label>CRECI</label>
                <div class="input-wrap">
                  <i class="fas fa-id-card"></i>
                  <input v-model="usuario.creci" type="text" placeholder="PR-000000-F" />
                </div>
              </div>
            </div>

            <div class="form-row">
              <div class="field-group">
                <label>E-mail</label>
                <div class="input-wrap">
                  <i class="fas fa-envelope"></i>
                  <input v-model="usuario.email" type="email" required />
                </div>
              </div>
              <div class="field-group">
                <label>WhatsApp</label>
                <div class="input-wrap">
                  <i class="fab fa-whatsapp" style="color:#25d366"></i>
                  <input v-model="usuario.telefone" type="tel" />
                </div>
              </div>
            </div>

            <div v-if="mensagem" class="mensagem-sucesso">
              <i class="fas fa-check-circle"></i> {{ mensagem }}
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-salvar">Salvar alterações</button>
              <button type="button" class="btn-sair" @click="sair">
                <i class="fas fa-sign-out-alt"></i> Sair da conta
              </button>
            </div>
          </form>
        </section>

        <!-- ABA: Anúncios -->
        <section v-if="abaAtiva === 'anuncios'" class="content-section">
          <div class="section-header">
            <h2>Meus Anúncios</h2>
            <button class="btn-novo-anuncio" @click="novoAnuncio">
              <i class="fas fa-plus"></i> Novo anúncio
            </button>
          </div>

          <!-- Métricas -->
          <div class="metricas-grid">
            <div class="metrica-card">
              <span class="met-label">Anúncios ativos</span>
              <span class="met-valor">{{ anuncios.filter(a=>a.ativo).length }}</span>
            </div>
            <div class="metrica-card">
              <span class="met-label">Visualizações hoje</span>
              <span class="met-valor">{{ totalViews }}</span>
            </div>
            <div class="metrica-card">
              <span class="met-label">Contatos recebidos</span>
              <span class="met-valor">{{ totalContatos }}</span>
            </div>
            <div class="metrica-card destaque">
              <span class="met-label">Plano atual</span>
              <span class="met-valor-sm">{{ usuario.tipo === 'corretor' ? 'Corretor Pro' : 'Gratuito' }}</span>
            </div>
          </div>

          <!-- Lista de anúncios -->
          <div v-if="!anuncios.length" class="empty-anuncios">
            <i class="fas fa-home"></i>
            <h3>Nenhum anúncio ainda</h3>
            <p>Publique seu primeiro imóvel e comece a receber contatos.</p>
            <button class="btn-salvar" @click="novoAnuncio">
              <i class="fas fa-plus"></i> Criar primeiro anúncio
            </button>
          </div>

          <div class="anuncios-list">
            <div v-for="anuncio in anuncios" :key="anuncio.id" class="anuncio-card">
              <div class="anuncio-thumb">
                <img :src="anuncio.img" :alt="anuncio.titulo" />
                <span class="status-dot" :class="{ ativo: anuncio.ativo }"></span>
              </div>
              <div class="anuncio-info">
                <h4>{{ anuncio.titulo }}</h4>
                <p class="anuncio-preco">R$ {{ anuncio.preco.toLocaleString('pt-BR') }}</p>
                <div class="anuncio-stats">
                  <span><i class="fas fa-eye"></i> {{ anuncio.views }} views</span>
                  <span><i class="fab fa-whatsapp"></i> {{ anuncio.contatos }} contatos</span>
                  <span class="anuncio-status" :class="{ ativo: anuncio.ativo }">
                    {{ anuncio.ativo ? 'Ativo' : 'Pausado' }}
                  </span>
                </div>
              </div>
              <div class="anuncio-actions">
                <button class="btn-icon" @click="editarAnuncio(anuncio.id)" title="Editar">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon" @click="toggleAnuncio(anuncio.id)" :title="anuncio.ativo ? 'Pausar' : 'Ativar'">
                  <i :class="anuncio.ativo ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
                <button class="btn-icon danger" @click="confirmarRemocao(anuncio.id)" title="Remover">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- ABA: Favoritos -->
        <section v-if="abaAtiva === 'favoritos'" class="content-section">
          <div class="section-header">
            <h2>Favoritos</h2>
            <p>Imóveis que você salvou para ver depois.</p>
          </div>
          <div class="empty-state">
            <i class="fas fa-heart"></i>
            <h3>Nenhum favorito ainda</h3>
            <p>Explore imóveis e salve os que mais gostar.</p>
            <router-link to="/" class="btn-salvar" style="display:inline-flex;gap:8px;align-items:center;text-decoration:none">
              <i class="fas fa-search"></i> Explorar imóveis
            </router-link>
          </div>
        </section>

        <!-- ABA: Segurança -->
        <section v-if="abaAtiva === 'seguranca'" class="content-section">
          <div class="section-header">
            <h2>Segurança</h2>
            <p>Gerencie sua senha e acesso.</p>
          </div>
          <div class="dados-form">
            <div class="field-group">
              <label>Senha atual</label>
              <div class="input-wrap">
                <i class="fas fa-lock"></i>
                <input v-model="senhaAtual" type="password" placeholder="••••••••" />
              </div>
            </div>
            <div class="form-row">
              <div class="field-group">
                <label>Nova senha</label>
                <div class="input-wrap">
                  <i class="fas fa-lock"></i>
                  <input v-model="novaSenha" type="password" placeholder="Mín. 6 caracteres" />
                </div>
              </div>
              <div class="field-group">
                <label>Confirmar nova senha</label>
                <div class="input-wrap">
                  <i class="fas fa-lock"></i>
                  <input v-model="confirmarNovaSenha" type="password" placeholder="Repita a senha" />
                </div>
              </div>
            </div>
            <div class="form-actions">
              <button class="btn-salvar" @click="alterarSenha">Alterar senha</button>
            </div>
          </div>
        </section>

      </main>

    </div>

    <!-- Modal confirmação remoção -->
    <div v-if="anuncioParaRemover" class="modal-overlay" @click.self="anuncioParaRemover = null">
      <div class="modal-box">
        <i class="fas fa-exclamation-triangle" style="color:#ef4444;font-size:2rem;margin-bottom:12px"></i>
        <h3>Remover anúncio?</h3>
        <p>Essa ação não pode ser desfeita. O anúncio será removido permanentemente.</p>
        <div class="modal-actions">
          <button class="btn-sair" @click="anuncioParaRemover = null">Cancelar</button>
          <button class="btn-danger" @click="removerAnuncio(anuncioParaRemover)">Sim, remover</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const abaAtiva = ref('dados')
const mensagem = ref('')
const anuncioParaRemover = ref(null)
const senhaAtual = ref(''); const novaSenha = ref(''); const confirmarNovaSenha = ref('')

const usuario = ref({
  nome: 'João Silva', email: 'joao@email.com',
  telefone: '(44) 99999-9999', creci: '', tipo: 'corretor',
})

const anuncios = ref([
  { id: 1, titulo: 'Casa moderna com piscina',     preco: 850000, ativo: true,  views: 248, contatos: 12, img: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=200&q=70' },
  { id: 2, titulo: 'Apartamento 2 quartos centro', preco: 320000, ativo: true,  views: 134, contatos: 7,  img: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=200&q=70' },
  { id: 3, titulo: 'Terreno 300m² Jd. Universo',  preco: 180000, ativo: false, views: 56,  contatos: 2,  img: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=200&q=70' },
])

const iniciais = computed(() => {
  return usuario.value.nome.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase()
})
const totalViews    = computed(() => anuncios.value.reduce((s, a) => s + a.views, 0))
const totalContatos = computed(() => anuncios.value.reduce((s, a) => s + a.contatos, 0))

const tabs = computed(() => [
  { key: 'dados',     label: 'Meus Dados',  icon: 'fas fa-user' },
  { key: 'anuncios',  label: 'Anúncios',    icon: 'fas fa-home', badge: anuncios.value.length || null },
  { key: 'favoritos', label: 'Favoritos',   icon: 'fas fa-heart' },
  { key: 'seguranca', label: 'Segurança',   icon: 'fas fa-lock' },
])

function salvar() {
  mensagem.value = 'Perfil atualizado com sucesso!'
  setTimeout(() => mensagem.value = '', 3000)
}
function sair() { router.push('/login') }
function novoAnuncio() { alert('Abrindo formulário de novo anúncio...') }
function editarAnuncio(id) { alert(`Editando anúncio #${id}`) }
function toggleAnuncio(id) {
  const a = anuncios.value.find(x => x.id === id)
  if (a) a.ativo = !a.ativo
}
function confirmarRemocao(id) { anuncioParaRemover.value = id }
function removerAnuncio(id) {
  anuncios.value = anuncios.value.filter(a => a.id !== id)
  anuncioParaRemover.value = null
}
function alterarSenha() {
  if (novaSenha.value !== confirmarNovaSenha.value) { alert('Senhas não coincidem'); return }
  alert('Senha alterada com sucesso!')
  senhaAtual.value = ''; novaSenha.value = ''; confirmarNovaSenha.value = ''
}
</script>

<style scoped>
.perfil-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(0, 180, 216, 0.18), transparent 34%),
    linear-gradient(180deg, var(--brisa-suave, #edfaff) 0%, #f8fbff 48%, #ffffff 100%);
  padding: clamp(20px, 3vw, 28px) var(--layout-gutter, 20px) clamp(40px, 5vw, 56px);
}

.perfil-inner {
  width: min(100%, var(--layout-max, 1120px));
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(260px, 280px) minmax(0, 1fr);
  gap: clamp(18px, 2.5vw, 24px);
  align-items: start;
}

.sidebar,
.content-section {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(3, 4, 94, 0.08);
  box-shadow: 0 18px 50px rgba(3, 4, 94, 0.07);
}

/* SIDEBAR CORRIGIDA */
.sidebar {
  border-radius: 24px;
  padding: 18px;
  position: sticky;
  top: 86px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow: hidden;
}

.perfil-avatar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 6px 18px;
  border-bottom: 1px solid #eef4fb;
  min-width: 0;
}

.avatar-circle {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--azul-royal, #03045e), var(--ceu-tecnologico, #00b4d8));
  display: grid;
  place-items: center;
  color: #ffffff;
  font-family: 'Syne', sans-serif;
  font-size: 1.12rem;
  font-weight: 900;
  box-shadow: 0 12px 28px rgba(3, 4, 94, 0.16);
  flex-shrink: 0;
}

.perfil-avatar h3 {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  color: var(--azul-royal, #03045e);
  margin: 0 0 7px;
  max-width: 170px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tipo-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 5px 10px;
  border-radius: 999px;
}

.tipo-badge.proprietario {
  background: #e0f2fe;
  color: #075985;
}

.tipo-badge.corretor {
  background: #dcfce7;
  color: #166534;
}

.perfil-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  margin: 0;
}

.nav-item {
  width: 100%;
  min-height: 58px;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  border: 0;
  border-radius: 20px;
  padding: 10px 14px;
  background: transparent;
  color: #475569;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 800;
  text-align: left;
  cursor: pointer;
  transition: 0.2s ease;
  position: relative;
}

.nav-item:hover {
  background: #f1f9ff;
  color: var(--azul-royal, #03045e);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(3, 4, 94, 0.08), rgba(0, 180, 216, 0.13));
  color: var(--azul-royal, #03045e);
}

.nav-item > i {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: #f1f5f9;
  display: grid;
  place-items: center;
  color: var(--azul-corporativo, #0077b6);
  font-size: 1rem;
  flex-shrink: 0;
}

.nav-item.active > i {
  background: #ffffff;
}

.nav-badge {
  min-width: 30px;
  height: 30px;
  border-radius: 999px;
  background: var(--ceu-tecnologico, #00b4d8);
  color: #ffffff;
  display: grid;
  place-items: center;
  padding: 0 9px;
  font-size: 0.82rem;
  font-weight: 900;
  position: static;
  margin: 0;
  line-height: 1;
}

.upgrade-card,
.plan-card {
  width: 100%;
  border-radius: 22px;
  padding: 20px;
  margin: 0;
  overflow: hidden;
}

.plan-card {
  background: linear-gradient(135deg, #eef9ff, #f8fcff);
  color: var(--azul-royal, #03045e);
  border: 1px solid rgba(0, 180, 216, 0.16);
}

.plan-card span {
  display: block;
  color: #64748b;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 900;
  margin-bottom: 8px;
}

.plan-card strong {
  display: block;
  font-family: 'Syne', sans-serif;
  font-size: 1.18rem;
  line-height: 1.2;
  margin: 0 0 10px;
  color: var(--azul-royal, #03045e);
}

.plan-card p {
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.upgrade-card {
  background: linear-gradient(135deg, var(--azul-royal, #03045e), var(--azul-corporativo, #0077b6));
  color: #ffffff;
}

.upgrade-icon {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.14);
  display: grid;
  place-items: center;
  color: #fbbf24;
  font-size: 1.15rem;
  margin-bottom: 12px;
}

.upgrade-card h4 {
  display: block;
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  line-height: 1.25;
  margin: 0 0 8px;
  color: #ffffff;
}

.upgrade-card p {
  font-size: 0.84rem;
  line-height: 1.55;
  margin: 0 0 14px;
  color: rgba(255, 255, 255, 0.78);
}

.btn-upgrade {
  width: 100%;
  min-height: 42px;
  border: 0;
  border-radius: 14px;
  background: #ffffff;
  color: var(--azul-royal, #03045e);
  font-weight: 900;
  cursor: pointer;
}

/* CONTEÚDO */
.perfil-content {
  min-width: 0;
}

.content-section {
  border-radius: 28px;
  padding: clamp(20px, 3vw, 32px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 14px;
}

.section-header h2 {
  font-family: 'Syne', sans-serif;
  font-size: clamp(1.35rem, 2.5vw, 1.8rem);
  font-weight: 900;
  color: var(--azul-royal, #03045e);
  margin: 0 0 6px;
}

.section-header p {
  font-size: 0.92rem;
  line-height: 1.55;
  color: #64748b;
  margin: 0;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.field-group {
  margin-bottom: 16px;
  min-width: 0;
}

.field-group label {
  display: block;
  font-size: 0.76rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #475569;
  margin-bottom: 8px;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrap > i:first-child {
  position: absolute;
  left: 14px;
  color: #94a3b8;
  font-size: 0.9rem;
  pointer-events: none;
  z-index: 1;
}

.input-wrap input {
  width: 100%;
  height: 50px;
  padding: 0 14px 0 42px;
  border: 1.5px solid #dbe7f3;
  border-radius: 16px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.93rem;
  font-weight: 700;
  color: var(--azul-royal, #03045e);
  outline: none;
  background: #f8fbff;
  transition: 0.2s ease;
}

.input-wrap input:focus {
  border-color: var(--ceu-tecnologico, #00b4d8);
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(0, 180, 216, 0.12);
}

.mensagem-sucesso {
  display: flex;
  align-items: center;
  gap: 9px;
  background: #dcfce7;
  color: #166534;
  border-radius: 16px;
  padding: 13px 16px;
  font-size: 0.9rem;
  font-weight: 800;
  margin: 6px 0 16px;
}

.form-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.btn-salvar,
.btn-sair,
.btn-novo-anuncio,
.btn-danger {
  min-height: 46px;
  border-radius: 999px;
  padding: 0 22px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 900;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: 0.2s ease;
  text-decoration: none;
}

.btn-salvar,
.btn-novo-anuncio {
  border: 0;
  color: #ffffff;
  background: linear-gradient(135deg, var(--azul-royal, #03045e), var(--azul-corporativo, #0077b6));
  box-shadow: 0 12px 26px rgba(3, 4, 94, 0.16);
}

.btn-salvar:hover,
.btn-novo-anuncio:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 34px rgba(3, 4, 94, 0.22);
}

.btn-sair {
  background: #ffffff;
  color: var(--azul-royal, #03045e);
  border: 1.5px solid #dbe7f3;
}

.btn-sair:hover {
  background: #f1f9ff;
}

.metricas-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 28px;
}

.metrica-card {
  min-height: 105px;
  background: #f8fbff;
  border: 1px solid #e4eef8;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.metrica-card.destaque {
  background: linear-gradient(135deg, rgba(3, 4, 94, 0.08), rgba(0, 180, 216, 0.12));
}

.met-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #64748b;
}

.met-valor {
  font-family: 'Syne', sans-serif;
  font-size: 1.7rem;
  font-weight: 900;
  color: var(--azul-royal, #03045e);
}

.met-valor-sm {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 900;
  color: var(--azul-royal, #03045e);
}

.anuncios-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.anuncio-card {
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  padding: 14px;
  border: 1px solid #e4eef8;
  border-radius: 22px;
  background: #ffffff;
  transition: 0.2s ease;
}

.anuncio-card:hover {
  border-color: rgba(0, 180, 216, 0.35);
  box-shadow: 0 16px 34px rgba(3, 4, 94, 0.08);
}

.anuncio-thumb {
  position: relative;
  width: 96px;
  height: 78px;
  border-radius: 16px;
  overflow: hidden;
  background: #e2e8f0;
}

.anuncio-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: #94a3b8;
  border: 2px solid #ffffff;
}

.status-dot.ativo {
  background: #22c55e;
}

.anuncio-info {
  min-width: 0;
}

.anuncio-info h4 {
  color: var(--azul-royal, #03045e);
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  line-height: 1.2;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.anuncio-preco {
  color: var(--azul-corporativo, #0077b6);
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 900;
  margin: 0 0 8px;
}

.anuncio-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.anuncio-stats span {
  font-size: 0.8rem;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-weight: 700;
}

.anuncio-status {
  color: #94a3b8;
  font-weight: 900;
}

.anuncio-status.ativo {
  color: #22c55e;
}

.anuncio-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  border: 1.5px solid #dbe7f3;
  background: #ffffff;
  color: #475569;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: 0.2s ease;
}

.btn-icon:hover {
  color: var(--azul-royal, #03045e);
  border-color: var(--ceu-tecnologico, #00b4d8);
  background: #f1f9ff;
}

.btn-icon.danger:hover {
  color: #ef4444;
  border-color: #ef4444;
  background: #fff5f5;
}

.empty-state,
.empty-anuncios {
  min-height: 300px;
  border: 1.5px dashed #cbd5e1;
  border-radius: 24px;
  background: #f8fbff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 36px 20px;
  color: #64748b;
}

.empty-state i,
.empty-anuncios i {
  font-size: 2.4rem;
  color: var(--ceu-tecnologico, #00b4d8);
  margin-bottom: 14px;
}

.empty-state h3,
.empty-anuncios h3 {
  font-family: 'Syne', sans-serif;
  font-size: 1.2rem;
  color: var(--azul-royal, #03045e);
  margin: 0 0 8px;
}

.empty-state p,
.empty-anuncios p {
  font-size: 0.92rem;
  line-height: 1.55;
  margin: 0 0 18px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(3, 4, 94, 0.45);
  backdrop-filter: blur(4px);
  display: grid;
  place-items: center;
  z-index: 500;
  padding: 20px;
}

.modal-box {
  width: min(400px, 100%);
  background: #ffffff;
  border-radius: 26px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 24px 80px rgba(3, 4, 94, 0.28);
}

.modal-box h3 {
  font-family: 'Syne', sans-serif;
  font-size: 1.3rem;
  font-weight: 900;
  color: var(--azul-royal, #03045e);
  margin: 0 0 8px;
}

.modal-box p {
  font-size: 0.9rem;
  line-height: 1.55;
  color: #64748b;
  margin: 0 0 24px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn-danger {
  background: #ef4444;
  color: #ffffff;
  border: 0;
}

.btn-danger:hover {
  background: #dc2626;
}

@media (max-width: 980px) {
  .perfil-inner {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    border-radius: 22px;
  }

  .perfil-nav {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .nav-item {
    min-height: 56px;
    grid-template-columns: 40px minmax(0, 1fr) auto;
  }

  .nav-item > i {
    width: 40px;
    height: 40px;
  }

  .plan-card,
  .upgrade-card {
    display: block;
  }

  .metricas-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .perfil-page {
    padding: 16px 12px 42px;
  }

  .content-section {
    border-radius: 22px;
    padding: 18px;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .anuncio-card {
    grid-template-columns: 86px minmax(0, 1fr);
    align-items: start;
  }

  .anuncio-thumb {
    width: 86px;
    height: 74px;
  }

  .anuncio-actions {
    grid-column: 1 / -1;
    justify-content: flex-end;
    border-top: 1px solid #e4eef8;
    padding-top: 12px;
  }

  .anuncio-info h4 {
    white-space: normal;
  }
}

@media (max-width: 560px) {
  .perfil-nav {
    grid-template-columns: 1fr;
  }

  .nav-item {
    min-height: 54px;
    border-radius: 16px;
    padding: 8px 12px;
  }

  .nav-item > i {
    width: 38px;
    height: 38px;
    border-radius: 14px;
  }

  .plan-card,
  .upgrade-card {
    padding: 16px;
    border-radius: 18px;
  }

  .plan-card strong {
    font-size: 1.05rem;
  }

  .metricas-grid {
    grid-template-columns: 1fr;
  }

  .form-actions .btn-salvar,
  .form-actions .btn-sair {
    width: 100%;
  }

  .anuncio-card {
    grid-template-columns: 1fr;
  }

  .anuncio-thumb {
    width: 100%;
    height: 160px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-actions .btn-sair,
  .modal-actions .btn-danger {
    width: 100%;
  }
}
</style>
