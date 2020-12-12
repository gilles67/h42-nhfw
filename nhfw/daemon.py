import sys, os, syslog


def fork_magic(pid_file, main_exec):
    # first fork
    try:
        pid = os.fork()
        if pid > 0:
            # Exit first parent
            sys.exit(0)
    except OSError as ose:
        sys.stderr.write("fork magic #1 failed: {} ({})\n".format(ose.errno, ose.strerror))
        sys.exit(1)

    #second fork
    os.chdir("/")
    os.setsid()
    os.umask(0)

     # Do second fork
    try:
        pid = os.fork()
        if pid > 0:
            fd = open(pid_file, 'w')
            fd.write("{}\n".format(pid))
            fd.close()
            sys.exit(0)
    except OSError as ose:
        sys.stderr.write("fork magic #2 failed: {} ({})\n".format(ose.errno, ose.strerror))
        sys.exit(1)


    main_exec()