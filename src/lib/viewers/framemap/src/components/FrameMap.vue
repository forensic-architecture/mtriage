<template>
  <div
    v-if="this.frames !== null && this.scores !== null"
    class="frame-map"
  >
    <div class="keyframe" v-for="index in this.length">
      <v-tooltip
        v-if="isOn(index)"
        top
        :open-delay="120"
        :key="index"
        class="on"
      >
        <span
          slot="activator"
          v-on:click="openFrame(index)"
          :style="getFrameColor(index)"
        />
        <span>{{ timeFmt(index) }}</span><br>
        <span>{{ scoreFmt(index)}}</span>
      </v-tooltip>
      <div
        v-else
        :key="index"
        class="off"
      />
    </div>
  </div>
</template>

<script>
import { fmtMinSec } from '../lib/util'

export default {
  name: 'FrameMap',
  props: {
    video_id: String,
    length: Number,
    frames: Array,
    scores: Array,
    label: String,
    threshold: Number
  },
  methods: {
    isOn: function(idx) {
      const _idx = this.frames.indexOf(idx)
      return _idx > -1 && this.scores[_idx] > this.threshold
    },
    openFrame: function(idx) {
      window.open(`https://youtu.be/${this.video_id}?t=${idx}`, '_blank')
    },
    timeFmt: function(idx) {
      return fmtMinSec(idx)
    },
    scoreFmt: function(idx) {
      const _idx = this.frames.indexOf(idx)
      return `${this.scores[_idx]}%`
    },
    getFrameColor: function(idx) {
      const _idx = this.frames.indexOf(idx)
      return `background-color: rgb(${100 + 155 * (this.scores[_idx] / 40)}, 0, 0)`
    },
  },
}
</script>

<style lang="scss">
$frame-color: #cc1616;

.frame-map {
  display: flex;
  flex: 1;
  flex-direction: row;
  width: 100%;
}

.keyframe {
  display: flex;
  flex: 1;
  .on {
    display: flex;
    flex: 1;
    &:hover {
      background-color: red;
      cursor: pointer;
    }
  }
  .off {
    display: flex;
    flex: 1;
    background-color: transparent;
  }
  .fill-whole {
    display: flex;
    flex: 1;
  }
}

</style>
