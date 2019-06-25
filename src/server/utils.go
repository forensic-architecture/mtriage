package main

import (
  "path/filepath"
  "os"
  "encoding/json"
  "io/ioutil"
)

// CONSTANTS

const ELEMENTS_DIR string = "elements"
const CONFIG_FILE string = "config.json"

// FILE PATHS

func getFilesInDir(dir string, skips []string) []File {
  var files []File
  err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
    if info.IsDir() {
      return nil
    }
    for i := 0; i < len(skips); i++ {
      if info.Name() == skips[i] {
        return nil
      }
    }
    name := info.Name()
    ext := filepath.Ext(path)
    files = append(files, File{ Path: path, Name: name, Ext: ext })
    return nil
  })
  if err != nil {
    panic(err)
  }
  return files
}

func getDirsInDir(dir string, skips []string) []Dir {
  var dirs []Dir
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
    dirs = append(dirs, Dir{ Path: path, Name: name })
    return nil
  })
  if err != nil {
    panic(err)
  }
  return dirs
}

func getPathBases(paths []string) []string {
  var bases []string
  for i := 0; i < len(paths); i++ {
    base := filepath.Base(paths[i])
    bases = append(bases, base)
  }
  return bases
}

func getPathBase(path string) string {
  return filepath.Base(path)
}

func resolveSymlink(symlink string) string {
  file, err := os.Readlink(symlink)
  if err != nil {
    // TODO - throw
  }
  return file
}

// IO

func writeToJsonFile(path string, jsonable interface{}) {
  file, err := json.MarshalIndent(jsonable, "", " ")
  if err != nil {
    panic(err)
  }
	err = ioutil.WriteFile(path, file, 0644)
  if err != nil {
    panic(err)
  }
}
