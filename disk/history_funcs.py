from db.schema import db, History


def write_history(item):
    obj = History(
        id=item.id,
        type=item.type,
        size=item.size,
        url=item.url,
        updateDate=item.updateDate,
        parentId=item.parentId,
    )
    return obj


def delete_history(item):
    record = History.query.filter_by(id=item.id).first()
    while record is not None:
        db.session.delete(record)
        record = History.query.filter_by(id=item.id).first()
