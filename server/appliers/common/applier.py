class Applier:
    def __init__(self, operation):
        self.operation = operation

    def apply(self, key, value):
        return self.operation(key, value)
