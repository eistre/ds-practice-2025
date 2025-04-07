class VectorClock:
    """
    Vector clock implementation
    """
    def __init__(self, size, clock=None):
        if clock:
            self.vc = clock[:]
        else:
            self.vc = [0] * size

    def merge_and_increment(self,idx, incoming):
        for i in range(len(self.vc)):
            self.vc[i] = max(self.vc[i], incoming[i])
        self.vc[idx] += 1

    def get(self):
        return self.vc[:]