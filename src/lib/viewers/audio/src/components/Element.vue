<template>
  <div
    :class="containerClasses"
    :key="this.state.containerKey"
  >
    <div class="graph-item-body" v-on:click="clickHandler">
      <div class="graph-item-title"><h3>{{ elementId }}</h3></div>
      <div class="graph-item-content">
        <h4>Duration: {{ this.element_data.duration }}</h4>
        <av-waveform
          :line-width="2"
          line-color="black"
          :canvHeight="100"
          canv-fill-color="#000"
          :audio-src="getFile()"
          :key="element_data" >
        </av-waveform>
        <v-stage ref="stage" :config="stageSize" :key="element_data">
          <v-layer>
            <v-rect :config="{
                x: this.stageSize.padding,
                y: 0,
                width: this.stageSize.width - this.stageSize.padding*2 -20,
                height: this.stageSize.height,
                stroke: 'black'
              }"
            />
            <v-rect v-for="onset in element_data.onsets" v-bind:key="onset" :config="{
                x: getXLoc(onset, element_data.duration),
                y: 0,
                width: 1,
                height: 200,
                fill: '#159415'
              }"
            />
          </v-layer>
        </v-stage>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import types from '../mutation-types'
import axios from 'axios'

const width = 518
const height = 100
const padding = 0

export default {
  name: 'GraphItem',
  props: {
    elementId: String,
    audio: String,
    onsets: String
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
      error: state => state.error
    })
  },
  data: function() {
    return {
      state: {
        expanded: false,
        containerKey: 0
      },
      element_data: {
        duration: 40,
        onsets: [10, 20, 25],
      },
      stageSize: {
        width: width,
        height: height,
        padding: padding
      }
    }
  },
  methods: {
    ...mapActions([
      'fetchElement'
    ]),
    clickHandler: function() {
      this.expandItem()
    },
    expandItem: function() {
      console.log("expanding")
      this.state.expanded = !this.state.expanded
    },
    getXLoc: function (onset, duration) {
      return padding + ((onset / duration) * (width - padding * 2 - 20))
    },
    getFile: function () {
      var call = 'http://localhost:8080/element?id=' + this.elementId + '&media=' + this.audio
      return call
    }
  },
  mounted () {
    var url = 'http://localhost:8080/element?id=' + this.elementId + '&media=' + this.onsets
    axios.get(url)
      .then(response => {
        this.element_data = response.data
        console.log(this.element_data)
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
  padding: 0px 0 20px 10px ;
  color: $text-colour;
  background-color: $card-colour;
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  min-height: 52px;
  max-height: 52px;
  overflow: hidden;
  transition: max-height $open-anim, min-height $open-anim;
  h4 {
    margin: 0 0 10px 0;
  }
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
