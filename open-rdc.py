# https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe
# https://renderdoc.org/docs/python_api/renderdoc/index.html
# D:\svn_pool\renderdoc\renderdoc\replay\replay_controller.h
# D:\svn_pool\renderdoc\renderdoc\api\replay\replay_enums.h

import os
import sys

sys.path.append('../renderdoc/x64/Release/pymodules')
os.environ["PATH"] += os.pathsep + os.path.abspath('../renderdoc/x64/Release')

import renderdoc as rd

DUMP_RENDER_TARGET = True

rdc_file = 'D:/rdc/YuanShen_2020.09.22_02.38.57_frame36700.rdc'

def setup_rdc(filename):
    # Open a capture file handle
    rd.InitialiseReplay(rd.GlobalEnvironment(), [])

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

# Define a recursive function for iterating over draws
def iterDraw(d, level = 1):
    # Print this drawcall
    if False:
        file.write("%s %s\n" % ('#'*level, d.name.replace('#', '__')))
    else:
        file.write("%s %d %s\n" % ('#'*level, d.eventId, d.name.replace('#', '__')))

    # Iterate over the draw's children
    for d in d.children:
        iterDraw(d, level + 1)

def dump_resource(controller, draw):
    controller.SetFrameEvent(draw.eventId, True)
    texsave = rd.TextureSave()

    if DUMP_RENDER_TARGET:
        # dump render targtes (aka outputs)
        for idx, output in enumerate(draw.outputs):
            texsave.resourceId = output
            if texsave.resourceId != rd.ResourceId.Null():
                filename = "draw_%04d_c%d" % (draw.eventId, idx)
                print("Saving images of %s at %d: %s" % (filename, draw.eventId, draw.name))
                texsave.alpha = rd.AlphaMapping.BlendToCheckerboard
                texsave.mip = 0
                texsave.slice.sliceIndex = 0

                # For formats with an alpha channel, preserve it
                texsave.alpha = rd.AlphaMapping.Preserve

                texsave.destType = rd.FileType.PNG
                controller.SaveTexture(texsave, filename + ".png")

def update_rdc(controller):

    file.write("* %s\n" % rdc_file)
    file.write("\n")
    # file.write("* API: %s\n" % (rdc.APIProps.pipelineType))

    # Start iterating from the first real draw as a child of markers
    draw = controller.GetDrawcalls()[0]

    while len(draw.children) > 0:
        draw = draw.children[0]

    # Counter for which pass we're in
    passnum = 0
    # Counter for how many draws are in the pass
    passcontents = 0
    # Whether we've started seeing draws in the pass - i.e. we're past any
    # starting clear calls that may be batched together
    inpass = False

    file.write("# Passes\n")
    file.write("- Pass #%d\n - starts with %d: %s\n" % (passnum, draw.eventId, draw.name))

    while draw != None:
        # When we encounter a clear
        if draw.flags & rd.DrawFlags.Clear:
            if inpass:
                file.write(" - contained %d draws\n" % (passcontents))
                passnum += 1
                file.write("- Pass #%d\n - starts with %d: %s\n" % (passnum, draw.eventId, draw.name))
                passcontents = 0
                inpass = False
        else:
            passcontents += 1
            inpass = True

        if False:
            if draw.flags & rd.DrawFlags.Clear: file.write("Clear ")
            if draw.flags & rd.DrawFlags.Drawcall: file.write("Drawcall ")
            if draw.flags & rd.DrawFlags.Dispatch: file.write("Dispatch ")
            if draw.flags & rd.DrawFlags.CmdList: file.write("CmdList ")
            if draw.flags & rd.DrawFlags.SetMarker: file.write("SetMarker ")
            if draw.flags & rd.DrawFlags.PushMarker: file.write("PushMarker ")
            if draw.flags & rd.DrawFlags.PopMarker: file.write("PopMarker ")
            if draw.flags & rd.DrawFlags.Present: file.write("Present ")
            if draw.flags & rd.DrawFlags.MultiDraw: file.write("MultiDraw ")
            if draw.flags & rd.DrawFlags.Copy: file.write("Copy ")
            if draw.flags & rd.DrawFlags.Resolve: file.write("Resolve ")
            if draw.flags & rd.DrawFlags.GenMips: file.write("GenMips ")
            if draw.flags & rd.DrawFlags.PassBoundary: file.write("PassBoundary ")

            if draw.flags & rd.DrawFlags.Indexed: file.write("Indexed ")
            if draw.flags & rd.DrawFlags.Instanced: file.write("Instanced ")
            if draw.flags & rd.DrawFlags.Auto: file.write("Auto ")
            if draw.flags & rd.DrawFlags.Indirect: file.write("Indirect ")
            if draw.flags & rd.DrawFlags.ClearColor: file.write("ClearColor ")
            if draw.flags & rd.DrawFlags.ClearDepthStencil: file.write("ClearDepthStencil ")
            if draw.flags & rd.DrawFlags.BeginPass: file.write("BeginPass ")
            if draw.flags & rd.DrawFlags.EndPass: file.write("EndPass ")
            if draw.flags & rd.DrawFlags.APICalls: file.write("APICalls ")

        # dump_resource(controller, draw)

        # Advance to the next drawcall
        draw = draw.next

    if inpass:
        file.write(" - contained %d draws\n" % (passcontents))

    # Iterate over all of the root drawcalls
    for d in controller.GetDrawcalls():
        iterDraw(d)        


def shutdown_rdc(cap, controller):
    controller.Shutdown()
    cap.Shutdown()
    rd.ShutdownReplay()

if 'pyrenderdoc' in globals():
    output_name = 'temp' + ".report.md.html"
    file = open(output_name,"w") 

    pyrenderdoc.Replay().BlockInvoke(update_rdc)
else:
    output_name = rdc_file + ".report.md.html"
    file = open(output_name,"w") 

    cap, controller = setup_rdc(rdc_file)
    update_rdc(controller)
    shutdown_rdc(cap, controller)

markdeep_ending = """
<meta charset="utf-8" emacsmode="-*- markdown -*-"><link rel="stylesheet" href="https://casual-effects.com/markdeep/latest/slate.css?">
<!-- Markdeep: --><style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src="markdeep.min.js"></script><script src="https://casual-effects.com/markdeep/latest/markdeep.min.js?"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility="visible")</script>
"""

file.write(markdeep_ending)
file.close()

print("%s" % (output_name))
