<template>
  <div class="h-full w-full flex flex-col font-mono text-[10px] leading-4 text-gray-400">
    <div class="mb-2 shrink-0 flex items-baseline justify-between border-b border-gray-800 pb-2">
        <div class="flex items-baseline gap-3">
            <h1 class="text-2xl font-bold text-white font-sans">The Physical Structure</h1>
            <span class="text-gray-600 font-sans text-xs">/ File System Mapping Strategy</span>
        </div>
    </div>

    <div class="grid grid-cols-[1.6fr_1fr] gap-2 h-full min-h-0">
        
        <div class="bg-[#0f1115] rounded-lg border border-gray-800 p-2 shadow-inner flex flex-col">
            <div class="text-gray-500 mb-1 border-b border-gray-800 pb-1 flex justify-between items-center shrink-0">
                <span class="text-white font-bold text-[10px]">src/&lt;context&gt;/</span>
                <span class="text-[8px] bg-blue-500/10 text-blue-400 px-1.5 rounded border border-blue-500/20">INTERNAL</span>
            </div>

            <div class="flex-1 flex flex-col min-h-0 gap-1 overflow-y-auto custom-scroll pr-1">
                <div class="relative group">
                    <div class="absolute left-0 top-0 bottom-0 w-[1px] bg-blue-500/20"></div>
                    <div class="flex items-center text-blue-400 font-bold hover:text-blue-300 transition-colors">
                        <span class="w-4 text-gray-700">├─</span> domain/
                        <span class="ml-2 text-[9px] text-gray-600 font-normal italic"># Pure Business Logic</span>
                    </div>
                    <div class="pl-4 ml-[1px] border-l border-dashed border-gray-800">
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">aggregates/</span> <span class="tree-comment"># Rules & Consistency</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">entities/</span> <span class="tree-comment"># Identity objects</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">vo/</span> <span class="tree-comment"># Immutable values</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">services/</span> <span class="tree-comment"># Stateless ops</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">events/</span> <span class="tree-comment"># Domain facts</span></div>
                        <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">errors/</span> <span class="tree-comment"># Exceptions</span></div>
                    </div>
                </div>

                <div class="relative group">
                    <div class="absolute left-0 top-0 bottom-0 w-[1px] bg-purple-500/20"></div>
                    <div class="flex items-center text-purple-400 font-bold hover:text-purple-300 transition-colors">
                        <span class="w-4 text-gray-700">├─</span> app/
                        <span class="ml-2 text-[9px] text-gray-600 font-normal italic"># Orchestration</span>
                    </div>
                    <div class="pl-4 ml-[1px] border-l border-dashed border-gray-800">
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">use_cases/</span> <span class="tree-comment"># Commands (Write)</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">queries/</span> <span class="tree-comment"># Data reading</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">workflows/</span> <span class="tree-comment"># Sagas</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">handlers/</span> <span class="tree-comment"># Event reactions</span></div>
                        <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">interfaces/</span> <span class="tree-comment"># Contracts</span></div>
                    </div>
                </div>

                <div class="relative group">
                    <div class="absolute left-0 top-0 bottom-0 w-[1px] bg-orange-500/20"></div>
                    <div class="flex items-center text-orange-400 font-bold hover:text-orange-300 transition-colors">
                        <span class="w-4 text-gray-700">└─</span> adapters/
                        <span class="ml-2 text-[9px] text-gray-600 font-normal italic"># Translation</span>
                    </div>
                    <div class="pl-4 ml-[1px] border-l border-dashed border-gray-800">
                        <div class="flex flex-col group/item">
                            <div class="flex items-center">
                                <span class="tree-dash">├─</span> 
                                <span class="text-gray-300 font-bold">driving/</span> 
                                <span class="ml-2 text-[9px] text-orange-400/70"># Drives App</span>
                            </div>
                            <div class="pl-4 ml-[1px] border-l border-dashed border-gray-800/50">
                                <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">controllers/</span> <span class="tree-comment"># API</span></div>
                                <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">consumers/</span> <span class="tree-comment"># Kafka/Rabbit</span></div>
                                <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">commands/</span> <span class="tree-comment"># CLI</span></div>
                            </div>
                        </div>

                        <div class="flex flex-col group/item">
                            <div class="flex items-center">
                                <span class="tree-dash">└─</span> 
                                <span class="text-gray-300 font-bold">driven/</span>
                                <span class="ml-2 text-[9px] text-green-400/70"># Driven by App</span>
                            </div>
                            <div class="pl-4 ml-[1px] border-l border-dashed border-gray-800/50">
                                <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">repositories/</span> <span class="tree-comment"># DB Access</span></div>
                                <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">gateways/</span> <span class="tree-comment"># Ext API</span></div>
                                <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">publishers/</span> <span class="tree-comment"># Msg Broker</span></div>
                                <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">acl/</span> <span class="tree-comment"># Anti-Corruption</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-2 h-full min-h-0">
            
            <div class="bg-[#0f1115] rounded-lg border border-gray-800 p-2 shadow-inner flex flex-col flex-1">
                <div class="text-gray-500 mb-1 border-b border-gray-800 pb-1 flex justify-between items-center shrink-0">
                     <span class="text-white font-bold text-[10px]">src/&lt;context&gt;/</span>
                     <span class="text-[8px] bg-green-500/10 text-green-400 px-1.5 rounded border border-green-500/20">IO LAYER</span>
                </div>

                <div class="flex-1 flex flex-col gap-1 overflow-y-auto custom-scroll">
                    <div>
                        <div class="text-green-400 font-bold"><span class="w-4 inline-block text-gray-700">├─</span> dto/</div>
                        <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5">
                            <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">driving/</span> <span class="tree-comment"># Input</span></div>
                            <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">driven/</span>  <span class="tree-comment"># Output</span></div>
                        </div>
                    </div>

                    <div>
                        <div class="text-green-400 font-bold"><span class="w-4 inline-block text-gray-700">├─</span> ports/</div>
                        <div class="pl-4 border-l border-dashed border-gray-800 ml-1.5">
                            <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">driving/</span> <span class="tree-comment"># API/CLI</span></div>
                            <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">driven/</span>  <span class="tree-comment"># DB/Redis</span></div>
                        </div>
                    </div>

                    <div class="mt-0.5 pt-0.5 border-t border-gray-800/50">
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder text-red-300 font-bold">composition.py</span> <span class="tree-comment"># Wiring</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">bootstrap.py</span></div>
                        <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">config.py</span></div>
                        <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">logger.py</span></div>
                    </div>
                </div>
            </div>

            <div class="bg-[#1a1212] rounded-lg border border-red-500/20 p-2 shadow-inner flex-1 flex flex-col">
                <div class="text-gray-500 mb-1 border-b border-red-900/30 pb-1 flex justify-between items-center shrink-0">
                     <span class="text-white font-bold text-[10px]">src/</span>
                     <span class="text-[8px] bg-red-500/10 text-red-400 px-1.5 rounded border border-red-500/20">GLOBAL</span>
                </div>
                
                <div class="flex-1 flex flex-col justify-start gap-1 overflow-y-auto custom-scroll">
                    <div>
                        <div class="text-gray-400 font-bold"><span class="w-4 inline-block text-gray-700">├─</span> shared/</div>
                        <div class="pl-4 border-l border-dashed border-red-900/30 ml-1.5">
                            <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">logging_setup.py</span></div>
                            <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder opacity-50">...</span></div>
                        </div>
                    </div>

                    <div>
                        <div class="text-red-400 font-bold"><span class="w-4 inline-block text-gray-700">└─</span> root/</div>
                        <div class="pl-4 border-l border-dashed border-red-900/30 ml-1.5">
                            <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">composition.py</span></div>
                            <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">app_config.py</span></div>
                            <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">bootstrap.py</span></div>
                            <div class="tree-item"><span class="tree-dash">├─</span> <span class="tree-folder">logger.py</span></div>
                            <div class="tree-item"><span class="tree-dash">└─</span> <span class="tree-folder">main.py</span></div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 3px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
}

.tree-item {
    display: flex;
    align-items: center;
    min-height: 14px;
}
.tree-dash {
    color: #4b5563; /* gray-600 */
    width: 1.25rem;
    display: inline-block;
    flex-shrink: 0;
}
.tree-folder {
    color: #d1d5db; /* gray-300 */
    white-space: nowrap;
}
.tree-comment {
    color: #4b5563; /* gray-600 */
    margin-left: 0.5rem;
    font-size: 0.55rem;
    font-style: italic;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    opacity: 0.8;
}
</style>