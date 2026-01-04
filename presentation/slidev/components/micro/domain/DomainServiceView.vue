<script setup lang="ts">
import DomainBaseLayout from './DomainBaseLayout.vue'

const code = `
class DeliveryCostCalculator:
    def calculate(
        self, 
        order: Order, 
        courier: Courier, 
        tariffs: TariffTable
    ) -> Money:
        
        base = tariffs.get_base(order.weight)
        dist = order.destination.distance_to(courier.location)
        
        # Complex domain logic
        multiplier = 1.0
        if order.is_vip:
            multiplier = 0.8
            
        return (base + dist * tariffs.per_km) * multiplier
`
</script>

<template>
  <DomainBaseLayout 
    title="Domain Services"
    subtitle="Stateless Logic"
    icon="i-carbon-calculation"
    description="Логика, которая не принадлежит ни одной конкретной сущности. Стейтлесс операции, часто использующие несколько сущностей для вычислений."
    :rules="[
      'Stateless (нет состояния)',
      'Pure Business Logic (без API/DB)',
      'Оперирует Сущностями и VO',
      'Сложные расчеты / Алгоритмы'
    ]"
    :folders="['services', 'policies', 'logic']"
    :regex="['.*service$', '.*policy$', '.*logic$']"
    code-file-name="src/domain/services/RoutingService.py"
    :code="code"
  />
</template>