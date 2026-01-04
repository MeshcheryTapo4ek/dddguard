<script setup lang="ts">
import GuardRule from './GuardRule.vue'
import DiagramPlaceholder from './DiagramPlaceholder.vue'
</script>

<template>
  <div class="h-full w-full flex flex-col">
    <h1 class="text-4xl font-bold mb-1">Driven Side</h1>
    <p class="text-gray-500 mb-6">Adapters, Ports & DTOs (Outbound)</p>

    <div class="grid grid-cols-2 gap-6 h-full min-h-0">
        
        <div class="flex flex-col h-full">
            <GuardRule 
                layer="Driven" 
                :folders="['adapters/driven', 'dto/driven', 'ports/driven']" 
            />
            
            <div class="flex flex-col gap-2 font-mono text-[10px] text-green-400 bg-green-500/5 p-4 rounded border border-green-500/20 mb-4">
                <div class="flex justify-between items-center opacity-50 text-purple-400">
                    <span>App Logic</span>
                    <span>Interface (Protocol)</span>
                </div>
                <div class="h-4 border-l border-dashed border-gray-600 ml-4"></div>
                <div class="p-2 bg-green-500/10 rounded border border-green-500/30 font-bold">
                    Driven Adapter <span class="font-normal opacity-70">(Repo/Gateway)</span>
                </div>
                <div class="h-4 border-l border-dashed border-gray-600 ml-4"></div>
                 <div class="flex items-center gap-2">
                    <span class="p-1 rounded bg-[#111] border border-gray-700">DTO</span>
                    <span>-></span>
                    <span class="p-1 rounded bg-[#111] border border-gray-700">Port (Redis/SQL)</span>
                </div>
            </div>
            
            <div class="flex-1 min-h-0">
                <DiagramPlaceholder label="Driven Flow Diagram" />
            </div>
        </div>

        <div class="space-y-6">
            <div class="p-4 bg-[#151926] rounded-xl border border-gray-800">
                <h3 class="text-sm font-bold text-green-400 mb-2">Components</h3>
                <ul class="text-xs text-gray-400 space-y-2 list-disc pl-4">
                    <li><b>Adapters:</b> Implement Interfaces. (e.g., `SqlOrderRepo`).</li>
                    <li><b>DTO:</b> Data shapes for external systems. (e.g., `StripeChargeRequest`).</li>
                    <li><b>Ports:</b> Low-level clients. (e.g., `Boto3Client`, `RedisPool`).</li>
                </ul>
            </div>

            <div class="p-4 bg-[#151926] rounded-xl border border-gray-800">
                <h3 class="text-sm font-bold text-green-400 mb-2">Implementation Example</h3>
                <div class="font-mono text-[10px] text-gray-300 bg-[#0B0F19] p-3 rounded border border-gray-800">
<pre># adapters/driven/repo.py
class SqlOrderRepo(OrderRepository): 
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, order: Order):
        # Map Domain Entity -> DB DTO
        dto = OrderDbModel.from_entity(order) 
        self.session.add(dto)</pre>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>