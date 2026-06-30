<template>
  <div class="auth-page">
    <div class="auth-visual">
      <div class="auth-brand">
        <div class="logo-mark">
          <i class="fas fa-map-marker-alt"></i>
        </div>
        <h2>GeoHouse</h2>
        <p>Portal imobiliário com busca por mapa</p>
      </div>
      <div class="auth-stats">
        <div class="stat"><strong>Mapa</strong><span>dinâmico</span></div>
        <div class="stat"><strong>2 tipos</strong><span>de anúncios</span></div>
        <div class="stat"><strong>5 zonas</strong><span>Cobertura</span></div>
      </div>
    </div>

    <div class="auth-form-side">
      <div class="form-card">
        <div class="form-header">
          <h1>Bem-vindo de volta</h1>
          <p>Entre para acessar seus favoritos e anúncios</p>
        </div>

        <form @submit.prevent="login" novalidate>
          <div class="field-group" :class="{ error: errors.email }">
            <label for="email">E-mail</label>
            <div class="input-wrap">
              <i class="fas fa-envelope"></i>
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="seu@email.com"
                @blur="validateEmail"
                autocomplete="email"
              />
            </div>
            <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
          </div>

          <div class="field-group" :class="{ error: errors.senha }">
            <div class="label-row">
              <label for="senha">Senha</label>
              <a href="#" class="forgot-link" @click.prevent>Esqueceu a senha?</a>
            </div>
            <div class="input-wrap">
              <i class="fas fa-lock"></i>
              <input
                id="senha"
                v-model="senha"
                :type="showSenha ? 'text' : 'password'"
                placeholder="Sua senha"
                autocomplete="current-password"
              />
              <button type="button" class="toggle-pass" @click="showSenha = !showSenha" tabindex="-1">
                <i :class="showSenha ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <p v-if="errors.senha" class="field-error">{{ errors.senha }}</p>
          </div>

          <p v-if="erroGlobal" class="erro-global">
            <i class="fas fa-exclamation-circle"></i> {{ erroGlobal }}
          </p>

          <button type="submit" class="btn-submit" :class="{ loading: carregando }">
            <span v-if="!carregando">Entrar</span>
            <span v-else><i class="fas fa-circle-notch fa-spin"></i> Entrando...</span>
          </button>
        </form>

        <div class="divider"><span>ou continue com</span></div>

        <div class="social-btns">
          <button class="btn-social" @click.prevent>
            <svg viewBox="0 0 24 24" width="18" height="18"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Google
          </button>
          <button class="btn-social" @click.prevent>
            <i class="fab fa-apple" style="font-size:1.1rem;color:#000"></i>
            Apple
          </button>
        </div>

        <p class="auth-switch">
          Não tem conta?
          <router-link to="/cadastro">Criar conta grátis</router-link>
        </p>

        <p class="auth-anunciar">
          Quer anunciar?
          <router-link to="/cadastro?tipo=anunciante" class="link-destaque">Ver planos de anúncio</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const API_URL    = import.meta.env.VITE_API_URL || ''
const router     = useRouter()
const email      = ref('')
const senha      = ref('')
const showSenha  = ref(false)
const carregando = ref(false)
const erroGlobal = ref('')
const errors     = reactive({ email: '', senha: '' })

function validateEmail() {
  if (!email.value) { errors.email = 'E-mail obrigatório'; return false }
  if (!/\S+@\S+\.\S+/.test(email.value)) { errors.email = 'E-mail inválido'; return false }
  errors.email = ''; return true
}

// Para onde cada papel vai depois do login.
const ROTA_POR_PAPEL = {
  admin: '/admin',
  corretor: '/perfil',
  proprietario: '/perfil',
  cliente: '/',
}

async function login() {
  erroGlobal.value = ''
  const emailOk = validateEmail()
  if (!senha.value) { errors.senha = 'Senha obrigatória'; return }
  errors.senha = ''
  if (!emailOk) return

  carregando.value = true
  try {
    const resposta = await fetch(`${API_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, senha: senha.value }),
    })

    if (!resposta.ok) {
      const erro = await resposta.json().catch(() => ({}))
      throw new Error(erro.detail || 'E-mail ou senha inválidos.')
    }

    const usuario = await resposta.json()
    localStorage.setItem('geohouse_user', JSON.stringify(usuario))
    router.push(ROTA_POR_PAPEL[usuario.tipo] || '/')
  } catch (erro) {
    erroGlobal.value = erro.message || 'Não foi possível entrar.'
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100dvh - 109px);
  display: grid;
  grid-template-columns: 1fr 1fr;
}

@media (max-width: 768px) {
  .auth-page { grid-template-columns: 1fr; }
  .auth-visual { display: none; }
}

/* VISUAL SIDE */
.auth-visual {
  background: linear-gradient(160deg, var(--azul-royal, #03045e) 0%, var(--ceu-tecnologico, #00B4D8) 100%);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 48px; gap: 48px;
}

.auth-brand { text-align: center; }
.logo-mark {
  width: 70px; height: 70px; border-radius: 20px;
  background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center;
  font-size: 2rem; color: #fff; margin: 0 auto 16px;
}
.auth-brand h2 { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #fff; margin: 0 0 6px; }
.auth-brand p  { color: rgba(255,255,255,0.7); font-size: 0.95rem; margin: 0; }

.auth-stats { display: flex; gap: 32px; }
.stat { text-align: center; }
.stat strong { display: block; font-size: 1.5rem; font-weight: 800; color: #fff; font-family: 'Syne', sans-serif; }
.stat span   { font-size: 0.8rem; color: rgba(255,255,255,0.65); }

/* FORM SIDE */
.auth-form-side {
  display: flex; align-items: center; justify-content: center;
  background: var(--brisa-suave, #f0f7ff); padding: 40px 24px;
}

.form-card {
  background: #fff; border-radius: 20px; padding: 40px 36px;
  width: 100%; max-width: 420px;
  box-shadow: 0 4px 40px rgba(3,4,94,0.08);
}

.form-header { margin-bottom: 28px; }
.form-header h1 { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; color: var(--azul-royal, #03045e); margin: 0 0 6px; }
.form-header p  { font-size: 0.9rem; color: #64748b; margin: 0; }

/* FIELDS */
.field-group { margin-bottom: 18px; }
.field-group label { display: block; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; margin-bottom: 7px; }

.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
.forgot-link { font-size: 0.8rem; color: var(--ceu-tecnologico, #00B4D8); font-weight: 600; text-decoration: none; }
.forgot-link:hover { color: var(--azul-royal, #03045e); }

.input-wrap { position: relative; display: flex; align-items: center; }
.input-wrap > i:first-child {
  position: absolute; left: 14px; color: #94a3b8; font-size: 0.9rem; pointer-events: none;
}
.input-wrap input {
  width: 100%; padding: 12px 16px 12px 40px;
  border: 1.5px solid #e2e8f0; border-radius: 12px;
  font-family: 'DM Sans', sans-serif; font-size: 0.95rem; color: var(--azul-royal, #03045e);
  outline: none; transition: border-color 0.2s, box-shadow 0.2s; background: #f8fafc;
}
.input-wrap input:focus { border-color: var(--ceu-tecnologico, #00B4D8); background: #fff; box-shadow: 0 0 0 3px rgba(0,180,216,0.12); }
.field-group.error .input-wrap input { border-color: #ef4444; }

.toggle-pass { position: absolute; right: 12px; background: none; border: none; color: #94a3b8; cursor: pointer; padding: 4px; font-size: 0.9rem; }
.toggle-pass:hover { color: #475569; }

.field-error { font-size: 0.78rem; color: #ef4444; margin: 5px 0 0; }
.erro-global { font-size: 0.85rem; color: #dc2626; background: #fee2e2; border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; }

/* BUTTON */
.btn-submit {
  width: 100%; padding: 14px; margin-top: 4px;
  background: linear-gradient(90deg, var(--azul-royal,#03045e), var(--ceu-tecnologico,#00B4D8));
  color: #fff; border: none; border-radius: 12px;
  font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 700;
  cursor: pointer; transition: opacity 0.2s, transform 0.2s;
}
.btn-submit:hover:not(.loading) { opacity: 0.88; transform: translateY(-1px); }
.btn-submit.loading { opacity: 0.75; cursor: wait; }

/* DIVIDER */
.divider { display: flex; align-items: center; gap: 12px; margin: 20px 0; }
.divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: #e2e8f0; }
.divider span { font-size: 0.78rem; color: #94a3b8; white-space: nowrap; }

/* SOCIAL */
.social-btns { display: flex; gap: 10px; margin-bottom: 20px; }
.btn-social {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 12px;
  background: #fff; font-family: 'DM Sans', sans-serif; font-size: 0.9rem; font-weight: 600;
  color: #334155; cursor: pointer; transition: all 0.2s;
}
.btn-social:hover { border-color: #cbd5e1; background: #f8fafc; }

/* LINKS */
.auth-switch { text-align: center; font-size: 0.875rem; color: #64748b; margin: 0 0 8px; }
.auth-switch a, .auth-anunciar a { color: var(--ceu-tecnologico, #00B4D8); font-weight: 700; text-decoration: none; }
.auth-switch a:hover { color: var(--azul-royal, #03045e); }
.auth-anunciar { text-align: center; font-size: 0.82rem; color: #94a3b8; margin: 0; }
.link-destaque { color: var(--azul-royal, #03045e) !important; font-weight: 700; }


/* UX refresh 2026 - GeoHouse */
:where(.auth-page, .perfil-page) {
  --surface: #ffffff;
  --line: #dbe7f3;
  --text-soft: #64748b;
}
:where(.form-card, .sidebar, .perfil-content, .content-section, .anuncio-card, .metrica-card) {
  border: 1px solid var(--line) !important;
  box-shadow: 0 22px 60px rgba(3,4,94,.10) !important;
}
:where(.form-card, .sidebar, .perfil-content, .content-section) {
  border-radius: 24px !important;
}
:where(.input-wrap input, .input-wrap select, .btn-submit, .btn-salvar, .btn-novo-anuncio, .btn-upgrade) {
  border-radius: 14px !important;
}
:where(.auth-visual) {
  position: relative;
  overflow: hidden;
}
:where(.auth-visual)::before {
  content: '';
  position: absolute;
  inset: 36px;
  border: 1px solid rgba(255,255,255,.20);
  border-radius: 34px;
  pointer-events: none;
}
:where(.logo-mark, .avatar-circle) {
  box-shadow: 0 16px 40px rgba(0,180,216,.28);
}
:where(.btn-submit, .btn-salvar) {
  box-shadow: 0 14px 32px rgba(0,119,182,.22);
}
:where(.input-wrap input:focus) {
  transform: translateY(-1px);
}
@media (max-width: 768px) {
  :where(.form-card) { padding: 28px 22px !important; }
}
</style>
