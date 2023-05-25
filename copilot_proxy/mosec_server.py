import os
import json
import time
from typing import List

from mosec import Server, ServerError, Worker, get_logger

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
        logger.info("Initialized Triton client...")

    def forward(self, data: List[dict]) -> List[dict]:
        try:
            result = self.engine(data=data, batch=True, logger=logger)
            return json.loads(result)
        except Exception as err:
            logger.error("Error fulfilling request: %s", err)
            raise ServerError(f"Error fulfilling request") from err

if __name__ == "__main__":
    server = Server()
    server.append_worker(
        Inference,
        num=os.environ.get("MAX_CONCURRENCY", 5),
        max_batch_size=os.environ.get("MAX_BATCH_SIZE", 4),
        max_wait_time=os.environ.get("MAX_BATCH_WAIT_MILLISECONDS", 250),
        timeout=os.environ.get("WORKER_TIMEOUT_SECONDS", 10)
    )
    server.run()
