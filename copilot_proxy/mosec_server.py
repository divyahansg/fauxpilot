import os
import json
import time
from typing import List

from mosec import Server, ValidationError, Worker, get_logger

from utils.codegen import CodeGenProxy

logger = get_logger()

class Inference(Worker):

    def __init__(self):
        super().__init__()
        self.engine = CodeGenProxy(
            host=os.environ.get("TRITON_HOST", "triton"),
            port=os.environ.get("TRITON_PORT", 8001),
            verbose=os.environ.get("TRITON_VERBOSITY", False)
        )
        logger.info("initializing Triton client...")

    def forward(self, data: List[dict]) -> List[dict]:
        logger.debug("received data: %s", data)
        result = self.engine(data=data, batch=True)
        logger.debug("result: %s", result)
        return json.loads(result)
        # try:
        #     count_time = float(data["time"])
        # except KeyError as err:
        #     raise ValidationError(f"cannot find key {err}") from err

        # return {"msg": f"sleep {data} seconds"}

if __name__ == "__main__":
    server = Server()
    server.append_worker(
        Inference,
        num=5,
        max_batch_size=8,
        max_wait_time=1000,
        timeout=10
    )
    server.run()
