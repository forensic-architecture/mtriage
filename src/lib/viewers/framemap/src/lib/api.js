import axios from 'axios'

const cfg = {
  url: "http://localhost:8080",
  analyser: "ranking",
  context: "military_vehicles_ambaz"
}

function fetchRankedElements (label, fromIndex) {
  const rUrl = `${cfg.url}/element?q=youtube/${cfg.analyser}&context=${cfg.context}&id=all&media=rankings.json`
  return axios.get(rUrl)
    .then(response => {
      const rankings = response.data
      console.log(label)
      const rankedElements = rankings[label]
      const urls = rankedElements.slice(fromIndex, fromIndex + 15).map(getElementUrl)
      const promises = urls.map(url => Promise.resolve(url).then(url => axios.get(url).catch(err => null)))
      return Promise.all(promises)
    })
    .then(fullElements => {
      return fullElements.map(el => el !== null ? el.data : null).filter(el => el !== null)
    })
}

function fetchElements () {
  return axios.get(`${cfg.url}/elementmap`)
    .then(response => {
      const elementmap = response.data
      const elementSets = elementmap.Analysed.filter(els => els.Component === cfg.analyser)
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

function fetchIndexedElements(fromIndex) {
  return axios.get(`${cfg.url}/elementmap`)
    .then(response => {

      const elementmap = response.data

      const elementSets = elementmap.Analysed.filter(els => els.Component === cfg.analyser)
      const elements = elementSets.filter(els => els.Context === cfg.context)
      if (elements.length !== 1) {
        alert("check your elements dir and context")
      }
      const ctxObj = elements[0]

      const urls = ctxObj.Elements.slice(fromIndex, fromIndex + 20).map(getElementUrl)
      const promises = urls.map(url => Promise.resolve(url).then(url => axios.get(url).catch(err => null)))
      return Promise.all(promises)
    })
    .then(fullElements => {
      return fullElements.map(el => el !== null ? el.data : null).filter(el => el !== null)
    })
}

function getElementUrl(id) {
  // const id = element.Id
  return `${cfg.url}/element?q=youtube/${cfg.analyser}&context=${cfg.context}&id=${id}&media=${id}.json`
}

export default {
  fetchElements,
  fetchIndexedElements,
  fetchRankedElements
}
