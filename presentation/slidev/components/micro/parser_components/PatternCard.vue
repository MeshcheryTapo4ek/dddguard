<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  patterns: string[]
  variant: 'domain' | 'app' | 'driving' | 'driven' | 'root' | 'other'
}>()

const colors = computed(() => {
  const map = {
    domain: 'border-blue-500/30 bg-blue-500/5 text-blue-300',
    app: 'border-purple-500/30 bg-purple-500/5 text-purple-300',
    driving: 'border-orange-500/30 bg-orange-500/5 text-orange-300',
    driven: 'border-green-500/30 bg-green-500/5 text-green-300',
    root: 'border-red-500/30 bg-red-500/5 text-red-300',
    other: 'border-gray-500/30 bg-gray-500/5 text-gray-300',
  }
  return map[props.variant]
})
</script>

<template>
  <div class="rounded-lg border p-3 flex flex-col gap-2 min-w-[140px]" :class="colors">
    <div class="text-[10px] uppercase tracking-widest font-bold opacity-70 border-b border-white/5 pb-1 mb-1">
      {{ label }}
    </div>
    <div class="flex flex-col gap-1.5">
      <code 
        v-for="p in patterns" :key="p"
        class="bg-[#0B0F19]/80 px-1.5 py-0.5 rounded text-[10px] font-mono border border-white/5"
      >
        {{ p }}
      </code>
    </div>
  </div>
</template>