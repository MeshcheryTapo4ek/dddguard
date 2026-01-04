<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useNav } from '@slidev/client'

const { clicks } = useNav()
const step = ref(0)

// 5 Steps: 0, 1, 2, 3, 4
watch(clicks, (newClick) => {
  if (newClick >= 0 && newClick <= 4) {
    step.value = newClick
  }
})

onMounted(() => {
  step.value = (clicks.value >= 0 && clicks.value <= 4) ? clicks.value : 0
})

const contexts = [
  {
    id: 'hall',
    title: 'Dining Hall',
    color: 'blue',
    hex: '#3b82f6', // blue-500
    icon: 'i-carbon-restaurant',
    // Мы убрали класс 'text-blue-400' из данных, так как будем красить через style для надежности
    domain: [{ k: 'table', v: '4' }, { k: 'guest', v: '"VIP"' }, { k: 'items', v: '["Pasta"]' }],
    useCases: ['Create Order', 'Add Notes', 'Split Bill'],
    tools: { in: { name: 'Guests', icon: 'i-carbon-user-multiple' }, out: { name: 'Tablet', icon: 'i-carbon-touch-1' } }
  },
  {
    id: 'kitchen',
    title: 'Kitchen',
    color: 'yellow',
    hex: '#eab308', // yellow-500
    icon: 'i-carbon-temperature-hot',
    domain: [{ k: 'chef', v: '"Mario"' }, { k: 'steps', v: '["Boil"]' }, { k: 'ingr', v: '["Bacon"]' }],
    useCases: ['Queue Order', 'Assign Station', 'Mark Ready'],
    tools: { in: { name: 'Tablet', icon: 'i-carbon-touch-1' }, out: { name: 'Service Window', icon: 'i-carbon-delivery' } }
  },
  {
    id: 'accounting',
    title: 'Accounting',
    color: 'pink',
    hex: '#ec4899', // pink-500
    icon: 'i-carbon-currency',
    domain: [{ k: 'total', v: '45.00' }, { k: 'tax', v: '20%' }, { k: 'status', v: '"PENDING"' }],
    useCases: ['Calc Tax', 'Apply Discount', 'Post Ledger'],
    tools: { in: { name: 'Tablet', icon: 'i-carbon-touch-1' }, out: { name: 'Fiscal Register', icon: 'i-carbon-receipt' } }
  }
]
</script>

<template>
  <div class="h-full w-full flex flex-col px-2 md:px-4 lg:px-6 relative overflow-hidden">
    
    <div class="flex flex-col justify-center items-center text-center relative z-20 shrink-0 transition-all duration-700"
         :class="step >= 3 ? 'h-24' : 'h-32'">
        <transition
            enter-active-class="transition duration-500 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            leave-active-class="transition duration-300 ease-in absolute w-full"
            leave-to-class="opacity-0 translate-y-2"
        >
            <div v-if="step === 0" key="step0" class="absolute w-full top-6 px-12">
                <div class="inline-flex items-center gap-2 border border-blue-500/30 rounded-full px-3 py-1 text-[10px] font-mono text-blue-400 mb-4 bg-blue-500/5 uppercase tracking-widest">
                    Phase 1: Bounded Context Definitions
                </div>
                <h2 class="text-4xl font-bold text-white mb-4 tracking-tight">
                    Один <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">Order</span>: разные смыслы
                </h2>
                <p class="text-gray-400 text-sm max-w-2xl mx-auto font-light leading-relaxed">
                   Разбиваем задачу на независимые зоны. Один и тот же объект (Заказ) имеет <b>разный состав полей</b> для разных участников процесса.
                </p>
            </div>

            <div v-else-if="step === 1" key="step1" class="absolute w-full top-6 px-12">
                 <div class="inline-flex items-center gap-2 border border-purple-500/30 rounded-full px-3 py-1 text-[10px] font-mono text-purple-400 mb-4 bg-purple-500/5 uppercase tracking-widest">
                    Phase 2: Business Logic
                </div>
                <h2 class="text-4xl font-bold text-white mb-4 tracking-tight">
                    Определяем <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-500">Behavior</span>
                </h2>
                <p class="text-gray-400 text-sm max-w-2xl mx-auto font-light leading-relaxed">
                    Описываем работу с доменными сущностями: как их правильно <b>изменять и модифицировать</b> согласно бизнес-правилам.
                </p>
            </div>

            <div v-else-if="step === 2" key="step2" class="absolute w-full top-6 px-12">
                <div class="inline-flex items-center gap-2 border border-green-500/30 rounded-full px-3 py-1 text-[10px] font-mono text-green-400 mb-4 bg-green-500/5 uppercase tracking-widest">
                    Phase 3: Ports & Adapters
                </div>
                <h2 class="text-4xl font-bold text-white mb-4 tracking-tight">
                    Подключаем <span class="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-teal-500">Infrastructure</span>
                </h2>
                <p class="text-gray-400 text-sm max-w-2xl mx-auto font-light leading-relaxed">
                    Добавляем жизни бизнес-логике. Мы окружаем чистое ядро связями с внешним миром через <b>Ports & Adapters</b>.
                </p>
            </div>

             <div v-else-if="step === 3" key="step3" class="absolute w-full top-4 px-12">
                <div class="inline-flex items-center gap-2 border border-slate-500/30 rounded-full px-3 py-1 text-[10px] font-mono text-slate-400 mb-3 bg-slate-500/5 uppercase tracking-widest">
                    Phase 4: Optimization
                </div>
                <h2 class="text-4xl font-bold text-white mb-3 tracking-tight">
                    Выделяем <span class="text-transparent bg-clip-text bg-gradient-to-r from-slate-200 to-slate-400">Shared Kernel</span>
                </h2>
                 <p class="text-gray-400 text-sm max-w-2xl mx-auto font-light leading-relaxed">
                    Минимизируем повторения кода (DRY), вынося общие части в фундамент, сохраняя независимость контекстов.
                </p>
            </div>

            <div v-else-if="step === 4" key="step4" class="absolute w-full top-4 px-12">
                <div class="inline-flex items-center gap-2 border border-rose-500/30 rounded-full px-3 py-1 text-[10px] font-mono text-rose-400 mb-3 bg-rose-500/5 uppercase tracking-widest">
                    Phase 5: Composition
                </div>
                <h2 class="text-4xl font-bold text-white mb-3 tracking-tight">
                    Собираем <span class="text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-red-500">Composition Root</span>
                </h2>
                 <p class="text-gray-400 text-sm max-w-2xl mx-auto font-light leading-relaxed">
                    Единое место сборки. Склеиваем независимые контексты в работающее приложение.
                </p>
            </div>
        </transition>
    </div>

    <div class="flex-1 relative w-full transition-all duration-1000 cubic-bezier(0.4, 0, 0.2, 1) flex flex-col transform origin-top"
         :class="[
            step === 3 ? 'pt-20 pb-4' : 'pt-12 pb-8',
            step === 4 ? 'translate-y-50 scale-90 opacity-80' : ''
         ]">
        
        <div class="grid grid-cols-3 gap-8 items-start transition-all duration-700"
             :class="step >= 3 ? 'flex-none h-auto items-end' : 'h-full'">
            
            <div v-for="ctx in contexts" :key="ctx.id" class="flex flex-col transition-all duration-700 relative z-20"
                 :class="step >= 3 ? 'justify-end items-center' : 'h-full justify-start'">
                
                <div 
                    class="rounded-2xl transition-all duration-700 flex flex-col relative overflow-hidden shadow-xl bg-[#151926] border"
                    :style="{ borderColor: step >= 2 ? ctx.hex + '4D' : ctx.hex + '1A' }"
                    :class="[
                        step >= 3 ? 'py-4 px-6 items-center justify-center bg-[#111318] hover:scale-105 hover:bg-[#1a1d24] z-20 w-full max-w-[220px]' : '' 
                    ]"
                >
                    <div class="transition-all duration-500 flex items-center gap-3 w-full"
                         :class="step >= 3 ? 'flex-col text-center justify-center border-none p-0' : 'p-3 border-b border-white/5 bg-white/5'">
                        
                        <div class="rounded-xl bg-[#0B0F19] border border-white/10 transition-all duration-500 flex items-center justify-center"
                             :style="{ 
                                boxShadow: step >= 3 ? `0 0 20px ${ctx.hex}40` : 'none',
                                borderColor: step >= 3 ? ctx.hex + '4D' : '' 
                             }"
                             :class="step >= 3 ? 'w-14 h-14 mb-2' : 'p-2'">
                            
                             <div :class="[ctx.icon, step >= 3 ? 'text-3xl' : 'text-xl']" :style="{ color: ctx.hex }" />
                        </div>
                        <span class="font-bold text-gray-200 tracking-wide transition-all duration-500"
                              :class="step >= 3 ? 'text-sm' : 'text-sm'">{{ ctx.title }}</span>
                    </div>

                    <div class="transition-all duration-700 overflow-hidden w-full ease-in-out"
                         :class="step >= 3 ? 'max-h-0 opacity-0' : 'max-h-[400px] opacity-100'">
                         
                         <div class="transition-all duration-500 ease-in-out bg-[#0B0F19] border-l-2" 
                              :style="{ borderColor: step === 0 ? 'transparent' : ctx.hex + '80' }"
                              :class="[step === 0 ? 'p-4' : 'px-4 py-3 bg-[#0B0F19]/50']">
                            <div v-if="step === 0" class="space-y-3">
                                <div class="text-[10px] font-mono text-gray-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                                    <div class="i-carbon-model-alt text-sm" /> Domain Model
                                </div>
                                <ul class="space-y-2 font-mono text-xs text-gray-400">
                                    <li v-for="(f, i) in ctx.domain" :key="i" class="flex gap-2">
                                        <span :style="{ color: ctx.hex }">{{ f.k }}:</span>
                                        <span class="text-gray-300">{{ f.v }}</span>
                                    </li>
                                </ul>
                            </div>
                            <div v-else class="flex items-center justify-between">
                                <div class="flex items-center gap-2 text-[10px] font-mono text-gray-400">
                                    <div class="i-carbon-model-alt" :style="{ color: ctx.hex }"/> Domain Model
                                </div>
                                <div class="text-[10px] text-gray-600 font-mono hidden xl:block">{{ ctx.domain.length }} fields</div>
                            </div>
                        </div>

                        <div class="transition-all duration-700 overflow-hidden relative border-l-2" :class="[step === 0 ? 'max-h-0 opacity-0 border-transparent' : 'opacity-100', step === 1 ? 'max-h-[200px] border-purple-500/0 bg-[#151926]' : '', step === 2 ? 'max-h-[50px] border-purple-500/50 bg-[#151926]/30' : '']">
                            <div v-if="step === 1" class="p-4">
                                <div class="text-[10px] font-mono mb-3 uppercase tracking-widest flex items-center gap-2 text-purple-400"><div class="i-carbon-function" /> Use Cases</div>
                                <div class="space-y-2"><div v-for="(uc, i) in ctx.useCases" :key="uc" class="flex items-center gap-3 p-2 rounded-lg border border-purple-500/20 bg-purple-500/10 transition-all duration-300"><div class="i-carbon-chevron-right text-[10px] text-purple-500" /><span class="text-xs font-bold text-gray-300">{{ uc }}</span></div></div>
                            </div>
                            <div v-if="step === 2" class="px-4 py-3 flex items-center justify-between h-full"><div class="flex items-center gap-2 text-[10px] font-mono text-gray-400"><div class="i-carbon-function text-purple-500"/> Business Logic</div><div class="text-[10px] text-gray-600 font-mono">{{ ctx.useCases.length }} rules</div></div>
                        </div>

                        <div class="transition-all duration-500 ease-out bg-[#0B0F19] border-t border-white/5" :class="step === 2 ? 'max-h-[120px] opacity-100 py-3' : 'max-h-0 opacity-0 py-0'">
                            <div class="grid grid-cols-2 h-full gap-3 px-3">
                                <div class="p-2 rounded border border-green-500/10 bg-green-500/5 flex flex-col items-center justify-center gap-1.5 group"><div class="text-[8px] font-mono text-green-500 uppercase w-full text-center border-b border-green-500/10 pb-1">Driving</div><div :class="ctx.tools.in.icon" class="text-xl text-green-400 group-hover:scale-110 transition-transform"/><div class="text-[9px] text-gray-300 font-bold text-center leading-tight">{{ ctx.tools.in.name }}</div></div>
                                <div class="p-2 rounded border border-orange-500/10 bg-orange-500/5 flex flex-col items-center justify-center gap-1.5 group"><div class="text-[8px] font-mono text-orange-500 uppercase w-full text-center border-b border-orange-500/10 pb-1">Driven</div><div :class="ctx.tools.out.icon" class="text-xl text-orange-400 group-hover:scale-110 transition-transform"/><div class="text-[9px] text-gray-300 font-bold text-center leading-tight">{{ ctx.tools.out.name }}</div></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="absolute -bottom-3 left-1/2 -translate-x-1/2 transition-all duration-700 z-10"
                     :class="step >= 3 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'">
                     <div class="i-carbon-caret-up text-xl" :style="{ color: ctx.hex }" />
                </div>
                <div class="absolute -bottom-[70px] left-1/2 -translate-x-1/2 w-px border-l-2 border-dashed transition-all duration-1000 z-0 origin-bottom"
                     :style="{ borderColor: ctx.hex + '80' }"
                     :class="[step >= 3 ? 'h-[70px] opacity-100' : 'h-0 opacity-0']"></div>

                <div class="absolute -top-[96px] left-1/2 -translate-x-1/2 w-px border-l-2 border-dashed border-rose-500/30 transition-all duration-1000 z-0 origin-top delay-300"
                     :class="step === 4 ? 'h-24 opacity-100' : 'h-0 opacity-0'"></div>
                <div class="absolute -top-3 left-1/2 -translate-x-1/2 transition-all duration-700 z-10 delay-300"
                     :class="step === 4 ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'">
                     <div class="i-carbon-caret-down text-xl text-rose-500" />
                </div>

            </div>
        </div>

        <div class="mt-auto w-full px-8 transition-all duration-700 ease-out z-10"
             :class="step >= 3 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-20 h-0 overflow-hidden'">
            <div class="bg-[#111318] border-t-2 border-slate-700/50 rounded-t-xl rounded-b-xl border-b border-x border-slate-800 p-4 shadow-2xl relative">
                <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-slate-500 shadow-[0_0_20px_rgba(100,116,139,0.5)]"></div>
                <div class="flex items-center gap-8 relative z-10">
                    <div class="flex items-center gap-3 text-slate-300 min-w-[200px] border-r border-slate-800 pr-6">
                        <div class="p-2 bg-slate-800 rounded"><div class="i-carbon-cube text-2xl text-slate-400" /></div>
                        <div><h3 class="text-lg font-bold">Shared Kernel</h3><div class="text-[10px] text-slate-500 font-mono uppercase tracking-widest">Foundation Layer</div></div>
                    </div>
                    <div class="flex-1 flex justify-around gap-4 text-xs font-mono text-gray-400 opacity-60">
                        <div class="flex items-center gap-2"><div class="i-carbon-model text-blue-400" /> Value Objects</div>
                        <div class="w-px h-4 bg-gray-700"></div>
                        <div class="flex items-center gap-2"><div class="i-carbon-code text-green-400" /> Utilities</div>
                        <div class="w-px h-4 bg-gray-700"></div>
                        <div class="flex items-center gap-2"><div class="i-carbon-plug text-purple-400" /> Contracts</div>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <div class="absolute top-40 left-0 w-full px-32 transition-all duration-1000 ease-out z-30"
            :class="step === 4 ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-10 pointer-events-none'">
        
        <div class="bg-[#111318] border border-rose-500/30 rounded-xl p-4 shadow-[0_0_50px_rgba(225,29,72,0.15)] flex items-center justify-between relative overflow-hidden backdrop-blur-sm">
            <div class="absolute inset-0 bg-gradient-to-r from-rose-500/10 to-transparent"></div>
            
            <div class="flex items-center gap-4 relative z-10">
                <div class="p-3 bg-rose-500/10 rounded-lg border border-rose-500/20 text-rose-400">
                    <div class="i-carbon-chemistry text-3xl" />
                </div>
                <div>
                    <h3 class="text-xl font-bold text-white">Composition Root</h3>
                    <div class="text-[10px] text-rose-300 font-mono">main.py / di_container.py</div>
                </div>
            </div>

            <div class="flex items-center gap-4 relative z-10 text-gray-400 font-mono text-xs">
                <div class="px-3 py-1.5 rounded bg-black/40 border border-white/5 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-rose-500/50"></div> App Config
                </div>
                <div class="px-3 py-1.5 rounded bg-black/40 border border-white/5 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-rose-500/50"></div> App Container
                </div>
                <div class="px-3 py-1.5 rounded bg-black/40 border border-white/5 flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-rose-500/50"></div> App Entrypoints
                </div>
            </div>
        </div>
    </div>

  </div>
</template>