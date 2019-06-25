<template>
  <div class="header">
    <div class="flex-across">
      <h3 id="header-text">mtriage-audio-viewer</h3>
      <small>{{ version }}</small>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Header',
  props: {
    version: String
  }
}
</script>

<style lang="scss">
$primary-color: #2a2a2a;
$text-color: white;

.header {
  color: $text-color;
  display: flex;
  justify-content: left;
  background-color: $primary-color;
  align-items: center;
  padding: 5px 20px;
}

.flex-across {
  display: flex;
  align-items: center;
}

#header-text {
  margin: 0 1em;
}
</style>
