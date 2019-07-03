package main

import (
  "log"
  "fmt"
  "github.com/jroimartin/gocui"
)

// OPTION INTERFACE

type option interface {
  Present(g *gocui.Gui, v *gocui.View) error
  Name() string
  IsModuleConfig() bool
}

// MULTIOPTION

type multiOption struct {
  options []string
  name string
  isModuleConfig bool
}

func (mo multiOption) Present(g *gocui.Gui, v *gocui.View) error {
  for _, option := range mo.options {
    fmt.Fprintln(v, option)
  }
  v.Highlight = true
  if _, err := g.SetCurrentView("main"); err != nil {
    return err
  }
  return nil
}

func (mo multiOption) Name() string {
  return mo.name
}

func (mo multiOption) IsModuleConfig() bool {
  return mo.isModuleConfig
}

// TEXTINPUTOPTION

type textInputOption struct {
  prompt string
  name string
  isModuleConfig bool
}

func (to textInputOption) Present(g *gocui.Gui, v *gocui.View) error {
  fmt.Fprintln(v, to.prompt)
  v.Highlight = false
  maxX, maxY := g.Size()
  if iView, err := g.SetView("input", maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView("input"); err != nil {
      return err
    }
  }
  return nil
}

func (to textInputOption) Name() string {
  return to.name
}

func (to textInputOption) IsModuleConfig() bool {
  return to.isModuleConfig
}

// SAVEOPTION

type saveOption struct {}

func (so saveOption) Present(g *gocui.Gui, v *gocui.View) error {

  fmt.Fprintln(v, "SAVE CONFIG")
  fmt.Fprintln(v, "-----------")
  fmt.Fprintln(v, "")
  fmt.Fprintln(v, "Please choose a file name for this workflow\nconfiguration.\n\nIt will be saved as a yaml file in your workflows\ndirectory.")
  v.Highlight = false

  maxX, maxY := g.Size()
  if iView, err := g.SetView("save", maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView("save"); err != nil {
      return err
    }
  }
  return nil
}

func (to saveOption) Name() string {
  return "save"
}

func (to saveOption) IsModuleConfig() bool {
  return false
}

// MTRIAGE INTERFACE

func getNextOption(g *gocui.Gui, cfg map[string]interface{}) option {
  switch c := len(history); c {
  case 0:
    return multiOption{ options: []string{"select","analyse"}, isModuleConfig: false, name: "phase" }
  case 1:
    return textInputOption{ prompt: "please enter a folder path", name: "folder", isModuleConfig: false  }
  case 2:
    phase := cfg["phase"].(string)
    modules := modulesForPhase(phase)
    return multiOption{ options: modules, isModuleConfig: false, name: "module" }
  default:
    logCfg(g, cfg)
    // return saveOption{}
    module := cfg["module"].(string)
    configOptions := configOptionsForModule(module)
    i := c - 3
    if i < len(configOptions) {
      name := configOptions[i]
      prompt := "please enter a " + name
      return textInputOption { prompt: prompt, isModuleConfig: true, name: name }
    } else {
      return saveOption{}
    }
  }
}

func modulesForPhase(phase string) []string {
  path, name := phaseToLibFolder(phase)
  return dirNamesIn(path, []string{name, "__pycache__"})
}

func phaseToLibFolder(phase string) (path string, name string) {
  if phase == PHASE_SELECT {
    return DIR_SELECTORS, LIB_SELECTORS
  } else if phase == PHASE_ANALYSE {
    return DIR_ANALYSERS, LIB_ANALYSERS
  } else {
    log.Panicln("invalid phase!")
    return "", ""
  }
}

func configOptionsForModule(module string) []string {
  return []string{ "option1", "option2" }
}
