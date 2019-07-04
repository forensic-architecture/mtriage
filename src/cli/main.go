package main

import (
  "fmt"
  "log"
  "os/exec"
  "github.com/jroimartin/gocui"
  "strconv"
  "strings"
)

// CONSTANTS

const VIEW_MAIN = "main"
const VIEW_SIDE = "side"
const VIEW_INPUT = "input"
const VIEW_SAVE = "save"
const VIEW_CONSOLE = "console"

const PHASE_SELECT = "select"
const PHASE_ANALYSE = "analyse"

const LIB_SELECTORS = "selectors"
const LIB_ANALYSERS = "analysers"

const EXEC_MTRIAGE = "../../mtriage"
const DIR_WORKFLOWS = "../../workflows"
const DIR_LIB = "../lib"
const DIR_SELECTORS = DIR_LIB + "/" + LIB_SELECTORS
const DIR_ANALYSERS = DIR_LIB + "/" + LIB_ANALYSERS

const TYPE_STRING = "string"
const TYPE_FOLDER = "folder"
const TYPE_DATE = "date"
const TYPE_INT = "int"
const TYPE_WHITELIST = "whitelist"
const TYPE_BOOL = "bool"

const MODULE_META = "meta"

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

  if v, err := g.SetView(VIEW_MAIN, 0, 0, sideWidth-2, maxY-helpHeight-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    v.SelBgColor = gocui.ColorGreen
    v.SelFgColor = gocui.ColorBlack
    if _, err := g.SetCurrentView(VIEW_MAIN); err != nil {
      return err
    }
    v.Wrap = true
    initCfg := make(map[string]interface{})
    initState := state{ cfg: initCfg, option: getNextOption(g, initCfg)}
    pushState(g, initState)
  }

  if v, err := g.SetView("help", 0, maxY - helpHeight, sideWidth-2, maxY-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    fmt.Fprintln(v, " Undo: ctrl+z")
    fmt.Fprintln(v, " Quit: ctrl+c")
  }

  if _, err := g.SetView(VIEW_SIDE, sideWidth, 0, maxX-1, maxY-logHeight-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
  }

  if v, err := g.SetView(VIEW_CONSOLE, sideWidth, maxY - logHeight, maxX-1, maxY-1); err != nil {
    if err != gocui.ErrUnknownView {
      return err
    }
    v.Autoscroll = true
  }

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
  if err := g.SetKeybinding(VIEW_MAIN, gocui.KeyArrowUp, gocui.ModNone, cursorUp); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_MAIN, gocui.KeyArrowDown, gocui.ModNone, cursorDown); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_MAIN, gocui.KeyEnter, gocui.ModNone, selectOption); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_INPUT, gocui.KeyEnter, gocui.ModNone, inputEntered); err != nil {
    return err
  }
  if err := g.SetKeybinding(VIEW_SAVE, gocui.KeyEnter, gocui.ModNone, saveFile); err != nil {
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
  path := DIR_WORKFLOWS + "/" + input + ".yaml"
  data := history[len(history)-1].cfg
  writeToYamlFile(path, data)
  return gocui.ErrQuit
}

func runWorkflow(g *gocui.Gui, path string) {
  // cmd := exec.Command(EXEC_MTRIAGE, "run", "../../examples/sel-local.yaml")
  cmd := exec.Command(EXEC_MTRIAGE, "run", path)
  cmd.Run()
}

func inputEntered(g *gocui.Gui, v *gocui.View) error {

  o := history[len(history)-1].option.(textInputOption)

  input := v.Buffer()
  if len(input) == 0 {
    return nil
  }
  input = input[:len(input)-1]  // remove trailing newline
  vInput := o.Validate(g, input)
  if vInput == nil {
    return nil
  }

  if err := g.DeleteView(VIEW_INPUT); err != nil {
    return err
  }
  if _, err := g.SetCurrentView(VIEW_MAIN); err != nil {
    return err
  }

  update(g, o, vInput)

  return nil
}

func undo(g *gocui.Gui, v *gocui.View) error {
  popState(g)
  return nil
}

func cursorUp(g *gocui.Gui, v *gocui.View) error {
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
      update(g, o, selectedOption)
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
    v, err := g.View(VIEW_SIDE)
    if err != nil {
      return err
    }
    if v != nil {
      v.Clear()
      printConfigInView(v, cfg)
    }
    return nil
}

func updateOptionView(g *gocui.Gui, o option) error {

  v, err := g.View(VIEW_MAIN)
  v.SetCursor(0, 0)
  if err != nil {
    return err
  }
  if v != nil {
    v.Clear()
    if err := g.DeleteView(VIEW_INPUT); err != nil {}
    if err := g.DeleteView(VIEW_SAVE); err != nil {}
    o.Present(g, v)
  }
  return nil
}

func logger(g *gocui.Gui, text string) {
  v, _ := g.View(VIEW_CONSOLE)
  if v != nil {
    fmt.Fprintln(v, text)
  }
}

func logCfg(g *gocui.Gui, cfg map[string]interface{}) {
  logger(g,  "------")
  for k, v := range cfg {
    if val, ok := v.(string); ok {
      logger(g,  k + ": " + val)
    } else {
      configMap := v.(map[string]string)
      for k1, v1 := range configMap {
        logger(g,  "    " + k1 + ": " + v1)
      }
    }
  }
  logger(g,  "------")
}

func printConfigInView(v *gocui.View, cfg map[string]interface{}) {

  if folder, ok := cfg["folder"].(string); ok {
    fmt.Fprintln(v, "folder: \"" + folder + "\"")
  }

  if phase, ok := cfg["phase"].(string); ok {
    fmt.Fprintln(v, "phase: \"" + phase + "\"")
  }

  if module, ok := cfg["module"].(string); ok {
    fmt.Fprintln(v, "module: \"" + module + "\"")
  }

  if config, ok := cfg["config"].(map[string]interface{}); ok {
    fmt.Fprintln(v, "config:")
    if children, ok := config["children"].([]map[string]interface{}); ok {
      fmt.Fprintln(v, "  children:")
      for i := range children {
        printMap(v, children[i], "    ")
      }
    } else {
      printMap(v, config, "  ")
    }
  }
}

func printMap(v *gocui.View, m map[string]interface{}, ind string) {
  for key1, val1 := range m {
    var strVal string
    b, ok := val1.(bool)
    if ok {
      strVal = strconv.FormatBool(b)
    }
    i, ok := val1.(int)
    if ok {
      strVal = strconv.Itoa(i)
    }
    whitelist, ok := val1.([]string)
    if ok {
      var str strings.Builder
      str.WriteString("[")
      for i := 0; i < len(whitelist); i++ {
        str.WriteString(whitelist[i])
        if i < len(whitelist)-1 {
          str.WriteString(",")
        }
      }
      str.WriteString("]")
      strVal = str.String()
    }
    if strVal == "" {
      strVal = val1.(string)
    }
    fmt.Fprintln(v, ind + key1 + ": \"" + strVal + "\"")
  }
}
