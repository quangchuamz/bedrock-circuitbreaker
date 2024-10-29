class FailureSimulator:
    def __init__(self):
        self.fail_next_requests = False
        self.failure_count = 0

    def enable_failures(self):
        self.fail_next_requests = True
        return {"message": "Failures enabled"}

    def disable_failures(self):
        self.fail_next_requests = False
        self.failure_count = 0
        return {"message": "Failures disabled"}

    def should_fail(self):
        if self.fail_next_requests:
            self.failure_count += 1
            return True
        return False

failure_simulator = FailureSimulator() 