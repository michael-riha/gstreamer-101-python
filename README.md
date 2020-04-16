# GStreamer-101-python
_This is a collection of all the examples I created in 2020, during my learning phase with GStreamer 1.0_

<br>
As everybody I started by using the gstreamer cli `gst-launch-1.0` and since I wanted to build plugins as well and not pollut my MacOS, with different versions of `gstreamer` and others, I decided to use `Docker`.

## Docker Container to run `gstreamer`

I include the `.dockerfile` I built based on `ubuntu` (`prev 18.04` but I changed to `19.10` during this phase).

What made this a bit difficult is that for simple `gstreamer` pipelines most people use `xvimagesink` or `glimagesink` or ... [ Platform-specific elements](https://gstreamer.freedesktop.org/documentation/tutorials/basic/platform-specific-elements.html?gi-language=python) to direktcly test and output your pipeline.

This is also possible with `docker` as you can use `XWindow` (in my case with XQuartz on MacOS) but it is not very handy, at least this is my impression.

So what I do most of the time, is using the [`tcpserversink`](https://gstreamer.freedesktop.org/documentation/tcp/tcpserversink.html?gi-language=python#tcpserversink-page) sending via TCP-port from the `container`.

And on the other end, I use `ffmpeg` wo receive the video on the host.

#### Example:

1. Expose a TCP-port on the container and bind it to a local port on the host `docker run -it -p 7001:7001 ...`

2. Start a simple TCP-Server
    - `videotestsrc`
    - `x264enc`
    - `tcpserversink` 

        `gst-launch-1.0
        videotestsrc is-live=true !
        queue ! videoconvert ! x264enc byte-stream=true !
        h264parse config-interval=1 ! queue ! matroskamux ! queue leaky=2 !
        tcpserversink port=7001 host=0.0.0.0 recover-policy=keyframe sync-method=latest-keyframe sync=false`

3. watch the video stream on the host with `ffmpeg`

    `ffplay tcp://127.0.0.1:7001`

    this will show you a window with a testvideo and this output in `ffmpeg`

    ```
    Input #0, matroska,webm, from 'tcp://127.0.0.1:7002':    
    0B f=0/0
    Metadata:
        encoder         : GStreamer matroskamux version 1.16.1
        creation_time   : 2020-xx-xxT14:00:47.000000Z
    Duration: N/A, start: 4761.466000, bitrate: N/A

    Stream #0:0(eng): Video: h264 (High 4:4:4 Predictive), yuv444p(tv, bt709, progressive), 1920x1080 [SAR 1:1 DAR 16:9], 30 fps, 30 tbr, 1k tbn, 60 tbc (default)

    Metadata:
      title           : Video
      ENCODER         : x264
    ```

## Building the `Docker`-Image

`docker build --tag=riha/gstreamer-101 .`

## Running the `Docker`-Image

`docker run -it $PWD/examples:/opt riha/riha/gstreamer-101:latest`


![Alt Text](https://media.giphy.com/media/3o7TKUM3IgJBX2as9O/giphy.gif)

# Jump to the `readme.md` inside of [/examples](https://github.com/michael-riha/gstreamer-101-python/tree/master/examples)