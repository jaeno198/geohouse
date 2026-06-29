<template>
  <div class="auth-page">

    <div class="auth-visual">
      <div class="auth-brand">
        <div class="logo-mark"><i class="fas fa-map-marker-alt"></i></div>
        <h2>GeoHouse</h2>
        <p>Crie sua conta gratuitamente</p>
      </div>
      <div class="plan-cards">
        <div class="plan-card" :class="{ active: tipoUsuario === 'proprietario' }" @click="tipoUsuario = 'proprietario'">
          <i class="fas fa-user"></i>
          <strong>Proprietário</strong>
          <span>Anuncie 1 imóvel grátis</span>
        </div>
        <div class="plan-card destacado" :class="{ active: tipoUsuario === 'corretor' }" @click="tipoUsuario = 'corretor'">
          <div class="plan-badge">Popular</div>
          <i class="fas fa-building"></i>
          <strong>Anunciante pago</strong>
          <span>Mais imóveis + destaque</span>
        </div>
      </div>
    </div>

    <div class="auth-form-side">
      <div class="form-card">
        <div class="form-header">
          <h1>Criar conta</h1>
          <p>Já tem conta? <router-link to="/login">Entrar</router-link></p>
        </div>

        <!-- Tipo seletor (mobile only) -->
        <div class="tipo-toggle-mobile">
          <button :class="{ active: tipoUsuario === 'proprietario' }" @click="tipoUsuario = 'proprietario'">
            <i class="fas fa-user"></i> Proprietário
          </button>
          <button :class="{ active: tipoUsuario === 'corretor' }" @click="tipoUsuario = 'corretor'">
            <i class="fas fa-building"></i> Corretor
          </button>
        </div>

        <form @submit.prevent="cadastrar" novalidate>
          <div class="fields-row">
            <div class="field-group">
              <label for="nome">Nome completo</label>
              <div class="input-wrap">
                <i class="fas fa-user"></i>
                <input id="nome" v-model="nome" type="text" placeholder="Seu nome" required />
              </div>
            </div>

            <div class="field-group" v-if="tipoUsuario === 'corretor'">
              <label for="creci">CRECI (opcional)</label>
              <div class="input-wrap">
                <i class="fas fa-id-card"></i>
                <input id="creci" v-model="creci" type="text" placeholder="PR-000000-F" />
              </div>
            </div>
          </div>

          <div class="field-group" :class="{ error: errors.email }">
            <label for="email">E-mail</label>
            <div class="input-wrap">
              <i class="fas fa-envelope"></i>
              <input id="email" v-model="email" type="email" placeholder="seu@email.com" @blur="validateEmail" />
            </div>
            <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
          </div>

          <div class="field-group">
            <label for="telefone">WhatsApp</label>
            <div class="input-wrap">
              <i class="fab fa-whatsapp" style="color:#25d366"></i>
              <input id="telefone" v-model="telefone" type="tel" placeholder="(44) 99999-9999" />
            </div>
            <p class="field-hint">Usado para contato com compradores</p>
          </div>

          <div class="fields-row">
            <div class="field-group" :class="{ error: errors.senha }">
              <label for="senha">Senha</label>
              <div class="input-wrap">
                <i class="fas fa-lock"></i>
                <input id="senha" v-model="senha" :type="showSenha ? 'text' : 'password'" placeholder="Mín. 6 caracteres" @input="validateSenha" />
                <button type="button" class="toggle-pass" @click="showSenha = !showSenha" tabindex="-1">
                  <i :class="showSenha ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div class="password-strength" v-if="senha">
                <div class="strength-bar" :style="`width:${forcaSenha.pct}%`" :class="forcaSenha.cls"></div>
              </div>
              <p v-if="errors.senha" class="field-error">{{ errors.senha }}</p>
            </div>

            <div class="field-group" :class="{ error: errors.confirmar }">
              <label for="confirmar">Confirmar senha</label>
              <div class="input-wrap">
                <i class="fas fa-lock"></i>
                <input id="confirmar" v-model="confirmarSenha" :type="showSenha ? 'text' : 'password'" placeholder="Repita a senha" @blur="validateConfirmar" />
              </div>
              <p v-if="errors.confirmar" class="field-error">{{ errors.confirmar }}</p>
            </div>
          </div>

          <label class="check-wrap">
            <input type="checkbox" v-model="aceite" required />
            <span>Aceito os <a href="#" @click.prevent>Termos de Uso</a> e a <a href="#" @click.prevent>Política de Privacidade</a></span>
          </label>
          <p v-if="errors.aceite" class="field-error">{{ errors.aceite }}</p>

          <button type="submit" class="btn-submit" :class="{ loading: carregando }">
            <span v-if="!carregando">
              Criar conta {{ tipoUsuario === 'corretor' ? '— Anunciante pago' : 'grátis' }}
            </span>
            <span v-else><i class="fas fa-circle-notch fa-spin"></i> Criando conta...</span>
          </button>
        </form>

        <p class="auth-note" v-if="tipoUsuario === 'corretor'">
          <i class="fas fa-info-circle"></i>
          Plano pago para aumentar visibilidade, receber mais contatos e gerenciar múltiplos anúncios.
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route  = useRoute()
const router = useRouter()

const tipoUsuario    = ref(route.query.tipo === 'anunciante' ? 'corretor' : 'proprietario')
const nome           = ref('')
const email          = ref('')
const telefone       = ref('')
const creci          = ref('')
const senha          = ref('')
const confirmarSenha = ref('')
const aceite         = ref(false)
const showSenha      = ref(false)
const carregando     = ref(false)
const errors         = reactive({ email: '', senha: '', confirmar: '', aceite: '' })

const forcaSenha = computed(() => {
  const s = senha.value
  if (!s) return { pct: 0, cls: '' }
  let score = 0
  if (s.length >= 6)  score++
  if (s.length >= 10) score++
  if (/[A-Z]/.test(s)) score++
  if (/[0-9]/.test(s)) score++
  if (/[^A-Za-z0-9]/.test(s)) score++
  if (score <= 1) return { pct: 20,  cls: 'weak' }
  if (score <= 3) return { pct: 60,  cls: 'ok' }
  return { pct: 100, cls: 'strong' }
})

function validateEmail() {
  if (!email.value) { errors.email = 'E-mail obrigatório'; return false }
  if (!/\S+@\S+\.\S+/.test(email.value)) { errors.email = 'E-mail inválido'; return false }
  errors.email = ''; return true
}

function validateSenha() {
  if (!senha.value || senha.value.length < 6) { errors.senha = 'Mínimo 6 caracteres' }
  else errors.senha = ''
}

function validateConfirmar() {
  if (senha.value !== confirmarSenha.value) errors.confirmar = 'Senhas não coincidem'
  else errors.confirmar = ''
}

async function cadastrar() {
  validateEmail(); validateSenha(); validateConfirmar()
  if (!aceite.value) { errors.aceite = 'Aceite os termos para continuar' }
  else errors.aceite = ''
  if (Object.values(errors).some(e => e)) return

  carregando.value = true
  await new Promise(r => setTimeout(r, 1000))
  carregando.value = false
  router.push('/')
}
</script>

<style scoped>
.auth-page { min-height: calc(100dvh - 109px); display: grid; grid-template-columns: 1fr 1fr; }
@media (max-width: 768px) { .auth-page { grid-template-columns: 1fr; } .auth-visual { display: none; } }

/* VISUAL */
.auth-visual {
  background: linear-gradient(160deg, var(--azul-royal, #03045e) 0%, var(--ceu-tecnologico, #00B4D8) 100%);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 48px; gap: 40px;
}
.auth-brand { text-align: center; }
.logo-mark { width: 70px; height: 70px; border-radius: 20px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #fff; margin: 0 auto 16px; }
.auth-brand h2 { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #fff; margin: 0 0 6px; }
.auth-brand p  { color: rgba(255,255,255,0.7); font-size: 0.95rem; margin: 0; }

.plan-cards { display: flex; flex-direction: column; gap: 12px; width: 100%; max-width: 280px; }
.plan-card {
  background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.2);
  border-radius: 14px; padding: 16px 18px; cursor: pointer; transition: all 0.2s;
  position: relative;
}
.plan-card:hover { background: rgba(255,255,255,0.18); }
.plan-card.active { background: rgba(255,255,255,0.22); border-color: rgba(255,255,255,0.7); }
.plan-card i { font-size: 1.1rem; color: rgba(255,255,255,0.8); margin-bottom: 6px; display: block; }
.plan-card strong { display: block; color: #fff; font-size: 0.95rem; font-weight: 700; margin-bottom: 2px; }
.plan-card span { font-size: 0.78rem; color: rgba(255,255,255,0.65); }
.plan-badge { position: absolute; top: -10px; right: 12px; background: #fbbf24; color: #78350f; font-size: 0.68rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; padding: 2px 9px; border-radius: 20px; }

/* FORM */
.auth-form-side { display: flex; align-items: center; justify-content: center; background: var(--brisa-suave, #f0f7ff); padding: 40px 24px; }
.form-card { background: #fff; border-radius: 20px; padding: 36px 32px; width: 100%; max-width: 460px; box-shadow: 0 4px 40px rgba(3,4,94,0.08); }
.form-header { margin-bottom: 22px; }
.form-header h1 { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--azul-royal, #03045e); margin: 0 0 4px; }
.form-header p  { font-size: 0.875rem; color: #64748b; margin: 0; }
.form-header a  { color: var(--ceu-tecnologico, #00B4D8); font-weight: 700; text-decoration: none; }

.tipo-toggle-mobile { display: none; }
@media (max-width: 768px) {
  .tipo-toggle-mobile { display: flex; gap: 8px; margin-bottom: 20px; }
  .tipo-toggle-mobile button { flex: 1; padding: 10px; border: 1.5px solid #e2e8f0; border-radius: 10px; background: #f8fafc; color: #475569; font-weight: 600; font-size: 0.85rem; cursor: pointer; }
  .tipo-toggle-mobile button.active { border-color: var(--ceu-tecnologico,#00B4D8); background: #f0f9ff; color: var(--azul-royal,#03045e); }
}

.fields-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 520px) { .fields-row { grid-template-columns: 1fr; } }

.field-group { margin-bottom: 16px; }
.field-group label { display: block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; margin-bottom: 6px; }

.input-wrap { position: relative; display: flex; align-items: center; }
.input-wrap > i:first-child { position: absolute; left: 12px; color: #94a3b8; font-size: 0.85rem; pointer-events: none; z-index: 1; }
.input-wrap input { width: 100%; padding: 11px 14px 11px 36px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-family: 'DM Sans',sans-serif; font-size: 0.9rem; color: var(--azul-royal,#03045e); outline: none; background: #f8fafc; transition: border-color 0.2s, box-shadow 0.2s; }
.input-wrap input:focus { border-color: var(--ceu-tecnologico,#00B4D8); background: #fff; box-shadow: 0 0 0 3px rgba(0,180,216,0.1); }
.field-group.error .input-wrap input { border-color: #ef4444; }
.toggle-pass { position: absolute; right: 10px; background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 0.85rem; padding: 4px; }

.field-error { font-size: 0.75rem; color: #ef4444; margin: 4px 0 0; }
.field-hint  { font-size: 0.75rem; color: #94a3b8; margin: 4px 0 0; }

.password-strength { height: 3px; background: #f1f5f9; border-radius: 10px; margin-top: 6px; overflow: hidden; }
.strength-bar { height: 100%; border-radius: 10px; transition: width 0.3s, background 0.3s; }
.strength-bar.weak   { background: #ef4444; }
.strength-bar.ok     { background: #f59e0b; }
.strength-bar.strong { background: #22c55e; }

.check-wrap { display: flex; align-items: flex-start; gap: 9px; font-size: 0.82rem; color: #475569; cursor: pointer; margin-bottom: 4px; line-height: 1.5; }
.check-wrap input { margin-top: 2px; accent-color: var(--ceu-tecnologico,#00B4D8); }
.check-wrap a { color: var(--ceu-tecnologico,#00B4D8); font-weight: 700; text-decoration: none; }

.btn-submit { width: 100%; padding: 13px; margin-top: 16px; background: linear-gradient(90deg, var(--azul-royal,#03045e), var(--ceu-tecnologico,#00B4D8)); color: #fff; border: none; border-radius: 12px; font-family: 'DM Sans',sans-serif; font-size: 0.95rem; font-weight: 700; cursor: pointer; transition: opacity 0.2s, transform 0.2s; }
.btn-submit:hover:not(.loading) { opacity: 0.88; transform: translateY(-1px); }
.btn-submit.loading { opacity: 0.7; cursor: wait; }

.auth-note { margin-top: 14px; font-size: 0.78rem; color: #64748b; background: #f8fafc; border-radius: 8px; padding: 10px 12px; }
.auth-note i { color: var(--ceu-tecnologico,#00B4D8); margin-right: 4px; }


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
