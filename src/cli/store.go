package main

import (
  "github.com/jroimartin/gocui"
  "log"
  "gopkg.in/yaml.v2"
  "strconv"
  "io/ioutil"
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
  newState.configs = copyMap(s.configs)
  return newState
}

func (s state) IsEmpty() bool {
  return s.phase == ""
}

func (s state) AsMap() map[string]interface{} {
  stateMap := make(map[string]interface{})
  if s.phase != "" {
    stateMap[OPT_PHASE] = s.phase
  }
  if s.folder != "" {
    stateMap[OPT_FOLDER] = s.folder
  }
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

// MODULE ARGS

type Arg struct {
  name string
  required bool
  input string
}

func (a Arg) String() string {
  return "name: " + a.name + " input: " + a.input + " required: " + strconv.FormatBool(a.required)
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

  newState := currentState().Copy()

  if _, ok := o.(saveOption); ok {
    newState.currentModule = ""
    newState.option = getNextOption(newState)
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
  newState.option = getNextOption(newState)
  pushState(newState)
}

func currentState() state {
  if len(history) > 0 {
    return history[len(history)-1]
  } else {
    initState := state{ option: getNextOption(state{}) }
    pushState(initState)
    return initState
  }
}

func getNextOption(newState state) option {

  if newState.folder == "" {
    return textInputOption{ prompt: "please enter the path to your working directory", name: "folder", validationType: TYPE_FOLDER  }
  }

  if newState.phase == "" {
    return multiOption{ options: []string{"select","analyse"}, name: "phase" }
  }

  if newState.currentModule == "" {
    modules := modulesForPhase(newState.phase)
    return multiOption{ options: modules, name: "module" }
  }

  configOptions := configOptionsForModule(newState.currentModule, newState.phase)
  moduleConfig := newState.configs[newState.currentModule].(map[string]interface{})
  existingKeys := keysForMap(moduleConfig)
  for i := range configOptions {
    option := configOptions[i]
    exists := false
    for j := range existingKeys {
      key := existingKeys[j]
      if option.name == key {
        exists = true
      }
    }

    if !exists {
      name := option.name
      input := option.input
      prompt := "please enter a " + input + " for argument:\n\n   "  + name
      return textInputOption { prompt: prompt, name: name, validationType: input }
    }
  }
  return saveOption{ isComposable: newState.phase == PHASE_ANALYSE }
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

func modulesForPhase(phase string) []string {
  path, _ := phaseToLibFolder(phase)
  return dirNamesIn(path, []string{MODULE_META})
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

func argsPathForModule(module string, phase string) string {
  phaseDir, _ := phaseToLibFolder(phase)
  return phaseDir + "/" + module + "/args.yaml"
}
