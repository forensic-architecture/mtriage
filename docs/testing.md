# Testing

Mtriage has three kinds of tests:
1. Tests for the core code that runs inside Docker (in src/test).
2. Tests for the outer orchestration logic (in test/).
3. Tests for analysers and selectors (in each component folder, in test/).

Each kind of test is run with appropriate containerisation given its context,
i.e. tests of type 1 are run inside Docker, whereas tests of type 2 are run
using the locally installed Python environment.

To run all tests, use the following command:
```
./mtriage dev test
```
See [docs/custom-components.md](./custom-components.md) for more information on
how to test a new component.
