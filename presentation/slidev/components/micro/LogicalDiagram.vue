<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Всего шагов в цикле анимации
const TOTAL_STEPS = 18
const currentStep = ref(0)
let timer = null

onMounted(() => {
  // Запускаем бесконечный цикл волны
  timer = setInterval(() => {
    currentStep.value = (currentStep.value + 1) % TOTAL_STEPS
  }, 600) // Скорость переключения (чем меньше, тем быстрее волна)
})

onUnmounted(() => {
  clearInterval(timer)
})

// Хелпер для проверки: активен ли сейчас этот шаг?
// s - номер шага, или массив шагов (если элемент должен гореть несколько тактов)
const is = (s) => Array.isArray(s) ? s.includes(currentStep.value) : currentStep.value === s

// Классы для активного состояния (Увеличение + Подсветка)
const activeClass = (color = 'orange') => {
  const glow = {
    orange: 'shadow-[0_0_30px_rgba(249,115,22,0.6)] border-orange-400',
    blue: 'shadow-[0_0_30px_rgba(59,130,246,0.6)] border-blue-400',
    purple: 'shadow-[0_0_30px_rgba(168,85,247,0.6)] border-purple-400',
    green: 'shadow-[0_0_30px_rgba(34,197,94,0.6)] border-green-400',
  }
  return `scale-110 z-30 brightness-125 ${glow[color] || ''}`
}

// Классы для активной стрелочки
const activeArrow = (color = 'text-gray-600') => {
    if (color === 'text-gray-600') return 'scale-100 opacity-50' // неактивна
    return `scale-150 ${color} drop-shadow-[0_0_10px_currentColor] opacity-100 font-bold`
}
</script>

<template>
  <div
    class="w-full h-full min-h-[500px] bg-[#0F1115] relative flex items-center justify-center border border-gray-800 rounded-2xl overflow-hidden select-none font-sans"
    style="background-image: radial-gradient(#ffffff08 1px, transparent 1px); background-size: 24px 24px;"
  >
    <div 
        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full blur-[80px] pointer-events-none transition-colors duration-1000 opacity-10"
        :class="currentStep < 8 ? 'bg-orange-500' : (currentStep < 11 ? 'bg-blue-500' : 'bg-green-500')" 
    />

    <div class="relative flex flex-col items-center transform scale-[0.65] md:scale-[0.75] xl:scale-[0.85] origin-center transition-transform duration-300">
      
      <div class="relative z-20 mb-1">
        <div 
            class="w-[420px] h-20 bg-gradient-to-b from-[#2996CC] to-[#2075A0] flex flex-col items-center justify-center text-white border border-[#56B7E6]/50 shadow-[0_0_20px_-5px_rgba(41,150,204,0.4)] rounded-xl transition-all duration-500 ease-in-out"
            :class="is(10) ? activeClass('blue') : ''"
        >
            <span class="font-bold text-xl tracking-widest drop-shadow-md">DOMAIN</span>
            <span class="text-[10px] text-blue-100/90 font-mono mt-0.5 tracking-wide">Pure Business Logic</span>
        </div>
        
        <div class="absolute -bottom-4 left-1/2 -translate-x-1/2 h-4 border-l border-gray-600/50"></div>
      </div>

      <div 
        class="i-carbon-arrow-down text-xl my-1 transition-all duration-300"
        :class="is([9, 11]) ? activeArrow('text-blue-400') : 'text-gray-600'" 
      />

      <div class="relative z-20 mb-8">
         <div class="absolute -top-4 left-1/2 -translate-x-1/2 h-4 border-l border-gray-600/50"></div>
        <div 
            class="w-[420px] h-20 bg-gradient-to-b from-[#B77BFF] to-[#9B51E0] flex flex-col items-center justify-center text-white border border-[#D4AFFF]/50 shadow-[0_0_20px_-5px_rgba(183,123,255,0.4)] rounded-xl transition-all duration-500 ease-in-out"
            :class="is([8, 12]) ? activeClass('purple') : ''"
        >
            <span class="font-bold text-xl tracking-widest drop-shadow-md">APP</span>
            <span class="text-[10px] text-purple-100/90 font-mono mt-0.5 tracking-wide">Orchestration & Use Cases</span>
        </div>
      </div>

      <div class="flex flex-row items-start justify-center gap-8">
        
        <div class="flex flex-row">
            <div class="w-10 flex items-center justify-center mr-4 transition-all duration-500" :class="currentStep < 8 ? 'opacity-100' : 'opacity-40'">
                <div class="-rotate-90 whitespace-nowrap text-orange-500/90 font-mono text-[10px] font-bold tracking-[0.2em] uppercase">
                    Driving Side (IN)
                </div>
            </div>

            <div class="flex flex-col items-center gap-2 w-[180px] relative">
                
                <div class="i-carbon-arrow-up text-lg transition-all duration-300" 
                     :class="is(7) ? activeArrow('text-orange-500') : 'text-gray-600'" />
                
                <div 
                    class="w-full h-16 bg-gradient-to-b from-[#D35400] to-[#A04000] flex flex-col items-center justify-center text-white border border-[#E67E22]/50 shadow-lg rounded-lg relative z-10 transition-all duration-500 ease-in-out"
                    :class="is(6) ? activeClass('orange') : ''"
                >
                    <span class="font-bold text-xs tracking-wider uppercase">Adapters</span>
                    <span class="text-[8px] text-orange-100/70 opacity-80 mt-0.5 font-mono">Consumers / API</span>
                    
                    <div 
                        class="absolute -left-12 top-1/2 -translate-y-1/2 text-3xl text-orange-500 transition-all duration-500"
                        :class="is(0) ? 'scale-125 opacity-100 translate-x-2 drop-shadow-[0_0_10px_orange]' : 'opacity-20 scale-100'"
                    >
                         <div class="i-carbon-arrow-right" />
                    </div>
                </div>

                <div class="i-carbon-arrow-up text-lg transition-all duration-300"
                     :class="is(5) ? activeArrow('text-orange-500') : 'text-gray-600'" />

                <div 
                    class="w-full py-1.5 bg-[#1e293b] border border-slate-700 rounded text-center transition-all duration-500 ease-in-out"
                    :class="is(4) ? 'scale-110 border-orange-400 shadow-[0_0_15px_rgba(249,115,22,0.4)] bg-slate-700' : ''"
                >
                    <span class="font-bold text-[10px] tracking-wider text-slate-300 block">DTO</span>
                    <span class="text-[8px] text-slate-500 font-mono block">Request Model</span>
                </div>

                <div class="i-carbon-arrow-up text-lg transition-all duration-300"
                     :class="is(3) ? activeArrow('text-orange-500') : 'text-gray-600'" />

                <div 
                    class="w-full h-12 bg-[#A84300]/80 flex flex-col items-center justify-center text-white border border-[#C05A15]/50 rounded-lg backdrop-blur-sm transition-all duration-500 ease-in-out"
                    :class="is([1, 2]) ? activeClass('orange') : ''"
                >
                    <span class="font-bold text-xs tracking-wider text-orange-50">PORTS</span>
                    <span class="text-[8px] text-orange-200/60 font-mono">FastAPI / CLI</span>
                </div>
            </div>
        </div>


        <div class="flex flex-row">
            <div class="flex flex-col items-center gap-2 w-[180px] relative">
                
                <div class="i-carbon-arrow-down text-lg transition-all duration-300"
                     :class="is(13) ? activeArrow('text-green-500') : 'text-gray-600'" />
                
                <div 
                    class="w-full h-16 bg-gradient-to-b from-[#27AE60] to-[#1E8449] flex flex-col items-center justify-center text-white border border-[#2ECC71]/50 shadow-lg rounded-lg relative z-10 transition-all duration-500 ease-in-out"
                    :class="is(14) ? activeClass('green') : ''"
                >
                    <span class="font-bold text-xs tracking-wider uppercase">Adapters</span>
                    <span class="text-[8px] text-green-100/70 opacity-80 mt-0.5 font-mono">DB / Gateways</span>

                    <div 
                        class="absolute -right-12 top-1/2 -translate-y-1/2 text-3xl text-green-500 transition-all duration-500"
                        :class="is(17) ? 'scale-125 opacity-100 translate-x-2 drop-shadow-[0_0_10px_lime]' : 'opacity-20 scale-100 translate-x-0'"
                    >
                         <div class="i-carbon-arrow-right" />
                    </div>
                </div>

                <div class="i-carbon-arrow-down text-lg transition-all duration-300"
                     :class="is(15) ? activeArrow('text-green-500') : 'text-gray-600'" />

                <div 
                    class="w-full py-1.5 bg-[#1e293b] border border-slate-700 rounded text-center transition-all duration-500 ease-in-out"
                    :class="is(16) ? 'scale-110 border-green-400 shadow-[0_0_15px_rgba(34,197,94,0.4)] bg-slate-700' : ''"
                >
                    <span class="font-bold text-[10px] tracking-wider text-slate-300 block">DTO</span>
                    <span class="text-[8px] text-slate-500 font-mono block">Response Model</span>
                </div>

                <div class="i-carbon-arrow-down text-lg transition-all duration-300"
                     :class="is(17) ? activeArrow('text-green-500') : 'text-gray-600'" />

                <div 
                    class="w-full h-12 bg-[#145A32]/80 flex flex-col items-center justify-center text-white border border-[#1E8449]/50 rounded-lg backdrop-blur-sm transition-all duration-500 ease-in-out"
                    :class="is(17) ? activeClass('green') : ''"
                >
                    <span class="font-bold text-xs tracking-wider text-green-50">PORTS</span>
                    <span class="text-[8px] text-green-200/60 font-mono">SQLAlchemy / S3</span>
                </div>
            </div>

            <div class="w-10 flex items-center justify-center ml-4 transition-all duration-500" :class="currentStep > 12 ? 'opacity-100' : 'opacity-40'">
                <div class="rotate-90 whitespace-nowrap text-green-500/90 font-mono text-[10px] font-bold tracking-[0.2em] uppercase">
                    Driven Side (OUT)
                </div>
            </div>
        </div>

      </div>
    </div>
  </div>
</template>