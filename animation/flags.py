class Range():
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, __o: int) -> bool:
        if isinstance(__o, int):
            return self.start <= __o and __o <= self.end
        return False

class Ranges():
    def __init__(self, ranges):
        self.ranges = ranges

    def __iter__(self):
        return iter(self.ranges)

class Flag(Ranges):
    def __init__(self,name,value,ranges):
        super().__init__(ranges)
        self.name = name
        self.value = value

    def __getitem__(self, key):
        if key in self:
            return self.value

class FakeFlag():
    def __getitem__(self, key):
        return None

class Flags():
    def __init__(self, flags):
        self.flags = flags

    def __iter__(self):
        return iter(self.flags)

    def __getitem__(self,key):
        for flag in self:
            if flag.name == key:
                return flag