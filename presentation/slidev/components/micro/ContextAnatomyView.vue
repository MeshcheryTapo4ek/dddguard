<script setup lang="ts">
import ContextTree from './ContextTree.vue'
</script>

<template>
  <div class="h-full w-full">
    <h1 class="text-4xl font-bold mb-2">Context Anatomy</h1>
    <p class="text-gray-400 mb-6">The Blueprint of a Bounded Context</p>

    <div class="grid grid-cols-[1.2fr_0.8fr] gap-6 h-[400px]">
        <div class="h-full overflow-hidden">
            <ContextTree />
        </div>

        <div class="flex flex-col gap-4">
            
            <div class="p-4 rounded-xl bg-[#151926] border border-blue-500/20">
                <h3 class="text-blue-400 font-bold mb-1 text-sm flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-blue-500"></div> Domain Layer
                </h3>
                <p class="text-[11px] text-gray-400 leading-normal">
                    Pure Business Logic. Изолирована от всего.
                    <br>Зависимости: <span class="text-red-400">0</span>.
                </p>
            </div>
            
            <div class="p-4 rounded-xl bg-[#151926] border border-purple-500/20">
                <h3 class="text-purple-400 font-bold mb-1 text-sm flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-purple-500"></div> Application Layer
                </h3>
                <p class="text-[11px] text-gray-400 leading-normal">
                    Orchestration & Use Cases. Управляет потоком данных.
                    <br>Импортирует: <span class="text-blue-400">Domain</span>.
                </p>
            </div>

            <div class="p-4 rounded-xl bg-[#151926] border border-green-500/20">
                <h3 class="text-green-400 font-bold mb-1 text-sm flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-green-500"></div> Infra (Adapters)
                </h3>
                <p class="text-[11px] text-gray-400 leading-normal">
                    Technology details. DB, API, Event Bus.
                    <br>Реализует интерфейсы из <span class="text-purple-400">App</span>.
                </p>
            </div>

            <div class="mt-auto opacity-50 text-[10px] font-mono text-center">
                * dddguard automatically enforces these boundaries
            </div>
        </div>
    </div>
  </div>
</template>