import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/styles.css'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Login    from './views/Login.vue'
import Cadastro from './views/Cadastro.vue'
import Perfil   from './views/Perfil.vue'
import Admin    from './views/Admin.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',         component: Dashboard },
    { path: '/login',    component: Login     },
    { path: '/cadastro', component: Cadastro  },
    { path: '/perfil',   component: Perfil, meta: { auth: true } },
    { path: '/admin',    component: Admin,  meta: { auth: true, papel: 'admin' } },
  ]
})

function usuarioLogado() {
  try {
    return JSON.parse(localStorage.getItem('geohouse_user') || 'null')
  } catch {
    return null
  }
}

// Guarda de rota: exige login e, em algumas rotas, papel especifico.
router.beforeEach((to) => {
  if (!to.meta.auth) return true

  const user = usuarioLogado()
  if (!user) return { path: '/login' }
  if (to.meta.papel && user.tipo !== to.meta.papel) return { path: '/' }
  return true
})

createApp(App).use(router).mount('#app')