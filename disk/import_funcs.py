from db.schema import Items, Children


def get_item_properties(item, update_date):
    item_id = item['id']
    data_type = item['type']

    if data_type == "FILE":
        size = item['size']
        url = item['url']
    else:
        size = None
        url = None

    if 'parentId' in item.keys():
        parent_id = item['parentId']
    else:
        parent_id = None

    obj_item = Items(
        id=item_id,
        type=data_type,
        size=size,
        url=url,
        updateDate=update_date,
        parentId=parent_id
    )
    return obj_item


def update_item(item):
    previous = Items.query.filter_by(id=item.id).first()
    previous.updateDate = item.updateDate
    previous.parentId = item.parentId
    if item.type == "FILE":
        previous.size = item.size
        previous.url = item.url


def folder_size_update(item):
    if item.type == "FILE":
        previous = Items.query.filter_by(id=item.id).first()
        if previous.size != item.size and previous.parentId == item.parentId:
            # меняем size у предков на величину разницы
            diff = item.size - previous.size
            parent_id = previous.parentId
            while parent_id is not None:
                parent = Items.query.filter_by(id=parent_id).first()
                parent.size += diff
                parent_id = parent.parentId
        elif previous.parentId != item.parentId:
            # уменьшаем size старых предков на старый размер,
            # увеличиваем size новых предков на новый размер (размеры могут быть одинаковыми)
            old_parent_id = previous.parentId
            while old_parent_id is not None:
                old_parent = Items.query.filter_by(id=old_parent_id).first()
                old_parent.size -= previous.size
                old_parent_id = old_parent.parentId
            new_parent_id = item.parentId
            while new_parent_id is not None:
                new_parent = Items.query.filter_by(id=new_parent_id).first()
                new_parent.size += item.size
                new_parent_id = new_parent.parentId


def folder_size_add(item):
    if item.type == "FILE":
        parent_id = item.parentId
        while parent_id is not None:
            parent = Items.query.filter_by(id=parent_id).first()
            if parent.size is None:
                parent.size = item.size
            else:
                parent.size += item.size
            parent_id = parent.parentId


def all_parents_date_update(item):
    upd_parents = []
    parent = Items.query.filter_by(id=item.parentId).first()
    while parent is not None:
        parent.updateDate = item.updateDate
        upd_parents.append(parent)
        parent = Items.query.filter_by(id=parent.parentId).first()
    return upd_parents


def children_add(item):
    relation = None
    upd = []
    if item.parentId is not None:
        relation = Children(
            parentId=item.parentId,
            childId=item.id
        )
        upd = all_parents_date_update(item)
    return relation, upd


def children_update(item):
    relation_to_delete = relation_to_add = None
    upd_parents = []
    previous = Items.query.filter_by(id=item.id).first()
    if item.parentId != previous.parentId:
        if previous.parentId is not None:
            relation_to_delete = Children.query.filter_by(id=item.parentId).first()
            upd1 = all_parents_date_update(previous)
            upd_parents.extend(upd1)
        if item.parentId is not None:
            relation_to_add = Children(
                parentId=item.parentId,
                childId=item.id
            )
            upd2 = all_parents_date_update(item)
            upd_parents.extend(upd2)
    return relation_to_delete, relation_to_add, upd_parents
