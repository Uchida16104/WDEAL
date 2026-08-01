/// <reference types="vite/client" />

declare global {
  interface Window {
    htmx?: any
    Chart?: any
    motion?: any
    __wdealChart?: any
    wdealDownload?: (kind: 'csv' | 'xlsx' | 'xlsm') => Promise<void>
  }
}
export {}
