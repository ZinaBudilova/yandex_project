from db.schema import DataType, Items, Children


def dict_preprocess(item_dict):
    item_dict.pop("_sa_instance_state")
    item_dict["date"] = item_dict.pop("updateDate")
    if item_dict["type"] == DataType.FILE:
        item_dict["type"] = "FILE"
    else:
        item_dict["type"] = "FOLDER"
        if item_dict["size"] is None:
            item_dict["size"] = 0


def add_children(item_dict):
    if item_dict["type"] == "FILE":
        item_dict["children"] = None
    else:
        item_dict["children"] = []
        relations = Children.query.filter_by(parentId=item_dict["id"]).all()
        for rel in relations:
            child = Items.query.filter_by(id=rel.childId).first()

            child_dict = child.__dict__
            dict_preprocess(child_dict)

            item_dict["children"].append(child_dict)
            add_children(child_dict)
