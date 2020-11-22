# Contributing to mtriage

Welcome and thanks for your interest!

The easiest way to get involved in the Forensic Architecture OSS community is
to [join the discussion on Discord](https://discord.gg/FJ4XsCg). If you're
having trouble getting up and running with any of our codebases, please don't
hesitate to ask questions on the #support channel.

### Releases We are developing mtriage on an approximate 2-week-long release
cycle. Issues being tackled in the current release usually have a 'release'
tag, and are normally listed in the [Release project
board](https://github.com/forensic-architecture/mtriage/projects/1).

You can learn about what we are currently working on by looking at the latest
update. [Updates can be found here](docs/updates).

### Help Wanted The best issues to get started on are those with a 'help
wanted' tag. Unless they are already assigned, these are generally issues that
are sufficiently removed from our core development cycle, and are typically
good for community contributors. Issues with an additional 'good first issue'
tag don't require a much knowledge of mtriage's internals specifically, and so
are ideal for new contributors.

### Tests and Formatting All python code is formatted with the
[black](https://github.com/ambv/black) formatter. (CI builds will fail if code
is not Black-formatted.)

Tests coverage is not complete, but they can be run with the following:
```
python ./mtriage dev test
```


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
   ./mtriage build --tag mycustomcomponent --whitelist whitelist.txt
   ```
3. Test the running of your component with the following command:
    ```
    ./mtriage run path/to/config.yml --tag mycustomcomponent --dev
    ```

Please note that mtriage is still in a very early stage of development, but we
will keep updating this document as the code changes.

Thanks again for your interest and for your future contributions!

