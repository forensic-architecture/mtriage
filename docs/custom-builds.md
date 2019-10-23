# Custom Builds

The default 'dev' and 'dev-gpu' mtriage images (available [here](https://cloud.docker.com/u/forensicarchitecture/repository/docker/forensicarchitecture/mtriage)) include dependencies for all selectors and all analysers. While this is useful for
playing around with mtriage locally, as everything is already installed, it is
unnecessarily weighty if you are trying to deploy mtriage, or use only some
components.

For this reason, it is possible to create custom mtriage builds through the
`mtriage dev build` command. Without any additional flags, this command will
build a Docker image with all dependencies for all components installed. (This
is the command that is run on successful merges to master to create the Docker
Hub image).

To exclude the dependencies for certain modules, you can pass a blacklist.txt
file via flag to the build command:
```
./mtriage dev build --blacklist example.blacklist.txt
```

Modules specified in the blacklist will *not* be installed in the build. For
example, if you wanted a build of mtriage with only dependencies for selectors
installed, you could pass a blacklist that specified all analysers.

TODO: add option to pass a whitelist, which is probably a more intuitive way of
doing it.

TODO: manufacture an appropriate tagging scheme for custom builds, and a flag
that allows forensicarchitecture/mtriage images with non-default tags to be run
via the CLI. 

