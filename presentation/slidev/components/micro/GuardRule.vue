<script setup lang="ts">
defineProps<{
    layer: string,
    folders: string[],
    regex?: string
}>()
</script>

<template>
    <div class="bg-[#111] border border-gray-800 rounded-lg p-3 font-mono text-xs mb-4 relative group overflow-hidden">
        <div class="absolute top-0 right-0 px-2 py-0.5 bg-gray-800 text-[9px] text-gray-400 rounded-bl font-bold">dddguard detector</div>
        
        <div class="flex items-center gap-2 mb-2">
            <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
            <span class="text-gray-300 font-bold uppercase tracking-wider text-[10px]">{{ layer }} Detection Rule</span>
        </div>

        <div class="flex flex-col gap-1 text-[10px]">
            <div class="flex gap-2">
                <span class="text-gray-500 w-12 shrink-0">Paths:</span>
                <div class="flex flex-wrap gap-1">
                    <span v-for="f in folders" :key="f" class="px-1 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 leading-none">
                        {{ f }}
                    </span>
                </div>
            </div>
            
            <div v-if="regex" class="flex gap-2">
                <span class="text-gray-500 w-12 shrink-0">Regex:</span>
                <code class="text-orange-400 bg-orange-500/10 px-1 py-0.5 rounded border border-orange-500/20 leading-none">{{ regex }}</code>
            </div>
        </div>
    </div>
</template>