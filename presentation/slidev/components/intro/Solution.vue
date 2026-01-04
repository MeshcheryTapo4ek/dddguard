<template>
  <div class="h-full w-full relative flex flex-col justify-center items-center text-center px-6">
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
    <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.1)_0%,transparent_60%)]"></div>
    
    <div class="relative z-10 w-full max-w-6xl mx-auto h-full flex flex-col justify-center">
      
      <div class="flex items-center gap-4 mb-6 justify-center opacity-80">
        <div class="h-px w-12 bg-gradient-to-r from-transparent to-blue-500"></div>
        <span class="text-blue-400 font-mono text-xs tracking-[0.3em] uppercase">Phase 2: Standardization</span>
        <div class="h-px w-12 bg-gradient-to-l from-transparent to-blue-500"></div>
      </div>

      <h1 class="text-5xl font-bold mb-4 tracking-tight">
        Architecture as <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">Code Constraint</span>
      </h1>
      <p class="text-lg text-gray-400 max-w-3xl mx-auto font-light leading-relaxed mb-12">
          Мы пишем код так, чтобы Архитектура поддерживала сама себя.
          <b class="text-gray-200">Линтеры</b> и <b class="text-gray-200">Статический анализ</b> превращают "договоренности" в жесткие правила.
      </p>

      <div class="grid grid-cols-3 gap-6 text-left">
          
          <div class="p-6 rounded-xl bg-[#0B0F19]/80 border border-blue-500/20 hover:border-blue-400/50 transition-all group backdrop-blur-sm">
              <div class="flex items-center gap-3 mb-4 pb-3 border-b border-blue-500/10">
                 <div class="p-2 bg-blue-500/10 rounded-lg text-blue-400"><carbon-chemistry class="text-xl" /></div>
                 <div class="flex flex-col">
                    <span class="text-[10px] font-mono text-blue-500/70 uppercase tracking-widest">Foundation</span>
                    <span class="text-sm font-bold text-gray-200">DDD & Pure Core</span>
                 </div>
              </div>
              <p class="text-xs text-gray-400 leading-relaxed font-mono">
                Isolation Strategy.
                <br>
                <span class="text-gray-500 block mt-2">
                Бизнес-логика полностью изолирована. Это позволяет писать быстрые и надежные <b>Unit-тесты</b> без сложного мокинга инфраструктуры.
                </span>
              </p>
          </div>

          <div class="p-6 rounded-xl bg-[#0B0F19]/80 border border-blue-500/20 hover:border-cyan-400/50 transition-all group backdrop-blur-sm">
               <div class="flex items-center gap-3 mb-4 pb-3 border-b border-blue-500/10">
                 <div class="p-2 bg-cyan-500/10 rounded-lg text-cyan-400"><carbon-security class="text-xl" /></div>
                 <div class="flex flex-col">
                    <span class="text-[10px] font-mono text-cyan-500/70 uppercase tracking-widest">Structure</span>
                    <span class="text-sm font-bold text-gray-200">Strict Boundaries</span>
                 </div>
              </div>
              <p class="text-xs text-gray-400 leading-relaxed font-mono">
                Automated Governance.
                <br>
                <span class="text-gray-500 block mt-2">
                Четкое разделение слоев ведет к стабильности. Линтер запрещает "грязные" импорты на уровне CI, не давая системе деградировать.
                </span>
              </p>
          </div>

          <div class="p-6 rounded-xl bg-[#0B0F19]/80 border border-blue-500/20 hover:border-indigo-400/50 transition-all group backdrop-blur-sm">
               <div class="flex items-center gap-3 mb-4 pb-3 border-b border-blue-500/10">
                 <div class="p-2 bg-indigo-500/10 rounded-lg text-indigo-400"><carbon-flow-data class="text-xl" /></div>
                 <div class="flex flex-col">
                    <span class="text-[10px] font-mono text-indigo-500/70 uppercase tracking-widest">Tooling</span>
                    <span class="text-sm font-bold text-gray-200">Context & Visibility</span>
                 </div>
              </div>
              <p class="text-xs text-gray-400 leading-relaxed font-mono">
                Observability.
                <br>
                <span class="text-gray-500 block mt-2">
                Инструмент собирает чистый контекст для <b>LLM-агентов</b> и генерирует актуальную визуализацию архитектуры (Draw.io).
                </span>
              </p>
          </div>

      </div>
    </div>
  </div>
</template>