<script setup lang="ts">
// Используем $nav из Slidev для навигации
</script>

<template>
  <div class="h-full flex flex-col justify-center px-10">
    <h1 class="text-4xl font-bold mb-12 flex items-center gap-4">
      <span class="text-gray-500">#</span> 
      Agenda
    </h1>

    <div class="grid grid-cols-2 gap-6">
      
      <div class="group p-6 rounded-xl border border-gray-800 bg-[#111] hover:border-red-500/50 hover:bg-[#151212] transition-all cursor-pointer" @click="$nav.go(3)">
        <div class="text-xs font-mono text-red-500 mb-2 uppercase tracking-widest">Chapter I</div>
        <h3 class="text-xl font-bold text-white mb-1 group-hover:text-red-400 transition-colors">The Problem</h3>
        <p class="text-sm text-gray-500">Chaos vs Order. Why we need rules.</p>
      </div>

      <div class="group p-6 rounded-xl border border-gray-800 bg-[#111] hover:border-blue-500/50 hover:bg-[#121418] transition-all cursor-pointer" @click="$nav.go(6)">
        <div class="text-xs font-mono text-blue-500 mb-2 uppercase tracking-widest">Chapter II</div>
        <h3 class="text-xl font-bold text-white mb-1 group-hover:text-blue-400 transition-colors">The DDD Method</h3>
        <p class="text-sm text-gray-500">Domain -> Logic -> Context Flow.</p>
      </div>

      <div class="group p-6 rounded-xl border border-gray-800 bg-[#111] hover:border-purple-500/50 hover:bg-[#141218] transition-all cursor-pointer" @click="$nav.go(8)">
        <div class="text-xs font-mono text-purple-500 mb-2 uppercase tracking-widest">Chapter III</div>
        <h3 class="text-xl font-bold text-white mb-1 group-hover:text-purple-400 transition-colors">Micro Architecture</h3>
        <p class="text-sm text-gray-500">Anatomy of a Component.</p>
      </div>

      <div class="group p-6 rounded-xl border border-gray-800 bg-[#111] hover:border-green-500/50 hover:bg-[#121614] transition-all cursor-pointer" @click="$nav.go(10)">
        <div class="text-xs font-mono text-green-500 mb-2 uppercase tracking-widest">Chapter IV</div>
        <h3 class="text-xl font-bold text-white mb-1 group-hover:text-green-400 transition-colors">The Toolkit</h3>
        <p class="text-sm text-gray-500">CLI, Linters, and Scaffolding.</p>
      </div>

    </div>
  </div>
</template>