import os
import logging.handlers
from global_var import Gui_Info


class Logger(logging.Logger):
    def __init__(self, filename=""):
        super(Logger, self).__init__(self)
        if not filename:
            filename = "debug.log"
        if not os.path.exists(Gui_Info["debug_dir"]):
            os.makedirs(Gui_Info["debug_dir"], exist_ok=True)
        self.filename = os.path.normpath(os.path.join(Gui_Info["debug_dir"], filename))

        # set the output format of the handler
        formatter = logging.Formatter(
            "[%(asctime)s] - %(filename)s [Line:%(lineno)d] - [%(levelname)s] - %(message)s")

        # create a handle in order to write into the log file
        fh = logging.handlers.TimedRotatingFileHandler(
            filename=self.filename, when='D', interval=1, backupCount=10, encoding='utf-8')
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
