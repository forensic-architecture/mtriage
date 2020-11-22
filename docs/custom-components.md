# Custom Components

Components are the main way in which mtriage is intended to be extended.
A custom component can either be a selector (to index and retrieve media to
kick of an mtriage workflow) or an analyser (to process media in an mtriage
workflow). 

Components currently sit within [src/lib/selectors](/src/lib/selectors) and
[src/lib/analysers](/src/lib/analysers). Each component is self-contained
(along with a listing of the dependencies it requires) inside a folder there.

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

