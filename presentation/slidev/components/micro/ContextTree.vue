<script setup lang="ts">
const props = defineProps<{
  activeLayer?: 'domain' | 'app' | 'adapters' | 'composition' | null
}>()
</script>

<template>
  <div class="font-mono text-[10px] leading-[1.1rem] bg-[#0B0F19] p-4 rounded-xl border border-gray-800 text-gray-500 shadow-2xl overflow-y-auto h-full relative select-none">
    
    <div class="sticky top-0 right-0 float-right ml-4 mb-2 flex flex-col gap-1.5 bg-[#111]/90 backdrop-blur p-2 rounded border border-gray-800 z-10">
        <div class="flex items-center gap-2"><div class="w-1.5 h-1.5 rounded-full bg-blue-500"></div> <span class="text-blue-400 text-[9px]">Domain</span></div>
        <div class="flex items-center gap-2"><div class="w-1.5 h-1.5 rounded-full bg-purple-500"></div> <span class="text-purple-400 text-[9px]">App</span></div>
        <div class="flex items-center gap-2"><div class="w-1.5 h-1.5 rounded-full bg-green-500"></div> <span class="text-green-400 text-[9px]">Infra</span></div>
    </div>

    <div class="flex flex-col">
        <div>src/</div>
        <div class="pl-3">├── &lt;context_name&gt;/</div>
        
        <div class="pl-6 transition-opacity duration-300" :class="activeLayer && activeLayer !== 'domain' ? 'opacity-20' : 'opacity-100'">
            <span class="text-gray-600">├── </span><span class="text-blue-400 font-bold">domain/</span> <span class="comment"># Pure Business Logic</span>
            <div class="pl-3 border-l border-blue-500/10 ml-[0.3rem]">
                <div>├── aggregates/ <span class="comment"># Rules & Consistency</span></div>
                <div>├── entities/   <span class="comment"># Identity objects</span></div>
                <div>├── vo/         <span class="comment"># Immutable values</span></div>
                <div>├── services/   <span class="comment"># Stateless ops</span></div>
                <div>├── events/     <span class="comment"># Domain facts</span></div>
                <div>└── errors/     <span class="comment"># Exceptions</span></div>
            </div>
        </div>

        <div class="pl-6 transition-opacity duration-300" :class="activeLayer && activeLayer !== 'app' ? 'opacity-20' : 'opacity-100'">
             <span class="text-gray-600">├── </span><span class="text-purple-400 font-bold">app/</span> <span class="comment"># Orchestration</span>
            <div class="pl-3 border-l border-purple-500/10 ml-[0.3rem]">
                <div>├── use_cases/  <span class="comment"># Commands</span></div>
                <div>├── queries/    <span class="comment"># Data reading</span></div>
                <div>├── workflows/  <span class="comment"># Sagas</span></div>
                <div>├── handlers/   <span class="comment"># Event reactions</span></div>
                <div>└── interfaces/ <span class="comment"># Port contracts</span></div>
            </div>
        </div>

        <div class="pl-6 transition-opacity duration-300" :class="activeLayer && activeLayer !== 'adapters' ? 'opacity-20' : 'opacity-100'">
             <span class="text-gray-600">├── </span><span class="text-green-400 font-bold">adapters/</span> <span class="comment"># Translation layer</span>
             <div class="pl-3 border-l border-green-500/10 ml-[0.3rem]">
                <div>├── driving/ <span class="comment"># Controllers</span></div>
                <div>└── driven/  <span class="comment"># Repositories</span></div>
             </div>
        </div>

        <div class="pl-6 transition-opacity duration-300" :class="activeLayer && activeLayer !== 'adapters' ? 'opacity-20' : 'opacity-100'">
             <span class="text-gray-600">├── </span><span class="text-green-400 font-bold">dto/</span> <span class="comment"># Data Carriers</span>
             <div class="pl-3 border-l border-green-500/10 ml-[0.3rem]">
                <div>├── driving/ <span class="comment"># Requests</span></div>
                <div>└── driven/  <span class="comment"># Responses</span></div>
             </div>
        </div>

        <div class="pl-6 transition-opacity duration-300" :class="activeLayer && activeLayer !== 'adapters' ? 'opacity-20' : 'opacity-100'">
             <span class="text-gray-600">├── </span><span class="text-green-400 font-bold">ports/</span> <span class="comment"># Infra Code</span>
             <div class="pl-3 border-l border-green-500/10 ml-[0.3rem]">
                <div>├── driving/ <span class="comment"># Entry points</span></div>
                <div>└── driven/  <span class="comment"># Egress points</span></div>
             </div>
        </div>

        <div class="pl-6 transition-opacity duration-300" :class="activeLayer && activeLayer !== 'composition' ? 'opacity-20' : 'opacity-100'">
            <span class="text-gray-600">└── </span><span class="text-red-400 font-bold">composition.py</span> <span class="comment"># Wiring</span>
        </div>
        
        <div class="mt-2 transition-opacity duration-300" :class="activeLayer && activeLayer !== 'composition' ? 'opacity-20' : 'opacity-100'">
            <div>├── shared/ <span class="comment"># Kernel & Libs</span></div>
            <div>└── root/   <span class="comment"># Global Entry</span></div>
            <div class="pl-3 border-l border-gray-700 ml-[0.3rem]">
                <div>├── composition.py</div>
                <div>├── main.py</div>
                <div>└── cli.py</div>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.comment {
    color: #4b5563; /* gray-600 */
    margin-left: 0.5rem;
    font-style: italic;
}
</style>