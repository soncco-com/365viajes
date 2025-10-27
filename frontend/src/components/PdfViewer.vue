<template>
  <q-dialog v-model="show" maximized>
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">{{ title }}</div>
        <q-space />

        <!-- Controles del PDF -->
        <div class="row q-gutter-sm items-center">
          <q-btn flat dense icon="zoom_out" @click="zoomOut" :disable="scale <= 0.5">
            <q-tooltip>Alejar</q-tooltip>
          </q-btn>

          <span class="text-body2">{{ Math.round(scale * 100) }}%</span>

          <q-btn flat dense icon="zoom_in" @click="zoomIn" :disable="scale >= 3">
            <q-tooltip>Acercar</q-tooltip>
          </q-btn>

          <q-separator vertical inset />

          <q-btn flat dense icon="print" @click="printPdf">
            <q-tooltip>Imprimir</q-tooltip>
          </q-btn>

          <q-btn flat dense icon="download" @click="downloadPdf">
            <q-tooltip>Descargar</q-tooltip>
          </q-btn>

          <q-btn flat dense icon="close" @click="close">
            <q-tooltip>Cerrar</q-tooltip>
          </q-btn>
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-pa-none pdf-container">
        <div v-if="loading" class="flex flex-center" style="height: 500px">
          <q-spinner-dots size="50px" color="primary" />
        </div>

        <div v-else-if="error" class="flex flex-center text-negative" style="height: 500px">
          <div class="text-center">
            <q-icon name="error" size="50px" />
            <p>{{ error }}</p>
          </div>
        </div>

        <div v-else ref="pdfContainer" class="pdf-viewer" :style="{ transform: `scale(${scale})` }">
          <canvas
            v-for="pageNum in numPages"
            :key="pageNum"
            :ref="(el) => (pageCanvases[pageNum - 1] = el)"
            class="pdf-page"
          ></canvas>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'

// Configurar worker de PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.js`

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  pdfUrl: {
    type: String,
    default: null,
  },
  pdfBlob: {
    type: Blob,
    default: null,
  },
  title: {
    type: String,
    default: 'Visualizador de PDF',
  },
  filename: {
    type: String,
    default: 'documento.pdf',
  },
})

const emit = defineEmits(['update:modelValue'])

const show = ref(props.modelValue)
const loading = ref(false)
const error = ref(null)
const pdfDoc = ref(null)
const numPages = ref(0)
const scale = ref(1.0)
const pageCanvases = ref([])
const pdfContainer = ref(null)

const loadPdf = async () => {
  if (!props.pdfUrl && !props.pdfBlob) return

  loading.value = true
  error.value = null

  try {
    let source

    if (props.pdfBlob) {
      const arrayBuffer = await props.pdfBlob.arrayBuffer()
      source = { data: arrayBuffer }
    } else {
      source = props.pdfUrl
    }

    const loadingTask = pdfjsLib.getDocument(source)
    pdfDoc.value = await loadingTask.promise
    numPages.value = pdfDoc.value.numPages

    await nextTick()
    await renderAllPages()
  } catch (err) {
    console.error('Error al cargar PDF:', err)
    error.value = 'Error al cargar el documento PDF'
  } finally {
    loading.value = false
  }
}

const renderAllPages = async () => {
  for (let pageNum = 1; pageNum <= numPages.value; pageNum++) {
    await renderPage(pageNum)
  }
}

const renderPage = async (pageNum) => {
  const page = await pdfDoc.value.getPage(pageNum)
  const canvas = pageCanvases.value[pageNum - 1]

  if (!canvas) return

  const viewport = page.getViewport({ scale: 1.5 })
  const context = canvas.getContext('2d')

  canvas.height = viewport.height
  canvas.width = viewport.width

  const renderContext = {
    canvasContext: context,
    viewport: viewport,
  }

  await page.render(renderContext).promise
}

const zoomIn = () => {
  if (scale.value < 3) {
    scale.value += 0.25
  }
}

const zoomOut = () => {
  if (scale.value > 0.5) {
    scale.value -= 0.25
  }
}

const printPdf = () => {
  if (props.pdfBlob) {
    const url = URL.createObjectURL(props.pdfBlob)
    const iframe = document.createElement('iframe')
    iframe.style.display = 'none'
    iframe.src = url
    document.body.appendChild(iframe)
    iframe.contentWindow.print()
  } else if (props.pdfUrl) {
    window.open(props.pdfUrl, '_blank')
  }
}

const downloadPdf = () => {
  if (props.pdfBlob) {
    const url = URL.createObjectURL(props.pdfBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = props.filename
    link.click()
    URL.revokeObjectURL(url)
  } else if (props.pdfUrl) {
    const link = document.createElement('a')
    link.href = props.pdfUrl
    link.download = props.filename
    link.click()
  }
}

const close = () => {
  show.value = false
}

// Watchers
watch(
  () => props.modelValue,
  (newVal) => {
    show.value = newVal
    if (newVal) {
      loadPdf()
    }
  },
)

watch(show, (newVal) => {
  emit('update:modelValue', newVal)
})

watch([() => props.pdfUrl, () => props.pdfBlob], () => {
  if (show.value) {
    loadPdf()
  }
})
</script>

<style lang="scss" scoped>
.pdf-container {
  height: calc(100vh - 100px);
  overflow: auto;
  background-color: #525659;
}

.pdf-viewer {
  transform-origin: top center;
  transition: transform 0.2s;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.pdf-page {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  background: white;
}
</style>
