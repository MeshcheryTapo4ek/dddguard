<script setup lang="ts">
// Static view
</script>

<template>
  <div class="h-full w-full flex flex-col justify-center px-12 relative">
    
    <div class="mb-4 text-center relative z-10"> 
       <div class="flex items-center gap-4 mb-1 justify-center opacity-80">
        <div class="h-px w-10 bg-gradient-to-r from-transparent to-yellow-500"></div>
        <span class="text-yellow-400 font-mono text-[10px] tracking-[0.2em] uppercase">Why This Matters</span>
        <div class="h-px w-10 bg-gradient-to-l from-transparent to-yellow-500"></div>
      </div>
      
      <h2 class="text-3xl font-bold text-white mb-1 tracking-tight">
        Architectural <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">Guarantees</span>
      </h2>
      <p class="text-gray-400 text-xs font-light">
        Система проектируется так, чтобы стоимость изменений оставалась линейной.
      </p>
    </div>

    <div class="grid grid-cols-2 gap-3 relative z-10">

      <div class="group relative p-3 rounded-xl bg-[#151926] border border-blue-500/20 hover:border-blue-500/50 transition-all duration-300 hover:-translate-y-1">
        <div class="flex items-start gap-3">
            <div class="mt-0.5 p-1.5 rounded-lg bg-blue-500/10 text-blue-400 shrink-0">
                <carbon-compass class="text-lg" />
            </div>
            <div>
                <h3 class="text-sm font-bold text-gray-200 mb-0.5">Structural Locality</h3>
                <p class="text-[11px] text-gray-400 leading-tight font-mono">
                  Ошибка в расчетах? -> Смотрим <b>Domain</b>.<br>
                  Ошибка в SQL? -> Смотрим <b>Adapters</b>.<br>
                  <span class="opacity-70 mt-1 block leading-tight">Мы всегда знаем точный слой для отладки, исключая блуждание по коду.</span>
                </p>
            </div>
        </div>
      </div>

      <div class="group relative p-3 rounded-xl bg-[#151926] border border-purple-500/20 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
         <div class="flex items-start gap-3">
            <div class="mt-0.5 p-1.5 rounded-lg bg-purple-500/10 text-purple-400 shrink-0">
                <carbon-layers class="text-lg" />
            </div>
            <div>
                <h3 class="text-sm font-bold text-gray-200 mb-0.5">Bounded Complexity</h3>
                <p class="text-[11px] text-gray-400 leading-tight font-mono">
                  Стек вызовов ограничен: <b>Domain -> App -> Infra</b>.<br>
                  Рост проекта не увеличивает глубину вложенности. Спагетти-код физически негде разместить.
                </p>
            </div>
        </div>
      </div>

      <div class="group relative p-3 rounded-xl bg-[#151926] border border-orange-500/20 hover:border-orange-500/50 transition-all duration-300 hover:-translate-y-1">
         <div class="flex items-start gap-3">
            <div class="mt-0.5 p-1.5 rounded-lg bg-orange-500/10 text-orange-400 shrink-0">
                <carbon-ibm-cloud-subnets class="text-lg" />
            </div>
            <div>
                <h3 class="text-sm font-bold text-gray-200 mb-0.5">Context Autonomy</h3>
                <p class="text-[11px] text-gray-400 leading-tight font-mono">
                  Модули (Contexts) тестируются изолированно.<br>
                  Вы можете рефакторить "Склад", гарантированно не ломая "Бухгалтерию". Нулевой риск регрессии.
                </p>
            </div>
        </div>
      </div>

      <div class="group relative p-3 rounded-xl bg-[#151926] border border-green-500/20 hover:border-green-500/50 transition-all duration-300 hover:-translate-y-1">
         <div class="flex items-start gap-3">
            <div class="mt-0.5 p-1.5 rounded-lg bg-green-500/10 text-green-400 shrink-0">
                <carbon-plug class="text-lg" />
            </div>
            <div>
                <h3 class="text-sm font-bold text-gray-200 mb-0.5">Vendor Independence</h3>
                <p class="text-[11px] text-gray-400 leading-tight font-mono">
                  Технологии - это детали реализации (Plugins).<br>
                  Смена базы данных (Postgres -> Mongo) или фреймворка - это локальная задача слоя адаптеров.
                </p>
            </div>
        </div>
      </div>

    </div>
  </div>
</template>