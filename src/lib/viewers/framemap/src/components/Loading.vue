<template>
  <div class="flex-fill flex-center">
    <v-progress-circular
      color="rgb(204, 22, 22)"
      :size="70"
      :width="7"
      indeterminate
    />
  </div>
</template>

<script>
export default {
  name: 'Loading',
  props: {
    version: String
  }
}
</script>

<style lang="scss">
$primary-color: #e2e2e2;

.flex-fill {
  display: flex;
  background-color: transparent;
  flex: 1;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
