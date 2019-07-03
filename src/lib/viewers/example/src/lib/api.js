import axios from 'axios'

const ROOT_URL = 'http://localhost:8080'

// const getReq = {
//   headers: {
//     'Content-Type': 'application/json',
//     'Access-Control-Allow-Origin': '*'
//   },
//   crossdomain: true,
//   method: 'get'
// }
//
// function get (url) {
//   return axios({
//     ...getReq,
//     url
//   })
// }

export default {
  fetchElements: () => axios.get(`${ROOT_URL}/elementmap`),
  fetchElement: elementId => axios.get(`${ROOT_URL}/element?id=${elementId}`)
}
