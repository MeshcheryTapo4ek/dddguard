<template>
  <div class="slidev-layout section h-full w-full flex flex-col justify-center items-center bg-[#0B0F19] text-center relative overflow-hidden">
    <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-gray-800/20 via-[#0B0F19] to-[#0B0F19]"></div>
    
    <div class="relative z-10 max-w-4xl">
      <div class="mb-6 font-mono text-sm tracking-[0.2em] uppercase opacity-50">
        <slot name="subtitle">Chapter</slot>
      </div>
      
      <h1 class="text-6xl font-black text-white mb-8 leading-tight tracking-tight">
        <slot />
      </h1>
      
      <div class="w-24 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent mx-auto opacity-50"></div>
    </div>
  </div>
</template>