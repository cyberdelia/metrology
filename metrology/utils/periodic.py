from threading import Thread, Event


class PeriodicTask(Thread):
    def __init__(self, interval=5., target=None):
        super(PeriodicTask, self).__init__()
        self.status = Event()
        self.interval = interval
        self.target = target
        self.daemon = True

    def stop(self):
        self.status.set()

    @property
    def stopped(self):
        return self.status.isSet()

    def run(self):
        while True:
            if self.stopped:
                return
            self.status.wait(self.interval)
            self.task()

    def task(self):
        if not self.target:
            raise NotImplementedError
        self.target()
