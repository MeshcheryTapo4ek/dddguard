<script setup lang="ts">
import DomainBaseLayout from './DomainBaseLayout.vue'

const code = `
@dataclass
class Order(AggregateRoot):
    id: OrderID
    items: list[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.NEW
    
    # Business Logic Entry Point
    def add_product(self, product: Product, qty: int):
        if self.status != OrderStatus.NEW:
            raise OrderModificationError('Order is locked')
            
        line = OrderLine(product.id, qty, product.price)
        self.items.append(line)
        
        # Internal consistency calculation
        self._recalculate_total()
`
</script>

<template>
  <DomainBaseLayout 
    title="Aggregate Roots"
    subtitle="Consistency Boundary"
    icon="i-carbon-network-3"
    description="Точка входа для бизнес-логики. Объединяет группу связанных сущностей в единый модуль согласованности (Cluster). Внешний мир общается только с Root."
    :rules="[
      'Transactional Boundary (сохраняем целиком)',
      'Cascading State Changes',
      'Запрет прямого доступа к items',
      'Гарантирует инварианты группы'
    ]"
    :folders="['aggregates', 'roots']"
    :regex="['.*aggregate$', '.*root$']"
    code-file-name="src/domain/aggregates/Order.py"
    :code="code"
  />
</template>