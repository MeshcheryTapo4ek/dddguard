<template>
  <div class="absolute inset-0 bg-[#0B0F19] flex flex-col items-center justify-center overflow-hidden select-none">
    
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.1),transparent_60%)] pointer-events-none"></div>
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] border border-blue-500/10 rounded-full animate-[spin_60s_linear_infinite] pointer-events-none"></div>
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] border border-blue-500/15 rounded-full border-dashed animate-[spin_50s_linear_infinite_reverse] pointer-events-none"></div>

    <div class="relative z-10 w-full max-w-5xl px-12 flex flex-col items-center text-center">
        
        <div class="mb-5 inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-[10px] font-mono uppercase tracking-[0.2em] backdrop-blur-md shadow-[0_0_15px_rgba(59,130,246,0.2)]">
            <carbon-chemistry class="text-xs" />
            The Heart of Software
        </div>
        
        <h1 class="text-5xl md:text-6xl font-black text-white mb-6 tracking-tight leading-tight drop-shadow-2xl">
            The <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-300 drop-shadow-[0_0_25px_rgba(59,130,246,0.6)]">Domain</span> Layer
        </h1>

        <p class="text-base md:text-lg text-gray-400 font-light leading-relaxed max-w-3xl mx-auto mb-10">
            Самая главная часть DDD. Это общий язык с заказчиком (<span class="text-blue-300 font-normal">Ubiquitous Language</span>).
            Здесь живут бизнес-сущности, правила и инварианты, <span class="text-gray-200">полностью очищенные</span> от инфраструктурного шума.
        </p>

        <div class="grid grid-cols-3 gap-5 w-full text-left">
            
            <div class="group p-4 rounded-xl bg-[#151926]/80 border border-blue-500/20 hover:border-blue-500/50 backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(59,130,246,0.1)]">
                <div class="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 mb-3 group-hover:scale-110 transition-transform duration-300 border border-blue-500/10">
                    <carbon-locked class="text-lg" />
                </div>
                <h3 class="text-base font-bold text-gray-100 mb-1">Pure Logic</h3>
                <p class="text-[11px] text-gray-500 leading-relaxed">
                    Zero dependencies. No SQL, no HTTP, no JSON annotations. Just pure Python code.
                </p>
            </div>

            <div class="group p-4 rounded-xl bg-[#151926]/80 border border-blue-500/20 hover:border-cyan-500/50 backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(34,211,238,0.1)]">
                <div class="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 mb-3 group-hover:scale-110 transition-transform duration-300 border border-cyan-500/10">
                    <carbon-chat class="text-lg" />
                </div>
                <h3 class="text-base font-bold text-gray-100 mb-1">Ubiquitous Lang</h3>
                <p class="text-[11px] text-gray-500 leading-relaxed">
                    Code speaks the same language as the business experts. Naming represents reality.
                </p>
            </div>

            <div class="group p-4 rounded-xl bg-[#151926]/80 border border-blue-500/20 hover:border-indigo-500/50 backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(99,102,241,0.1)]">
                <div class="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-3 group-hover:scale-110 transition-transform duration-300 border border-indigo-500/10">
                    <carbon-rule class="text-lg" />
                </div>
                <h3 class="text-base font-bold text-gray-100 mb-1">Invariants</h3>
                <p class="text-[11px] text-gray-500 leading-relaxed">
                    Impossible states are represented by raised Exceptions. Consistency is guaranteed.
                </p>
            </div>

        </div>
    </div>
  </div>
</template>