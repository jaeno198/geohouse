import { ref } from 'vue'

const STORAGE_KEY = 'geohouse_kml_layers'

function loadFromStorage() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

const kmlLayers = ref(loadFromStorage())

function saveToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(kmlLayers.value))
  } catch (e) {
    if (e.name === 'QuotaExceededError') {
      throw new Error('Dados muito grandes para o armazenamento local. Tente importar apenas os bairros de uma cidade.')
    }
    throw e
  }
}

// ─── KML parser ──────────────────────────────────────────────────────────────

function parseKmlCoords(text) {
  return text
    .trim()
    .split(/\s+/)
    .map((c) => {
      const [lon, lat] = c.split(',').map(Number)
      return [lon, lat]
    })
    .filter(([lon, lat]) => !isNaN(lon) && !isNaN(lat))
}

export function parseKML(kmlText) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(kmlText, 'application/xml')
  const features = []

  doc.querySelectorAll('Placemark').forEach((placemark) => {
    const name = placemark.querySelector('name')?.textContent?.trim() || ''
    const polygons = placemark.querySelectorAll('Polygon')
    if (polygons.length === 0) return

    if (polygons.length === 1) {
      const poly = polygons[0]
      const outerEl = poly.querySelector('outerBoundaryIs coordinates')
      if (!outerEl) return
      const rings = [parseKmlCoords(outerEl.textContent)]
      poly.querySelectorAll('innerBoundaryIs coordinates').forEach((el) =>
        rings.push(parseKmlCoords(el.textContent)),
      )
      features.push({ type: 'Feature', properties: { name }, geometry: { type: 'Polygon', coordinates: rings } })
    } else {
      const multiRings = []
      polygons.forEach((poly) => {
        const outerEl = poly.querySelector('outerBoundaryIs coordinates')
        if (!outerEl) return
        const rings = [parseKmlCoords(outerEl.textContent)]
        poly.querySelectorAll('innerBoundaryIs coordinates').forEach((el) =>
          rings.push(parseKmlCoords(el.textContent)),
        )
        multiRings.push(rings)
      })
      if (multiRings.length) {
        features.push({ type: 'Feature', properties: { name }, geometry: { type: 'MultiPolygon', coordinates: multiRings } })
      }
    }
  })

  return { type: 'FeatureCollection', features }
}

// ─── Shapefile parser ─────────────────────────────────────────────────────────

function ringSignedArea(coords) {
  let area = 0
  for (let i = 0, j = coords.length - 1; i < coords.length; j = i++) {
    area += (coords[j][0] + coords[i][0]) * (coords[j][1] - coords[i][1])
  }
  return area / 2
}

function buildPolygonGeometry(rings) {
  const outers = []
  const holes = []

  for (const ring of rings) {
    const area = ringSignedArea(ring)
    // CW (area < 0 in geographic coords) = outer ring in shapefile spec
    if (area <= 0) {
      outers.push([...ring].reverse()) // reverse to CCW for GeoJSON
    } else {
      holes.push([...ring].reverse()) // reverse to CW for GeoJSON holes
    }
  }

  if (outers.length === 0) {
    // fallback: treat all as outer rings
    return rings.length === 1
      ? { type: 'Polygon', coordinates: [rings[0]] }
      : { type: 'MultiPolygon', coordinates: rings.map((r) => [r]) }
  }

  if (outers.length === 1) {
    return { type: 'Polygon', coordinates: [outers[0], ...holes] }
  }

  // Multiple outer rings → MultiPolygon; assign all holes to first outer
  return {
    type: 'MultiPolygon',
    coordinates: outers.map((outer, i) => (i === 0 ? [outer, ...holes] : [outer])),
  }
}

function readDbfFields(dbfBuffer) {
  const view = new DataView(dbfBuffer)
  const headerSize = view.getInt16(8, true)
  const fields = []
  let offset = 32
  while (offset < headerSize - 1) {
    const nameBytes = new Uint8Array(dbfBuffer, offset, 11)
    let name = ''
    for (let i = 0; i < 11 && nameBytes[i] !== 0; i++) name += String.fromCharCode(nameBytes[i])
    if (!name) break
    const type = String.fromCharCode(view.getUint8(offset + 11))
    const length = view.getUint8(offset + 16)
    fields.push({ name, type, length })
    offset += 32
  }
  return fields
}

export function getShapefileFields(dbfBuffer) {
  return readDbfFields(dbfBuffer).map((f) => f.name)
}

export function parseShapefile(shpBuffer, dbfBuffer, encoding = 'utf-8') {
  const shpView = new DataView(shpBuffer)
  const dbfView = new DataView(dbfBuffer)

  // DBF metadata
  const numRecords = dbfView.getInt32(4, true)
  const headerSize = dbfView.getInt16(8, true)
  const recordSize = dbfView.getInt16(10, true)
  const fields = readDbfFields(dbfBuffer)

  // Read all DBF records
  let decoder
  try {
    decoder = new TextDecoder(encoding)
  } catch {
    decoder = new TextDecoder('utf-8')
  }

  const records = []
  let dbfOffset = headerSize
  for (let i = 0; i < numRecords; i++) {
    const deleted = dbfView.getUint8(dbfOffset) === 0x2a
    dbfOffset++
    const props = {}
    for (const field of fields) {
      const bytes = new Uint8Array(dbfBuffer, dbfOffset, field.length)
      props[field.name] = deleted ? '' : decoder.decode(bytes).trim()
      dbfOffset += field.length
    }
    records.push(props)
  }

  // Read SHP records
  const fileLength = shpView.getInt32(24, false) * 2 // big-endian, in 16-bit words → bytes
  const features = []
  let shpOffset = 100 // skip file header
  let recIdx = 0

  while (shpOffset + 8 <= fileLength && recIdx < records.length) {
    const contentLength = shpView.getInt32(shpOffset + 4, false) * 2
    shpOffset += 8

    const shapeType = shpView.getInt32(shpOffset, true)

    const props = records[recIdx++]

    if (shapeType === 0) {
      // Null shape – skip
      shpOffset += contentLength
      continue
    }

    // Polygon (5), PolygonZ (15), PolygonM (25)
    if (shapeType === 5 || shapeType === 15 || shapeType === 25) {
      const numParts = shpView.getInt32(shpOffset + 36, true)
      const numPoints = shpView.getInt32(shpOffset + 40, true)

      const parts = []
      for (let p = 0; p < numParts; p++) {
        parts.push(shpView.getInt32(shpOffset + 44 + p * 4, true))
      }
      parts.push(numPoints) // sentinel

      const pointsBase = shpOffset + 44 + numParts * 4
      const rings = []
      for (let p = 0; p < numParts; p++) {
        const ring = []
        for (let j = parts[p]; j < parts[p + 1]; j++) {
          const x = shpView.getFloat64(pointsBase + j * 16, true)
          const y = shpView.getFloat64(pointsBase + j * 16 + 8, true)
          ring.push([x, y])
        }
        rings.push(ring)
      }

      features.push({
        type: 'Feature',
        properties: props,
        geometry: buildPolygonGeometry(rings),
      })
    }

    shpOffset += contentLength
  }

  return { type: 'FeatureCollection', features }
}

export function detectEncoding(cpgText) {
  const t = (cpgText || '').trim().toUpperCase()
  if (t.includes('UTF') && t.includes('8')) return 'utf-8'
  if (t.includes('1252') || t.includes('WINDOWS-1252') || t.includes('ANSI 1252')) return 'windows-1252'
  if (t.includes('8859')) return 'iso-8859-1'
  if (t.includes('LATIN') || t.includes('ISO-8859')) return 'iso-8859-1'
  return 'utf-8'
}

// ─── Centroid ────────────────────────────────────────────────────────────────

export function getKmlCentroid(bairroName, layers) {
  const layer = layers.find((l) => l.bairro.toLowerCase() === bairroName.toLowerCase())
  if (!layer) return null

  let bestRing = null
  let maxLen = 0

  for (const feature of layer.geoJSON.features) {
    const { type, coordinates } = feature.geometry || {}
    const rings =
      type === 'Polygon' ? [coordinates[0]]
      : type === 'MultiPolygon' ? coordinates.map((p) => p[0])
      : []
    for (const ring of rings) {
      if (ring && ring.length > maxLen) { maxLen = ring.length; bestRing = ring }
    }
  }

  if (!bestRing) return null
  const lon = bestRing.reduce((s, c) => s + c[0], 0) / bestRing.length
  const lat = bestRing.reduce((s, c) => s + c[1], 0) / bestRing.length
  return { lat, lng: lon }
}

// ─── Store API ────────────────────────────────────────────────────────────────

export function useKmlStore() {
  function addLayer(name, bairro, kmlText) {
    const geoJSON = parseKML(kmlText)
    if (!geoJSON.features.length) throw new Error('KML sem polígonos reconhecíveis.')
    const layer = { id: Date.now().toString(), name, bairro, geoJSON }
    kmlLayers.value = [...kmlLayers.value, layer]
    saveToStorage()
    return layer.id
  }

  function addLayersFromGeojson(geojson, nameField) {
    const base = Date.now()
    const newLayers = geojson.features
      .map((feature, i) => {
        const bairro = (feature.properties?.[nameField] || '').trim()
        if (!bairro || !feature.geometry) return null
        return {
          id: `${base}_${i}`,
          name: bairro,
          bairro,
          geoJSON: { type: 'FeatureCollection', features: [feature] },
        }
      })
      .filter(Boolean)

    if (!newLayers.length) throw new Error('Nenhuma feature com geometria válida encontrada.')
    kmlLayers.value = [...kmlLayers.value, ...newLayers]
    saveToStorage()
    return newLayers.length
  }

  function removeLayer(id) {
    kmlLayers.value = kmlLayers.value.filter((l) => l.id !== id)
    saveToStorage()
  }

  function clearAll() {
    kmlLayers.value = []
    saveToStorage()
  }

  return { kmlLayers, addLayer, addLayersFromGeojson, removeLayer, clearAll }
}
