package main

import (
  "log"
  "fmt"
  "github.com/jroimartin/gocui"
  "gopkg.in/yaml.v2"
  "strconv"
  "io/ioutil"
  "time"
  "strings"
)

// MODULE ARGS

type Arg struct {
  name string
  required bool
  input string
}

func (a Arg) String() string {
  return "name: " + a.name + " input: " + a.input + " required: " + strconv.FormatBool(a.required)
}

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
  validationType string
  childModule string
}

func (to textInputOption) Present(g *gocui.Gui, v *gocui.View) error {
  fmt.Fprintln(v, to.prompt)
  v.Highlight = false
  maxX, maxY := g.Size()
  if iView, err := g.SetView(VIEW_INPUT, maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView(VIEW_INPUT); err != nil {
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

func (to textInputOption) Validate(g *gocui.Gui, input string) interface{} {
  switch to.validationType {
  case TYPE_INT:
    inInt, err := strconv.Atoi(input)
    if err != nil {
      logger(g, input + " is not an integer")
      return nil
    }
    return inInt
  case TYPE_FOLDER:
    exists := dirExists("../../" + input)
    if !exists {
      logger(g, "folder " + input + " does not exist")
      return nil
    }
    return input
  case TYPE_DATE:
    // TODO: should be the format used by the analyser
    const dtFormat = "2006/01/02 15:04:05"
    _, err := time.Parse(dtFormat, input)
    if err != nil {
      logger(g, input + " is not a valid date format. Dates must be formatted YYYY/MM/DD HH:MM:SS")
      return nil
    }
    return input
  case TYPE_BOOL:
    inBool, err := strconv.ParseBool(input)
    if err != nil {
      logger(g, input + " is not a bool. Please enter 'true' or 'false'")
      return nil
    }
    return inBool
  case TYPE_WHITELIST:
    whitelist := strings.Split(input, ",")
    return whitelist
  default:  // accepts anything
    return input
  }
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
  if iView, err := g.SetView(VIEW_SAVE, maxX/2-30, maxY/2, maxX/2+30, maxY/2+2); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    iView.Editable = true
    if _, err := g.SetCurrentView(VIEW_SAVE); err != nil {
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
  switch stageCounter {
  case 0:
    return multiOption{ options: []string{"select","analyse"}, isModuleConfig: false, name: "phase" }
  case 1:
    phase := cfg["phase"].(string)
    modules := modulesForPhase(phase)
    return multiOption{ options: modules, isModuleConfig: false, name: "module" }
  case 2:
    return textInputOption{ prompt: "please enter the path to your working directory", name: "folder", isModuleConfig: false, validationType: TYPE_FOLDER  }
  default:
    module := cfg["module"].(string)
    phase := cfg["phase"].(string)
    configOptions := configOptionsForModule(module, phase)
    i := stageCounter - 3
    if i < len(configOptions) {
      name := configOptions[i].name
      input := configOptions[i].input
      prompt := "please enter a " + input + " for argument:\n\n   "  + name
      return textInputOption { prompt: prompt, isModuleConfig: true, name: name, validationType: input }
    } else {
      return saveOption{}
    }
  }
}

func modulesForPhase(phase string) []string {
  path, _ := phaseToLibFolder(phase)
  return dirNamesIn(path, []string{"meta"})
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

func configOptionsForModule(module string, phase string) []Arg {

  argsPath := argsPathForModule(module, phase)

  file, err := ioutil.ReadFile(argsPath)
  if err != nil {
    log.Panicln(err)
  }

  var argsWild []map[string]interface{}
  err = yaml.Unmarshal(file, &argsWild)
  if err != nil {
    log.Panicln(err)
  }

  argsTame := []Arg{}

  if phase == PHASE_ANALYSE {
    els_in := Arg{ name: "elements_in", input: TYPE_WHITELIST, required: true }
    argsTame = append(argsTame, els_in)
  }

  for i := range argsWild {
    name, ok := argsWild[i]["name"].(string)
    if !ok {
      log.Panicln("invalid args yaml! name not string")
    }
    input, ok := argsWild[i]["input"].(string)
    if !ok {
      log.Panicln("invalid args yaml! input not string")
    }
    required, ok := argsWild[i]["required"].(bool)
    if !ok {
      log.Panicln("invalid args yaml! required not bool")
    }
    arg := Arg{ name: name, input: input, required: required }
    argsTame = append(argsTame, arg)
  }

  return argsTame
}

func argsPathForModule(module string, phase string) string {
  phaseDir, _ := phaseToLibFolder(phase)
  return phaseDir + "/" + module + "/args.yaml"
}
