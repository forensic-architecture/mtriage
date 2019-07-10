<template>
  <div class="table">
    <h1>Showing matches for: {{ label }}</h1>
    <Graph :elements="elements" :label="label" :threshold="threshold" />
    <Loading v-if="!!fetching" />
    <div v-if="!!error" class="flexc">
      <h1>A network connection occurred. Make sure you are correctly configured with a running backend.</h1>
    </div>
  </div>
</template>

<script>
import Loading from './Loading.vue'
import Graph from './Graph.vue'
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Container',
  components: {
    Loading,
    Graph
  },
  props: {
    label: String,
    threshold: Number
  },
  methods: {
    ...mapActions([
      'fetchElements',
      'fetchRankedElements'
    ]),
    scroll() {
      window.onscroll = () => {
        let bottomOfWindow = Math.max(window.pageYOffset, document.documentElement.scrollTop, document.body.scrollTop) + window.innerHeight === document.documentElement.offsetHeight
        if (bottomOfWindow) {
         this.fetchRankedElements(this.label)
        }
      }
    }
  },
  computed: {
    ...mapState({
      fetching: 'fetching',
      elements: 'elements',
      error: 'error',
      ranking: 'ranking'
    })
  },
  mounted: function () {
    this.fetchRankedElements(this.label)
    this.scroll()
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
