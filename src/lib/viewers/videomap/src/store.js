import Vue from 'vue'
import Vuex from 'vuex'
import types from './mutation-types'
import api from './lib/api'
import exampleData from './assets/test.json'
import { ranker, rankByFrameCount } from './lib/rank';

Vue.use(Vuex)

const stubData = rankByFrameCount(exampleData.videos)

export default new Vuex.Store({
  state: {
    version: '0.1',
    fetching: true,
    meta: null,
    error: null,
    pages: [stubData]
    // pages: []
  },
  mutations: {
    [types.FETCH_ITEMS_ATTEMPT] (state) {
      state.fetching = true
    },
    [types.FETCH_ALL_PAGES] (state, pages) {
      state.pages = pages
      state.fetching = false
    },
    [types.FETCH_META_SUCCESS] (state, meta) {
      state.meta = meta
    },
    [types.FETCH_ITEMS_ERROR] (state, msg) {
      state.error = msg
    }
  },
  actions: {
    fetchItems ({ commit, state }, pages) {
      commit(types.FETCH_ITEMS_ATTEMPT)
      api.fetchMeta()
        .then(result => {
          commit(types.FETCH_META_SUCCESS, result.data)
          return api.fetchAll()
        })
        .then(result => {
          commit(types.FETCH_ALL_PAGES, result.data)
        })
        .catch(err => {
          commit(types.FETCH_ITEMS_ERROR, err.message)
        })
    }
  }
})
