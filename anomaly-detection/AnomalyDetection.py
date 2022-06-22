from alibi_detect.utils.saving import load_detector
import numpy as np
import pandas as pd
import json


class AnomalyDetection(object):
    def __init__(self):
        print("Initializing Anomaly Detection model")
        self._model = load_detector("./model")

    def predict_raw(self, request):
        now = pd.Timestamp(ts_input=request["ds"])
        y = request["y"]
        result = self._model.predict(pd.DataFrame(data={"ds": [now], "y": [y]}))
        value = int(result["data"]["is_outlier"]["is_outlier"].squeeze())
        print(request)
        return json.dumps(
            {"now": now.to_pydatetime().isoformat(), "y": y, "outlier": value}
        )
