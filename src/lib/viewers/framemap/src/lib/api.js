import axios from 'axios'

const ROOT_URL = 'http://localhost:8080'

function fetchElements() {
  return axios.get(`${ROOT_URL}/elements`)
    .then(elements => {
      const urls = elements.data.map(getElementUrl)
      return Promise.all(urls.map(url => axios.get(url)))
    })
    .then(fullElements => {
      console.log("ciao")
      console.log(fullElements.map(el => el.data))
    })
}

function getElementUrl(element) {
  const id = element.Id
  const filename = element.Media.json[0]
  return `${ROOT_URL}/element?id=${id}&media=${filename}`
  // return `${ROOT_URL}/element?id=${id}`
}

export default {
  fetchElements,
}
