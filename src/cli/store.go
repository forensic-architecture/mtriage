package main

import (
  "github.com/jroimartin/gocui"
  "log"
)

// TYPES

type state struct {
  cfg map[string]interface{}
  option option
}

func (s state) Copy() state {
  newState := s
  newState.cfg = make(map[string]interface{})
  for k,v := range s.cfg {
    newState.cfg[k] = v
  }
  return newState
}

// STATE

var history []state = []state{}
var stageCounter int

// MUTATIONS

func pushState(g *gocui.Gui, newState state) {
  history = append(history, newState)

  // directly updating the ui is not ideal -
  // observer pattern would make for looser coupling
  updateConfigView(g, newState.cfg)
  updateOptionView(g, newState.option)
  stageCounter++
}

func popState(g *gocui.Gui) {
  if len(history) > 1 {
    history = history[:len(history)-1]
    updateConfigView(g, history[len(history)-1].cfg)
    updateOptionView(g, history[len(history)-1].option)
    stageCounter--
  }
}

func update(g *gocui.Gui, o option, value interface{}) {
  newState := history[len(history)-1].Copy()
  if !o.IsModuleConfig() {
      newState.cfg[o.Name()] = value
  } else {
      if _, ok := newState.cfg["config"]; !ok {
        newState.cfg["config"] = make(map[string]interface{})
      }
      config := newState.cfg["config"].(map[string]interface{})
      config[o.Name()] = value
  }
  newState.option = getNextOption(g, newState.cfg)
  pushState(g, newState)
}

func convertToMeta(cfg map[string]interface{}) map[string]interface{} {

  if cfg["phase"].(string) == PHASE_SELECT {
    log.Panicln("tried to convert a select config to meta-analyser")
  }
  if cfg["module"].(string) == MODULE_META {
    return cfg
  }
  newCfg := make(map[string]interface{})
  newCfg["phase"] = cfg["phase"]
  newCfg["folder"] = cfg["folder"]
  newCfg["module"] = MODULE_META

  config := cfg["config"].(map[string]interface{})
  childConfig := make(map[string]interface{})
  for k, _ := range config {
    childConfig[k] = config[k]
  }

  children := make([]map[string]interface{},1,1)
  children = append(children, childConfig)

  innerConfig := make(map[string]interface{})
  innerConfig["children"] = children
  newCfg["config"] = innerConfig

  return newCfg
}

func currentState() state {
  if len(history) > 0 {
    return history[len(history)-1]
  }
  return state{}
}
