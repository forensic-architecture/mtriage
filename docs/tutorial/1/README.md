# 1a. Working with selectors

Mtriage workflows are orchestrated using YAML files. These config files
indicate components used to select and/or process media. Most mtriage YAML
files are very simple, and mostly consist of configuration specific to the
components being run. For example, here is the config for the youtube run we'll
do in a second:

```yaml
folder: media/demo_official/1
select:
  name: Local
  config:
    source: data/demo/1local
    # aggregate: true
```


In order to analyse media with mtriage, we first need to 'select' that media
from somewhere. Selectors designate and index a 'media space', and then
download the relevant media in that space as local mtriage elements (elements
are essentially folders). In this example we'll use the
[Local](../src/lib/selectors/Local) selector, which simply selects from media
already on your computer's file system.

Let's try running the config:

```
./mtriage run docs/tutorial/1/1a.yaml
```

You should see the following logs:

```
Local: index: Indexing local folder...
Local: index: indexed file: 1.txt
Local: index: indexed file: 2.md
Local: index: indexed file: 3.jpg
```

If you look in media/demo_official/1/Local/data, you'll see the three folders,
each containing one of the indexed media, as well as an 'element_map.csv'. You
won't normally need to look carefully at the folder structure in folders
mtriage produces, but it's helpful to have a look to get an idea of how things
are working under the hood. 

As a quick primer, mtriage works by formatting media as 'elements', which in
this case are represented simply as folders on disk. (Later we'll see that we
can store elements remotely, as well.) Selectors work by indexing media, and
then retrieving that media and storing them as elements. This prepares media to
be processed using an Analyser, which take elements as input and produce
elements as output. The 'elements_map.csv' is a listing that mtriage uses
internally.

# 1b. Working with analysers

Now that we've selected some elements, let's get to analysing them. We're going
to use the very straightforward 'ExtractTypes' analyser, which simply extracts
elements that have media with particular types. Here's the config:

```yaml
folder: media/demo_official/1
elements_in:
  - Local
analyse:
  name: ExtractTypes
  config:
    exts:
      - txt
      - md
```

The first line here indicates that we are working with the elements in the
folder 'media/demo_official/1'. The `elements_in` attribute indicates which
elements we want to process, which we specify via __the name of the selector we
used to produce them__. All workflows in mtriage are contained by a base
selector in this way. If we had used multiple selectors to index and retrieve
media, we could add extra line items in the `elements_in` array to indicate we
want to use them as well.

The `analyse` attribute indicates which analyse we want to use, and the
configuration we want to use for the analyser. The 'ExtractTypes' analyser
recieves an array of extensions (`exts`) that represents a whitelist of the
media types we want to extract.


Let's run this config and take a look at the result:

```
./mtriage run docs/tutorial/1/1b.yaml
```

We should see the following logs:

```
ExtractTypes: None: Running in parallel
ExtractTypes: analyse: Extracting element 1 with paths: ['1.txt']
ExtractTypes: analyse: Extracting element 2 with paths: ['2.md']
ExtractTypes: analyse: No extracted media in element 3.
```

As we can see, the analyser has extracted the two elements with media that have
matching extensions, and skipped over element 3 (which contains '3.jpg'). The
first logged line is an important aspect of mtriage's value add: it runs these
operations in parallel, across as many CPUs are available on your computer.

# 1c. Putting it all together

We can put both selection and analysis together in a single config, as follows:

```yaml
folder: media/demo_official/1
select:
  name: Local
  config:
    source: data/demo/1local
analyse:
  name: ExtractTypes
  config:
    exts:
      - txt
      - md
```

And run it with:

```
./mtriage run docs/tutorial/1/1c.yaml
```

Of course, this particular workflow isn't very useful at all, but hopefully you
are already beginning to see how we can use mtriage to orchestrate much more
meaningful and powerful media workflows. In the next tutorial, we'll use
mtriage to reformat audio files.

[Go to tutorial 2](/docs/tutorial/2/README.md)
