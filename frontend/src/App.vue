<template>
  <main class="mx-auto max-w-[1600px] p-4 md:p-6 lg:p-8">
    <header class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black tracking-tight md:text-5xl">WDEAL</h1>
        <p class="mt-1 text-slate-400">Web Data Editor, Analyzer and Learner</p>
      </div>
      <div class="flex flex-wrap gap-2 text-xs text-slate-300">
        <span class="rounded-full border border-slate-700 bg-slate-900 px-3 py-1">HTMX</span>
        <span class="rounded-full border border-slate-700 bg-slate-900 px-3 py-1">Vue</span>
        <span class="rounded-full border border-slate-700 bg-slate-900 px-3 py-1">Alpine</span>
        <span class="rounded-full border border-slate-700 bg-slate-900 px-3 py-1">Chart.js</span>
        <span class="rounded-full border border-slate-700 bg-slate-900 px-3 py-1">Motion One</span>
        <span class="rounded-full border border-slate-700 bg-slate-900 px-3 py-1">hyperscript</span>
      </div>
    </header>

    <div class="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
      <section class="rounded-[28px] border border-slate-800 bg-slate-900/80 p-4 shadow-2xl shadow-black/20 md:p-6">
        <div class="mb-4 flex items-center justify-between gap-3">
          <div>
            <h2 class="text-xl font-bold">Live editor</h2>
            <p class="text-sm text-slate-400">SQL / CSV / VBA are analyzed on every change.</p>
          </div>
          <div class="flex gap-2">
            <button class="rounded-xl bg-slate-700 px-4 py-2 text-sm font-semibold hover:bg-slate-600" @click="loadDemo">Load demo</button>
            <button class="rounded-xl bg-slate-700 px-4 py-2 text-sm font-semibold hover:bg-slate-600" @click="clearAll">Clear</button>
          </div>
        </div>

        <form
          id="wdeal-form"
          class="space-y-4"
          hx-post="`${API_URL}/api/analyze`"
          hx-trigger="load, input changed delay:450ms from:textarea, change from:select, change from:input[type='checkbox']"
          hx-target="#analysis-panel"
          hx-swap="innerHTML"
        >
          <div class="grid gap-4 2xl:grid-cols-3">
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-300">SQL</label>
              <textarea
                id="sql_text"
                name="sql_text"
                v-model="sqlText"
                class="min-h-64 w-full rounded-2xl border border-slate-700 bg-slate-950 p-4 font-mono text-sm leading-6 text-slate-100 outline-none focus:border-blue-500"
              ></textarea>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-300">CSV</label>
              <textarea
                id="csv_text"
                name="csv_text"
                v-model="csvText"
                class="min-h-64 w-full rounded-2xl border border-slate-700 bg-slate-950 p-4 font-mono text-sm leading-6 text-slate-100 outline-none focus:border-blue-500"
              ></textarea>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-300">VBA</label>
              <textarea
                id="vba_text"
                name="vba_text"
                v-model="vbaText"
                class="min-h-64 w-full rounded-2xl border border-slate-700 bg-slate-950 p-4 font-mono text-sm leading-6 text-slate-100 outline-none focus:border-blue-500"
              ></textarea>
            </div>
          </div>

          <div class="grid gap-4 rounded-2xl border border-slate-800 bg-slate-950/80 p-4 md:grid-cols-[1fr_1fr_auto]">
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-300">Chart mode</label>
              <ModePills v-model="chartMode" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <label class="space-y-2">
                <span class="text-sm font-medium text-slate-300">Preview rows</span>
                <input
                  name="max_rows"
                  v-model.number="maxRows"
                  type="number"
                  min="1"
                  max="200"
                  class="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-blue-500"
                />
              </label>
              <div class="flex items-end gap-3 pb-1">
                <label class="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200">
                  <input name="show_legend" type="checkbox" v-model="showLegend" />
                  Legend
                </label>
                <label class="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200">
                  <input name="show_grid" type="checkbox" v-model="showGrid" />
                  Grid
                </label>
              </div>
            </div>
            <div class="flex items-end justify-end gap-2">
              <button type="button" class="rounded-2xl bg-emerald-600 px-4 py-3 font-semibold text-white hover:bg-emerald-500" @click="download('csv')">CSV</button>
              <button type="button" class="rounded-2xl bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-500" @click="download('xlsx')">XLSX</button>
              <button type="button" class="rounded-2xl bg-violet-600 px-4 py-3 font-semibold text-white hover:bg-violet-500" @click="download('xlsm')">XLSM</button>
            </div>
          </div>
        </form>
      </section>

      <section class="rounded-[28px] border border-slate-800 bg-slate-900/80 p-4 shadow-2xl shadow-black/20 md:p-6">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">Analysis</h2>
            <p class="text-sm text-slate-400">Server-rendered fragment swapped by HTMX.</p>
          </div>
          <div class="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300">
            <span class="font-semibold text-slate-100">{{ summaryText }}</span>
          </div>
        </div>
        <div id="analysis-panel" class="min-h-[720px] rounded-[24px] border border-slate-800 bg-slate-950/60 p-4">
          <div class="text-slate-400">Loading analysis…</div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import ModePills from './components/ModePills'
import { mountChart } from './lib/charts'
import type { AnalysisPayload } from './lib/types'
const sqlText = ref(`SELECT * FROM input_data`)
const csvText = ref(`name,department,score,city
Aki,Sales,91,Tokyo
Mika,Engineering,88,Osaka
Jun,Marketing,95,Nagoya
`)
const vbaText = ref(`Option Explicit

Public Sub NormalizeValues()
    Dim i As Integer
    For i = 1 To 10
        If i Mod 2 = 0 Then
            Debug.Print i
        End If
    Next i
End Sub
`)
const chartMode = ref<'completeness' | 'missing' | 'types'>('completeness')
const maxRows = ref(25)
const showLegend = ref(true)
const showGrid = ref(true)

const summaryText = computed(() => {
  return `${chartMode.value} · ${maxRows.value} rows`
})

function loadDemo() {
  sqlText.value = `SELECT department, AVG(score) AS avg_score, COUNT(*) AS people
FROM input_data
GROUP BY department
ORDER BY avg_score DESC`
  csvText.value = `name,department,score,city,active
Aki,Sales,91,Tokyo,true
Mika,Engineering,88,Osaka,true
Jun,Marketing,95,Nagoya,true
Ren,Sales,84,Tokyo,false
`
  vbaText.value = `Option Explicit

Private Function RankScore(ByVal value As Double) As String
    If value >= 90 Then
        RankScore = "A"
    ElseIf value >= 80 Then
        RankScore = "B"
    Else
        RankScore = "C"
    End If
End Function`
  triggerAnalyze()
}

function clearAll() {
  sqlText.value = ''
  csvText.value = ''
  vbaText.value = ''
  triggerAnalyze()
}

function buildFormData(): FormData {
  const formData = new FormData()
  formData.set('sql_text', sqlText.value)
  formData.set('csv_text', csvText.value)
  formData.set('vba_text', vbaText.value)
  formData.set('chart_mode', chartMode.value)
  formData.set('max_rows', String(maxRows.value))
  if (showLegend.value) formData.set('show_legend', 'on')
  if (showGrid.value) formData.set('show_grid', 'on')
  return formData
}

async function download(kind: 'csv' | 'xlsx' | 'xlsm') {
  const response = await fetch(`${API_URL}/api/export/${kind}`, {
    method: 'POST',
    body: buildFormData(),
  })
  if (!response.ok) {
    window.alert(`Export failed: ${response.status}`)
    return
  }
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `wdeal-export.${kind}`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function triggerAnalyze() {
  window.htmx?.trigger('#wdeal-form', 'input')
}

function installChartAfterSwap() {
  document.body.addEventListener('htmx:afterSwap', async (evt: any) => {
    const target = evt?.detail?.target
    if (!target || target.id !== 'analysis-panel') return

    await nextTick()
    const script = document.getElementById('wdeal-analysis-json')
    const canvas = document.getElementById('wdeal-chart') as HTMLCanvasElement | null
    if (!script || !canvas) return

    const payload = JSON.parse(script.textContent || '{}') as AnalysisPayload
    mountChart(canvas, payload)

    if (window.motion) {
      try {
        window.motion.animate(target, { opacity: [0, 1], y: [12, 0] }, { duration: 0.24 })
      } catch {
        // no-op
      }
    }
  })
}

onMounted(() => {
  installChartAfterSwap()
  triggerAnalyze()
})
</script>
