<template>
  <div class="table">
    <Elements :elements="elements" />
    <Loading v-if="fetching" />
    <div v-if="error" class="flexc">
      <h1>A network connection error occurred. Make sure you are correctly configured.</h1>
    </div>
  </div>
</template>

<script>
import Loading from './Loading.vue'
import { mapState, mapActions } from 'vuex'
import Elements from './Elements.vue'

export default {
  name: 'ElementTable',
  components: {
    Loading,
    Elements
  },
  methods: {
    ...mapActions([
      'fetchElements'
    ])
  },
  computed: {
    ...mapState({
      fetching: state => state.fetching,
      elements: state => state.elements,
      error: state => state.error
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
