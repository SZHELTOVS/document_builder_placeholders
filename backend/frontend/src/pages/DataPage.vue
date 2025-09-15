<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5 col">Наборы данных</div>
      <div class="col-auto">
        <q-btn label="Создать набор" color="primary" class="q-mr-sm" @click="openEditor()" />
        <q-btn label="Импорт из шаблона" color="secondary" @click="openImport()" />
      </div>
    </div>

    <q-list bordered class="q-mt-md">
      <q-item v-for="set in sets" :key="set.id" clickable>
        <q-item-section>
          <q-item-label>{{ set.title }}</q-item-label>
          <q-item-label caption>
            {{ (set.placeholders || []).map(p => p.name + '=' + (p.value ?? '')).join(', ') }}
          </q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn dense flat icon="description" color="secondary" @click="openExport(set)" />
          <q-btn dense flat icon="edit" @click.stop="openEditor(set)" />
          <q-btn dense flat icon="delete" color="negative" @click.stop="deleteSet(set.id)" />
        </q-item-section>
      </q-item>
    </q-list>

    <!-- Диалог создания/редактирования набора -->
    <q-dialog v-model="dialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ form.id ? 'Редактировать' : 'Создать' }} набор</div>
        </q-card-section>

        <q-card-section>
          <q-input v-model="form.title" label="Название набора" class="q-mb-md" />

          <div
            v-for="(ph, index) in form.placeholders"
            :key="index"
            class="row q-col-gutter-md q-mb-sm items-center"
          >
            <q-input v-model="ph.name" label="Имя" class="col-5" dense />
            <q-input v-model="ph.value" label="Значение" class="col-5" dense />
            <div class="col-2">
              <q-btn icon="delete" color="negative" flat dense @click="removePlaceholder(index)" />
            </div>
          </div>

          <q-btn flat icon="add" label="Добавить плейсхолдер"
                 @click="form.placeholders.push({name:'', value:''})" />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Отмена" v-close-popup />
          <q-btn flat label="Сохранить" color="primary" @click="saveSet" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Диалог импорта плейсхолдеров из шаблона -->
    <q-dialog v-model="importDialog">
      <q-card style="min-width: 520px">
        <q-card-section>
          <div class="text-h6">Импорт из шаблона DOCX</div>
        </q-card-section>

        <q-card-section>
          <q-select
            v-model="selectedDocId"
            :options="docOptions"
            option-value="id"
            option-label="name"
            emit-value
            map-options
            label="Выберите шаблон"
            outlined dense
          />
          <div class="text-caption q-mt-sm">
            Шаблоны берутся из списка /api/docs/ (те, что вы загружали).
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Отмена" v-close-popup />
          <q-btn :disable="!selectedDocId" flat color="secondary" label="Предзаполнить форму"
                 @click="importPlaceholders" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Диалог экспорта -->
    <q-dialog v-model="exportDialog">
      <q-card style="min-width: 520px">
        <q-card-section>
          <div class="text-h6">Выберите шаблон для экспорта</div>
        </q-card-section>

        <q-card-section>
          <q-select
            v-model="selectedExportDocId"
            :options="docOptions"
            option-value="id"
            option-label="name"
            emit-value
            map-options
            label="Шаблон"
            outlined dense
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Отмена" v-close-popup />
          <q-btn :disable="!selectedExportDocId" flat color="primary" label="Скачать DOCX"
                 @click="exportSet" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useQuasar } from "quasar"
import axios from "axios"

const $q = useQuasar()

// --- Наборы ---
const sets = ref([])

// --- Диалог редактирования/создания ---
const dialog = ref(false)
const form = ref({ id: null, title: "", placeholders: [] })

// --- Импорт ---
const importDialog = ref(false)
const selectedDocId = ref(null)
const docs = ref([])
const docOptions = ref([])

// --- Экспорт ---
const exportDialog = ref(false)
const selectedExportDocId = ref(null)
const selectedSetForExport = ref(null)

// ---------- Загрузка данных ----------
async function loadSets() {
  const res = await axios.get("/api/placeholder-sets/")
  sets.value = res.data
}

async function loadDocs() {
  const { data } = await axios.get("/api/docs/")
  docs.value = data || []
  docOptions.value = docs.value.map(d => ({ id: d.id, name: d.name }))
}

// ---------- Редактирование ----------
function openEditor(set = null) {
  if (set) {
    form.value = JSON.parse(JSON.stringify(set))
    if (!Array.isArray(form.value.placeholders)) form.value.placeholders = []
  } else {
    form.value = { id: null, title: "", placeholders: [] }
  }
  dialog.value = true
}

function removePlaceholder(idx) {
  form.value.placeholders.splice(idx, 1)
}

async function saveSet() {
  try {
    if (form.value.id) {
      await axios.put(`/api/placeholder-sets/${form.value.id}/`, form.value)
    } else {
      await axios.post(`/api/placeholder-sets/`, form.value)
    }
    dialog.value = false
    await loadSets()
    $q.notify({ type: "positive", message: "Набор сохранён" })
  } catch (e) {
    console.error(e)
    $q.notify({ type: "negative", message: "Ошибка сохранения" })
  }
}

async function deleteSet(id) {
  try {
    await axios.delete(`/api/placeholder-sets/${id}/`)
    await loadSets()
    $q.notify({ type: "positive", message: "Набор удалён" })
  } catch (e) {
    console.error(e)
    $q.notify({ type: "negative", message: "Ошибка удаления" })
  }
}

// ---------- Импорт ----------
function openImport() {
  importDialog.value = true
  selectedDocId.value = null
  if (!docs.value.length) loadDocs()
}

function dedupe(arr) {
  const seen = new Set()
  return arr.filter(x => {
    if (seen.has(x)) return false
    seen.add(x)
    return true
  })
}

async function importPlaceholders() {
  if (!selectedDocId.value) return
  try {
    const { data } = await axios.get(`/api/docs/${selectedDocId.value}/placeholders/`)
    const placeholders = data?.placeholders || []
    const simpleNames = dedupe(placeholders.filter(ph => typeof ph === "string").map(String))
    if (!simpleNames.length) {
      $q.notify({ type: "warning", message: "Простых плейсхолдеров не найдено" })
      return
    }

    const currentMap = new Map((form.value.placeholders || []).map(p => [p.name, p.value ?? ""]))
    form.value.placeholders = dedupe([...currentMap.keys(), ...simpleNames])
      .map(name => ({ name, value: currentMap.get(name) ?? "" }))

    if (!form.value.title) {
      const doc = docs.value.find(d => d.id === selectedDocId.value)
      if (doc?.name) form.value.title = `Набор: ${doc.name}`
    }

    importDialog.value = false
    dialog.value = true
    $q.notify({ type: "positive", message: `Импортировано полей: ${simpleNames.length}` })
  } catch (e) {
    console.error(e)
    $q.notify({ type: "negative", message: "Ошибка импорта плейсхолдеров" })
  }
}

// ---------- Экспорт ----------
function openExport(set) {
  selectedSetForExport.value = set
  selectedExportDocId.value = null
  if (!docs.value.length) loadDocs()
  exportDialog.value = true
}

async function exportSet() {
  if (!selectedExportDocId.value || !selectedSetForExport.value) return
  try {
    const url = `/api/docs/${selectedExportDocId.value}/render/`
    const response = await axios.post(url, { set_id: selectedSetForExport.value.id }, { responseType: "blob" })
    const blob = new Blob([response.data], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = "result.docx"
    link.click()
    $q.notify({ type: "positive", message: "Файл сформирован" })
    exportDialog.value = false
  } catch (e) {
    console.error(e)
    $q.notify({ type: "negative", message: "Ошибка при генерации файла" })
  }
}

onMounted(() => {
  loadSets()
})
</script>
