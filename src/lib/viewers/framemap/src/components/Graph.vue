<template>
  <div class="graph-container">
    <div
      v-for="(el, key) in elements"
    >
      {{el}}
    </div>
    <!-- <VideoCell -->
    <!--   v&#45;for="(video, key) in elements" -->
    <!--   :key="key" -->
    <!--   :video_id="video.id" -->
    <!--   :title="video.title" -->
    <!--   :uploadDate="video.upload_date" -->
    <!--   :webpageUrl="video.webpage_url" -->
    <!--   :description="video.description" -->
    <!--   :duration="video.duration" -->
    <!--   :frames="video.frames" -->
    <!--   :scores="video.scores" -->
    <!-- ></VideoCell> -->
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
      elements: Array
    },
  }
</script>
