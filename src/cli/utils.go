package main

import (
  "os"
  // "path/filepath"
  "log"
  "io/ioutil"
  "gopkg.in/yaml.v2"
)

func writeToYamlFile(path string, data map[string]interface{}) {
  d, err := yaml.Marshal(&data)
  if err != nil {
          log.Fatalf("error: %v", err)
  }
  err = ioutil.WriteFile(path, d, 0644)
  if err != nil {
    panic(err)
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
