class AttentionRouter:
    def __init__(self, w=(0.5, 0.3, 0.2)):
        self.w = w
    def score(self, novelty, importance, latency_ms):
        return self.w[0]*novelty + self.w[1]*importance - self.w[2]*(latency_ms/1000)
    def route(self, task):
        s = self.score(task.novelty, task.importance, task.latency_ms)
        return "fast_lane" if s > 0.3 else "defer"
