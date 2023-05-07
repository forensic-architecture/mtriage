# Install 

mtriage is currently in active development, and is not yet packaged in any way.
It uses [Docker](https://www.docker.com/products/docker-desktop) to manage
dependencies, which you will need to download to ensure mtriage works as
expected. 

Follow the instructions relevant to your operating system to install Docker CE.
Docker Desktop (Mac installation [here](https://docs.docker.com/v17.12/docker-for-mac/install/),
Ubuntu installation [here](https://docs.docker.com/v17.12/install/linux/docker-ce/ubuntu/)). 
If you have a CUDA GPU, you can use [Nvidia Docker](https://github.com/NVIDIA/nvidia-docker)
instead of Docker to make certain analysers more performant.

NOTE (05/2023): if you are on Apple Silicon, your machine will not be able to natively run FA's docker images. In order to fix this, you'll need to [enable virtualization](https://collabnix.com/warning-the-requested-images-platform-linux-amd64-does-not-match-the-detected-host-platform-linux-arm64-v8/) by changing some settings in Docker Desktop. Navigate to Settings > General and make sure the "Use Virtualization framework" box is checked. After, navigate to Settings > Features in development and check the "Use Rosetta for x86/amd64 emulation on Apple Silicon." If you're well-versed in Docker, you can set the 'platform' flag to 'linux/amd64' in the Dockerfile. If not, the easiest solution is to modify your personal ~/.bashrc or ~/.zshrc file and add ``export DOCKER_DEFAULT_PLATFORM=linux/amd64`` to it. 

You also need to ensure that [Python 3](https://www.python.org/downloads/) is installed on your computer. Most modern operating systems have a version installed by default. Mtriage will _probably_ work with Python 2.x as well, but it's untested. 

Once you have Docker and Python installed, you can clone the source code and
install the requirements (the only runtime dependency is [pyyaml](https://pyyaml.org/)).

```bash
git clone https://github.com/forensic-architecture/mtriage.git
pip3 install -r requirements.txt
```

### additional setup
Run the test suite to ensure that everython is working. This command may take
a while, as the first time you run mtriage it will download the [latest Docker
image](https://hub.docker.com/r/forensicarchitecture/mtriage). Mtriage commands will run much faster after this first one:

```bash
./mtriage dev test
```

Depending on what components you intend to use, there may be additional setup
required. Check the [component docs folder](/docs/components) before using an 
analyser or if you run into an authentication or setup issue.

Assuming this command completed and all the tests passed, you are now ready to
run mtriage workflows! 
