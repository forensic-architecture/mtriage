# Contributing to mtriage

Hi there! Thank you already, for taking the time to contribute to improve
mtriage. This document is the right place to start. Read it thoroughly!

## What do I need to know to help?
### Python
The majority of mtriage is written in Python. You'll be best placed to
contribute if you're comfortable working with classes, decorators, etc- but
don't worry if these terms are not familiar just yet!

### Docker
Mtriage uses Docker containers to abstract dependencies from needing to be
installed on the local host. It's not essential, but a good operational
knowledge of Docker will be helpful.

## Do I need to be an experienced Python developer?
Contributing can of course be about contributing code, but it can also take
many other forms. A great amount of work that remains to be done to make
mtriage a usable community tool doesn't involve writing any code. The following
are just a few examples of other welcome contributions:

- Writing, updating or correcting documentation.
- Requesting a feature
- Reporting a bug

If you're new to this project and looking for a good problem to get started,
you might want to check out the open issues that are tagged ["good first issue"](https://github.com/forensic-architecture/mtriage/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22).

These are a rnage of the issues that have come up in conversation for which we
would welcome community contributions. These are, however, by no means
exhaustive! If you see a gap or have an idea, please open up an issue to
discuss it with mtriage's maintainers.

## What parts of mtriage are being actively developed?
You can learn about what we are currently working on by looking at the latest
update. [Updates can be found here](docs/updates).

## How do I make a contribution?
1. Make sure you have a [GitHub account](https://github.com/signup/free)
2. Fork the repository on GitHub. This is necessary so that you can push your
    changes, as you can't do this directly on our repo.
3. Get set up with a local instance of mtriage. The easiest way to do this is
   by [following through the tutorial](https://github.com/forensic-architecture/mtriage/blob/main/docs/tutorial/1/README.md).
4. [Join our Discord server](https://discord.gg/PjHKHJD5KX). Here you'll be able
    to track commits that are actively being made across our projects; but more
    importantly it's where you can ask questions if something's not clear or
    not working as you expect. The #mtriage and #support channels are the two
    best places to ask questions about setting mtriage up, or how it works.

Once you're set up with a local copy of mtriage, you can start modifying code
and making changes. 

When you're ready to submit a contribution, you can do it by making a pull
request from a branch on your forked copy of timemap to this repository. You
can do this with the following steps:
1. Push the changes to a remote repository. If the changes you have made
   address a bug, you should name it `bug/{briefdesc}`, where `{briefdesc}` is
   a hyphen-separated description of your change. If instead you are
   contributing changes as a feature request, name it `feature/{briefdesc`}. If
   in doubt, prefix your branch with `feature/`.
2. Submit a pull request to the `develop` branch of
   `forensic-architecture/mtriage` (not `main`!).
3. Wait for the pull request to be reviewed by a maintainer.
4. Make changes to the pull request if the reviewing maintainer recommends
   them.
5. Celebrate your success once your pull request is merged!

### How do I validate my changes? 
We are still working on a full set of tests, but there are some basic ones in
place that need to pass before we can merge any contributions.

Tests can be run with the following command:
```
./mtriage dev test
```

All code must be formatted according to the
[black](https://github.com/ambv/black) formatter. (CI builds will fail if code
is not Black-formatted.)

## New components
If you are contributing a new component (i.e. an analyser or a selector),
ensure that your component lists the correct dependencies. You can do so by
ensuring that it works in a [standalone custom build](./docs/custom-builds.md).


