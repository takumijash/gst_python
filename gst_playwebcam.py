##########################################################
#To implement a pipeline with python code
#
# gst-launch-1.0 -v v4l2src device=/dev/video0 ! video/x-raw,width=1280,height=720
# ! videoconvert ! xvimagesink
#
# gst-launch-1.0 -v v4l2src device=/dev/video0 ! capsfilter caps=video/x-raw,
# width=1280,height=720 ! videoconvert ! xvimagesink
#
##########################################################
import traceback
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject  # noqa:F401,F402


# Initializes Gstreamer, it's variables, paths
Gst.init(sys.argv)


def on_message(bus: Gst.Bus, message: Gst.Message, loop: GObject.MainLoop):
    mtype = message.type
    """
        Gstreamer Message Types and how to parse
        https://lazka.github.io/pgi-docs/Gst-1.0/flags.html#Gst.MessageType
    """
    if mtype == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()

    elif mtype == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(err, debug)
        loop.quit()
    elif mtype == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print(err, debug)

    return True


# Gst.Pipeline https://lazka.github.io/pgi-docs/Gst-1.0/classes/Pipeline.html
pipeline = Gst.Pipeline()

# Creates element by name
# https://lazka.github.io/pgi-docs/Gst-1.0/classes/ElementFactory.html#Gst.ElementFactory.make
src     = Gst.ElementFactory.make("v4l2src", "my_video_test_src")
cfilter = Gst.ElementFactory.make("capsfilter")
convert = Gst.ElementFactory.make("videoconvert", "my_videoconvert")
sink    = Gst.ElementFactory.make("xvimagesink", "my_xvimagesink")

# Setup capability
src.set_property("device", "/dev/video0")
cfilter.set_property("caps",Gst.Caps.from_string("video/x-raw,width=1280,height=720"))

# add to pipeline
pipeline.add(src)
pipeline.add(cfilter)
pipeline.add(convert)
pipeline.add(sink)

# link element
src.link(cfilter)
cfilter.link(convert)
convert.link(sink)

# https://lazka.github.io/pgi-docs/Gst-1.0/classes/Bus.html
bus = pipeline.get_bus()

# allow bus to emit messages to main thread
bus.add_signal_watch()

# Start pipeline
pipeline.set_state(Gst.State.PLAYING)

# Init GObject loop to handle Gstreamer Bus Events
loop = GObject.MainLoop()

# Add handler to specific signal
# https://lazka.github.io/pgi-docs/GObject-2.0/classes/Object.html#GObject.Object.connect
bus.connect("message", on_message, loop)

try:
    loop.run()
except Exception:
    traceback.print_exc()
    loop.quit()

# Stop Pipeline
pipeline.set_state(Gst.State.NULL)
del pipeline
