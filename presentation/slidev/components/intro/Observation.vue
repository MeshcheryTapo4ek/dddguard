<template>
  <div class="h-full w-full relative flex flex-col justify-center items-center px-6">
    
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
    <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_top_right,rgba(239,68,68,0.1)_0%,transparent_50%)]"></div>

    <div class="relative z-10 w-full max-w-6xl mx-auto">
      
      <div class="flex items-center gap-4 mb-12 justify-center opacity-80">
        <div class="h-px w-12 bg-gradient-to-r from-transparent to-red-500"></div>
        <span class="text-red-400 font-mono text-xs tracking-[0.3em] uppercase">Phase 1: The Threshold</span>
        <div class="h-px w-12 bg-gradient-to-l from-transparent to-red-500"></div>
      </div>

      <div class="grid grid-cols-2 gap-16 items-center">
        
        <div class="text-left space-y-8">
          <h1 class="text-5xl font-bold leading-tight tracking-tight">
            "The first 1000 lines<br>
            always look <span class="text-gray-200">perfect</span>, <span class="text-red-500 font-black">BUT...</span>"
          </h1>

          <div class="relative pl-6 border-l-2 border-red-500/30">
            <p class="text-xl text-gray-200 font-light leading-relaxed mb-4">
               ...once you cross that threshold, you start <span class="text-red-400 font-bold">regretting</span> every early decision.
            </p>
            
            <p class="text-sm text-gray-400 leading-relaxed max-w-md">
              Связность растет экспоненциально. Проект превращается в "черный ящик", полный неявных зависимостей, который страшно трогать.
            </p>
          </div>
          
          <div class="flex items-center gap-3 text-xs font-mono text-red-400/60 pt-4 opacity-70">
             <carbon-warning-filled /> SYSTEM INTEGRITY COMPROMISED
          </div>
        </div>
        
        <div class="relative group">
          <div class="absolute -inset-0.5 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-2xl blur opacity-40 group-hover:opacity-60 transition duration-1000"></div>
          
          <div class="relative p-8 bg-[#0B0F19]/90 backdrop-blur-sm rounded-2xl border border-red-500/20 shadow-2xl">
            
            <div class="flex items-center justify-between mb-8 border-b border-red-500/10 pb-4">
               <div class="flex items-center gap-2 text-red-400 font-mono text-[10px] uppercase tracking-widest">
                  <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                  Diagnostics Report
               </div>
               <span class="font-mono text-[10px] text-red-500/50">ERR_ARCH_DECAY</span>
            </div>
            
            <ul class="space-y-6">
              
              <li class="flex items-start gap-4 group/item">
                  <div class="mt-1 p-2 rounded bg-red-500/10 text-red-400 group-hover/item:bg-red-500/20 transition-colors">
                    <carbon-network-4 class="text-lg" />
                  </div>
                  <div>
                    <strong class="text-gray-200 block text-sm font-bold mb-1 group-hover/item:text-red-300 transition-colors">Implicit Coupling</strong>
                    <span class="text-xs text-gray-500 leading-relaxed block font-mono">
                      Вы меняете одну строку в "простом" хелпере, а ломается модуль на другом конце системы.
                    </span>
                  </div>
              </li>

              <li class="flex items-start gap-4 group/item">
                  <div class="mt-1 p-2 rounded bg-orange-500/10 text-orange-400 group-hover/item:bg-orange-500/20 transition-colors">
                    <carbon-user-avatar-filled-alt class="text-lg" />
                  </div>
                  <div>
                    <strong class="text-gray-200 block text-sm font-bold mb-1 group-hover/item:text-orange-300 transition-colors">Cognitive Overflow</strong>
                    <span class="text-xs text-gray-500 leading-relaxed block font-mono">
                      Ментальная модель проекта больше не помещается в RAM разработчика. Ошибки становятся неизбежными.
                    </span>
                  </div>
              </li>

              <li class="flex items-start gap-4 group/item">
                  <div class="mt-1 p-2 rounded bg-rose-500/10 text-rose-400 group-hover/item:bg-rose-500/20 transition-colors">
                    <carbon-code-reference class="text-lg" />
                  </div>
                  <div>
                    <strong class="text-gray-200 block text-sm font-bold mb-1 group-hover/item:text-rose-300 transition-colors">Code Pollution</strong>
                    <span class="text-xs text-gray-500 leading-relaxed block font-mono">
                      Разработчики (и агенты) тратят ресурсы не на бизнес-задачи, а на распутывание "спагетти-кода".
                    </span>
                  </div>
              </li>

            </ul>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>