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
    elementIndex: [],
    elements: {}
  },
  mutations: {
    [types.FETCH_ELEMENT_INDEX_ATTEMPT] (state) {
      state.fetching = true
    },
    [types.FETCH_ELEMENT_INDEX] (state, elementIndex) {
      state.elementIndex = elementIndex
      console.log(elementIndex)
      state.fetching = false
    },
    [types.FETCH_ELEMENT_INDEX_ERROR] (state, msg) {
      state.error = msg
    },
    [types.FETCH_ELEMENT_ATTEMPT] (state) {
      state.fetching = true
    },
    [types.FETCH_ELEMENT] (state, element) {
      const elementId = element['Id']
      state.elements[elementId] = element
      state.fetching = false
    },
    [types.FETCH_ELEMENT_ERROR] (state, msg) {
      state.error = msg
    }
  },
  actions: {
    fetchElementIndex ({ commit, state }) {
      commit(types.FETCH_ELEMENT_INDEX_ATTEMPT)
      api.fetchElementIndex()
        .then(result => {
          commit(types.FETCH_ELEMENT_INDEX, result.data['Elements'])
        })
        .catch(err => {
          commit(types.FETCH_ELEMENT_INDEX_ERROR, err.message)
        })
    },
    fetchElement ({ commit, state }, element) {
      api.fetchElement(element)
        .then(result => {
          commit(types.FETCH_ELEMENT, result.data)
        })
        .catch(err => {
          commit(types.FETCH_ELEMENT_ERROR, err.message)
        })
    }
  }
})
