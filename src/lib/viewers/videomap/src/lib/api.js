import axios from 'axios'

const ROOT_URL = 'http://localhost:5000'
const VIDEOS_PER_PAGE = 100

const getReq = {
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
  },
  crossdomain: true,
  method: 'get'
}

function get (url) {
  return axios({
    ...getReq,
    url
  })
}

export default {
  fetchMeta: () => get(`${ROOT_URL}/api/meta`),
  fetchAll: () => get(`${ROOT_URL}/api/paged/${VIDEOS_PER_PAGE}`),
  fetchPage: pageNo => get(`${ROOT_URL}/api/paged/${VIDEOS_PER_PAGE}/${pageNo}`)
}
