# https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe
import os
import sys

sys.path.append('../renderdoc/x64/Release/pymodules')
os.environ["PATH"] += os.pathsep + os.path.abspath('../renderdoc/x64/Release')

import renderdoc as rd

rdc_file = 'D:/ue4-arpg.rdc'

# Prints 'CullMode.FrontAndBack'
print(rd.CullMode.FrontAndBack)

def setup_rdc(filename):
    # Open a capture file handle
    cap = rd.OpenCaptureFile()

    # Open a particular file - see also OpenBuffer to load from memory
    status = cap.OpenFile(rdc_file, '', None)

    # Make sure the file opened successfully
    if status != rd.ReplayStatus.Succeeded:
        raise RuntimeError("Couldn't open file: " + str(status))

    # Make sure we can replay
    if not cap.LocalReplaySupport():
        raise RuntimeError("Capture cannot be replayed")

    # Initialise the replay
    status,controller = cap.OpenCapture(rd.ReplayOptions(), None)

    if status != rd.ReplayStatus.Succeeded:
        raise RuntimeError("Couldn't initialise replay: " + str(status))

    return cap, controller

def update_rdc(cap, controller):
    print("%d top-level drawcalls" % len(controller.GetDrawcalls()))


def shutdown_rdc(cap, controller):
    controller.Shutdown()
    cap.Shutdown()
    rd.ShutdownReplay()

cap, controller = setup_rdc(rdc_file)
update_rdc(cap, controller)
shutdown_rdc(cap, controller)