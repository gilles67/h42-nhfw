import syslog, os, yaml

class NhfwConfigBase:
    _initial = None 
    _config = None
    def __init__(self, initial=None):
        if initial:
            self._initial = initial
        self._parseConfig()

    def _parseConfig(self):
        if os.path.isfile(self.CONFIG_FILE):
            try:
                fd = open(self.CONFIG_FILE, 'r')
                self._config = yaml.load(fd, Loader=yaml.SafeLoader)
                fd.close()
            except:
                syslog.syslog("[Error] Parse configuration file : {}".format(self.CONFIG_FILE))
        else:
            if self._initial:
                self._genereateConfig()

    def _genereateConfig(self):
        config = self._initial()
        dir = os.path.dirname(self.CONFIG_FILE)
        if not os.path.exists(dir):
            os.makedirs(dir)
        try:
            fd = open(CONFIG_FILE, 'w')
            yaml.dump(config, fd)
            fd.close()
            self._parseConfig()
        except:
            syslog.syslog("[Error] Generate configuration file : {}".format(CONFIG_FILE))

