package main

import (
  "fmt"
  "log"
  "io/ioutil"

  "github.com/jroimartin/gocui"
  "gopkg.in/yaml.v2"
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

type option interface {
  Present(g *gocui.Gui, v *gocui.View) error
  Name() string
  IsModuleConfig() bool
}

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

type saveOption struct {}

func (so saveOption) Present(g *gocui.Gui, v *gocui.View) error {

  fmt.Fprintln(v, "SAVE CONFIG")
  fmt.Fprintln(v, "-----------")
  fmt.Fprintln(v, "")
  fmt.Fprintln(v, "Please choose a file name for this workflow\nconfiguration.\n\nIt will be saved as a yaml file in your workflows\ndirectory.")

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


// GLOBAL STATE

var history []state = []state {}

// MUTATIONS

func pushState(g *gocui.Gui, newState state) {
  history = append(history, newState)
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

// GOCUI LIFECYCLE

func main() {

  g, err := gocui.NewGui(gocui.OutputNormal)
  if err != nil {
    log.Panicln(err)
  }
  defer g.Close()

  g.Cursor = true

  g.SetManagerFunc(layout)

  if err := keybindings(g); err != nil {
    log.Panicln(err)
  }

  if err := g.MainLoop(); err != nil && err != gocui.ErrQuit {
    log.Panicln(err)
  }
}

func layout(g *gocui.Gui) error {

  maxX, maxY := g.Size()
  sideWidth := 60
  helpHeight := 4
  logHeight := 30

  if v, err := g.SetView("main", 0, 0, sideWidth-2, maxY-helpHeight-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    v.SelBgColor = gocui.ColorGreen
    v.SelFgColor = gocui.ColorBlack
    if _, err := g.SetCurrentView("main"); err != nil {
      return err
    }
    v.Wrap = true
    initState := state{ cfg: make(map[string]interface{}), option: getNextOption(g)}
    pushState(g, initState)
  }

  if v, err := g.SetView("help", 0, maxY - helpHeight, sideWidth-2, maxY-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    fmt.Fprintln(v, " Undo: ctrl+z")
    fmt.Fprintln(v, " Quit: ctrl+c")
  }

  if _, err := g.SetView("side", sideWidth, 0, maxX-1, maxY-logHeight-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
  }

  if v, err := g.SetView("log", sideWidth, maxY - logHeight, maxX-1, maxY-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    v.Autoscroll = true
  }

  // also a panel that explain the keys to use

  return nil
}

func quit(g *gocui.Gui, v *gocui.View) error {
  return gocui.ErrQuit
}

func keybindings(g *gocui.Gui) error {
  if err := g.SetKeybinding("", gocui.KeyCtrlC, gocui.ModNone, quit); err != nil {
    log.Panicln(err)
  }
  if err := g.SetKeybinding("", gocui.KeyCtrlZ, gocui.ModNone, undo); err != nil {
    log.Panicln(err)
  }
  if err := g.SetKeybinding("main", gocui.KeyArrowUp, gocui.ModNone, cursorUp); err != nil {
    return err
  }
  if err := g.SetKeybinding("main", gocui.KeyArrowDown, gocui.ModNone, cursorDown); err != nil {
    return err
  }
  if err := g.SetKeybinding("main", gocui.KeyEnter, gocui.ModNone, selectOption); err != nil {
    return err
  }
  if err := g.SetKeybinding("input", gocui.KeyEnter, gocui.ModNone, inputEntered); err != nil {
    return err
  }
  if err := g.SetKeybinding("save", gocui.KeyEnter, gocui.ModNone, saveFile); err != nil {
    return err
  }

  return nil
}

// EVENT HANDLERS

func saveFile(g *gocui.Gui, v *gocui.View) error {
  input := v.Buffer()
  if len(input) == 0 {
    return nil
  }
  input = input[:len(input)-1]  // remove trailing newline
  path := "../../workflows/" + input + ".yaml"
  data := history[len(history)-1].cfg
  writeToYamlFile(path, data)
  return gocui.ErrQuit
}

func inputEntered(g *gocui.Gui, v *gocui.View) error {

  input := v.Buffer()
  if len(input) == 0 {
    return nil
  }
  input = input[:len(input)-1]  // remove trailing newline
  optionName := history[len(history)-1].option.Name()
  isModuleConfig := history[len(history)-1].option.IsModuleConfig()
  update(g, optionName, input, isModuleConfig)

  if err := g.DeleteView("input"); err != nil {
    // log.Panicln("here")
    return nil
  }
  if _, err := g.SetCurrentView("main"); err != nil {
    return err
  }

  return nil
}

func undo(g *gocui.Gui, v *gocui.View) error {
  popState(g)
  return nil
}

func cursorUp(g *gocui.Gui, v *gocui.View) error {
  logger(g, "cursor up")
  // type assertion: current option is multiOption
  // history[len(history)-1].option.(multiOption)

  if v != nil {
    ox, oy := v.Origin()
    cx, cy := v.Cursor()
    if err := v.SetCursor(cx, cy-1); err != nil && oy > 0 {
      if err := v.SetOrigin(ox, oy-1); err != nil {
        return err
      }
    }
  }
  return nil
}

func cursorDown(g *gocui.Gui, v *gocui.View) error {
  logger(g, "cursor down")
  // type assertion: current option is multiOption
  o := history[len(history)-1].option.(multiOption)

  if v != nil {
    cx, cy := v.Cursor()
    if cy < len(o.options)-1 {
      if err := v.SetCursor(cx, cy+1); err != nil {
        ox, oy := v.Origin()
        if err := v.SetOrigin(ox, oy+1); err != nil {
          return err
        }
      }
    }
  }
  return nil
}

func selectOption(g *gocui.Gui, v *gocui.View) error {

  // type assertion: current option is multiOption
  o := history[len(history)-1].option.(multiOption)

  if v != nil {

    _, cy := v.Cursor()
    if cy < len(o.options) {

      selectedOption := o.options[cy]
      update(g, o.Name(), selectedOption, o.IsModuleConfig())
    }
  }
  return nil
}

// HELPERS

func printToView(g *gocui.Gui, view string, text string) error {
  v, err := g.View(view)
  if err != nil {
    return err
  }
  if v != nil {
    fmt.Fprintln(v, text)
  }
  return nil
}

func updateConfigView(g *gocui.Gui, cfg map[string]interface{}) error {

    v, err := g.View("side")
    if err != nil {
      return err
    }
    if v != nil {

      v.Clear()

      for key, val := range cfg {
        // value is either a string or not
        if s, ok := val.(string); ok {
          fmt.Fprintln(v, key + ": \"" + s + "\"")
        } else {
          // TODO: has to be a map
          // is a map
        }
      }
    }
    return nil
}

func updateOptionView(g *gocui.Gui, o option) error {
  logger(g, "update option")

  v, err := g.View("main")
  if err != nil {
    return err
  }
  if v != nil {
    v.Clear()
    if err := g.DeleteView("input"); err != nil {}
    if err := g.DeleteView("save"); err != nil {}
    o.Present(g, v)
  }
  return nil
}

func logger(g *gocui.Gui, text string) {
  v, _ := g.View("log")
  if v != nil {
    fmt.Fprintln(v, text)
  }
}

// TODO logic will hook into mtriage
func getNextOption(g *gocui.Gui) option {
  c := len(history)
  if c == 0 {
    return multiOption{ options: []string{"select","analyse"}, isModuleConfig: false, name: "phase" }
  } else if c == 1 {
    return textInputOption{ prompt: "please enter a folder path", name: "folder", isModuleConfig: false  }
  } else {
    return saveOption{}
  }
}

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
