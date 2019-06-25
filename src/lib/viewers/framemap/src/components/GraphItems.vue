<template>
  <div class="graph-container">
    <GraphItem
      v-for="(video, key) in items"
      :key="key"
      :video_id="video.id"
      :title="video.title"
      :uploadDate="video.upload_date"
      :webpageUrl="video.webpage_url"
      :description="video.description"
      :duration="video.duration"
      :frames="video.frames"
      :scores="video.scores"
    ></GraphItem>
  </div>
</template>

<script>
  // import { rankByFrameCount } from '../lib/rank'
  import GraphItem from './GraphItem.vue'

  export default {
    components: {
      GraphItem
    },
    props: {
      items: Array
    },
  }
</script>
