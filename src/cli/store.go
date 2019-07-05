package main

import (
  "github.com/jroimartin/gocui"
  "log"
)

// TYPES

type state struct {
  option option
  phase string
  folder string
  currentModule string
  configs map[string]interface{}
}

func (s state) Copy() state {
  newState := s
  newState.configs = make(map[string]interface{})
  newState.configs = copyMap(s.configs)
  return newState
}

func (s state) IsEmpty() bool {
  return s.phase == ""
}

func (s state) AsMap() map[string]interface{} {
  stateMap := make(map[string]interface{})
  stateMap[OPT_PHASE] = s.phase
  stateMap[OPT_FOLDER] = s.folder
  if s.configs != nil {
    keys := keysForMap(s.configs)
    keyCount := len(keys)
    switch keyCount {
    case 0:
      break
    case 1:
      moduleName := keys[0]
      moduleConfig := s.configs[moduleName].(map[string]interface{})
      stateMap["module"] = moduleName
      stateMap["config"] = moduleConfig
    default:
      stateMap["module"] = MODULE_META
      children := make(map[string]interface{})
      for i := range keys {
        k := keys[i]
        children[k] = s.configs[k]
      }
      configMap := make(map[string]interface{})
      configMap["children"] = children
      stateMap["config"] = configMap
    }
  }
  return stateMap
}

// STATE

var history []state = []state{}
var stageCounter int

// MUTATIONS

func pushState(newState state) {
  history = append(history, newState)
  stageCounter++
}

func popState(g *gocui.Gui) {
  if len(history) > 1 {
    history = history[:len(history)-1]
    stageCounter--
  }
}

func update(g *gocui.Gui, o option, value interface{}) {

  newState := currentState(g).Copy()

  if _, ok := o.(saveOption); ok {
    newState.currentModule = ""
    newState.option = getNextOption(g, newState)
    pushState(newState)
    return
  }

  if newState.currentModule != "" {
    moduleConfig := newState.configs[newState.currentModule].(map[string]interface{})
    moduleConfig[o.Name()] = value
  } else {
    optionName := o.Name()
    switch optionName {
    case OPT_PHASE:
      newState.phase = value.(string)
    case OPT_FOLDER:
      newState.folder = value.(string)
    case OPT_MODULE:
      if newState.configs == nil {
        newState.configs = make(map[string]interface{})
      }
      moduleName := value.(string)
      newState.currentModule = moduleName
      newState.configs[moduleName] = make(map[string]interface{})
    default:
      log.Panicln("option neither phase nor folder but no current module name")
    }
  }
  newState.option = getNextOption(g, newState)
  pushState(newState)
}

func currentState(g *gocui.Gui) state {
  if len(history) > 0 {
    return history[len(history)-1]
  } else {
    initState := state{ option: getNextOption(g, state{}) }
    pushState(initState)
    return currentState(g)
  }
}

func save(g *gocui.Gui, name string) {
  path := DIR_WORKFLOWS + "/" + name + ".yaml"
  stateMap := currentState(g).AsMap()
  yamlData := mapToYaml(stateMap)
  writeDataToFile(yamlData, path)
}
