import axios from 'axios'

const cfg = {
  url: "http://localhost:8080",
  analysed: "keras_pretrained",
  context: "triplechaser"
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
      const promises = urls.map(url => Promise.resolve(url).then(url => axios.get(url).catch(err => null)))
      return Promise.all(promises)
    })
    .then(fullElements => {
      return fullElements.map(el => el !== null ? el.data : null).filter(el => el !== null)
    })
}

function getElementUrl(element) {
  const id = element.Id
  return `${cfg.url}/element?q=youtube/${cfg.analysed}&context=${cfg.context}&id=${id}&media=${id}.json`
}

export default {
  fetchElements,
}
