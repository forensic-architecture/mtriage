<template>
  <div
    :class="containerClasses"
  >
    <div class="graph-item-body" v-on:click="expandItem">
      <div class="graph-item-title">{{ title }}</div>
    </div>
    <div class="graph-item-footer">
      <FrameMap
        :video_id="video_id"
        :length="duration"
        :frames="frames"
        :scores="scores"
      />
    </div>
     <!-- TODO: break this into another component -->
    <div :class="extensionClasses">
      <div class="desc-column">
        <div class="text">
          <h4>Description</h4>
          <div>{{ descriptionFmt }}</div>
        </div>
      </div>
      <div class="detail-column">
        <div class="detail-row">
          <div class="text">
            <h4>Rank</h4>
            <div>{{ rankFmt }}</div>
          </div>
        </div>
        <div class="detail-row">
          <div class="text">
            <h4>Duration</h4>
            <div>{{ durationFmt }}</div>
          </div>
        </div>
        <div class="detail-row">
          <div class="text">
            <h4>Upload Date</h4>
            <div>{{ dateFmt }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FrameMap from './FrameMap.vue'
import { fmtMinSec } from '../lib/util'

const monthNames = [
  "January", "February", "March",
  "April", "May", "June", "July",
  "August", "September", "October",
  "November", "December"
];

export default {
  name: 'GraphItem',
  components: {
    FrameMap
  },
  props: {
    video_id: String,
    title: String,
    uploadDate: String,
    webpageUrl: String,
    description: String,
    duration: Number,
    frames: Array,
    scores: Array
  },
  computed: {
    rankFmt: function() {
      return this.$vnode.key + 1
    },
    descriptionFmt: function() {
      if (this.description == '') {
        return 'No description.'
      } else {
        return this.description
      }
    },
    dateFmt: function() {
      const d0 = `${this.uploadDate.substring(0,4)}-${this.uploadDate.substring(4,6)}-${this.uploadDate.substring(6)}`
      const d = new Date(d0)
      const day = d.getDate()
      const monthIndex = d.getMonth()
      const year = d.getFullYear()
      return day + ' ' + monthNames[monthIndex] + ' ' + year
    },
    durationFmt: function() {
      return fmtMinSec(this.duration)
    },
    containerClasses: function() {
      if (this.state.expanded) {
        return 'graph-item-container expanded'
      } else {
        return 'graph-item-container'
      }
    },
    extensionClasses: function() {
      if (this.state.expanded) {
        return 'graph-item-extension'
      } else {
        return 'graph-item-extension no-display'
      }
    }
  },
  data: function() {
    return {
      state: {
        expanded: false
      }
    }
  },
  methods: {
    expandItem: function() {
      this.state.expanded = !this.state.expanded
    }
  }
}
</script>

<style lang="scss">
$card-colour: #2a2a2a;
$text-colour: white;
$secondary-color: white;
$highlight-colour: #2a2a2a;

$extension-size: 200px;
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
  transition: max-height $open-anim, min-height $open-anim;
  &.expanded {
    min-height: 40px + $extension-size;
    max-height: 40px + $extension-size;
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
    max-height: 38px;
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
  padding: 5px 5px;
}

.no-display {
  display: none !important;
}

</style>
