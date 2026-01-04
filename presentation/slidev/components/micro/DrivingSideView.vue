<script setup lang="ts">
import GuardRule from './GuardRule.vue'
import DiagramPlaceholder from './DiagramPlaceholder.vue'
</script>

<template>
  <div class="h-full w-full flex flex-col">
    <h1 class="text-4xl font-bold mb-1">Driving Side</h1>
    <p class="text-gray-500 mb-6">Entry Points & Control (Inbound)</p>

    <div class="grid grid-cols-2 gap-6 h-full min-h-0">
        
        <div class="flex flex-col h-full">
            <GuardRule 
                layer="Driving" 
                :folders="['adapters/driving', 'dto/driving', 'ports/driving']" 
            />
            
            <div class="flex flex-col gap-2 font-mono text-[10px] text-blue-400 bg-blue-500/5 p-4 rounded border border-blue-500/20 mb-4">
                 <div class="flex items-center gap-2">
                    <span class="p-1 rounded bg-[#111] border border-gray-700">External</span>
                    <span>-></span>
                    <span class="p-1 rounded bg-[#111] border border-gray-700">Port (FastAPI)</span>
                </div>
                <div class="h-4 border-l border-dashed border-gray-600 ml-4"></div>
                <div class="flex items-center gap-2">
                     <span class="p-1 rounded bg-[#111] border border-gray-700">DTO (Request)</span>
                </div>
                <div class="h-4 border-l border-dashed border-gray-600 ml-4"></div>
                <div class="p-2 bg-blue-500/10 rounded border border-blue-500/30 font-bold">
                    Driving Adapter <span class="font-normal opacity-70">(Controller)</span>
                </div>
                <div class="h-4 border-l border-dashed border-gray-600 ml-4"></div>
                <div class="opacity-50 text-purple-400">App (Use Case)</div>
            </div>

            <div class="flex-1 min-h-0">
                <DiagramPlaceholder label="Driving Flow Diagram" />
            </div>
        </div>

        <div class="space-y-6">
            <div class="p-4 bg-[#151926] rounded-xl border border-gray-800">
                <h3 class="text-sm font-bold text-blue-400 mb-2">Components</h3>
                <ul class="text-xs text-gray-400 space-y-2 list-disc pl-4">
                    <li><b>Ports:</b> Framework entrypoints. (e.g., `FastAPI`, `Click`).</li>
                    <li><b>DTO:</b> Input Contracts. (e.g., `CreateOrderRequest` - Pydantic).</li>
                    <li><b>Adapters:</b> Controllers. Convert DTO -> Domain/App calls.</li>
                </ul>
            </div>

            <div class="p-4 bg-[#151926] rounded-xl border border-gray-800">
                <h3 class="text-sm font-bold text-blue-400 mb-2">Implementation Example</h3>
                <div class="font-mono text-[10px] text-gray-300 bg-[#0B0F19] p-3 rounded border border-gray-800">
<pre># adapters/driving/api.py
@router.post("/orders") # Port
async def create(
    body: CreateOrderRequest, # DTO
    use_case: CreateOrderUC = Depends()
):
    try:
        # Adapter Logic
        return await use_case.execute(body)
    except DomainError as e:
        raise HTTPException(400, str(e))</pre>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>