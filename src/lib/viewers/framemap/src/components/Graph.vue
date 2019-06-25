<template>
  <div class="table">
    <GraphItems :items="items" />
    <Loading v-if="!fetching" />
    <div v-if="!!error" class="flexc">
      <h1>A network connection occurred. Make sure you are correctly configured with a running backend.</h1>
    </div>
  </div>
</template>

<script>
import Loading from './Loading.vue'
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Graph',
  components: {
    Loading,
    'GraphItems': () => import('./GraphItems.vue')
  },
  methods: {
    ...mapActions([
      'fetchItems'
    ])
  },
  computed: {
    ...mapState({
      fetching: 'fetching',
      items: state => state.pages ? state.pages[0] : [],
      error: 'error'
    })
  },
  mounted: function () {
    // this.fetchItems()
  }
}
</script>

<style lang="scss">
$primary-color: #e2e2e2;

h1 {
  color: white;
  max-width: 800px;
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
