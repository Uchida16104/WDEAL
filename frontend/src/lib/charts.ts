import type { AnalysisPayload } from './types'

export function createChartConfig(payload: AnalysisPayload) {
  return {
    type: payload.chart.type,
    data: {
      labels: payload.chart.labels,
      datasets: [
        {
          label: payload.chart.dataset_label,
          data: payload.chart.values,
          borderWidth: 2,
          tension: 0.35,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: payload.chart.show_legend },
      },
      scales: payload.chart.type === 'doughnut'
        ? {}
        : {
            x: { grid: { display: payload.chart.show_grid } },
            y: { grid: { display: payload.chart.show_grid }, beginAtZero: true },
          },
    },
  }
}

export function mountChart(canvas: HTMLCanvasElement, payload: AnalysisPayload) {
  if (window.__wdealChart) {
    window.__wdealChart.destroy()
  }
  const context = canvas.getContext('2d')
  if (!context || !window.Chart) return
  window.__wdealChart = new window.Chart(context, createChartConfig(payload))
}
