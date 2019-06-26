<template>
  <div class="graph-container">
    <Element
      v-for="(element) in elements"
      :key="element['Id']"
      :elementId="element['Id']"
      :audio="element['Media']['all'][0]"
      :onsets="element['Media']['all'][1]"
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
