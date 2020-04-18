

## `example1.py`

This is where I started with `python3` by "just" replacing the CLI command 

```
gst-launch-1.0 \
videotestsrc is-live=true ! \
queue ! videoconvert ! x264enc byte-stream=true ! \
h264parse config-interval=1 ! queue ! matroskamux ! queue leaky=2 ! \
tcpserversink port=7001 host=0.0.0.0 recover-policy=keyframe sync-method=latest-keyframe sync=false
```

in Python. 🤓

_Please note that I am no `python` ninja, so don#t be to hard with the code-style_

Since I am a lazy guy (also called software engineer) I did not want to write much repeating code.

This is why I added a little `Helper`-loop which does 

- Creating the GStreamer Elements `element= Gst.ElementFactory.make(...)` [Link](https://lazka.github.io/pgi-docs/#Gst-1.0/classes/ElementFactory.html#Gst.ElementFactory.make)

- as well as setting the properties for me `element.set_property(...)`

#### btw -> found it late but this documentation saved my life [GST1.0 Python Docs](https://lazka.github.io/pgi-docs/#Gst-1.0)

---

## `example2.py`

Next step was to try to find a simple ingest opportunity with focus on latency.
So I choose UDP to send via `ffmpeg` -> `gstreamer` -> and receive it back via `ffmpeg`

1. `ffmpeg -re -f lavfi     -i "testsrc=size=1920x1080:rate=25"     -f lavfi     -i "sine=frequency=800:sample_rate=48000" -preset ultrafast -vcodec libx264 -tune zerolatency -b 900k -f mpegts udp://127.0.0.1:2088` 

    _To send an `udp`-stream to the docker container._

2. `gst-launch-1.0 udpsrc port=2088 ! queue ! decodebin ! queue ! videoconvert ! x264enc byte-stream=true tune="zerolatency"  ! h264parse config-interval=1 ! queue ! matroskamux ! queue leaky=2 ! tcpserversink port=7001 host=0.0.0.0 recover-policy=keyframe sync-method=latest-keyframe sync=false`

    _Recieve the `udp`-stream and offer it via `tcpserversink` to the host outside of the container_

3. `ffplay tcp://127.0.0.1:7001`

    _This is the command every test will result in, till now, receive the stream as a `tcp`-stream with `ffplay`_
<br>
<br>
#### So we need to bin another port for SRT to the Container which is UDP !!!

`docker run -it $PWD/examples:/opt -p 7001:7001 -p 2088:2088/udp riha/gstreamer-101:latest`

### Introducing debugging GStreamer

If you want to learn something about the Elements itself `Gstreamer` offers a nice CLI tool called `gst-inspect-1.0`, where you can inspect all available Elements like `gst-inspect-1.0 videotestsrc`, which shows you all the avilable Pad and Caps, aso.

Ohhh yes, Pads and Caps are a hugh topic.
I did not care much about it the first few days since the CLI `gst-launch-1.0` takes care about everything itself.
As you start writing your own programs this topic gets highly actual, since a lot of things break because you need to take care of Pads and their availablity.

- Always
- Sometimes
- Request

So it is good to read [this page from the official docs](https://gstreamer.freedesktop.org/documentation/application-development/basics/pads.html), which I of course did not do, as it seems to be too complex when you start. Big mistake!

I read [this very nice blog post](http://lifestyletransfer.com/how-to-write-gstreamer-plugin-with-python/) which helped me a lot, like a lot lot
<br>
<br>
<br>
![Alt Text](https://media.giphy.com/media/wi8Ez1mwRcKGI/giphy.gif)

<br>
<br>
Really!
<br>
<br>
<br>

There is a good way to debug `Gstreamer` within the CLI.

You just set the Debug-Level in the ENV variable `GST_DEBUG=4 gst-launch-1.0 ...`

Or you can output so9 called `*.dot`-Files by setting this ENV variable `GST_DEBUG_DUMP_DOT_DIR=/opt/ gst-launch-1.0 ...`

You would need to install `graphviz` to transform those `DOT`-Files into Images to look at.

I used a little `bash` script which I put inside the `/snippets`-folder !

### But how to do it in python?

I wrote a little function `def draw_pipeline(pipe, filename):` which I use ever since, it has been copied an pasted into all my `python`-scripts where GStreamer is available and is the **MOST HELP** so far!

**Look at it in `example2.py`!**

- it needs to have `apt-get install -y graphviz-dev graphviz` installed on the OS
- as well as `pip3 install pygraphviz` for python as well!

_should be in the `Dockerfile`, but let's find out_
```
Yes, it is in the `installs/install-python-utils.sh`
```

---

## `example3.py`

Next I wanted to get real ingested video into this pipeline. As everybody it switching from `rtmp` to `srt` on a professional base, I wanted to feed the pipeline with an external SRT-stream, I create with `ffmpeg`, an put this one into the mix.

_pipeline looks like_

```
gst-launch-1.0 -v srtsrc uri="srt://:2088?mode=listener" ! queue ! decodebin ! queue ! x264enc byte-stream=true ! h264parse config-interval=-1 ! queue ! matroskamux ! queue leaky=2 ! tcpserversink port=7001 host=0.0.0.0 recover-policy=keyframe
```

`ffmpeg`-SRT ingest look like this

```
ffmpeg  -re     -f lavfi     -i "testsrc=size=1920x1080:rate=25"     -f lavfi     -i "sine=frequency=800:sample_rate=48000"     -preset:v superfast     -pix_fmt yuv420p     -map 0:v     -map 1:a     -c:v libx264 -tune zerolatency -profile:v high -preset veryfast -bf 0 -refs 3 -sc_threshold 0     -g 30     -keyint_min 30     -b:v 6000k     -c:a aac -ar 48000 -ac 2 -max_muxing_queue_size 1024 -f mpegts "srt://:2088"
```



`GST_DEBUG=4 gst-launch-1.0 udpsrc port=2088 ! queue ! decodebin ! queue ! videoconvert ! x264enc byte-stream=true ! \
h264parse config-interval=1 ! queue ! matroskamux ! queue leaky=2 ! \
tcpserversink port=7001 host=0.0.0.0 recover-policy=keyframe sync-method=latest-keyframe sync=false`
