#!/usr/bin/env python

# mix of:
# https://www.programcreek.com/python/example/88577/gi.repository.Gst.Pipeline
# https://github.com/GStreamer/gst-python/blob/master/examples/helloworld.py
# http://lifestyletransfer.com/how-to-launch-gstreamer-pipeline-in-python/

import sys
import os
import collections
from pprint import pprint
import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib

import pdb
import datetime

'''
gst-launch-1.0 udpsrc port=2088 ! queue ! \
decodebin ! queue ! videoconvert ! x264enc byte-stream=true tune="zerolatency" ! \
h264parse config-interval=1 ! queue ! matroskamux ! \
queue leaky=2 ! tcpserversink port=7001 host=0.0.0.0 recover-policy=keyframe sync-method=latest-keyframe sync=false
'''

def main():
  
  #introducing debug in the program itself!
  set_debug(4)
  
  #  https://stackoverflow.com/questions/3426870/calculating-time-difference
  start_time = datetime.datetime.now()
  # not necessarry anymore
  #GObject.threads_init()
  Gst.init(None)

  pipeline = Gst.Pipeline()
  message_bus = pipeline.get_bus()
  message_bus.add_signal_watch()
  #message_bus.connect('message', bus_call, None)

  udp_src= Gst.ElementFactory.make("udpsrc", None)
  udp_src.set_property("port", 2088)
  pipeline.add(udp_src)

  queue0= Gst.ElementFactory.make("queue", None)
  pipeline.add(queue0)

  decodebin= Gst.ElementFactory.make("decodebin", None)
  pipeline.add(decodebin)

  queue1= Gst.ElementFactory.make("queue", None)
  pipeline.add(queue1)

  videoconvert= Gst.ElementFactory.make("videoconvert", None)
  pipeline.add(videoconvert)

  x264enc = Gst.ElementFactory.make('x264enc', None)
  x264enc.set_property("byte-stream", True)
  x264enc.set_property("tune", "zerolatency")
  pipeline.add(x264enc)

  h264parse = Gst.ElementFactory.make('h264parse', None)
  h264parse.set_property("config-interval", 1)
  pipeline.add(h264parse)

  queue2 = Gst.ElementFactory.make('queue', None)
  pipeline.add(queue2)

  matroskamux = Gst.ElementFactory.make('matroskamux', None)
  pipeline.add(matroskamux)

  queue3 = Gst.ElementFactory.make('queue', None)
  queue3.set_property("leaky", 2)
  pipeline.add(queue3)

  tcpserversink = Gst.ElementFactory.make('tcpserversink', None)
  tcpserversink.set_property("port", 7001)
  tcpserversink.set_property("host", "0.0.0.0")
  tcpserversink.set_property("recover-policy", "keyframe")
  tcpserversink.set_property("sync-method", "latest-keyframe")
  tcpserversink.set_property("sync", False)
  pipeline.add(tcpserversink)

  # now link them
  udp_src.link(queue0)
  queue0.link(decodebin)
  # decodebin has a `sometimes`-pad we need to listen to this!
  decodebin.connect("pad-added", decoder_callback, pipeline, queue1)

  queue1.link(videoconvert)
  videoconvert.link(x264enc)
  x264enc.link(h264parse)
  h264parse.link(queue2)
  queue2.link(matroskamux)
  matroskamux.link(queue3)
  queue3.link(tcpserversink)

  draw_pipeline(pipeline, "udpPipeline_on_linked")
  #pdb.set_trace()
  # start play back and listed to events
  pipeline.set_state(Gst.State.PLAYING)
  # create and event loop and feed gstreamer bus mesages to it
  loop = GLib.MainLoop()
  # start play back and listed to events
  pipeline.set_state(Gst.State.PLAYING)
  try:
    loop.run()
  except:
    loop.quit()

def decoder_callback(element, pad, pipeline, queue_to_connect):
  print("a new pad has been added to {element}".format(element=element.name))
  # will be called twice one for audio, one for video!
  #pdb.set_trace()
  if not pad.has_current_caps():
      print (pad, 'has no caps, ignoring')
      return
  
  caps = pad.query_caps(None)
  structure_name = caps.to_string()
  if structure_name.startswith("video"):
      #now link the decodebin_pad -> queue1_pad which is a static pad!
      v_queue_pad = queue_to_connect.get_static_pad("sink")
      pad.link(v_queue_pad)
  '''
  #not yet!
  elif structure_name.startswith("audio"):
  '''
  draw_pipeline(pipeline, "udpPipeline_on_pad_added")

# http://lifestyletransfer.com/how-to-launch-gstreamer-pipeline-in-python/
def bus_call(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
  # https://stackoverflow.com/questions/49858346/how-te-retrieve-stream-statistics-in-gstreamer
  t = message.type
  sys.stdout.write("Received message from -> %s \n" % (message.src.name))
  if t == Gst.MessageType.EOS:
      sys.stdout.write("End-of-stream\n")
  elif t == Gst.MessageType.ERROR:
      err, debug = message.parse_error()
      sys.stderr.write("Error: %s: %s\n" % (err, debug)) 
  elif t == Gst.MessageType.WARNING: 
        # Handle warnings 
        err, debug = message.parse_warning() 
        sys.stderr.write("Warning: %s: %s\n" % (err, debug))
  # https://git.smart-cactus.org/ben/cam-stream/blob/0483fa5d3bb82e8a4212d7190d4541ed4d0653d5/stream.py
  elif t == Gst.MessageType.STATE_CHANGED:
        sys.stderr.write('state changed: %s\n' % (message.parse_state_changed(),))
  elif t == Gst.MessageType.STREAM_STATUS:
        sys.stderr.write('stream status: %s\n' % (message.parse_stream_status(),))
  elif t == Gst.MessageType.QOS: 
        # Handle Qus
        live, running_time, stream_time, timestamp, duration = message.parse_qos() 
        #sys.stderr.write("Qos Message: live %r, running_time %i, stream_time %i, timestamp: %i, duration: %i \n" % (live, running_time, stream_time, timestamp, duration))
        #sys.stderr.write('qos: %s' % (message.parse_qos(),))
  elif t == Gst.MessageType.ELEMENT:
        sys.stderr.write('Element message: %s\n' % (message.get_structure().to_string(),))
  elif t == Gst.MessageType.BUFFERING:
        sys.stderr.write('Buffering message: %s\n' % (message.get_structure().to_string(),))
  elif t == Gst.MessageType.PROGRESS:
        sys.stderr.write('Progress message: %s\n' % (message.get_structure().to_string(),))
  else:
        sys.stderr.write('Bus message: %s: %s \n' % (message.timestamp, t))
        pprint(message)
  return True

# https://gist.github.com/sreimers/5952263
def set_debug(level):
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(level)

# https://lazka.github.io/pgi-docs/Gst-1.0/functions.html#Gst.debug_bin_to_dot_file
def draw_pipeline(pipe, filename):
    #Gst.debug_bin_to_dot_file(pipe, Gst.DebugGraphDetails.ALL, "pipeline-dot")
    # https://pygraphviz.github.io/documentation/pygraphviz-1.3rc1/reference/agraph.html
    import pygraphviz as pgv
    dot_data= Gst.debug_bin_to_dot_data(pipe, Gst.DebugGraphDetails.ALL)
    G= pgv.AGraph(dot_data)
    print("now let's print some graph: "+filename+".png")
    file_path = '{name}.png'.format(
    grandparent=os.path.dirname(os.path.dirname(__file__)),
    name=filename)
    G.draw(file_path, format="png",prog="dot")

if __name__ == '__main__':
  #https://stackoverflow.com/questions/4205317/capture-keyboardinterrupt-in-python-without-try-except
  try:
    main()
  except KeyboardInterrupt:
    print("cleaning up")
    if loop!= False:
      loop.quit()
  
    if pipeline!= False:
      pipeline.set_state(Gst.State.NULL)
    
    sys.exit()
