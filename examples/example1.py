#!/usr/bin/env python

# mix of:
# https://www.programcreek.com/python/example/88577/gi.repository.Gst.Pipeline
# https://github.com/GStreamer/gst-python/blob/master/examples/helloworld.py
# http://lifestyletransfer.com/how-to-launch-gstreamer-pipeline-in-python/

import sys
import collections
from pprint import pprint
import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib

import pdb

'''
gst-launch-1.0 \
videotestsrc is-live=true ! \
queue ! videoconvert ! x264enc byte-stream=true ! \
h264parse config-interval=1 ! queue ! matroskamux ! queue leaky=2 ! \
tcpserversink port=7001 host=0.0.0.0 recover-policy=keyframe sync-method=latest-keyframe sync=false
'''

def main(args):
  # depricated but still in much of the tutorials I found!
  #GObject.threads_init()
  Gst.init(None)
  # ! NO PYTHON DEV WARING ! -> https://pymotw.com/2/collections/namedtuple.html
  Element = collections.namedtuple('Element', ['type', 'attributes'])

  elements = [
    Element('videotestsrc', { "is-live": True}),
    Element('queue', {}),
    Element('videoconvert', {}),
    Element('x264enc', {"byte-stream": True}),
    Element('h264parse', {"config-interval":1}),
    Element('queue', {}),
    Element('matroskamux', {}),
    Element('queue', {"leaky": 2}),
    Element('tcpserversink', {"port": 7001, "host": "0.0.0.0", "recover-policy": "keyframe", "sync-method":"latest-keyframe", "sync": False}),
  ]

  pipeline = Gst.Pipeline()
  message_bus = pipeline.get_bus()
  message_bus.add_signal_watch()
  message_bus.connect('message', bus_call, None)

  elements_created= dict()
  # ! NO PYTHON DEV WARING ! -> https://stackoverflow.com/questions/25150502/python-loop-index-of-key-value-for-loop-when-using-items
  for index, item in enumerate(elements):
    name = item.type+str(index)
    elements_created[name] = Gst.ElementFactory.make(item.type, name)
    for key, value in item.attributes.items():
        #pdb.set_trace()
        elements_created[name].set_property(key, value)
    pipeline.add(elements_created[name])

  # https://www.geeksforgeeks.org/iterate-over-a-list-in-python/
  length = len(elements) 
  i = 0
  # Iterating to connect the elements
  while i < length-1: 
    pprint(elements[i].type+str(i)) 
    current_name_in_created= elements[i].type+str(i)
    next_name_in_created= elements[i+1].type+str(i+1)
    ## now link them!
    print(current_name_in_created+"->"+next_name_in_created)
    elements_created[current_name_in_created].link(elements_created[next_name_in_created])
    i += 1

  pprint(elements_created)
  #pdb.set_trace()
  # start play back and listed to events
  pipeline.set_state(Gst.State.PLAYING)
  # create and event loop and feed gstreamer bus mesages to it
  loop = GLib.MainLoop()
  try:
    loop.run()
  except:
    loop.quit()

  # cleanup
  print("cleaning up")
  pipeline.set_state(Gst.State.NULL)
  sys.exit()


# http://lifestyletransfer.com/how-to-launch-gstreamer-pipeline-in-python/
def bus_call(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
  t = message.type
  if t == Gst.MessageType.EOS:
      sys.stdout.write("End-of-stream\n")
      loop.quit()
  elif t == Gst.MessageType.ERROR:
      err, debug = message.parse_error()
      sys.stderr.write("Error: %s: %s\n" % (err, debug))
      loop.quit()
  elif t == Gst.MessageType.WARNING: 
        # Handle warnings 
        err, debug = message.parse_warning() 
        sys.stderr.write("Warning: %s: %s\n" % (err, debug))
  return True

if __name__ == '__main__':
  #done in main!
  #sys.exit(main(sys.argv))

  #https://stackoverflow.com/questions/4205317/capture-keyboardinterrupt-in-python-without-try-except
  try:
    main(sys.argv)
  except KeyboardInterrupt:
      # do nothing here
      pass
