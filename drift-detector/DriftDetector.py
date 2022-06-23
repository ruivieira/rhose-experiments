from alibi_detect.utils.saving import load_detector
import numpy as np
import pandas as pd
import json
from collections import deque


class DriftDetector(object):
    def __init__(self):
        print("Initializing Drift Detection model")
        self._model = load_detector("./model")
        self._queue = deque([], maxlen=50)

    def predict_raw(self, request):
        y = request["y"]
        self._queue.append(y)
        print(f"Queue size {len(self._queue)}")
        if len(self._queue) > 10:
            inputs = np.array(list(self._queue)).reshape(-1, 1)
            print(inputs)
            result = self._model.predict(inputs)
            value = int(result["data"]["is_drift"])
        else:
            value = 0
        print(request)
        return json.dumps({"y": y, "drift": value})
