<script setup lang="ts">
import DomainBaseLayout from './DomainBaseLayout.vue'

const code = `
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: Currency  # Enum

    def __post_init__(self):
        if self.amount < 0:
            raise NegativeMoneyError(self.amount)

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise CurrencyMismatchError()
        return Money(self.amount + other.amount, self.currency)

# Usage
price = Money(100, 'USD')
`
</script>

<template>
  <DomainBaseLayout 
    title="Value Objects"
    subtitle="Immutable Measures"
    icon="i-carbon-text-link"
    description="Объекты, которые не несут смысла сами по себе, но описывают свойства других объектов. Не имеют жизненного цикла. Два VO равны, если равны их значения."
    :rules="[
      'Immutable (неизменяемые)',
      'Structural Equality (сравнение по полям)',
      'Self-Validation (валидация в __init__)',
      'Pure Functions (без сайд-эффектов)'
    ]"
    :folders="['vo', 'enums', 'types']"
    :regex="['.*vo$', '.*value$', '.*enum$']"
    code-file-name="src/domain/vo/Money.py"
    :code="code"
  />
</template>