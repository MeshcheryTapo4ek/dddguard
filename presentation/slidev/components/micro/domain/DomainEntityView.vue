<script setup lang="ts">
import DomainBaseLayout from './DomainBaseLayout.vue'

const code = `
@dataclass(kw_only=True)
class Courier:
    id: CourierID = field(default_factory=uuid4)
    name: str
    status: CourierStatus = CourierStatus.OFFLINE
    location: Coordinates | None = None

    def go_online(self, location: Coordinates):
        self.location = location
        self.status = CourierStatus.READY
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, Courier) and self.id == other.id
`
</script>

<template>
  <DomainBaseLayout 
    title="Entities"
    subtitle="Identity & Lifecycle"
    icon="i-carbon-id-management"
    description="Объекты с жизненным циклом. Главное отличие — наличие уникального ID. Атрибуты могут меняться, но ID остается неизменным. Это 'главные герои' вашего приложения."
    :rules="[
      'Identity Equality (сравнение по ID)',
      'Mutable State (состояние меняется методами)',
      'Invariants Check (защита целостности)',
      'Содержат VO и другие примитивы'
    ]"
    :folders="['entities', 'models']"
    :regex="['.*entity$', '.*ent$', '.*model$']"
    code-file-name="src/domain/entities/Courier.py"
    :code="code"
  />
</template>