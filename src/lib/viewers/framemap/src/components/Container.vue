<template>
  <div class="table">
    <h1>Showing matches for: {{ this.label }}</h1>
    <Graph :elements="elements" :label="this.label" />
    <Loading v-if="!!fetching" />
    <div v-if="!!error" class="flexc">
      <h1>A network connection occurred. Make sure you are correctly configured with a running backend.</h1>
    </div>
  </div>
</template>

<script>
import Loading from './Loading.vue'
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Container',
  components: {
    Loading,
    'Graph': () => import('./Graph.vue')
  },
  props: {
    label: String,
  },
  methods: {
    ...mapActions([
      'fetchElements'
    ])
  },
  computed: {
    ...mapState({
      fetching: 'fetching',
      elements: 'elements',
      error: 'error',
    })
  },
  mounted: function () {
    this.fetchElements()
  }
}
</script>

<style lang="scss">
$primary-color: #e2e2e2;

h1 {
  padding-bottom: 30px;
}

.table {
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  flex: 1;
  min-height: 100%;
}

.graph-container {
  text-align: left;
}

.hidden {
  display: none;
}

</style>
