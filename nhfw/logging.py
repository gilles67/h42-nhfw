import os, sys, logging
import logging.handlers

nhfwlog = None
logger_name = __name__

def nhfwlog_name(name):
    global logger_name
    logger_name = name
    global nhfwlog
    nhfwlog = generate_logger()
    nhfwlog.debug("Logging name changed name={}".format(name))

def reset_logger(forked=False): 
    global nhfwlog
    nhfwlog = generate_logger(forked)
    nhfwlog.debug("Logging reset name={}, forked={}".format(logger_name, forked))

def generate_logger(forked=False):
    global logger_name
    nhfwlog = logging.getLogger(logger_name)
    nhfwlog.setLevel(logging.DEBUG)
    nhfwlog.handlers.clear()

    syshdl = logging.handlers.SysLogHandler(address = '/dev/log')
    sysfmt = logging.Formatter("%(name)s [" + str(os.getpid()) + "]: %(message)s")
    syshdl.setFormatter(sysfmt)
    nhfwlog.addHandler(syshdl)

    if not forked:
        stdhdl = logging.StreamHandler(sys.stderr)
        stdhdl.setFormatter(sysfmt)
        nhfwlog.addHandler(stdhdl)
   
    return nhfwlog

if nhfwlog == None:
    nhfwlog = generate_logger()
    nhfwlog.debug("Logging system loaded")
