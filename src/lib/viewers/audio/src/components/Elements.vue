<template>
  <div class="graph-container">
    <Element
      v-for="(element) in elements"
      :key="element"
      :elId="element"
    ></Element>
  </div>
</template>

<script>
  import Element from './Element.vue'
  export default {
    components: {
      Element
    },
    props: {
      elements: Array
    }
  }
</script>
