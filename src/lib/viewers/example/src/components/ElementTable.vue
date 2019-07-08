<template>
  <div>
    <h1>Selected</h1>
    <hr/>
    <div v-for="elements in elementmap.Selected">
      <div v-if="elements.Elements !== null">
        <h2>Context: {{elements.Context}}</h2>
        <h2>Component: {{elements.Component}}</h2>
        <div class="table">
          <Elements :elements="elements.Elements" />
          <Loading v-if="fetching" />
          <div v-if="error" class="flexc">
            <h1>A network connection error occurred. Make sure you are correctly configured.</h1>
          </div>
        </div>
      </div>
    </div>
    <h1>Analysed</h1>
    <hr/>
    <div v-for="elements in elementmap.Analysed">
      <div v-if="elements.Elements !== null">
        <h2>Context: {{elements.Context}}</h2>
        <h2>Component: {{elements.Component}}</h2>
        <div class="table">
          <Elements :elements="elements.Elements" />
          <Loading v-if="fetching" />
          <div v-if="error" class="flexc">
            <h1>A network connection error occurred. Make sure you are correctly configured.</h1>
          </div>
        </div>
      </div>
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
      elementmap: state => state.elementmap,
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

h1, h2 {
  text-align: left;
}

hr {
  margin: 15px 0;
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
