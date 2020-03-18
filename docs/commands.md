## commands 

### `./mtriage run path/to/file.yaml`

The primary command to trigger new mtriage workflows. Each run takes a YAML
file that specifies which selectors and analysers to run (i.e. `./mtriage run
examples/youtube.yaml`). See [examples folder](./examples) for examples of how
to specify different analyser options.

You can also pass the following flags to the run command:

| flag  | description |
|-------|-------------|
| `--gpu` | Run using the mtriage GPU image. This will speed up certain analysers that depend on it |
| `--tag` | Allows you to run mtriage with a custom build by passing the name of the Docker image tag you used during the custom build (see below) |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |
| `--dev` | Run using local code, to see changes in development. This will also bypass internal mtriage error handling, allowing you to see the origin of errors |

### `./mtriage dev build`

The command to build an mtriage Docker image from source code. You won't need
this unless you are developing mtriage, as the latest images are also on [Docker
Hub](https://hub.docker.com/repository/docker/forensicarchitecture/mtriage).

| flag  | description |
|-------|-------------|
| `--gpu` | Build the GPU image. Will build the CPU image otherwise |
| `--tag` | Give your build a custom tag. Will default to 'dev' or 'dev-gpu' |
| `--blacklist` | Give build a path to a blacklist that lists which components to exclude. See [example.blacklist.txt](./example.blacklist.txt) for format. |
| `--whitelist` | Give build a path to a whitelist that lists which components to include. |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |

### `./mtriage dev test`

Run all mtriage tests. These run in two parts for the time being: one inside 
Docker, and one on your local Python installation.

| flag  | description |
|-------|-------------|
| `--verbose` | Run verbose tests, showing all print statements in the console. |
| `--gpu` | Test the GPU image. Will build the CPU image otherwise |
| `--tag` | Test with a custom tag. Will default to 'dev' or 'dev-gpu' |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |

### `./mtriage dev clean `

Remove all mtriage Docker containers, stopped or running.

### `./mtriage dev`

Open a bash shell inside mtriage's Docker container. For debugging.

| flag  | description |
|-------|-------------|
| `--gpu` | Run the GPU image. Will run the CPU image otherwise |
| `--tag` | Run with a custom tag. Will default to 'dev' or 'dev-gpu' |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |
| `--yaml` | Pass a path to an mtriage YAML config to saturate the shell environment with its runtime parameters. (I.e. if you run `python run.py` from inside the src folder, it will use this YAML). |


