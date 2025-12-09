import json
import time
from typing import Any, Dict

class Logger:
    def __init__(self, *, filepath="audit.json", level="INFO"):
        self.filepath = filepath
        self.level = level
        self.levels = ["DEBUG", "INFO", "WARN", "ERROR"]

    def _should_log(self, level: str) -> bool:
        return self.levels.index(level) >= self.levels.index(self.level)

    def _write(self, level: str, message: Any):
        entry: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
        }

        # NDJSON: one JSON object per line
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def debug(self, message: Any):
        if self._should_log("DEBUG"):
            self._write("DEBUG", message)

    def info(self, message: Any):
        if self._should_log("INFO"):
            self._write("INFO", message)

    def warn(self, message: Any):
        if self._should_log("WARN"):
            self._write("WARN", message)

    def error(self, message: Any):
        if self._should_log("ERROR"):
            self._write("ERROR", message)


logger = Logger()
