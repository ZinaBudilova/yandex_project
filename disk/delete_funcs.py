from db.schema import Items, Children


def delete_children(relation):
    children_del = Children.query.filter_by(parentId=relation.childId).first()
    if children_del is not None:
        return delete_children(children_del)
    item_del = Items.query.filter_by(id=relation.childId).first()
    child_del = Children.query.filter_by(childId=relation.childId).first()
    return item_del, child_del
