import os
import logging.handlers
import global_var as gl


class Logger(logging.Logger):
    def __init__(self, filename=""):
        super(Logger, self).__init__(self)
        if not filename:
            filename = "debug.log"
        if "nt" in os.name:
            dbg_dirname = os.path.normpath(os.path.join(gl.Gui_Info["win_tmp"], gl.Gui_Info["dbg_reldir"]))
        else:
            dbg_dirname = os.path.join(os.path.expanduser('~'), gl.Gui_Info["dbg_reldir"])
        if not os.path.exists(dbg_dirname):
            os.makedirs(dbg_dirname, exist_ok=True)
        self.logfile = os.path.normpath(os.path.join(dbg_dirname, filename))

        # set the output format of the handler
        formatter = logging.Formatter(
            "[%(asctime)s] - %(filename)s [Line:%(lineno)d] - [%(levelname)s] - %(message)s")

        # create a handle in order to write into the log file
        fh = logging.handlers.TimedRotatingFileHandler(
            filename=self.logfile, when='D', interval=1, backupCount=10, encoding='utf-8')
        fh.suffix = "%Y%m%d-%H%M.log"
        fh.setLevel(logging.INFO)  # level: DEBUG，INFO，WARNING，ERROR, CRITICAL
        fh.setFormatter(formatter)

        # create a handler in order to print out in the console
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)  # level: DEBUG，INFO，WARNING，ERROR, CRITICAL
        ch.setFormatter(formatter)

        # add handler for the logger
        self.addHandler(fh)
        self.addHandler(ch)


if __name__ == "__main__":
    log = Logger()
    log.info("Starting to check.")
