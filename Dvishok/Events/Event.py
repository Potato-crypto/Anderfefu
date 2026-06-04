
class Event:
    def __init__(self, type, **kwargs):
        self.type = type
        self.dict = kwargs


    def __getitem__(self, key):
        return self.dict[key]


    def __contains__(self, key):
        return key in self.dict