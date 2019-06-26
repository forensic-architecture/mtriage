import Vue from 'vue'
import App from './App.vue'
import Vuetify from 'vuetify'
import AudioVisual from 'vue-audio-visual'
import VueKonva from 'vue-konva'
import store from './store'
import 'vuetify/dist/vuetify.min.css'

Vue.config.productionTip = false
Vue.use(Vuetify)
Vue.use(AudioVisual)
Vue.use(VueKonva)

new Vue({
  store,
  render: h => h(App)
}).$mount('#app')
