package main

import (
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
