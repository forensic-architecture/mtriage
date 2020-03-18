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
image](https://cloud.docker.com/u/forensicarchitecture/repository/docker/forensicarchitecture/mtriage). Mtriage commands will run much faster after this first one:

```bash
./mtriage dev test
```

Depending on what components you intend to use, there may be additional setup
required. Check the [component docs folder](./docs/components) before using an 
analyser or if you run into an authentication or setup issue.

Assuming this command completed and all the tests passed, you are now ready to
run mtriage workflows! 
