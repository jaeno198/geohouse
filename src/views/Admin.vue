<template>
  <div class="admin-page">

    <!-- Login gate -->
    <div v-if="!autenticado" class="admin-login">
      <div class="login-card">
        <h1>Painel Administrativo</h1>
        <p>Acesso restrito</p>
        <form @submit.prevent="autenticar">
          <input
            v-model="senhaInput"
            type="password"
            placeholder="Senha de administrador"
            autocomplete="current-password"
          />
          <p v-if="erroLogin" class="erro-msg">Senha incorreta.</p>
          <button type="submit">Entrar</button>
        </form>
      </div>
    </div>

    <!-- Admin panel -->
    <div v-else class="admin-inner">

      <header class="admin-header">
        <div>
          <h1>Painel Admin — Camadas de Bairros</h1>
          <p>Importe arquivos KML ou Shapefile para delimitar bairros no mapa.</p>
        </div>
        <button class="btn-logout" @click="sair">Sair</button>
      </header>

      <!-- Mode tabs -->
      <div class="mode-tabs">
        <button :class="{ active: modo === 'shapefile' }" @click="modo = 'shapefile'">
          Shapefile (.shp + .dbf)
        </button>
        <button :class="{ active: modo === 'kml' }" @click="modo = 'kml'">
          KML (.kml)
        </button>
      </div>

      <!-- ─── SHAPEFILE UPLOAD ─── -->
      <section v-if="modo === 'shapefile'" class="upload-section">
        <h2>Importar Shapefile</h2>
        <p class="section-desc">
          Selecione os arquivos do shapefile. O <strong>.shp</strong> e o <strong>.dbf</strong> são obrigatórios.
          O <strong>.cpg</strong> garante a leitura correta de acentos.
        </p>

        <div class="shp-drop-grid">
          <label class="drop-zone" :class="{ filled: shpFiles.shp }">
            <input type="file" accept=".shp" @change="(e) => onShpFile(e, 'shp')" />
            <span class="drop-ext">.shp</span>
            <span class="drop-label">{{ shpFiles.shp ? shpFiles.shp.name : 'Geometrias (obrigatório)' }}</span>
          </label>

          <label class="drop-zone" :class="{ filled: shpFiles.dbf }">
            <input type="file" accept=".dbf" @change="(e) => onShpFile(e, 'dbf')" />
            <span class="drop-ext">.dbf</span>
            <span class="drop-label">{{ shpFiles.dbf ? shpFiles.dbf.name : 'Atributos (obrigatório)' }}</span>
          </label>

          <label class="drop-zone optional" :class="{ filled: shpFiles.cpg }">
            <input type="file" accept=".cpg" @change="(e) => onShpFile(e, 'cpg')" />
            <span class="drop-ext">.cpg</span>
            <span class="drop-label">{{ shpFiles.cpg ? shpFiles.cpg.name : 'Encoding (opcional)' }}</span>
          </label>
        </div>

        <!-- Field selection (after reading DBF header) -->
        <div v-if="shpFieldNames.length" class="field-select-box">
          <label class="form-field">
            <span>Qual campo contém o nome do bairro?</span>
            <select v-model="shpNameField">
              <option value="">Selecione...</option>
              <option v-for="f in shpFieldNames" :key="f" :value="f">{{ f }}</option>
            </select>
          </label>

          <div v-if="shpPreview" class="shp-preview">
            <strong>{{ shpPreview.count }}</strong> feições encontradas
            <span v-if="shpPreview.sample">
              · Ex: "{{ shpPreview.sample }}"
            </span>
          </div>
        </div>

        <p v-if="erroShp" class="erro-msg">{{ erroShp }}</p>
        <p v-if="sucessoShp" class="sucesso-msg">{{ sucessoShp }}</p>

        <div class="form-actions">
          <button
            class="btn-enviar"
            :disabled="!shpFiles.shp || !shpFiles.dbf || !shpNameField || carregandoShp"
            @click="importarShapefile"
          >
            {{ carregandoShp ? 'Processando...' : 'Importar camadas' }}
          </button>
        </div>
      </section>

      <!-- ─── KML UPLOAD ─── -->
      <section v-if="modo === 'kml'" class="upload-section">
        <h2>Importar KML</h2>
        <p class="section-desc">
          Suba um KML com a cidade inteira. Cada <strong>&lt;Placemark&gt;</strong> se torna
          uma camada separada usando o seu <strong>&lt;name&gt;</strong> como nome do bairro.
        </p>

        <div class="file-drop" @dragover.prevent @drop.prevent="onKmlDrop">
          <input ref="kmlInput" type="file" accept=".kml,.xml" @change="onKmlChange" />
          <div class="file-drop-label">
            <span v-if="kmlArquivo">{{ kmlArquivo.name }}</span>
            <span v-else>Arraste um .kml ou <u>clique para selecionar</u></span>
          </div>
        </div>

        <div v-if="kmlPreview" class="shp-preview">
          <strong>{{ kmlPreview.count }}</strong> bairro(s) encontrado(s)
          <span v-if="kmlPreview.sample"> · Ex: "{{ kmlPreview.sample }}"</span>
          <span v-if="kmlPreview.semNome" class="aviso-sem-nome">
            · {{ kmlPreview.semNome }} sem &lt;name&gt; serão ignorados
          </span>
        </div>

        <p v-if="erroKml" class="erro-msg">{{ erroKml }}</p>
        <p v-if="sucessoKml" class="sucesso-msg">{{ sucessoKml }}</p>

        <div class="form-actions">
          <button class="btn-enviar" :disabled="!kmlArquivo || !kmlPreview || carregandoKml" @click="importarKml">
            {{ carregandoKml ? 'Processando...' : 'Importar camadas' }}
          </button>
        </div>
      </section>

      <!-- ─── LAYERS LIST ─── -->
      <section class="layers-section">
        <div class="layers-header">
          <h2>Camadas cadastradas <span class="count">{{ kmlLayers.length }}</span></h2>
          <button v-if="kmlLayers.length" class="btn-clear-all" @click="confirmarLimpar = true">
            Limpar tudo
          </button>
        </div>

        <div v-if="kmlLayers.length === 0" class="empty-layers">
          Nenhuma camada cadastrada. Importe um shapefile ou KML acima.
        </div>

        <ul v-else class="layers-list">
          <li v-for="layer in kmlLayers" :key="layer.id" class="layer-item">
            <div class="layer-info">
              <strong>{{ layer.name }}</strong>
              <span class="layer-bairro">{{ layer.bairro }}</span>
              <span class="layer-features">{{ layer.geoJSON.features.length }} polígono(s)</span>
            </div>
            <button class="btn-remove" @click="layerParaRemover = layer">Remover</button>
          </li>
        </ul>
      </section>

    </div>

    <!-- Confirm remove layer -->
    <div v-if="layerParaRemover" class="overlay-confirm" @click.self="layerParaRemover = null">
      <div class="confirm-box">
        <p>Remover a camada <strong>{{ layerParaRemover.name }}</strong>?</p>
        <div class="confirm-actions">
          <button @click="layerParaRemover = null">Cancelar</button>
          <button class="btn-danger" @click="removerConfirmado">Remover</button>
        </div>
      </div>
    </div>

    <!-- Confirm clear all -->
    <div v-if="confirmarLimpar" class="overlay-confirm" @click.self="confirmarLimpar = false">
      <div class="confirm-box">
        <p>Remover <strong>todas as {{ kmlLayers.length }} camadas</strong>?</p>
        <div class="confirm-actions">
          <button @click="confirmarLimpar = false">Cancelar</button>
          <button class="btn-danger" @click="limparTudo">Limpar tudo</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useKmlStore, getShapefileFields, parseShapefile, detectEncoding, parseKML } from '@/composables/useKmlStore'
import { BAIRROS_MARINGA } from '@/data/bairrosMaringa'

const ADMIN_PASSWORD = 'geohouse2025'
const ADMIN_SESSION_KEY = 'geohouse_admin_ok'

const autenticado = ref(localStorage.getItem(ADMIN_SESSION_KEY) === '1')
const senhaInput = ref('')
const erroLogin = ref(false)

function autenticar() {
  if (senhaInput.value === ADMIN_PASSWORD) {
    localStorage.setItem(ADMIN_SESSION_KEY, '1')
    autenticado.value = true
    erroLogin.value = false
  } else {
    erroLogin.value = true
  }
}

function sair() {
  localStorage.removeItem(ADMIN_SESSION_KEY)
  autenticado.value = false
  senhaInput.value = ''
}

const { kmlLayers, addLayer, addLayersFromGeojson, removeLayer, clearAll } = useKmlStore()
const bairros = BAIRROS_MARINGA
const modo = ref('shapefile')

// ─── Shapefile state ───────────────────────────────────────────────────────────

const shpFiles = ref({ shp: null, dbf: null, cpg: null })
const shpFieldNames = ref([])
const shpNameField = ref('')
const shpPreview = ref(null)
const erroShp = ref('')
const sucessoShp = ref('')
const carregandoShp = ref(false)
const shpGeoJSON = ref(null)

function onShpFile(e, ext) {
  shpFiles.value[ext] = e.target.files[0] || null
  erroShp.value = ''
  sucessoShp.value = ''
  shpGeoJSON.value = null
  shpPreview.value = null
}

// When both SHP+DBF are selected, read DBF header to get field names
watch([() => shpFiles.value.shp, () => shpFiles.value.dbf], async ([shp, dbf]) => {
  shpFieldNames.value = []
  shpNameField.value = ''
  shpPreview.value = null
  if (!shp || !dbf) return

  try {
    const dbfBuf = await dbf.arrayBuffer()
    const fields = getShapefileFields(dbfBuf)
    shpFieldNames.value = fields

    // Auto-select the most likely name field
    const candidates = ['NM_BAIRRO', 'NOME', 'NAME', 'NM_MUNICIP', 'BAIRRO', 'NOME_BAIRR', 'NOM_BAIRRO']
    const auto = candidates.find((c) => fields.map((f) => f.toUpperCase()).includes(c.toUpperCase()))
    if (auto) shpNameField.value = fields.find((f) => f.toUpperCase() === auto.toUpperCase()) || ''
  } catch (e) {
    erroShp.value = 'Erro ao ler o .dbf: ' + e.message
  }
})

// When name field is picked, show preview count
watch(shpNameField, async (field) => {
  shpPreview.value = null
  shpGeoJSON.value = null
  if (!field || !shpFiles.value.shp || !shpFiles.value.dbf) return

  try {
    const [shpBuf, dbfBuf] = await Promise.all([
      shpFiles.value.shp.arrayBuffer(),
      shpFiles.value.dbf.arrayBuffer(),
    ])
    const encoding = shpFiles.value.cpg
      ? detectEncoding(await shpFiles.value.cpg.text())
      : 'utf-8'

    const geojson = parseShapefile(shpBuf, dbfBuf, encoding)
    shpGeoJSON.value = geojson

    const validFeatures = geojson.features.filter(
      (f) => f.properties?.[field]?.trim() && f.geometry,
    )
    const sample = validFeatures[0]?.properties?.[field]?.trim() || ''
    shpPreview.value = { count: validFeatures.length, sample }
  } catch (e) {
    erroShp.value = 'Erro ao processar shapefile: ' + e.message
  }
})

async function importarShapefile() {
  erroShp.value = ''
  sucessoShp.value = ''
  carregandoShp.value = true

  try {
    let geojson = shpGeoJSON.value

    if (!geojson) {
      const [shpBuf, dbfBuf] = await Promise.all([
        shpFiles.value.shp.arrayBuffer(),
        shpFiles.value.dbf.arrayBuffer(),
      ])
      const encoding = shpFiles.value.cpg
        ? detectEncoding(await shpFiles.value.cpg.text())
        : 'utf-8'
      geojson = parseShapefile(shpBuf, dbfBuf, encoding)
    }

    const count = addLayersFromGeojson(geojson, shpNameField.value)
    sucessoShp.value = `${count} camadas importadas com sucesso!`
    shpFiles.value = { shp: null, dbf: null, cpg: null }
    shpFieldNames.value = []
    shpNameField.value = ''
    shpGeoJSON.value = null
    shpPreview.value = null
  } catch (e) {
    erroShp.value = e.message || 'Erro ao importar shapefile.'
  } finally {
    carregandoShp.value = false
  }
}

// ─── KML state ────────────────────────────────────────────────────────────────

const kmlInput = ref(null)
const kmlArquivo = ref(null)
const kmlPreview = ref(null)
const kmlGeoJSON = ref(null)
const erroKml = ref('')
const sucessoKml = ref('')
const carregandoKml = ref(false)

async function processarKmlArquivo(file) {
  kmlArquivo.value = file
  kmlPreview.value = null
  kmlGeoJSON.value = null
  erroKml.value = ''
  sucessoKml.value = ''
  if (!file) return
  try {
    const texto = await file.text()
    const geojson = parseKML(texto)
    const comNome = geojson.features.filter((f) => f.properties?.name?.trim())
    const semNome = geojson.features.length - comNome.length
    kmlGeoJSON.value = geojson
    kmlPreview.value = {
      count: comNome.length,
      sample: comNome[0]?.properties?.name || '',
      semNome: semNome || 0,
    }
  } catch (e) {
    erroKml.value = 'Erro ao ler o KML: ' + e.message
  }
}

function onKmlChange(e) { processarKmlArquivo(e.target.files[0] || null) }
function onKmlDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.kml') || file.name.endsWith('.xml'))) processarKmlArquivo(file)
}

async function importarKml() {
  erroKml.value = ''
  sucessoKml.value = ''
  carregandoKml.value = true
  try {
    const count = addLayersFromGeojson(kmlGeoJSON.value, 'name')
    sucessoKml.value = `${count} camadas importadas com sucesso!`
    kmlArquivo.value = null
    kmlGeoJSON.value = null
    kmlPreview.value = null
    if (kmlInput.value) kmlInput.value.value = ''
  } catch (err) {
    erroKml.value = err.message || 'Erro ao importar KML.'
  } finally {
    carregandoKml.value = false
  }
}

// ─── Layer management ─────────────────────────────────────────────────────────

const layerParaRemover = ref(null)
const confirmarLimpar = ref(false)

function removerConfirmado() {
  if (layerParaRemover.value) { removeLayer(layerParaRemover.value.id); layerParaRemover.value = null }
}

function limparTudo() {
  clearAll()
  confirmarLimpar.value = false
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f0f4f8;
  font-family: Inter, system-ui, sans-serif;
}

/* Login */
.admin-login {
  display: grid;
  place-items: center;
  min-height: 80vh;
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: min(100%, 380px);
  box-shadow: 0 8px 32px rgba(3, 4, 94, .12);
  text-align: center;
}

.login-card h1 { font-size: 1.4rem; font-weight: 800; color: #03045e; margin: 0 0 6px; }
.login-card p  { font-size: .88rem; color: #5f6f89; margin: 0 0 24px; }

.login-card input {
  width: 100%; padding: 12px 16px;
  border: 1.5px solid #dbe4ef; border-radius: 10px;
  font-size: .95rem; outline: none; margin-bottom: 12px;
  box-sizing: border-box; transition: border-color .15s;
}

.login-card input:focus { border-color: #0077b6; }

.login-card button {
  width: 100%; padding: 12px; background: #03045e; color: #fff;
  border: 0; border-radius: 10px; font-size: .95rem; font-weight: 700;
  cursor: pointer; transition: background .15s;
}

.login-card button:hover { background: #0077b6; }

/* Inner */
.admin-inner { max-width: 860px; margin: 0 auto; padding: 32px 20px 80px; }

.admin-header {
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: 16px; margin-bottom: 24px;
}

.admin-header h1 { font-size: 1.4rem; font-weight: 800; color: #03045e; margin: 0 0 4px; }
.admin-header p  { font-size: .85rem; color: #5f6f89; margin: 0; }

.btn-logout {
  padding: 8px 18px; border: 1.5px solid #dbe4ef; background: #fff;
  border-radius: 8px; font-size: .85rem; cursor: pointer; color: #5f6f89;
  white-space: nowrap; transition: border-color .15s, color .15s;
}
.btn-logout:hover { border-color: #dc2626; color: #dc2626; }

/* Mode tabs */
.mode-tabs {
  display: flex; gap: 4px; background: #e2e8f0;
  border-radius: 12px; padding: 4px; margin-bottom: 20px;
  width: fit-content;
}

.mode-tabs button {
  padding: 9px 20px; border: 0; border-radius: 9px; background: transparent;
  font-size: .88rem; font-weight: 600; color: #5f6f89; cursor: pointer;
  transition: background .15s, color .15s;
}

.mode-tabs button.active { background: #fff; color: #03045e; box-shadow: 0 1px 6px rgba(0,0,0,.1); }

/* Sections */
.upload-section, .layers-section {
  background: #fff; border-radius: 16px; padding: 28px;
  margin-bottom: 20px; box-shadow: 0 2px 12px rgba(3, 4, 94, .06);
}

.upload-section h2, .layers-section h2 {
  font-size: 1rem; font-weight: 700; color: #03045e; margin: 0 0 6px;
}

.section-desc { font-size: .83rem; color: #5f6f89; margin: 0 0 20px; line-height: 1.5; }

/* Shapefile drop grid */
.shp-drop-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.drop-zone {
  position: relative;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 6px; padding: 20px 12px;
  border: 2px dashed #cbd5e1; border-radius: 12px;
  background: #f8fafc; cursor: pointer;
  transition: border-color .15s, background .15s;
  text-align: center;
}

.drop-zone input[type="file"] {
  position: absolute; inset: 0; opacity: 0; cursor: pointer;
  width: 100%; height: 100%; border: 0; padding: 0;
}

.drop-zone:hover { border-color: #0077b6; background: #f0f9ff; }
.drop-zone.filled { border-color: #0077b6; background: #eff8ff; border-style: solid; }
.drop-zone.optional { opacity: .85; }

.drop-ext {
  font-size: .95rem; font-weight: 800; color: #03045e;
  font-family: 'Courier New', monospace;
}

.drop-label { font-size: .73rem; color: #64748b; word-break: break-all; }
.drop-zone.filled .drop-label { color: #0077b6; font-weight: 600; }

/* Field selection */
.field-select-box {
  background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 12px; padding: 16px; margin-bottom: 16px;
  display: flex; flex-direction: column; gap: 12px;
}

.shp-preview {
  font-size: .82rem; color: #374151;
  background: #e0f2fe; border-radius: 8px; padding: 8px 12px;
}

.shp-preview strong { color: #0077b6; font-weight: 700; }

/* Form field */
.form-field { display: flex; flex-direction: column; gap: 6px; }
.form-field span { font-size: .8rem; font-weight: 600; color: #374151; }

.form-field input, .form-field select {
  padding: 10px 14px; border: 1.5px solid #dbe4ef; border-radius: 10px;
  font-size: .92rem; outline: none; background: #fff; transition: border-color .15s;
}

.form-field input:focus, .form-field select:focus { border-color: #0077b6; }

/* KML file drop */
.file-drop {
  position: relative; border: 2px dashed #dbe4ef; border-radius: 10px;
  padding: 20px; text-align: center; cursor: pointer;
  transition: border-color .15s, background .15s;
}

.file-drop:hover { border-color: #0077b6; background: #f0f9ff; }

.file-drop input[type="file"] {
  position: absolute; inset: 0; opacity: 0; cursor: pointer;
  width: 100%; height: 100%; border: 0; padding: 0;
}

.file-drop-label { font-size: .88rem; color: #5f6f89; pointer-events: none; }
.file-drop-label u { color: #0077b6; }

/* Feedback */
.erro-msg    { color: #dc2626; font-size: .82rem; margin: 0; }
.sucesso-msg { color: #16a34a; font-size: .82rem; margin: 0; }
.aviso-sem-nome { color: #92400e; }

/* Actions */
.form-actions { margin-top: 8px; }

.btn-enviar {
  padding: 12px 28px; background: #03045e; color: #fff;
  border: 0; border-radius: 10px; font-size: .92rem; font-weight: 700;
  cursor: pointer; transition: background .15s;
}

.btn-enviar:hover:not(:disabled) { background: #0077b6; }
.btn-enviar:disabled { opacity: .45; cursor: not-allowed; }

/* KML form */
.upload-form { display: flex; flex-direction: column; gap: 16px; }

/* Layers list */
.layers-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
}

.layers-header h2 { margin: 0; display: flex; align-items: center; gap: 10px; }

.count {
  background: #e0f2fe; color: #0077b6;
  font-size: .75rem; padding: 2px 8px; border-radius: 20px; font-weight: 700;
}

.btn-clear-all {
  padding: 6px 14px; border: 1.5px solid #fca5a5; background: #fff;
  border-radius: 8px; font-size: .8rem; color: #dc2626; cursor: pointer;
  transition: background .15s, color .15s;
}

.btn-clear-all:hover { background: #dc2626; color: #fff; }

.empty-layers { font-size: .88rem; color: #5f6f89; padding: 8px 0; }

.layers-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }

.layer-item {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 12px 16px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 10px;
}

.layer-info { display: flex; flex-direction: column; gap: 2px; }
.layer-info strong { font-size: .88rem; color: #111827; }
.layer-bairro { font-size: .75rem; color: #0077b6; font-weight: 600; }
.layer-features { font-size: .72rem; color: #9ca3af; }

.btn-remove {
  padding: 5px 12px; border: 1.5px solid #fca5a5; background: #fff;
  border-radius: 8px; font-size: .78rem; color: #dc2626;
  cursor: pointer; white-space: nowrap; transition: background .15s, color .15s;
}
.btn-remove:hover { background: #dc2626; color: #fff; }

/* Confirm overlay */
.overlay-confirm {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: grid; place-items: center; z-index: 9999;
}

.confirm-box {
  background: #fff; border-radius: 14px; padding: 28px;
  width: min(100%, 360px); text-align: center;
  box-shadow: 0 12px 40px rgba(0,0,0,.2);
}

.confirm-box p { font-size: .95rem; color: #111827; margin: 0 0 20px; }

.confirm-actions { display: flex; gap: 10px; justify-content: center; }

.confirm-actions button {
  padding: 9px 22px; border-radius: 8px;
  border: 1.5px solid #dbe4ef; background: #fff; font-size: .88rem; cursor: pointer;
}

.btn-danger { background: #dc2626 !important; color: #fff !important; border-color: #dc2626 !important; }

@media (max-width: 540px) {
  .shp-drop-grid { grid-template-columns: 1fr 1fr; }
  .shp-drop-grid .drop-zone:last-child { grid-column: span 2; }
}
</style>
