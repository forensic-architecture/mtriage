import axios from 'axios'

const ROOT_URL = 'http://localhost:8080'

const ANALYSED_DIR = "keras_pretrained"
const CONTEXT = "demo_youtube_select"

function fetchElements() {
  return axios.get(`${ROOT_URL}/elementmap`)
    .then(response => {
      const elementmap = response.data
      const elementSets = elementmap.Analysed.filter(els => els.Component === ANALYSED_DIR)
      const elements = elementSets.filter(els => els.Context === CONTEXT)
      if (elements.length !== 1) {
        alert("check your elements dir and context")
      }
      const ctxObj = elements[0]
      const urls = ctxObj.Elements.map(getElementUrl)
      return Promise.all(urls.map(url => axios.get(url)))
    })
    .then(fullElements => {
      return fullElements.map(el => el.data)
    })
}

function getElementUrl(_, idx) {
  return `${ROOT_URL}/element?q=youtube/${ANALYSED_DIR}&context=${CONTEXT}&id=${idx}`
}

export default {
  fetchElements,
}
