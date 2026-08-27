# chess game (pet project by Alexander Postavets)

class Logger():

    """the class describes the
    event logging in the game"""
    
    def __init__(self):
        self._log = list('' for line in range(4))
        # add the application name and version to the Log sequence
        self._log.insert(0, "Chess (version: 0.1)")
        # number of records in log sequence
        self._counter = 1

    # add new event
    def info(self, *args):
        for arg in args:
            self._log.append(f"{self.counter} {str(arg)}")
            self._counter += 1
            if len(self._log > 4):
                del self._log[0]

    # display the log
    def view(self):
        for line in reversed(self._log):
            print(line)