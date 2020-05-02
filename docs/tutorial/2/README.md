# 2a. An audio workflow

Now that we're familiar with selectors and analysers in principle, let's run
a couple of workflows to get a sense for mtriage's flexibility. Here's a config
that selects a generic audio file using Local, and then converts it to a
specific extension, mp4:

```yaml
folder: media/demo_official/2
select:
  name: Local
  config:
    source: data/demo/2audio
analyse:
  name: ConvertAudio
  config:
    output_ext: mp4
```

Let's run it:

```
./mtriage run docs/tutorial/2/2a.yaml
```

You should see the following output:

```
Local: index: Indexing local folder...
Local: index: indexed file: coffee.m4a
ConvertAudio: None: Running in parallel
ConvertAudio: analyse: Converted 'coffee' from .m4a to .mp3
```

Try creating a different folder in the 'data' folder with several different
video files, modifying the `source` attribute in the config to point to it, and
running this updated config. We're now starting to get a sense of how mtriage
is useful to scale up simple media analysis in parallel for bulk processing.

# 2b. Chaining analysers

What makes mtriage really useful for constructing workflows is the ability to
chain different analysers together. The Etype system tells us something about
the inputs and outputs of each analyser, and with this information we can
reliably string analysers together to do successive analysis.

```yaml
folder: media/demo_official/2
select:
  name: Local
  config:
    source: data/demo/2audio
analyse:
  - name: ConvertAudio
    config:
      output_ext: mp3
  - name: ConvertAudio
    config:
      output_ext: aac
```

Say we wanted to convert an audio file to two different output formats. We can
do it by specifying an analysis chain with two ConvertAudio parts. Let's run
this config:

```
./mtriage run docs/tutorials/2/2b.yaml
```

We'll get the following:

```
Local: index: Indexing local folder...
Local: index: indexed file: coffee.m4a
ConvertAudio: None: Running in parallel
ConvertAudio: analyse: Converted 'coffee' from .m4a to .mp3
ConvertAudio: None: Running in parallel
ConvertAudio: analyse: Converted 'coffee' from .mp3 to .aac
```

Mtriage runs this config in the order that its specificed: selecting media with
the Local selector, using ConvertAudio to convert this selected media to mp3,
and then converting that media (the mp3 file) to aac, using ConvertAudio with
a different configuration.

When mtriage runs analysers in a chain, it keeps the intermediary results by
default. Therefore this config works to produce the two audio versions of the
source video file in which we are interested. In tutorial 3, we'll see how to
conveniently visualise the results of mtriage workflows with
[mtriage-viewer](https://github.com/forensic-architecture/mtriage-viewer).

As we're only extracting audio from one file here, it doesn't make sense to run
analysis in parallel. (As soon as there are as many elements being analysed as
there are CPUs available, however, it does make sense; which is why mtriage
runs in parallel by default.) We can easily run analysis serially by setting
`in_parallel` to false in an analyser's config:

```yaml
folder: media/demo_official/2
select:
  name: Local
  config:
    source: data/demo/2audio
analyse:
  - name: ConvertAudio
    config:
      in_parallel: no
      output_ext: mp3
  - name: ConvertAudio
    config:
      in_parallel: no
      output_ext: aac
```

Try uncommenting the relevant lines with `in_parallel` in
docs/tutorial/2/2b.yaml, and running the config again. You should see
a different line logging that indicates mtriage is running analysis serially.

In the next tutorial, we'll work with the Youtube selector to analyse videos
that are selected using youtube's search API, showing the full power  and
extensibility of mtriage.

[Go to tutorial 3](/docs/tutorial/3/README.md)
