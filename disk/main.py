import flask
import os
import json

from db.schema import db, Items, Children, History
import validation
import import_funcs
from delete_funcs import delete_children
from nodes_funcs import add_children, dict_preprocess
from updates_funcs import minus_day, dict_preprocess_light
from history_funcs import write_history, delete_history


current_dir = os.path.abspath(os.path.dirname(__file__))

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(current_dir, "db", "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.app = app
db.init_app(app)


@app.route("/imports", methods=["POST"])
def imports():
    """Импортирует элементы файловой системы. Элементы импортированные повторно обновляют текущие."""
    request_data = flask.request.get_json()
    update_date = request_data["updateDate"]
    items = request_data["items"]
    if not validation.query_validate(items):
        flask.abort(400)
    else:
        for raw_item in items:
            item = import_funcs.get_item_properties(raw_item, update_date)
            valid, update = validation.item_format_validate(item)
            upd_parents = []
            if not valid:
                flask.abort(400)
            # add
            elif not update:
                db.session.add(item)  # items
                import_funcs.folder_size_add(item)
                relation, upd_parents = import_funcs.children_add(item)  # children
                if relation is not None:
                    db.session.add(relation)
            # update
            else:
                import_funcs.update_item(item)  # items
                import_funcs.folder_size_update(item)
                relation_del, relation_add, upd_parents = import_funcs.children_update(item)  # children
                if relation_del is not None:
                    db.session.delete(relation_del)
                if relation_add is not None:
                    db.session.add(relation_add)
            db.session.commit()
            # history
            record = write_history(item)
            db.session.add(record)
            for parent in upd_parents:
                prev_parent_record = History.query.filter_by(key=parent.id + " " + parent.updateDate).first()
                if prev_parent_record is None:
                    parent_record = write_history(parent)
                    db.session.add(parent_record)
                # in case folder's size increases several times during one update
                elif prev_parent_record.size != parent.size:
                    prev_parent_record.size = parent.size
            db.session.commit()
    return "successful import"


@app.route("/delete/<item_id>", methods=["DELETE"])
def delete(item_id):
    """Удалить элемент по идентификатору. При удалении папки удаляются все дочерние элементы."""
    args = flask.request.args
    date = args.get("date")
    item = Items.query.get(item_id)
    if item is None:
        flask.abort(404)
    elif not validation.date_validate(date):
        flask.abort(400)
    else:
        if item.type.value == "FOLDER":
            relation = Children.query.filter_by(parentId=item.id).first()
            while relation is not None:
                item_del, child_del = delete_children(relation)
                delete_history(item_del)
                db.session.delete(item_del)
                db.session.delete(child_del)
                db.session.commit()
                relation = Children.query.filter_by(parentId=item.id).first()
        delete_history(item)
        db.session.delete(item)
        db.session.commit()
    return "successful deletion"


@app.route("/nodes/<root_id>", methods=["GET"])
def nodes(root_id):
    """Получить информацию об элементе по идентификатору.
    При получении информации о папке также предоставляется информация о её дочерних элементах."""
    result = None
    item = Items.query.get(root_id)
    if item is None:
        flask.abort(404)
    else:
        result = item.__dict__
        dict_preprocess(result)
        add_children(result)
    return json.dumps(result)


@app.route("/updates", methods=["GET"])
def updates():
    """Получение списка **файлов**, которые были обновлены за последние 24 часа включительно [date - 24h, date]
    от времени, переданном в запросе."""
    result = []
    args = flask.request.args
    date = args.get("date")
    if not validation.date_validate(date):
        flask.abort(400)
    else:
        day_before = minus_day(date)
        data = Items.query.filter(Items.updateDate <= date, Items.updateDate >= day_before)
        for d in data:
            if d.type.value == "FILE":
                item = d.__dict__
                dict_preprocess_light(item)
                result.append(item)
    return json.dumps(result)


@app.route("/node/<item_id>/history", methods=["GET"])
def history(item_id):
    """Получение истории обновлений по элементу за заданный полуинтервал [from, to).
    История по удаленным элементам недоступна."""
    result = []
    args = flask.request.args
    date_start = args.get("dateStart")
    date_end = args.get("dateEnd")
    item = Items.query.get(item_id)
    if item is None:
        flask.abort(404)
    elif not validation.date_validate(date_start) or not validation.date_validate(date_end):
        flask.abort(400)
    else:
        records = History.query.filter(
            History.id == item.id,
            History.updateDate > date_start,
            History.updateDate <= date_end
        )
        if records is not None:
            for rec in records:
                item = rec.__dict__
                dict_preprocess(item)
                result.append(item)
    return json.dumps(result)


@app.errorhandler(400)
def validation_failed(e):
    return "Validation Failed", 400


@app.errorhandler(404)
def item_not_found(e):
    return "Item not found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
