import re
from db.schema import Items


def date_validate(date):
    result = True
    regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):' \
            r'([0-5][0-9])(\.[0-9]+)?Z?'
    match_iso8601 = re.compile(regex).match
    if match_iso8601(date) is None:
        result = False
    return result


def item_format_validate(item):
    valid = True

    # поле id не может быть равно null
    if item.id is None:
        valid = False
        # print("null id")

    # только 2 типа: папка и файл
    if item.type != "FOLDER" and item.type != "FILE":
        valid = False
        # print("type is neither file nor folder")

    # поле size при импорте папки всегда должно быть равно null
    if item.type == "FOLDER" and item.size is not None:
        valid = False
        # print("folder with existing size")

    # поле size для файлов всегда должно быть больше 0
    if item.type == "FILE" and (item.size is None or item.size <= 0):
        valid = False
        # print("file with size <= 0")

    # поле url при импорте папки всегда должно быть равно null
    if item.type == "FOLDER" and item.url is not None:
        valid = False
        # print("folder with an url")

    # размер поля url при импорте файла всегда должен быть меньше либо равным 255
    if item.type == "FILE" and len(item.url) > 255:
        valid = False
        # print("non-valid url")

    # дата обрабатывается согласно ISO 8601 (такой придерживается OpenAPI)
    # если дата не удовлетворяет данному формату, ответом будет код 400
    if not date_validate(item.updateDate):
        valid = False
        # print("non-valid date")

    # элементы импортированные повторно обновляют текущие
    # id каждого элемента является уникальным среди остальных элементов
    # при обновлении элемента обновленными считаются **все** их параметры
    # при обновлении параметров элемента обязательно обновляется поле **date** в соответствии с временем обновления
    update = False
    repeat = None
    if item.id is not None:
        repeat = Items.query.get(item.id)
        if repeat is not None:
            update = True
            # print("updating existing file")

    # изменение типа элемента с папки на файл и с файла на папку не допускается
    if update:
        if repeat.type.value != item.type:
            valid = False
            # print("changed file type")

    # родителем элемента может быть только папка
    # принадлежность к папке определяется полем parentId
    # элементы могут не иметь родителя (при обновлении parentId на null элемент остается без родителя)
    if item.parentId is not None:
        parent = Items.query.get(item.parentId)
        if parent.type.value != "FOLDER":
            valid = False
            # print("parent is not a folder", parent.type)

    # несуществующий родитель
    if item.parentId is not None:
        parent = Items.query.get(item.parentId)
        if Items.query.get(parent.id) is None:
            valid = False
            # print("parent with this id does not exist")

    return valid, update


def query_validate(items):
    # в одном запросе не может быть двух элементов с одинаковым id
    valid = True
    ids = [item['id'] for item in items]
    if len(set(ids)) < len(ids):
        valid = False
        # print("query is not valid")
    return valid
