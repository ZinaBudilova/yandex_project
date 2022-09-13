from db.schema import History


def write_history(item):
    obj = History(
        id=item.id,
        type=item.type,
        size=item.size,
        url=item.url,
        updateDate=item.updateDate,
        parentId=item.parentId
    )
    return obj
