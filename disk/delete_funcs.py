from db.schema import Items, Children


def delete_children(relation):
    children_del = Children.query.filter_by(parentId=relation.childId).first()
    if children_del is not None:
        return delete_children(children_del)
    item_del = Items.query.filter_by(id=relation.childId).first()
    child_del = Children.query.filter_by(childId=relation.childId).first()
    return item_del, child_del


def decrease_parents_sizes(item, update_date):
    parent_id = item.parentId
    while parent_id is not None:
        parent = Items.query.filter_by(id=parent_id).first()
        parent.size -= item.size
        parent.updateDate = update_date
        parent_id = parent.parentId
