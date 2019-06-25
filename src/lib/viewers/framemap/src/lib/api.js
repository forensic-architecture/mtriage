import axios from 'axios'

const ROOT_URL = 'http://localhost:8080'

export default {
  fetchElements: () => axios.get(`${ROOT_URL}/elements`),
  fetchElement: elementId => axios.get(`${ROOT_URL}/element?id=${elementId}`)
}
