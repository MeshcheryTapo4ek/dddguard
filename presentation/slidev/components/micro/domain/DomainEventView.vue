<script setup lang="ts">
import DomainBaseLayout from './DomainBaseLayout.vue'

const code = `
@dataclass(frozen=True)
class OrderStatusChanged(DomainEvent):
    order_id: OrderID
    old_status: OrderStatus
    new_status: OrderStatus
    timestamp: datetime = field(default_factory=now)

@dataclass(frozen=True)
class CourierAssigned(DomainEvent):
    order_id: OrderID
    courier_id: CourierID
`
</script>

<template>
  <DomainBaseLayout 
    title="Domain Events"
    subtitle="Facts of the Past"
    icon="i-carbon-bullhorn"
    description="Декларативное объявление о том, что что-то важное произошло. Развязывает логику. Агрегаты публикуют события, а не вызывают сервисы напрямую."
    :rules="[
      'Immutable (факт нельзя изменить)',
      'Named in Past Tense (Shipped, Created)',
      'Carries minimal required data (IDs)',
      'Triggers Side Effects (в других слоях)'
    ]"
    :folders="['events', 'domain_events']"
    :regex="['.*event$', '.*occurred$']"
    code-file-name="src/domain/events/order_events.py"
    :code="code"
  />
</template>