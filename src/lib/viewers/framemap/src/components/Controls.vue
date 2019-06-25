<template>
  <div class="controls-container">
    <v-card
      class="control-card"
      :max-height="600"
      tile
    >
      <v-card-title class="title">Threshold:</v-card-title>
      <div class="dropdown-container">
        <v-slider
          v-model="slider"
          color="#cc1616"
        ></v-slider>
      </div>
    </v-card>
    <v-card
      class="control-card"
      :max-height="600"
      tile
    >
      <v-card-title class="title">Rank:</v-card-title>
      <div class="dropdown-container">
        <v-overflow-btn
          :items="dropdown_rank"
          label="Select ranking algorithm"
          target="#dropdown-example"
          editable
        ></v-overflow-btn>
      </div>
    </v-card>
    <br/>
  </div>
</template>

<script>
export default {
  data: () => ({
    dropdown_rank: [
      { text: 'Most positive frames', callback: () => console.log('ciao') },
      { text: 'Most successive positive frames', callback: () => console.log('ciao') },
      { text: 'Highest proportion of positive frames', callback: () => console.log('ciao') },
      { text: 'Most successive positive frames (> 5 seconds)', callback: () => console.log('ciao') },
      { text: 'Most successive positive frames (> 10 seconds)', callback: () => console.log('ciao') },
    ],
    slider: 45
  })
}
</script>

<style lang="scss">
$hover-color: #cc1616;

.controls-container {
  margin: 0 0 2em 0;
}

.control-card {
  margin: 1em;
  .title {
    font-size: 12pt;
    font-weight: 500;
  }
}

.dropdown-container {
  margin: 0em 4em;
}
</style>
