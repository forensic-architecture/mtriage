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
  history = append(history, newState)

  // directly updating the ui is not ideal,
  // - for looser coupling between data and ui
  // would be better to implement an observer pattern
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

func update(g *gocui.Gui, key string, value string, isModuleConfig bool) {
  newState := history[len(history)-1].Copy()
  if !isModuleConfig {
      newState.cfg[key] = value
  } else {
      if _, ok := newState.cfg["config"]; !ok {
        newState.cfg["config"] = make(map[string]string)
      }
      config := newState.cfg["config"].(map[string]string)
      config[key] = value
  }
  newState.option = getNextOption(g)
  pushState(g, newState)
}
