class MemTable:
    def __init__(self, memory_list):
        self.memory_list = memory_list

    def find(self, index):
        # print(self.memory_list)
        return dict(self.memory_list[index])
