# if the name isn't plugin, it's likely LocalAudioDev or 1045800357
# (meaning it was ran by Anki!)
# This if statement prevents the functions from automatically running
# and essentially starting the server again
if __name__ != "plugin":
    from .server import run_server
    from .gui import init_gui

    run_server()
    init_gui()
