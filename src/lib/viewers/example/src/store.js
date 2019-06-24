import Vue from 'vue'
import Vuex from 'vuex'
import api from './lib/api'
import types from './mutation-types'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    version: '0.1',
    fetching: true,
    error: null,
    elements: []
  },
  mutations: {
    [types.FETCH_ELEMENTS_ATTEMPT] (state) {
      state.fetching = true
    },
    [types.FETCH_ELEMENTS] (state, elements) {
      state.elements = elements
      console.log(elements)
      state.fetching = false
    },
    [types.FETCH_ELEMENTS_ERROR] (state, msg) {
      state.error = msg
    }
  },
  actions: {
    fetchElements ({ commit, state }, pages) {
      commit(types.FETCH_ELEMENTS_ATTEMPT)
      api.fetchElements()
        .then(result => {
          commit(types.FETCH_ELEMENTS, result.data)
        })
        .catch(err => {
          commit(types.FETCH_ELEMENTS_ERROR, err.message)
        })
    }
  }
})
