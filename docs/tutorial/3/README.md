# 3a. Selecting media with Youtube

The Youtube selector uses [Youtube's Data API](https://developers.google.com/youtube/v3)
to find videos uploaded between certain dates using a search term. This API
requires an API key, which is free to get. Follow the instructions in [the
documentation](/docs/components/youtube.md), adding the API key in a line in
the .env file at the root of your mtriage folder.

With the API key in our mtriage environment, we can run the following config to
select some videos from youtube:

```yaml
folder: media/demo_official/3
select:
  name: Youtube
  config:
    search_term: Tear gas 
    uploaded_before: "2015-10-02T00:00:00Z"
    uploaded_after: "2015-10-01T00:00:00Z"
```

Let's run it:

```
./mtriage run docs/tutorial/3/3a.yaml
```

The Youtube selector indexes videos by making an API call, and then downloads
the videos in parallel according to however many CPU cores your computer has
available. By default, it downloads the videos at very low quality, and it also
retrieves a 'meta.json' file regarding the video's provenance and other meta
information.


NOTE: This step currently doesn't work, and, until we get a better Docker image up, you'll need to use a workaround. The installation as-is uses an old version of youtube-dl and cannot properly fetch videos. To fix this, you need to:

1. Run ``./mtriage dev`` to open a shell in the terminal
2. Run ``pip3 install yt-dlp``. It may give you an error message, but it's likely this is okay.
3. Check that yt-dlp has installed correctly. Run ``pip3 show yt-dlp`` and you should see a version installed. (Also okay if this command fails).
4. Run ``python3 src/run.py --yaml docs/tutorial/3/3a.yaml`` which should work properly.

# 3b. Image classification with KerasPretrained 

Let's now classify the frames in the videos that we've downloaded using image
classifiers that have been pretrained on the labels in the
[ImageNet](http://www.image-net.org/) database. We'll do so using a neural net
architecture called [ResNet](https://arxiv.org/abs/1512.03385), which is
a state-of-the-art architecture for image classification. We'll give the
KerasPretrained analyser the three labels we're interested in--tank, rifle, and
military uniform--to indicate that we want to predict the appearance of these
objects in the videos' frames.

```yaml
folder: media/demo_official/3
elements_in:
  - Youtube
analyse:
  - name: Frames
  - name: KerasPretrained
    config:
      model: ResNet50
      labels:
        - tank
        - rifle
        - military uniform
```

Note that the first time you runthis config, it will download the pretrained
weights for Resnet, which is a file ~100mb in size (this download only happens
once):

```
./mtriage run docs/tutorial/3/3b.yaml
```

# 3c. A complete mtriage workflow

Now that we've tested the parts, let put this all together in a single
workflow, and broaden the media space slightly:

```yaml
folder: media/demo_official/3c
select:
  name: Youtube
  config:
    search_term: tear gas + mexico
    uploaded_before: "2018-11-30T00:00:00Z"
    uploaded_after: "2018-11-15T00:00:00Z"
analyse:
  - name: Frames
  - name: ImageDedup
    config:
      threshold: 3
      method: dhash
  - name: KerasPretrained
    config:
      model: ResNet50
      labels:
        - tank
        - rifle
        - military uniform
  - name: Rank
```


In this config, we select videos uploaded between the 15th and 30th of November
in 2018 that match both "tear gas" and "mexico" in Youtube's search API. Once
downloaded, we split each video into frames, deduplicate similar images using
[dhash](https://github.com/maccman/dhash), classify deduplicated frames using
resnet, and then create an additional JSON that ranks the classified videos
according to the number of positive frames they contain (using the `Rank` analyser).

That's a fair bit of computational work. Go and grab a beverage while this
command runs to completion, if you like:

```
./mtriage run docs/tutorial/3/3c.yaml
```
Once it's finished, take a look at the files that the workflow has produced in
the media/demo_official/3c folder. You should see everything in a 'Youtube'
folder (as you may recall, mtriage runs are organised internally by selector),
and then most of the created media in a 'derived' folder inside that.

You're officially finished with the mtriage tutorial. If you want to work
through the media mtriage has just analysed using a frontend interface,
however, as we do here at [Forensic Architecture](https://forensic-architecture.org),
head over to our [mtriage-viewer](https://github.com/forensic-architecture/mtriage-viewer)
and follow the instructions there!
