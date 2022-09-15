import dateutil.parser
from datetime import timedelta
from db.schema import DataType


def minus_day(date):
    parsed = dateutil.parser.isoparse(date)
    parsed -= timedelta(hours=24)
    return parsed.isoformat()


def dict_preprocess_light(item_dict):
    item_dict.pop("_sa_instance_state")
    item_dict["date"] = item_dict.pop("updateDate")
    if item_dict["type"] == DataType.FILE:
        item_dict["type"] = "FILE"
    else:
        item_dict["type"] = "FOLDER"
