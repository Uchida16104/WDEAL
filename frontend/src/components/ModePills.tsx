import { defineComponent, h } from 'vue'

export default defineComponent({
  name: 'ModePills',
  props: {
    modelValue: {
      type: String,
      required: true,
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const options = [
      { value: 'completeness', label: 'Completeness' },
      { value: 'missing', label: 'Missing cells' },
      { value: 'types', label: 'Column types' },
    ]

    return () =>
      h(
        'div',
        { class: 'flex flex-wrap gap-2' },
        options.map((opt) =>
          h(
            'button',
            {
              type: 'button',
              onClick: () => emit('update:modelValue', opt.value),
              class:
                'rounded-full border px-3 py-2 text-sm transition ' +
                (props.modelValue === opt.value
                  ? 'border-blue-400 bg-blue-500/20 text-blue-200'
                  : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500'),
            },
            opt.label,
          ),
        ),
      )
  },
})
