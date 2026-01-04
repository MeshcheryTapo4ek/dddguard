<script setup lang="ts">
import DomainBaseLayout from './DomainBaseLayout.vue'

const code = `
class LogisticsError(Exception):
    pass

class OrderAlreadyShippedError(LogisticsError):
    def __init__(self, order_id: str):
        super().__init__(f'Order {order_id} is already shipped')

class CapacityExceededError(LogisticsError):
    def __init__(self, current: int, max: int):
        self.current = current
        self.max = max
        super().__init__(
            f'Capacity exceeded: {current}/{max}'
        )
`
</script>

<template>
  <DomainBaseLayout 
    title="Domain Errors"
    subtitle="Business Invariants"
    icon="i-carbon-warning-alt"
    description="Ошибки — это часть языка домена. Они говорят о том, что операция невозможна по бизнес-причинам, а не техническим."
    :rules="[
      'Explicit Naming (не просто Error)',
      'Содержат бизнес-контекст',
      'Наследуются от базового DomainError',
      'Ловятся в App Layer или Controller'
    ]"
    :folders="['errors', 'exceptions']"
    :regex="['.*error$', '.*exception$']"
    code-file-name="src/domain/errors.py"
    :code="code"
  />
</template>