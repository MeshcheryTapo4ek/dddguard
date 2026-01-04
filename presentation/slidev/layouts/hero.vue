<template>
  <div class="slidev-layout hero h-full w-full bg-[#0B0F19] text-white relative overflow-hidden">
    
    <div class="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>

    <div class="grid grid-cols-2 h-full items-center gap-12 px-12 relative z-10">

      <div class="flex flex-col items-start text-left z-20">
        <div class="px-3 py-1 mb-6 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-300 text-xs font-mono tracking-widest uppercase">
          Architecture as Code
        </div>
        
        <h1 class="text-7xl font-black leading-tight tracking-tighter mb-6">
          dddguard
        </h1>
        
        <p class="text-xl text-gray-400 font-light leading-relaxed mb-8 max-w-lg">
          The all-in-one toolkit for 
          <span class="text-white font-medium">Domain-Driven Design</span>.
          <br class="mb-4 block" />
          Unifies <span class="text-green-400 font-mono text-base">Smart Context Scanner</span>, 
          <span class="text-blue-400 font-mono text-base">Architecture Linter</span>, 
          <span class="text-purple-400 font-mono text-base">Scaffolder</span>, and 
          <span class="text-orange-400 font-mono text-base">Draw.io Visualizer</span>.
        </p>

        <div class="flex items-center gap-4">
          <div class="group relative flex items-center gap-3 px-5 py-3 rounded-lg bg-[#151926] border border-gray-800 hover:border-blue-500/50 transition-all cursor-pointer">
            <span class="text-gray-500 select-none">$</span>
            <span class="font-mono text-green-300">uv tool install dddguard</span>
            <div class="opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                <carbon-copy class="text-gray-500 text-sm" />
            </div>
          </div>
        </div>
        
        <div class="mt-12 flex gap-6 text-xs font-mono opacity-40">
          <span>MIT License</span>
          <span>Python 3.10+</span>
        </div>
      </div>

      <div class="relative transform scale-95">
        <div class="rounded-xl bg-[#0f111a] border border-gray-800 shadow-2xl overflow-hidden font-mono text-xs leading-relaxed transform rotate-1 hover:rotate-0 transition-transform duration-500">
          <div class="flex items-center px-4 py-3 bg-[#1a1d2d] border-b border-gray-800 gap-2">
            <div class="w-3 h-3 rounded-full bg-red-500/50"></div>
            <div class="w-3 h-3 rounded-full bg-yellow-500/50"></div>
            <div class="w-3 h-3 rounded-full bg-green-500/50"></div>
            <div class="ml-auto text-gray-600">bash — 80x24</div>
          </div>
          <div class="p-6 text-gray-300">
            <div class="flex gap-2 mb-2">
              <span class="text-green-400">➜</span>
              <span class="text-blue-400">~</span>
              <span>dddguard scan --format llm</span>
            </div>
            <div class="mb-4 text-gray-500">
              &gt; Analyzing codebase...<br />
              &gt; 6 Contexts found<br />
              &gt; <span class="text-green-400">Generated context_dump.xml (142kb)</span>
            </div>
            
            <div class="flex gap-2 mb-2">
              <span class="text-green-400">➜</span>
              <span class="text-blue-400">~</span>
              <span>dddguard draw</span>
            </div>
            <div class="mb-4 text-gray-500">
              &gt; Mapping dependencies...<br />
              &gt; <span class="text-blue-400">Saved architecture.drawio</span>
            </div>

            <div class="flex gap-2 mb-2">
              <span class="text-green-400">➜</span>
              <span class="text-blue-400">~</span>
              <span>dddguard lint</span>
            </div>
            <div class="pl-2 border-l-2 border-red-500/30 text-red-300 bg-red-500/5 p-2 rounded mb-2">
              ✖ Violation: 'infrastructure' imported in 'domain'
            </div>
          </div>
        </div>
        <div class="absolute -z-10 -bottom-6 -right-6 w-full h-full border border-gray-700/30 rounded-xl"></div>
      </div>
    </div>
  </div>
</template>