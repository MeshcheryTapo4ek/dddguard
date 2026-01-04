<script setup lang="ts">
import { computed } from 'vue'
import { $slidev } from '@slidev/client'

// 0: Layer Detection, 1: Folder Exact Match, 2: Regex Loop
const step = computed(() => $slidev.nav.clicks || 0)

// Конфигурация для каждого шага
const phases = [
  {
    id: 0,
    title: 'LAYER DETECTION',
    subtitle: 'Narrowing the scope',
    fileContext: 'src/logistics/domain/services/...',
    activeTree: 'domain',
    // Код для определения слоя
    code: [
      { text: 'def detect_layer(path: Path) -> Layer:', indent: 0, color: 'text-purple-400' },
      { text: '# 1. Split path into segments', indent: 2, color: 'text-gray-500' },
      { text: 'parts = path.split(os.sep)', indent: 2, color: 'text-gray-300' },
      { text: '', indent: 0, color: '' },
      { text: '# 2. Check against top-level keywords', indent: 2, color: 'text-gray-500' },
      { text: 'if "domain" in parts: return Layer.DOMAIN', indent: 2, color: 'text-blue-400 font-bold bg-blue-500/10' },
      { text: 'if "app" in parts: return Layer.APP', indent: 2, color: 'text-gray-400' },
      { text: 'if "adapters" in parts:', indent: 2, color: 'text-gray-400' },
        { text: 'get_direction_adapters(parts)', indent: 4, color: 'text-green-500/80' },
      { text: 'if "ports" in parts:', indent: 2, color: 'text-gray-400' },
        { text: 'get_direction_ports(parts)', indent: 4, color: 'text-green-500/80' },
      { text: 'if "dto" in parts:', indent: 2, color: 'text-gray-400' },
        { text: 'return get_direction_dto(parts)', indent: 4, color: 'text-green-500/80' },

    ]
  },
  {
    id: 1,
    title: 'FOLDER LOOKUP',
    subtitle: 'Context-Aware Dictionary',
    fileContext: '.../domain/aggregates/Order.py',
    activeTree: 'folder',
    code: [
      { text: 'def resolve_by_folder(folder: str, layer: Optional[Layer]):', indent: 0, color: 'text-purple-400' },
      { text: '# 1. Load patterns ONLY for this layer', indent: 2, color: 'text-gray-500' },
      { text: 'patterns = FoldersRegistry.filter(layer)', indent: 2, color: 'text-blue-300' },
      { text: '', indent: 0, color: '' },
      { text: '# 2. Exact O(1) Lookup', indent: 2, color: 'text-gray-500' },
      { text: '# Domain: { "aggregates": TYPE.AGGREGATE, ... }', indent: 2, color: 'text-green-500/50 italic' },
      { text: 'if folder in patterns:', indent: 2, color: 'text-purple-400' },
      { text: 'return patterns[folder]', indent: 4, color: 'text-green-400 font-bold' },
      { text: '', indent: 0, color: '' },
      { text: 'return None # Fallback to Regex', indent: 2, color: 'text-gray-500' },
    ]
  },
  {
    id: 2,
    title: 'REGEX MATCHING',
    subtitle: 'Priority-based Loop',
    fileContext: '.../driven/postgres/sql_order_repository.py',
    activeTree: 'file',
    // Код для регексов (сложная логика)
    code: [
      { text: 'def resolve_by_name(filename: str, layer: Layer):', indent: 0, color: 'text-purple-400' },
      { text: 'name = strip_extension(filename)', indent: 2, color: 'text-gray-400' },
      { text: '', indent: 0, color: '' },
      { text: '# 1. Get Regexes (Driven Side)', indent: 2, color: 'text-gray-500' },
      { text: 'regexes = Registry.regexes.get(layer)', indent: 2, color: 'text-blue-300' },
      { text: '', indent: 0, color: '' },
      { text: '# 2. Sort: Specifics (Longer) first', indent: 2, color: 'text-gray-500' },
      { text: 'regexes.sort(key=lambda r: len(r.pattern), reverse=True)', indent: 2, color: 'text-yellow-400' },
      { text: '', indent: 0, color: '' },
      { text: '# 3. First Match Wins', indent: 2, color: 'text-gray-500' },
      { text: 'for r in regexes:', indent: 2, color: 'text-purple-400' },
      { text: 'if r.match(name): return r.type', indent: 4, color: 'text-green-400 font-bold' },
    ]
  }
]
</script>

<template>
  <div class="h-full w-full flex flex-col font-mono text-[10px] leading-4 text-gray-400">
    
    <div class="mb-2 shrink-0 flex items-baseline justify-between border-b border-gray-800 pb-2">
        <div class="flex items-baseline gap-3">
            <h1 class="text-2xl font-bold text-white font-sans">Parsing Logic</h1>
            <span class="text-gray-600 font-sans text-xs">/ Context-Aware Strategy</span>
        </div>
        <div class="flex gap-1">
            <div v-for="(p, idx) in phases" :key="p.id" 
                 class="px-2 py-0.5 rounded border transition-all duration-300"
                 :class="step === idx ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'border-transparent text-gray-700 opacity-50'">
                0{{ idx + 1 }}. {{ p.title }}
            </div>
        </div>
    </div>

    <div class="grid grid-cols-[1.2fr_1.8fr] gap-4 h-full min-h-0">
        
        <div class="bg-[#0f1115] rounded-lg border border-gray-800 p-3 shadow-inner flex flex-col relative overflow-hidden transition-all duration-500">
            <div class="text-gray-500 mb-3 border-b border-gray-800 pb-1 flex justify-between items-center shrink-0">
                <span class="text-white font-bold text-[10px]">FILE SYSTEM</span>
                <span class="text-[8px] bg-gray-700/30 text-gray-400 px-1.5 rounded border border-gray-700/50">{{ phases[step].fileContext }}</span>
            </div>

            <div class="flex-1 flex flex-col gap-1.5 pl-2 relative">
                
                <div class="flex items-center text-gray-500"><span class="w-4">├─</span> src/</div>
                <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 flex flex-col gap-1.5">
                    <div class="flex items-center text-gray-500"><span class="w-4">├─</span> logistics/</div>
                    
                    <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 flex flex-col gap-1.5">
                        
                        <div v-if="step === 0" class="group transition-all duration-300">
                             <div class="flex items-center bg-blue-500/10 -mx-2 px-2 py-1 rounded border border-blue-500/20">
                                <span class="tree-dash text-blue-500">├─</span> 
                                <span class="text-blue-400 font-bold">domain/</span>
                                <span class="ml-auto text-[8px] text-blue-300 opacity-70"><- DETECT LAYER</span>
                             </div>
                             <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 mt-1.5 opacity-40">
                                <div class="tree-item"><span class="tree-dash">├─</span> services/</div>
                                <div class="tree-item"><span class="tree-dash">└─</span> CostCalculator.py</div>
                             </div>
                        </div>

                        <div v-else-if="step === 1" class="group transition-all duration-300">
                             <div class="flex items-center opacity-50"><span class="tree-dash">├─</span> domain/</div>
                             <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 mt-1.5">
                                <div class="flex items-center bg-purple-500/10 -mx-2 px-2 py-1 rounded border border-purple-500/20">
                                    <span class="tree-dash text-purple-500">├─</span> 
                                    <span class="text-purple-400 font-bold">aggregates/</span>
                                    <span class="ml-auto text-[8px] text-purple-300 opacity-70"><- KNOWN FOLDER</span>
                                </div>
                                <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 mt-1.5 opacity-40">
                                    <div class="tree-item"><span class="tree-dash">└─</span> Order.py</div>
                                </div>
                             </div>
                        </div>

                        <div v-else class="group transition-all duration-300">
                             <div class="flex items-center opacity-30"><span class="tree-dash">└─</span> adapters/</div>
                             <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 mt-1.5">
                                <div class="flex items-center opacity-50"><span class="tree-dash">└─</span> driven/</div>
                                <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 mt-1.5">
                                     <div class="flex items-center opacity-70"><span class="tree-dash">└─</span> postgres/ <span class="text-[8px] ml-2 text-red-500 italic">(unknown)</span></div>
                                     <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5 mt-1.5">
                                         <div class="flex items-center bg-green-500/10 -mx-2 px-2 py-1 rounded border border-green-500/20">
                                            <span class="tree-dash text-green-500">└─</span> 
                                            <span class="text-green-400 font-bold">sql_order_repository.py</span>
                                            <span class="ml-auto text-[8px] text-green-300 opacity-70"><- REGEX TARGET</span>
                                         </div>
                                     </div>
                                </div>
                             </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>

        <div class="bg-[#111] rounded-lg border border-gray-800 p-3 shadow-inner flex flex-col relative">
            <div class="text-gray-500 mb-3 border-b border-gray-800 pb-1 flex justify-between items-center shrink-0">
                 <span class="text-white font-bold text-[10px]">core/parser.py</span>
                 <span class="text-[8px] bg-blue-900/30 text-blue-300 px-1.5 rounded border border-blue-500/20">
                    {{ phases[step].subtitle }}
                 </span>
            </div>

            <div class="flex-1 font-mono text-[11px] leading-6 overflow-hidden relative">
                <transition mode="out-in" name="fade">
                    <div :key="step" class="flex flex-col">
                        <div v-for="(line, i) in phases[step].code" :key="i"
                             class="whitespace-pre flex"
                             :class="line.color">
                             <span class="w-6 text-gray-700 select-none text-right mr-3 text-[9px] pt-0.5">{{ i + 1 }}</span>
                             <span :style="{ paddingLeft: line.indent + 'ch' }">{{ line.text }}</span>
                        </div>
                    </div>
                </transition>
            </div>

            <div class="mt-auto pt-3 border-t border-gray-800">
                <div v-if="step === 0" class="flex items-center gap-2 text-[10px]">
                    <span class="text-gray-500">Input:</span> <span class="text-gray-300">.../domain/...</span>
                    <span class="text-gray-600">-></span>
                    <span class="text-blue-400 font-bold">Layer.DOMAIN</span>
                </div>
                <div v-if="step === 1" class="flex items-center gap-2 text-[10px]">
                    <span class="text-gray-500">Scope:</span> <span class="text-blue-400">DOMAIN</span>
                    <span class="text-gray-500">Folder:</span> <span class="text-purple-400">aggregates</span>
                    <span class="text-gray-600">-></span>
                    <span class="text-green-400 font-bold">AGGREGATE</span>
                </div>
                <div v-if="step === 2" class="flex items-center gap-2 text-[10px]">
                    <span class="text-gray-500">Regex:</span> <span class="text-yellow-400">.*Repository</span>
                    <span class="text-gray-500">File:</span> <span class="text-gray-300">sql_order_repository</span>
                    <span class="text-gray-600">-></span>
                    <span class="text-green-400 font-bold">REPOSITORY</span>
                </div>
            </div>
        </div>

    </div>
  </div>
</template>

<style scoped>
.tree-item {
    display: flex;
    align-items: center;
}
.tree-dash {
    width: 1.25rem;
    display: inline-block;
    flex-shrink: 0;
}
/* Code transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>