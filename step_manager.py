class UserStep():
    uid = 0
    step = 0
    command = None
    responses = {}

    def __init__(self, uid):
        self.uid = uid

    def get_step(self):
        return self.step

    def set_step(self, step):
        self.step = step

    def get_command(self):
        return self.command

    def set_command(self, command):
        self.command = command

    def reset(self):
        self.step = 0
        self.command = None

    def save_response(self, step, response):
        self.responses[step] = response

    def get_response(self, step):
        return self.responses[step]
