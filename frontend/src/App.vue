<template>
  <div id="app">

    <!-- TOP BAR — fora do container para ocupar 100% da largura -->
    <div class="top-bar">
      Milhares de imóveis à venda e aluguel em todo o Brasil
    </div>

    <!-- NAVBAR -->
    <header>
      <nav>
        <router-link to="/" class="nav-brand">
          <img src="@/assets/img/logos/logo.jpeg" alt="GeoHouse" />
        </router-link>
        <div class="nav-actions">
          <router-link to="/login">Entrar</router-link>
          <router-link to="/cadastro">Cadastrar</router-link>
          <router-link to="/perfil">Meu Perfil</router-link>
          <router-link to="/admin" class="nav-admin">Admin</router-link>
          <button class="btn-anunciar" @click="modalAberto = true">
            <i class="fas fa-plus"></i> Anunciar Grátis
          </button>
        </div>
      </nav>
    </header>

    <main class="app-main">
      <router-view :search-query="searchQuery" />
    </main>

    <!-- FOOTER -->
    <footer>
        <div class="footer-inner">
          <div class="footer-brand">
            <span class="footer-logo-text">GeoHouse</span>
            <p>Portal imobiliário com busca inteligente por mapa. Encontre imóveis em Maringá e região com filtros precisos.</p>
            <div class="footer-social">
              <a href="#" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
              <a href="#" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
              <a href="#" aria-label="WhatsApp"><i class="fab fa-whatsapp"></i></a>
              <a href="#" aria-label="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
            </div>
          </div>
          <div class="footer-col">
            <h5>Navegar</h5>
            <router-link to="/">Buscar Imóveis</router-link>
            <router-link to="/login">Entrar na Conta</router-link>
            <router-link to="/cadastro">Criar Conta Grátis</router-link>
            <router-link to="/perfil">Meu Perfil</router-link>
          </div>
          <div class="footer-col">
            <h5>Contato</h5>
            <address>
              <span>contato@geohouse.com.br</span>
              <span>Maringá – PR</span>
              <span>(44) 3000-0000</span>
            </address>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2025 GeoHouse — Todos os direitos reservados.</p>
          <p>Feito com ♥ em Maringá</p>
        </div>
    </footer>

    <!-- MODAL — fora do fluxo principal para sobrepor tudo -->
    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false">
      <div class="modal-box">
        <div class="modal-header">
          <div class="modal-header-icon"><i class="fas fa-home"></i></div>
          <div class="modal-header-text">
            <h2>Anunciar Imóvel</h2>
            <p>Gratuito · Publicação imediata no mapa</p>
          </div>
          <button class="modal-close" @click="modalAberto = false" aria-label="Fechar">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-fields">
          <label class="modal-field">
            <span>Título do anúncio</span>
            <input v-model="novoAnuncio.titulo" type="text" placeholder="Ex: Apartamento 3 quartos no centro" />
          </label>
          <label class="modal-field">
            <span>Descrição</span>
            <textarea v-model="novoAnuncio.descricao" placeholder="Descreva o imóvel, diferenciais, localização..." rows="3"></textarea>
          </label>
          <div class="modal-row">
            <label class="modal-field">
              <span>Modalidade</span>
              <select v-model="novoAnuncio.modalidade">
                <option value="venda">Venda</option>
                <option value="aluguel">Aluguel</option>
              </select>
            </label>
            <label class="modal-field">
              <span>Tipo</span>
              <select v-model="novoAnuncio.tipo">
                <option value="">Selecionar</option>
                <option value="casa">Casa</option>
                <option value="apartamento">Apartamento</option>
                <option value="terreno">Terreno</option>
                <option value="comercial">Comercial</option>
              </select>
            </label>
            <label class="modal-field">
              <span>Preço (R$)</span>
              <input v-model.number="novoAnuncio.preco" type="number" placeholder="350000" min="0" />
            </label>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-publicar" @click="publicarAnuncio">
            <i class="fas fa-check-circle"></i> Publicar Anúncio
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const searchQuery = ref('')
const modalAberto = ref(false)

const novoAnuncio = ref({
  titulo: '',
  descricao: '',
  modalidade: 'venda',
  tipo: '',
  preco: null,
})

function publicarAnuncio() {
  alert('✅ Anúncio publicado com sucesso!')
  novoAnuncio.value = { titulo: '', descricao: '', modalidade: 'venda', tipo: '', preco: null }
  modalAberto.value = false
}
</script>

<style>
header nav .nav-brand img,
header nav a img {
  display: block;
  height: 48px;
  max-width: 160px;
  width: auto;
  object-fit: contain;
}

header nav .nav-admin {
  font-size: .78rem;
  color: #9ca3af;
  opacity: .7;
}
</style>