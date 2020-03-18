# Why Mtriage?

Recent advances in deep learning make it a very powerful technique when
analysing visual and audio media. The state of the art in object detection in
images performs comparably to humans, and the recognition of speech and other
audio signatures is also impressively effective. Due to these capabilities,
deep learning has the potential to dramatically effect the scale on which human
rights organisations can track and monitor weapons, trade, and other objects
that signify possible human rights abuses.

In practice, however, using machine learning in human rights research is
difficult. The state of tooling is such that it is difficult to use for anyone
who does not have a background in software development. Even if the simple aim
is to run a pretrained classifier for object detection on an image, there is
often a lot of installation pain and indirection in online resources. On top of
this, to deploy classifiers at scale, analysing thousands of videos rather than
just one image, a lot of custom plumbing is required. Human rights researchers
do often not have the resource to employ an in-house software developer for
this plumbing, which effectively means that human rights research rarely uses
machine learning. At best, it is limited to a few organisations who have the
technical resource to deploy custom software infrastructure, or who can partner
with data science firms to do so.

We developed mtriage to address the insufficiency in machine learning tooling
for human rights research, with the hope that it can democratise the use of
machine learning-- and also other more advanced computational analytic
techniques. In the first instance, it provides both pretrained object detection
classifiers, as well as the means to use them to analyse public domain media.
Mtriage is structured modularly: we intend to add new classifiers, and to
support new sources and kinds of public domain media, as we develop these
capabilities for ongoing and future Forensic Architecture investigations.

Mtriage is open source and in active development. This means that everyone can
not only use mtriage in their own research, but also that community
contributions (of a new classifier, or a new media source) can potentially be
made available to all other users as upstream contributions.

To get started with mtriage, check out [Getting Started](docs/getting-started.md).
