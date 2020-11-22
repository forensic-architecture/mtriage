# Custom Builds

The default 'dev' and 'dev-gpu' mtriage images (available
[here](https://cloud.docker.com/u/forensicarchitecture/repository/docker/forensicarchitecture/mtriage))
include dependencies for all selectors and all analysers. While this is useful
for playing around with mtriage locally, as everything is already installed, it
is unnecessarily weighty if you are trying to deploy mtriage, or use only some
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

You can also pass a whitelist with the `--whitelist` flag.

### Testing Components in a Standalone Build

If you are contributing a new analyser or selector, you should confirm that it
runs without issues in a standalone build. Mtriage uses whitelists to allow the
creation of standalone builds. Work through the following steps to create
a custom build with your component:

1. Create a 'whitelist.txt' in the core mtriage directory, which contains
   a single line with the name of your new component. For example, if your
   component is called 'MyCustomComponent', your whitelist would look like
   this:
    ```
    MyCustomComponent
    ```
2. Create the custom mtriage image with solely your component with the
   following command:
   ```
   ./mtriage dev build --tag mycustomcomponent --whitelist whitelist.txt
   ```
3. Test the running of your component with the following command:
    ```
    ./mtriage run path/to/config.yml --tag mycustomcomponent --dev
    ```

Please note that mtriage is still in a very early stage of development, but we
will keep updating this document as the code changes.

Thanks again for your interest and for your future contributions!

