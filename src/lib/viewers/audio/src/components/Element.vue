<template>
  <div
    :class="containerClasses"
    :key="this.state.containerKey"
  >
    <div class="graph-item-body" v-on:click="clickHandler">
      <div class="graph-item-title"><h3>{{ elId }}</h3></div>
      <div class="graph-item-content" v-if="element != null">
        <h4>Media:</h4>
        <div class=graph-item-list>
          <p v-for="(mediaItem) in media" >{{ mediaItem }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import types from '../mutation-types'
export default {
  name: 'GraphItem',
  props: {
    elId: String
  },
  computed: {
    containerClasses: function() {
      if (this.state.expanded) {
        return 'graph-item-container expanded'
      } else {
        return 'graph-item-container'
      }
    },
    ...mapState({
      fetching: state => state.fetching,
      error: state => state.error,
      element: function (state) {
        console.log("changed")
        return state.elements[this.elId]
      },
      media: function (state) {
        const el = state.elements[this.elId]
        console.log(el)
        return el['Media']['all']
      }
    })
  },
  data: function() {
    return {
      state: {
        expanded: false,
        containerKey: 0
      }
    }
  },
  methods: {
    ...mapActions([
      'fetchElement'
    ]),
    clickHandler: function() {
      this.expandItem()
      if(this.state.expanded) {
        this.fetchElement(this.elId)
      }
    },
    expandItem: function() {
      this.state.expanded = !this.state.expanded
    }
  },
  mounted() {
    this.$store.subscribe((mutation, state) => {
      switch(mutation.type) {
        case types.FETCH_ELEMENT:
          console.log('element updated')
          this.state.containerKey += 1
      }
    })
  }
}
</script>

<style lang="scss">
$card-colour: #2a2a2a;
$text-colour: white;
$secondary-color: white;
$highlight-colour: #2a2a2a;

$extension-size: 100px;
$open-anim: 0s ease-in;

.graph-item-container {
  margin: 0 0 15px 0;
  color: $text-colour;
  background-color: $card-colour;
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  min-height: 50px;
  max-height: 50px;
  overflow: hidden;
  transition: max-height $open-anim, min-height $open-anim;
  &.expanded {
    min-height: none;
    max-height: none;
  }
  &:hover {
    cursor: crosshair;
    background-color: lighten($card-colour, 30%);
    .graph-item-footer {
      border-color: lighten($card-colour, 30%);
    }
  }
  .graph-item-body {
    flex: 1;
  }
  .graph-item-footer {
    display: flex;
    flex: 1;
    max-height: 25px;
    min-height: 25px;
    background-color: $secondary-color;
    border: 10px solid $highlight-colour;
  }
  .graph-item-extension {
    display: flex;
    flex: 1;
    margin-bottom: -$extension-size;
    min-height: $extension-size;
    max-height: $extension-size;
    background-color: transparent;
    font-size: 10pt;
    h4 {
      margin: 0;
      text-decoration: underline;
    }
    .text {
      padding: 0 5px;
    }
    .desc-column {
      flex: 3;
      overflow: auto;
    }
    .detail-column {
      flex: 1;
      border-left: 1px $card-colour solid;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .detail-row {
      flex: 1;
      border-bottom: 1px $card-colour solid;
    }

  }
}

.v-tooltip {
  span {
    display: flex;
    flex: 1;
  }
}

.graph-item-title {
  padding: 12px 10px;
}

.graph-item-content {
  padding: 5px 10px;
}

.graph-item-list {
  padding : 0px 5px;
}

.no-display {
  display: none !important;
}

</style>
