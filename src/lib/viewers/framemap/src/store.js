// import exampleData from './assets/test.json'
// const stubData = rankByFrameCount(exampleData.videos)
import Vue from 'vue'
import Vuex from 'vuex'
import api from './lib/api'
import types from './mutation-types'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    version: '0.1',
    fetching: false,
    error: null,
    elements: []
  },
  mutations: {
    [types.FETCH_ELEMENTS_ATTEMPT] (state) {
      state.fetching = true
    },
    [types.FETCH_ELEMENTS] (state, elements) {
      state.elements = elements
      state.fetching = false
    },
    [types.FETCH_ELEMENTS_ERROR] (state, msg) {
      state.error = msg
    },
    [types.FETCH_NEXT_ELEMENTS_ATTEMPT] (state) {
      state.fetching = true
    },
    [types.FETCH_NEXT_ELEMENTS] (state, elements) {
      state.elements = state.elements.concat(elements)
      state.fetching = false
    },
    [types.FETCH_NEXT_ELEMENTS_ERROR] (state, msg) {
      state.error = msg
    },
    [types.FETCH_RANKING] (state, ranking) {
      state.ranking = ranking
      state.fetching = false
    }
  },
  actions: {
    fetchRankedElements ({ commit, state }, label) {
      commit(types.FETCH_NEXT_ELEMENTS_ATTEMPT)
      const fromIndex = this.state.elements.length
      api.fetchRankedElements(label, fromIndex)
        .then(result => {
          commit(types.FETCH_NEXT_ELEMENTS, result)
        })
        .catch(err => {
          console.log(err.message)
          commit(types.FETCH_NEXT_ELEMENTS_ERROR, err.message)
        })
    }
  }
})
