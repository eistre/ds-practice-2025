class VectorClock:
    """
    Vector clock implementation
    """
    def __init__(self, size):
        self.vc = [0] * size

    def merge_and_increment(self, idx, incoming_vcs):
        for incoming in incoming_vcs:
            for i in range(len(self.vc)):
                self.vc[i] = max(self.vc[i], incoming.clock[i])
        self.vc[idx] += 1

    def get(self):
        return self.vc[:]
    
    def compare(self,incoming_vc):
        return all(incoming_vc[i] >= self.vc[i] for i in range(len(self.vc)))
