<script setup lang="ts">
defineProps<{ label?: string }>()
</script>
<template>
    <div class="w-full h-full min-h-[200px] rounded-xl border-2 border-dashed border-gray-700 bg-[#0B0F19]/50 flex items-center justify-center relative overflow-hidden group">
        <div class="absolute inset-0 bg-[radial-gradient(#ffffff05_1px,transparent_1px)] [background-size:16px_16px]"></div>
        
        <div class="flex flex-col items-center gap-3 opacity-40 group-hover:opacity-60 transition-opacity">
            <carbon-chart-relationship class="text-4xl" />
            <span class="font-mono text-xs uppercase tracking-widest border border-gray-600 px-3 py-1 rounded text-center">
                {{ label || 'Diagram Area' }}<br>
                <span class="text-[9px] opacity-70 normal-case">(To be drawn)</span>
            </span>
        </div>
    </div>
</template>