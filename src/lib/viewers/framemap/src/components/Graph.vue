<template>
  <div class="graph-container">
    <VideoCell
      v-for="(video, key) in elements"
      :key="key"
      :video_id="video.webpage_url.split('=')[1]"
      :title="video.title"
      :uploadDate="video.upload_date"
      :webpageUrl="video.webpage_url"
      :description="video.description"
      :duration="video.duration"
      :frames="getFrames(video)"
      :scores="getScores(video)"
    ></VideoCell>
  </div>
</template>

<script>
  // import { rankByFrameCount } from '../lib/rank'
  import VideoCell from './VideoCell.vue'

  export default {
    name: 'Graph',
    components: {
      VideoCell
    },
    props: {
      elements: Array,
      label: String,
    },
    methods: {
      getFrames(video) {
        const lbls = Object.keys(video.labels)
        if (lbls.includes(this.label)) {
          return video.labels[this.label].frames
        }
        return null
      },
      getScores(video) {
        const lbls = Object.keys(video.labels)
        if (lbls.includes(this.label)) {
          return video.labels[this.label].scores
        }
        return null
      }
    }
  }
</script>
