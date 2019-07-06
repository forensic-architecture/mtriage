package main

import (
  "os"
  "log"
  "io/ioutil"
  "gopkg.in/yaml.v2"
)

func mapToYaml(data map[string]interface{}) []byte {
  d, err := yaml.Marshal(&data)
  if err != nil {
    log.Panicln(err)
  }
  return d
}

func mapToYamlString(data map[string]interface{}) string {
  return string(mapToYaml(data))
}

func writeDataToFile(data []byte, path string) {
  err := ioutil.WriteFile(path, data, 0644)
  if err != nil {
    log.Panicln(err)
  }
}

func dirNamesIn(dir string, skips []string) []string {

  files, err := ioutil.ReadDir(dir)
  if err != nil {
    log.Panicln(err)
  }

  var dirs []string
  for _, file := range files {
    if !file.IsDir() {
      continue
    }
    shouldSkip := false
    for i := range skips {
      if file.Name() == skips[i] {
        shouldSkip = true
      }
    }
    if shouldSkip {
      continue
    }
    dirs = append(dirs, file.Name())
  }
  return dirs
}

func dirExists(path string) bool {
  if stat, err := os.Stat(path); err == nil && stat.IsDir() {
    return true
  }
  return false
}

func dirIsValid(path string) bool {
  if dirExists(path) {
    return true
  }
  err := os.Mkdir(path, 0755)
  if err == nil {
    os.Remove(path)
    return true
  }
  return false
}

func keysForMap(m map[string]interface{}) []string {
  keys := []string{}
  for k := range m {
    keys = append(keys, k)
  }
  return keys
}

func copyMap(m map[string]interface{}) map[string]interface{} {
  // assumes any maps within m have type map[string]interface{}
  newMap := make(map[string]interface{})
  for k,v := range m {
    if innerMap, ok := v.(map[string]interface{}); ok {
      newMap[k] = copyMap(innerMap)
    } else {
      newMap[k] = v
    }
  }
  return newMap
}

func save(name string, stateMap map[string]interface{}) {
  path := DIR_WORKFLOWS + "/" + name + ".yaml"
  yamlData := mapToYaml(stateMap)
  writeDataToFile(yamlData, path)
}
