<template>
  <div class="h-full w-full relative flex flex-col justify-center items-center px-6">
    
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
    <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_bottom,rgba(16,185,129,0.1)_0%,transparent_60%)]"></div>

    <div class="relative z-10 w-full max-w-5xl mx-auto">
      
      <div class="flex items-center gap-4 mb-4 justify-center opacity-80">
        <div class="h-px w-12 bg-gradient-to-r from-transparent to-green-500"></div>
        <span class="text-green-400 font-mono text-xs tracking-[0.3em] uppercase">Phase 3: The Payoff</span>
        <div class="h-px w-12 bg-gradient-to-l from-transparent to-green-500"></div>
      </div>

      <h2 class="text-4xl font-bold text-white mb-6 text-center tracking-tight">
        Engineering <span class="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600">ROI</span>
      </h2>

      <div class="grid grid-cols-2 gap-4">

        <div class="col-span-2 group relative p-5 rounded-2xl bg-[#0B0F19]/80 border border-green-500/20 hover:border-green-400/50 transition-all duration-500 backdrop-blur-sm">
            <div class="absolute top-0 right-0 p-3 opacity-30 group-hover:opacity-100 transition-opacity">
                 <div class="flex gap-2">
                    <span class="text-[9px] font-mono border border-green-500 text-green-500 px-1.5 py-0.5 rounded uppercase">Human</span>
                    <span class="text-[9px] font-mono border border-green-500 text-green-500 px-1.5 py-0.5 rounded uppercase">Agent</span>
                 </div>
            </div>

            <div class="flex items-start gap-5">
                <div class="p-3 rounded-xl bg-green-500/10 text-green-400 group-hover:scale-110 transition-transform duration-500 border border-green-500/10">
                    <carbon-model-alt class="text-2xl" />
                </div>
                <div>
                    <h3 class="text-lg font-bold text-gray-100 mb-1">Pattern-Driven Clarity</h3>
                    <p class="text-xs text-gray-400 leading-normal max-w-3xl mb-3">
                        Следование паттернам (DDD) стандартизирует граф зависимостей. 
                        Разработчики и <b class="text-green-400">AI-агенты</b> перестают тратить ресурсы на "реверс-инжиниринг" спагетти-кода, мгновенно понимая, где находится нужная логика.
                    </p>
                    <div class="flex items-center gap-3 text-[10px] font-mono text-green-500/70">
                        <span class="flex items-center gap-1"><carbon-checkmark /> Reduced Cognitive Load</span>
                        <span class="w-1 h-1 bg-green-500 rounded-full opacity-50"></span>
                        <span class="flex items-center gap-1"><carbon-checkmark /> Context Optimization</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="group relative p-5 rounded-2xl bg-[#0B0F19]/80 border border-green-500/20 hover:border-green-400/50 transition-all duration-500 backdrop-blur-sm hover:-translate-y-1">
             <div class="flex items-center justify-between mb-3">
                <div class="p-2 rounded-lg bg-emerald-500/10 text-emerald-400"><carbon-test-tool class="text-xl" /></div>
                <span class="text-[9px] font-mono text-emerald-500/50 uppercase tracking-widest">Stability</span>
             </div>
             
             <h3 class="text-base font-bold text-gray-200 mb-2">Refactoring Confidence</h3>
             <p class="text-[11px] text-gray-400 leading-normal mb-3">
                Изолированное ядро покрывается быстрыми юнит-тестами. Вы меняете инфраструктуру, зная, что бизнес-правила не сломаны.
             </p>
             <div class="pl-3 border-l-2 border-emerald-500/30">
                <p class="text-[10px] text-gray-500 font-mono">Regression Risk: <span class="text-emerald-400">Minimized</span></p>
             </div>
        </div>

        <div class="group relative p-5 rounded-2xl bg-[#0B0F19]/80 border border-green-500/20 hover:border-green-400/50 transition-all duration-500 backdrop-blur-sm hover:-translate-y-1">
             <div class="flex items-center justify-between mb-3">
                <div class="p-2 rounded-lg bg-green-500/10 text-green-400"><carbon-direction-fork class="text-xl" /></div>
                <span class="text-[9px] font-mono text-green-500/50 uppercase tracking-widest">Velocity</span>
             </div>
             
             <h3 class="text-base font-bold text-gray-200 mb-2">Traceable Evolution</h3>
             <p class="text-[11px] text-gray-400 leading-normal mb-3">
                Изменения бизнес-логики локализованы. Никаких побочных эффектов в UI или API при правке формулы расчета.
             </p>
             <div class="pl-3 border-l-2 border-green-500/30">
                <p class="text-[10px] text-gray-500 font-mono">Modification Cost: <span class="text-green-400">Linear</span></p>
             </div>
        </div>

      </div>

    </div>
  </div>
</template>