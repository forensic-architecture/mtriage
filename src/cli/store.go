package main

import (
  "github.com/jroimartin/gocui"
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

var history []state = []state {}

// MUTATIONS

func pushState(g *gocui.Gui, newState state) {
  // logCfg(g, newState.cfg)
  history = append(history, newState)

  // directly updating the ui is not ideal -
  // observer pattern would make for looser coupling
  updateConfigView(g, newState.cfg)
  updateOptionView(g, newState.option)
}

func popState(g *gocui.Gui) {
  if len(history) > 1 {
    history = history[:len(history)-1]
    updateConfigView(g, history[len(history)-1].cfg)
    updateOptionView(g, history[len(history)-1].option)
  }
}

func update(g *gocui.Gui, key string, value interface{}, isModuleConfig bool) {
  newState := history[len(history)-1].Copy()
  if !isModuleConfig {
      newState.cfg[key] = value
  } else {
      if _, ok := newState.cfg["config"]; !ok {
        newState.cfg["config"] = make(map[string]interface{})
      }
      config := newState.cfg["config"].(map[string]interface{})
      config[key] = value
  }
  newState.option = getNextOption(g, newState.cfg)
  pushState(g, newState)
}

func currentState() state {
  if len(history) > 0 {
    return history[len(history)-1]
  }
  return state{}
}
