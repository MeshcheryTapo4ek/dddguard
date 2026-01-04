<script setup lang="ts">
import GuardRule from './GuardRule.vue'
import DiagramPlaceholder from './DiagramPlaceholder.vue'
</script>

<template>
  <div class="h-full w-full flex flex-col">
    <h1 class="text-4xl font-bold mb-1">Composition & Shared</h1>
    <p class="text-gray-500 mb-6">Wiring it all together</p>

    <div class="grid grid-cols-2 gap-6 h-full min-h-0">
        
        <div class="flex flex-col h-full">
            <GuardRule 
                layer="Composition" 
                :folders="['composition.py', 'root', 'shared']" 
            />
            <div class="text-sm text-gray-400 mb-4 leading-relaxed">
                <b>Composition Root:</b> Единственное место, где компоненты узнают друг о друге. DI Container setup.
                <br><br>
                <b>Shared:</b> Ядро переиспользуемого кода (Kernel). Статичные утилиты и общие типы.
            </div>
            <div class="flex-1 min-h-0">
                <DiagramPlaceholder label="Dependency Injection Diagram" />
            </div>
        </div>

        <div class="space-y-4">
            
            <div class="p-4 bg-[#151926] rounded-xl border border-gray-800">
                <h3 class="text-sm font-bold text-red-400 mb-2">Composition Root</h3>
                <div class="font-mono text-[10px] text-gray-300 bg-[#0B0F19] p-3 rounded border border-gray-800">
<pre># root/composition.py
def build_container():
    c = Container()
    
    # Wire Contexts
    c.register(OrderRepository, SqlOrderRepo)
    c.register(PaymentGateway, StripeAdapter)
    
    return c</pre>
                </div>
            </div>

            <div class="p-4 bg-[#151926] rounded-xl border border-gray-800">
                <h3 class="text-sm font-bold text-gray-400 mb-2">Shared Kernel</h3>
                <ul class="text-xs text-gray-500 space-y-1 list-disc pl-4">
                    <li>`shared/domain`: Base Entity, ValueObject classes.</li>
                    <li>`shared/ports`: Generic clients (e.g. Kafka wrapper).</li>
                </ul>
            </div>

             <div class="p-4 bg-[#151926] rounded-xl border border-gray-800">
                <h3 class="text-sm font-bold text-gray-400 mb-2">Entrypoints</h3>
                <ul class="text-xs text-gray-500 space-y-1 list-disc pl-4">
                    <li>`main.py` -> Runs HTTP Server</li>
                    <li>`cli.py` -> Runs Console App</li>
                </ul>
            </div>

        </div>
    </div>
  </div>
</template>