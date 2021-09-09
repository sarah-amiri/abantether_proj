import json
from bson import ObjectId
from datetime import datetime
from typing import Any


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId) or isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)
