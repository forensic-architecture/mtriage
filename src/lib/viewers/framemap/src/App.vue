<template>
  <v-app id="app">
    <Header :version="version" />
    <div id="body-container">
      <div class="container">
        <!-- <div class="info&#45;case">
           <Controls />
        </div> -->
        <div class="content-case">
          <Container :label="label" :threshold="threshold" />
        </div>
      </div>
    </div>
  </v-app>
</template>

<script>
import { mapState } from 'vuex'
import Header from './components/Header.vue'
import Container from './components/Container.vue'
import Controls from './components/Controls.vue'
import cfg from './LABEL'

export default {
  name: 'app',
  computed: {
    ...mapState({
      version: 'version',
    }),
  },
  data() {
    return cfg
  },
  components: {
    Header,
    Container,
    Controls
  },
}
</script>

<style lang="scss">
$primary-color: blue;
$background-color: #f1f1f1;
$card-colour: #1a1a1a;

$break-small: 320px;
$break-large: 1024px;

@mixin respond-to($media) {
  @if $media == handhelds {
    @media only screen and (max-width: $break-small) { @content; }
  }
  @else if $media == medium-screens {
    @media only screen and (min-width: $break-small + 1) and (max-width: $break-large - 1) { @content; }
  }
  @else if $media == wide-screens {
    @media only screen and (min-width: $break-large) { @content; }
  }
}

body {
  margin: 0px;
}

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  display: flex;
  flex-direction: column;
  margin: 0px;
  background-color: $background-color;
}

#body-container {
  display: flex;
  justify-content: space-between;
}

.container {
  display: flex;
  flex-direction: row-reverse;

  @include respond-to(medium-screens) {
    flex-direction: column;
  }
  .content-case {
    flex: 2;
  }
  .info-case {
    flex: 1;
    background-color: transparent;
    padding: 0 1em;
    h2 {
      color: white;
    }
  }
}

.flexc {
  display: flex;
  justify-content: center;
  align-items: center;
}

img {
  width: 4em;
}
</style>
