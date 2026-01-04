<script setup lang="ts">
import GuardRule from './GuardRule.vue'
import DiagramPlaceholder from './DiagramPlaceholder.vue'
</script>

<template>
  <div class="h-full w-full flex flex-col">
    <h1 class="text-4xl font-bold mb-1">The Application Layer</h1>
    <p class="text-gray-500 mb-6">Orchestration & Use Cases</p>

    <div class="grid grid-cols-2 gap-6 h-full min-h-0">
        <div class="flex flex-col h-full">
            <GuardRule 
                layer="App" 
                :folders="['app', 'use_cases', 'queries', 'workflows', 'interfaces']" 
            />
            <div class="text-sm text-gray-400 mb-4 leading-relaxed">
                Здесь мы определяем, <b>как</b> использовать домен.
                Никакой бизнес-логики, только координация и направление потоков.
            </div>
            <div class="flex-1 min-h-0">
                <DiagramPlaceholder label="Command Flow Diagram" />
            </div>
        </div>

        <div class="space-y-4 overflow-y-auto pr-2 pb-4 h-[400px] scrollbar-thin">
            
            <div class="p-3 bg-[#111] rounded border border-gray-800">
                <h3 class="text-sm font-bold text-purple-400 mb-1">01. Use Cases (Commands)</h3>
                <p class="text-[10px] text-gray-500 mb-2">Write Operations. Changes State.</p>
                <div class="font-mono text-[10px] text-gray-300 bg-[#0B0F19] p-2 rounded">
<pre>@dataclass(frozen=True, slots=True)
class CreateOrderUseCase:
    repo: OrderRepository # Interface

    async def execute(self, cmd: CreateOrderDTO):
        order = Order.create(cmd.items)
        await self.repo.save(order)
        return order.id</pre>
                </div>
            </div>

            <div class="p-3 bg-[#111] rounded border border-gray-800">
                <h3 class="text-sm font-bold text-purple-400 mb-1">02. Queries</h3>
                <p class="text-[10px] text-gray-500 mb-2">Read Operations. Fast track.</p>
                <div class="font-mono text-[10px] text-gray-300 bg-[#0B0F19] p-2 rounded">
<pre>@dataclass(frozen=True, slots=True)
class GetUserOrdersQuery:
    reader: DatabaseReader

    async def execute(self, uid: UUID):
        return await self.reader.fetch(
            "SELECT * FROM orders...", uid
        )</pre>
                </div>
            </div>

            <div class="p-3 bg-[#111] rounded border border-gray-800">
                <h3 class="text-sm font-bold text-purple-400 mb-1">03. Interfaces (Ports)</h3>
                <p class="text-[10px] text-gray-500 mb-2">Contracts for Infrastructure.</p>
                <div class="font-mono text-[10px] text-gray-300 bg-[#0B0F19] p-2 rounded">
<pre>class OrderRepository(Protocol):
    async def save(self, order: Order) -> None:
        ...</pre>
                </div>
            </div>

        </div>
    </div>
  </div>
</template>