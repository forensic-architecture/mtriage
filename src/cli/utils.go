package main

import (
  "os"
  "path/filepath"
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
  var dirs []string
  err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
    if !info.IsDir() {
      return nil
    }
    for i := 0; i < len(skips); i++ {
      if info.Name() == skips[i] {
        return nil
      }
    }
    name := info.Name()
    dirs = append(dirs, name)
    return nil
  })
  if err != nil {
    panic(err)
  }
  return dirs
}

func dirExists(path string) bool {
  if stat, err := os.Stat(path); err == nil && stat.IsDir() {
    return true
  }
  return false
}
