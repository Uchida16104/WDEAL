export interface AnalysisColumn {
  name: string
  dtype: string
  non_null: number
  missing: number
  unique: number
  sample: Array<string | number | boolean | null>
  null_ratio: number
}

export interface AnalysisPayload {
  summary: {
    rows: number
    columns: number
    missing_cells: number
    duplicate_rows: number
    memory_bytes: number
    dtype_distribution: Record<string, number>
  }
  columns: AnalysisColumn[]
  preview_rows: Array<Record<string, unknown>>
  preview_columns: string[]
  preview_shape: { rows: number; columns: number }
  numeric_summary: Record<string, Record<string, unknown>>
  missing_by_column: Array<{ column: string; missing: number; null_ratio: number }>
  chart: {
    type: 'bar' | 'doughnut'
    labels: string[]
    values: number[]
    dataset_label: string
    show_legend: boolean
    show_grid: boolean
    show_nulls: boolean
  }
  chart_mode: 'completeness' | 'missing' | 'types'
  sql: {
    query_kind: string
    statement_count: number
    token_count: number
    keywords: string[]
  }
  vba: {
    line_count: number
    non_empty_lines: number
    blank_lines: number
    character_count: number
    procedure_count: number
    procedure_names: string[]
    attribute_count: number
    attributes: string[]
    comment_lines: number
    on_error_count: number
    top_identifiers: Array<{ name: string; count: number }>
    indentation: { max_indent: number; avg_indent: number }
    complexity_signals: Record<string, number>
    complexity_score: number
  }
  errors: string[]
  result_csv: string
  source_rows: number
  source_columns: number
}
