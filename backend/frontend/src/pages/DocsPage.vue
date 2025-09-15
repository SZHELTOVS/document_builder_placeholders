<template>

  <q-page class="q-pa-md">

    <!-- Заголовок -->
    <div class="row items-center q-mb-md">
      <div class="col text-h6">Список шаблонов</div>
      <div class="col-auto">
        <q-btn icon="add" color="primary" label="Добавить шаблон" @click="showUploadCard = true" />
      </div>
    </div>

    <!-- Список шаблонов -->
    <q-list bordered separator>
      <q-item v-for="doc in docs" :key="doc.id" clickable v-ripple>
        <q-item-section @click="selectDoc(doc)">
          {{ doc.name }}
        </q-item-section>
        <q-item-section side class="row items-center">
          <span>{{ doc.uploaded_at }}</span>
          <q-btn dense flat round icon="delete" color="negative" 
                 @click.stop="deleteDoc(doc.id)" class="q-ml-sm" />
        </q-item-section>
      </q-item>
    </q-list>

    <!-- Карточка загрузки нового документа -->
    <q-card v-if="showUploadCard" flat bordered class="q-pa-md q-mt-md bg-grey-1">
      <q-card-section>
        <div class="text-h5 text-primary">Загрузка документа</div>

        <q-file
          v-model="file"
          label="Выберите .docx файл"
          accept=".docx"
          outlined
          dense
          use-chips
          class="q-mt-md"
        />

        <q-btn
          label="Загрузить"
          icon="upload"
          color="primary"
          class="q-mt-sm"
          :disable="!file"
          @click="upload"
        />

        <q-btn
          label="Отмена"
          icon="close"
          color="negative"
          flat
          class="q-mt-sm q-ml-sm"
          @click="showUploadCard = false"
        />
      </q-card-section>
    </q-card>

    <!-- Форма заполнения выбранного шаблона -->
    <q-card v-if="placeholders.length" flat bordered class="q-pa-md q-mt-xl">
      <q-card-section>
        <div class="text-h6 text-primary">Заполните данные</div>

        <div v-for="(ph, idx) in placeholders" :key="typeof ph === 'string' ? ph + idx : ph.name + idx">
          <div v-if="typeof ph === 'string'">
            <q-input outlined v-model="values[ph]" :label="formatLabel(ph)" dense class="q-my-sm"/>
          </div>

          <div v-else-if="ph.type === 'table'" class="q-mt-md">
            <div class="text-subtitle1 q-mb-sm">{{ formatLabel(ph.name) }}</div>
            <q-table
              flat bordered
              :rows="values[ph.name]"
              :columns="getTableColumns(ph.columns)"
              :row-key="(row, index) => index"
              hide-bottom dense
            >
              <template v-for="col in ph.columns" :key="col.name" v-slot:[`body-cell-${col.name}`]="props">
                <q-td :props="props">
                  <q-input v-model="props.row[col.name]" dense outlined hide-bottom-space />
                </q-td>
              </template>
              <template v-slot:body-cell-actions="props">
                <q-td class="text-center">
                  <q-btn color="negative" icon="delete" flat dense round @click="removeRow(ph.name, props.rowIndex)" />
                </q-td>
              </template>
            </q-table>
            <q-btn label="Добавить строку" color="primary" class="q-mt-sm" @click="() => addRow(ph.name, ph.columns)"/>
          </div>
        </div>

        <q-btn label="Заполнить документ" icon="done" color="positive" class="q-mt-lg" @click="fillDoc"/>
      </q-card-section>
    </q-card>

  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

const $q = useQuasar()

const showUploadCard = ref(false)
const file = ref(null)
const fileId = ref(null)
const placeholders = ref([])
const values = ref({})
const docs = ref([])

function formatLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function getTableColumns(columns) {
  return [
    ...columns.map(col => ({ name: col.name, label: formatLabel(col.label || col.name), align: 'left', field: col.name })),
    { name: 'actions', label: '', align: 'center' }
  ]
}

function addRow(tableName, columns) {
  if (!values.value[tableName]) values.value[tableName] = []
  const row = {}
  for (const col of columns) row[col.name] = ''
  values.value[tableName] = [...values.value[tableName], row]
}

function removeRow(tableName, index) {
  values.value[tableName] = values.value[tableName].filter((_, i) => i !== index)
}

async function loadDocs() {
  try {
    const { data } = await axios.get('/api/docs/')
    docs.value = data.map(d => ({
      id: d.id,
      name: d.name,
      uploaded_at: d.uploaded_at,
      placeholders: []
    }))
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Ошибка загрузки шаблонов' })
  }
}

async function deleteDoc(docId) {
  try {
    await axios.delete(`/api/docs/${docId}/delete/`)
    docs.value = docs.value.filter(d => d.id !== docId)
    $q.notify({ type: 'positive', message: 'Шаблон удалён' })
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Ошибка при удалении шаблона' })
  }
}

async function selectDoc(doc) {
  fileId.value = doc.id
  try {
    const { data } = await axios.get(`/api/docs/${doc.id}/placeholders/`)
    placeholders.value = data.placeholders || []

    const newValues = {}
    for (const ph of placeholders.value) {
      if (typeof ph === 'string') newValues[ph] = ''
      else if (ph.type === 'table') {
        newValues[ph.name] = [Object.fromEntries(ph.columns.map(c => [c.name, '']))]
      }
    }
    values.value = newValues
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Ошибка загрузки шаблона' })
  }
}

async function upload() {
  if (!file.value) return
  const formData = new FormData()
  formData.append('file', file.value)
  try {
    const { data } = await axios.post('/api/upload/', formData)
    fileId.value = data.file_id
    placeholders.value = data.placeholders || []

    const newValues = {}
    for (const ph of placeholders.value) {
      if (typeof ph === 'string') newValues[ph] = ''
      else if (ph.type === 'table') newValues[ph.name] = [Object.fromEntries(ph.columns.map(c => [c.name, '']))]
    }
    values.value = newValues
    showUploadCard.value = false
    await loadDocs()
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Ошибка загрузки файла' })
  }
}

async function fillDoc() {
  try {
    const { data } = await axios.post(
      '/api/fill/',
      { file_id: fileId.value, values: values.value },
      { responseType: 'blob' }
    )
    const url = URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'filled.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error(err)
    $q.notify({ type: 'negative', message: 'Ошибка при заполнении документа' })
  }
}

onMounted(() => {
  loadDocs()
})
</script>
