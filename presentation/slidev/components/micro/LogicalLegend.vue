<template>
  <div class="mt-8 flex flex-col gap-4 text-sm font-mono text-gray-500">
    <div class="flex items-center gap-3">
      <div class="w-3 h-3 rounded-full bg-[#2996CC] shadow-[0_0_10px_rgba(41,150,204,0.3)]"></div>
      <span class="text-gray-300">Domain (Pure)</span>
    </div>
    <div class="flex items-center gap-3">
      <div class="w-3 h-3 rounded-full bg-[#B77BFF] shadow-[0_0_10px_rgba(183,123,255,0.3)]"></div>
      <span class="text-gray-300">App (Orchestration)</span>
    </div>
    <div class="flex items-center gap-3">
      <div class="w-3 h-3 bg-gradient-to-r from-orange-500 to-green-500 rounded-sm opacity-80"></div>
      <span class="text-gray-400">Adapters (Dirty IO)</span>
    </div>
  </div>
</template>