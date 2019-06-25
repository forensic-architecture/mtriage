import axios from 'axios'

const ROOT_URL = 'http://localhost:8080'

export default {
  fetchElementIndex: () => axios.get(`${ROOT_URL}/elementIndex`),
  fetchElement: elementId => axios.get(`${ROOT_URL}/element?id=${elementId}`),
  fetchElementMedia: (elementId, media) => axios.get(`${ROOT_URL}/element?id=${elementId}&media=${media}`)
}
