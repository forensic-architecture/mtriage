import axios from 'axios'

const cfg = {
  url: "http://localhost:8080",
  analysed: "keras_pretrained",
  context: "demo_youtube_select"
}

function fetchElements() {
  return axios.get(`${cfg.url}/elementmap`)
    .then(response => {
      const elementmap = response.data
      const elementSets = elementmap.Analysed.filter(els => els.Component === cfg.analysed)
      const elements = elementSets.filter(els => els.Context === cfg.context)
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
  return `${cfg.url}/element?q=youtube/${cfg.analysed}&context=${cfg.context}&id=${idx}`
}

export default {
  fetchElements,
}
