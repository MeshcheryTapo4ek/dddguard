<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  subtitle: string
  icon?: string
  description: string
  rules: string[]
  folders: string[]
  regex: string[]
  codeFileName: string
  code: string
}>()

// --- REGEX HIGHLIGHTER (Logic Kept Same) ---
const highlightedCode = computed(() => {
  if (!props.code) return ''
  let c = props.code.trim()
  c = c.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  const placeholders: string[] = []
  const push = (html: string) => { 
    placeholders.push(html)
    return `%%%${placeholders.length - 1}%%%` 
  }
  c = c.replace(/(#.*$)/gm, (match) => push(`<span class="text-gray-500 italic font-normal">${match}</span>`))
  c = c.replace(/('.*?')/g, (match) => push(`<span class="text-green-400">${match}</span>`))
  c = c.replace(/(".*?")/g, (match) => push(`<span class="text-green-400">${match}</span>`))
  
  const keywords = ['def', 'class', 'return', 'if', 'else', 'elif', 'raise', 'import', 'from', 'as', 'pass', 'try', 'except', 'async', 'await', 'dataclass', 'field']
  c = c.replace(new RegExp(`\\b(${keywords.join('|')})\\b`, 'g'), '<span class="text-purple-400 font-bold">$1</span>')

  const types = ['str', 'int', 'bool', 'None', 'list', 'dict', 'Optional', 'Decimal', 'UUID', 'datetime', 'True', 'False', 'AggregateRoot', 'DomainEvent', 'Money', 'Currency', 'CourierID', 'CourierStatus', 'Coordinates', 'Order', 'OrderLine', 'Product', 'Exception']
  c = c.replace(new RegExp(`\\b(${types.join('|')})\\b`, 'g'), '<span class="text-teal-300">$1</span>')

  c = c.replace(/(@[\w]+)/g, '<span class="text-yellow-400">$1</span>')
  c = c.replace(/\b(self)\b/g, '<span class="text-red-400 opacity-80 italic">$1</span>')
  c = c.replace(/%%%(\d+)%%%/g, (_, i) => placeholders[parseInt(i)])
  return c
})
</script>

<template>
  <div class="h-full w-full bg-[#0B0F19] grid grid-cols-[280px_1fr] font-sans text-gray-300 relative overflow-hidden">
    
    <div class="absolute -left-20 top-20 w-[300px] h-[300px] bg-blue-600/10 rounded-full blur-[80px] pointer-events-none"></div>

    <div class="flex flex-col h-full border-r border-gray-800/60 bg-[#0B0F19]/80 backdrop-blur-sm relative z-10">
      
      <div class="p-5 border-b border-gray-800/60 bg-gradient-to-b from-[#111318] to-transparent">
        <div class="flex items-center gap-3 mb-3">
          <div class="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.15)]">
             <div :class="icon || 'i-carbon-cube'" class="text-2xl" />
          </div>
          <div class="flex flex-col">
             <span class="text-[10px] font-mono text-blue-500 uppercase tracking-widest font-bold leading-none mb-1">{{ subtitle }}</span>
             <h1 class="text-2xl font-black text-white leading-none tracking-tight">{{ title }}</h1>
          </div>
        </div>
        
        <div class="flex flex-wrap gap-1.5 mt-2">
            <span v-for="f in folders" :key="f" class="px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 border border-gray-700 font-mono text-[8px] leading-none">/{{ f }}/</span>
            <span v-for="r in regex" :key="r" class="px-1.5 py-0.5 rounded bg-gray-800 text-gray-500 border border-gray-700 font-mono text-[8px] leading-none italic">{{ r }}</span>
        </div>
      </div>

      <div class="flex-1 flex flex-col p-5 overflow-y-auto custom-scroll gap-6">
        
        <div>
           <div class="text-[9px] font-bold text-gray-600 uppercase tracking-widest mb-2">Definition</div>
           <p class="text-[11px] leading-[1.6] text-gray-300 font-light text-justify">
              {{ description }}
           </p>
        </div>

        <div class="mt-auto">
            <div class="text-[9px] font-bold text-gray-600 uppercase tracking-widest mb-2 flex items-center gap-2">
               Strict Invariants
            </div>
            <ul class="flex flex-col gap-2">
                <li v-for="(rule, idx) in rules" :key="idx" 
                    class="flex items-start gap-2 p-2 rounded bg-[#151926] border border-gray-800/50">
                    <div class="i-carbon-checkmark-filled text-blue-500 text-[10px] mt-0.5 shrink-0" />
                    <span class="text-[10px] text-gray-300 leading-snug">{{ rule }}</span>
                </li>
            </ul>
        </div>

      </div>
    </div>

    <div class="relative bg-[#0d0f14] flex flex-col h-full min-h-0">
        
        <div class="flex items-center justify-between px-4 py-2 bg-[#111] border-b border-gray-800 shrink-0 z-20">
           <div class="flex items-center gap-2">
               <div class="flex gap-1.5">
                  <div class="w-2 h-2 rounded-full bg-red-500/20"></div>
                  <div class="w-2 h-2 rounded-full bg-yellow-500/20"></div>
                  <div class="w-2 h-2 rounded-full bg-green-500/20"></div>
               </div>
               <span class="text-[10px] font-mono text-gray-500 ml-2 border-l border-gray-800 pl-2">{{ codeFileName }}</span>
           </div>
           <div class="text-[9px] font-mono text-blue-500/50">READ-ONLY</div>
        </div>

        <div class="flex-1 overflow-auto custom-scroll relative">
           <div class="absolute inset-0 p-5">
              <pre class="font-mono text-[11px] leading-[1.65] text-gray-300 whitespace-pre" v-html="highlightedCode"></pre>
           </div>
        </div>
        
        <div class="absolute bottom-3 right-5 pointer-events-none z-20">
            <span class="text-[9px] font-mono font-bold text-gray-700 tracking-[0.2em] uppercase">Python 3.10+</span>
        </div>
    </div>

  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 4px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 2px;
}
.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: #444;
}
</style>