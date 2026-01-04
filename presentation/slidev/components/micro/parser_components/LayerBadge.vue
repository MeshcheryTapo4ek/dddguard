<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  type: 
    | 'DOMAIN' | 'APP' 
    | 'ADAPT_IN' | 'ADAPT_OUT' 
    | 'PORT_IN' | 'PORT_OUT' 
    | 'DTO_IN' | 'DTO_OUT' 
    | 'COMPOSITION' | 'ROOT' | 'OTHER'
}>()

const styles = computed(() => {
  const map: Record<string, string> = {
    DOMAIN: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    APP: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    
    ADAPT_IN: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    PORT_IN: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    DTO_IN: 'bg-orange-500/10 text-orange-400 border-orange-500/20',

    ADAPT_OUT: 'bg-green-500/10 text-green-400 border-green-500/20',
    PORT_OUT: 'bg-green-500/10 text-green-400 border-green-500/20',
    DTO_OUT: 'bg-green-500/10 text-green-400 border-green-500/20',

    COMPOSITION: 'bg-red-500/10 text-red-400 border-red-500/20',
    ROOT: 'bg-red-500/10 text-red-400 border-red-500/20',
    OTHER: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  }
  return map[props.type] || map.OTHER
})

const labels: Record<string, string> = {
    DOMAIN: 'DOMAIN', APP: 'APP',
    ADAPT_IN: 'ADAPTER (Driving)', ADAPT_OUT: 'ADAPTER (Driven)',
    PORT_IN: 'PORT (Driving)', PORT_OUT: 'PORT (Driven)',
    DTO_IN: 'DTO (Driving)', DTO_OUT: 'DTO (Driven)',
    COMPOSITION: 'COMPOSITION', ROOT: 'ROOT', OTHER: 'OTHER'
}
</script>

<template>
  <span 
    class="px-2 py-1 rounded border font-mono text-[10px] font-bold tracking-wider inline-block whitespace-nowrap shadow-sm"
    :class="styles"
  >
    {{ labels[type] }}
  </span>
</template>