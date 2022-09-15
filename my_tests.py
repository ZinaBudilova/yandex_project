import urllib.parse
import sys
from unit_test import request


""""==========/imports========="""


def null_id():
    # null id --> 400
    batch = {
        "items": [
            {
                "type": "FOLDER",
                "id": None,
                "parentId": None
            }
        ],
        "updateDate": "2022-09-15T14:45:46.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Null-id test passed...")


def invalid_data_type():
    # тип данных не FOLDER и не FILE --> 400
    batch = {
        "items": [
            {
                "type": "NEW_TYPE",
                "id": "072cdf36-340e-4007-853a-af3197080f18",
                "parentId": None
            }
        ],
        "updateDate": "2022-09-15T14:45:46.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Invalid-type test passed...")


def file_as_a_parent():
    # родитель элемента - файл --> 400

    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    batch = {
        "items": [
            {
                "type": "FILE",
                "url": "url1",
                "id": file_id,
                "parentId": None,
                "size": 64
            },
            {
                "type": "FILE",
                "url": "url1/url2",
                "id": "590fbfad-7a61-4c56-b300-2f88f575f0b8",
                "parentId": "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e",
                "size": 32
            }
        ],
        "updateDate": "2022-09-15T14:45:46.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("File-as-a-parent test passed...")

    # удаляем загруженный в БД файл 1
    params = urllib.parse.urlencode({
        "date": "2022-09-15T14:45:47.000Z"
    })
    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def folder_with_nonnull_url():
    # папка с url != null --> 200, так как при type=FOLDER функция get_item_properties всегда обнуляет url

    folder_id = "072cdf36-340e-4007-853a-af3197080f18"

    batch = {
        "items": [
            {
                "type": "FOLDER",
                "id": folder_id,
                "parentId": None,
                "url": "/my_folder"
            }
        ],
        "updateDate": "2022-09-15T15:43:55.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = {
        "type": "FOLDER",
        "id": folder_id,
        "size": 0,
        "url": None,
        "parentId": None,
        "date": "2022-09-15T15:43:55.000Z",
        "children": []
    }

    status, response = request(f"/nodes/{folder_id}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    if response != expected:
        print("Nonnull-url-folder test failed. Response tree doesn't match expected tree.")
        sys.exit(1)

    print("Nonnull-url-folder test passed...")

    # удаляем загруженную в БД папку
    params = urllib.parse.urlencode({
        "date": "2022-09-15T15:43:56Z"
    })
    status, _ = request(f"/delete/{folder_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def file_with_too_long_url():
    # файл с len(url) > 255 --> 400
    batch = {
        "items": [
            {
                "type": "FILE",
                "id": "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e",
                "parentId": None,
                "size": 1024,
                "url": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla sodales congue ultrices. "
                       "Morbi et libero feugiat, tempor tellus sit amet, condimentum nibh. Quisque id diam erat. "
                       "Morbi eget dictum ipsum. Pellentesque habitant morbi tristique senectus et sed."
            }
        ],
        "updateDate": "2022-09-15T15:53:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Too-long-url test passed...")


def folder_with_nonnull_size():
    # папка с url != size --> 200, так как при type=FOLDER функция get_item_properties всегда обнуляет size
    folder_id = "072cdf36-340e-4007-853a-af3197080f18"

    batch = {
        "items": [
            {
                "type": "FOLDER",
                "id": folder_id,
                "parentId": None,
                "size": 666,
            }
        ],
        "updateDate": "2022-09-15T15:56:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = {
        "type": "FOLDER",
        "id": folder_id,
        "size": 0,
        "url": None,
        "parentId": None,
        "date": "2022-09-15T15:56:00.000Z",
        "children": []
    }

    status, response = request(f"/nodes/{folder_id}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    if response != expected:
        print("Nonnull-size-folder test failed. Response tree doesn't match expected tree.")
        sys.exit(1)

    print("Nonnull-size-folder test passed...")

    # удаляем загруженную в БД папку
    params = urllib.parse.urlencode({
        "date": "2022-09-15T15:56:02Z"
    })
    status, _ = request(f"/delete/{folder_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def file_with_negative_size():
    # файл с size < 0 --> 400
    batch = {
        "items": [
            {
                "type": "FILE",
                "id": "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e",
                "parentId": None,
                "size": -9999,
                "url": "my_file"
            }
        ],
        "updateDate": "2022-09-15T15:57:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Negative-size test passed...")


def equal_ids_in_one_request():
    # два элемента с одинаковым id в одном запросе --> 400
    batch = {
        "items": [
            {
                "type": "FILE",
                "id": "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e",
                "parentId": None,
                "size": 10,
                "url": "my_file1"
            },
            {
                "type": "FILE",
                "id": "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e",
                "parentId": None,
                "size": 20,
                "url": "my_file2"
            }
        ],
        "updateDate": "2022-09-15T15:58:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Equal-ids-in-one-request test passed...")


def invalid_date_for_import():
    # дата не соответствует ISO 8601 --> 400
    batch = {
        "items": [
            {
                "type": "FILE",
                "id": "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e",
                "parentId": None,
                "size": 100,
                "url": "my_file"
            }
        ],
        "updateDate": "16:00:30 15.09.2022"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Invalid-date test passed...")


def update_date_after_updating_item():
    # дата обновляется при обновлении элемента --> 200

    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    batch = {
        "items": [
            {
                "type": "FILE",
                "id": file_id,
                "parentId": None,
                "size": 100,
                "url": "my_file"
            }
        ],
        "updateDate": "2022-09-15T15:58:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    batch = {
        "items": [
            {
                "type": "FILE",
                "id": file_id,
                "parentId": None,
                "size": 200,
                "url": "my_larger_file"
            }
        ],
        "updateDate": "2022-09-15T16:04:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = {  # ожидаем, что date обновилась
        "type": "FILE",
        "id": file_id,
        "size": 200,
        "url": "my_larger_file",
        "parentId": None,
        "date": "2022-09-15T16:04:00.000Z",
        "children": None
    }

    status, response = request(f"/nodes/{file_id}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    if response != expected:
        print("Date-updating test failed. Response tree doesn't match expected tree.")
        sys.exit(1)

    print("Date-updating test passed...")

    # удаляем загруженный в БД файл
    params = urllib.parse.urlencode({
        "date": "2022-09-15T16:07:00Z"
    })
    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def test_import():
    print("Testing imports:")
    # ==add==
    null_id()
    invalid_data_type()
    file_as_a_parent()
    folder_with_nonnull_url()
    file_with_too_long_url()
    folder_with_nonnull_size()
    file_with_negative_size()
    equal_ids_in_one_request()
    invalid_date_for_import()

    # ==update==
    update_date_after_updating_item()
    print("Imports tests passed.\n")


""""=========/delete========="""


def id_not_found_for_delete():
    # ненайденный id --> 404
    params = urllib.parse.urlencode({
        "date": "2022-09-15T15:58:00.000Z"
    })

    status, _ = request(f"/nodes/{'MyBrandNewId'}?{params}", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"
    print("Id-not-found test passed...")


def invalid_date_for_delete():
    # дата не соответствует ISO 8601 --> 400
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    batch = {
        "items": [
            {
                "type": "FILE",
                "id": file_id,
                "parentId": None,
                "size": 100,
                "url": "my_file"
            }
        ],
        "updateDate": "2022-09-15T15:58:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    params = urllib.parse.urlencode({
        "date": "15 сентября 2022 года нашей эры"
    })

    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Invalid-date test passed...")

    # теперь удаляем файл из БД
    params = urllib.parse.urlencode({
        "date": "2022-09-15T16:07:00Z"
    })
    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def no_date_for_delete():
    # дата удаления не указана --> 400
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    batch = {
        "items": [
            {
                "type": "FILE",
                "id": file_id,
                "parentId": None,
                "size": 100,
                "url": "my_file"
            }
        ],
        "updateDate": "2022-09-15T15:58:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, _ = request(f"/delete/{file_id}", method="DELETE")
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("No-date test passed...")

    # теперь удаляем файл из БД
    params = urllib.parse.urlencode({
        "date": "2022-09-15T16:07:00Z"
    })
    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def test_delete():
    print("Testing delete:")
    id_not_found_for_delete()
    invalid_date_for_delete()
    no_date_for_delete()
    print("Delete tests passed.\n")


""""=========/nodes========="""


def empty_folder():
    # для пустой папки size = 0, children = [] --> 200
    folder_id = "072cdf36-340e-4007-853a-af3197080f18"

    batch = {
        "items": [
            {
                "type": "FOLDER",
                "id": folder_id,
                "parentId": None,
            }
        ],
        "updateDate": "2022-09-15T15:56:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = {
        "type": "FOLDER",
        "id": folder_id,
        "size": 0,
        "url": None,
        "parentId": None,
        "date": "2022-09-15T15:56:00.000Z",
        "children": []
    }

    status, response = request(f"/nodes/{folder_id}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    if response != expected:
        print("Empty-folder test failed. Response tree doesn't match expected tree.")
        sys.exit(1)

    print("Empty-folder test passed...")

    # удаляем загруженную в БД папку
    params = urllib.parse.urlencode({
        "date": "2022-09-15T15:56:02Z"
    })
    status, _ = request(f"/delete/{folder_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def id_not_found_for_nodes():
    # ненайденный id --> 404
    status, response = request(f"/nodes/{'MyBrandNewId'}", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"
    print("Id-not-found test passed...")


def test_nodes():
    print("Testing nodes:")
    empty_folder()
    id_not_found_for_nodes()
    print("Nodes tests passed.\n")


""""=========/updates========="""


def invalid_date_for_updates():
    # дата не соответствует ISO 8601 --> 400
    params = urllib.parse.urlencode({
        "date": "9999.5 год до нашей эры"
    })
    status, _ = request(f"/updates?{params}", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("Invalid-date test passed...")


def no_date_for_updates():
    # дата отсчета не указана --> 400
    status, _ = request(f"/updates", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"
    print("No-date test passed...")


def no_updates():
    # нет обновленных за данный период элементов - выдаем [] --> 200
    params = urllib.parse.urlencode({
        "date": "2022-09-15T15:56:02Z"
    })
    status, response = request(f"/updates?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = []
    if response != expected:
        print("No-updates test failed. Response list doesn't match expected list.")
        sys.exit(1)

    print("No-updates test passed...")


def no_folder_updates():
    # не выдаем обновления папок --> 200
    folder_id = "072cdf36-340e-4007-853a-af3197080f18"
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    batch = {
        "items": [
            {
                "type": "FOLDER",
                "id": folder_id,
                "parentId": None,
            },
            {
                "type": "FILE",
                "id": file_id,
                "parentId": folder_id,
                "size": 100,
                "url": "folder/my_file"
            }
        ],
        "updateDate": "2022-09-15T16:54:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    params = urllib.parse.urlencode({
        "date": "2022-09-15T17:02:00.000Z"
    })
    status, response = request(f"/updates?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = [
        {
            "id": file_id,
            "type": "FILE",
            "url": "folder/my_file",
            "parentId": folder_id,
            "size": 100,
            "date": "2022-09-15T16:54:00.000Z"
        }
    ]
    if response != expected:
        print("No-folder-updates test failed. Response list doesn't match expected list.")
        sys.exit(1)
    print("No-folder-updates test passed...")

    # удаляем загруженную в БД папку с файлом
    status, _ = request(f"/delete/{folder_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def no_updates_for_deleted_item():
    # не выдаем обновления удаленных элементов --> 200
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    batch = {
        "items": [
            {
                "type": "FILE",
                "id": file_id,
                "parentId": None,
                "size": 100,
                "url": "my_file"
            }
        ],
        "updateDate": "2022-09-15T16:54:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    params = urllib.parse.urlencode({
        "date": "2022-09-15T16:58:00.000Z"
    })
    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    params = urllib.parse.urlencode({
        "date": "2022-09-15T17:02:00.000Z"
    })
    status, response = request(f"/updates?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = []
    if response != expected:
        print("Deleted-item-updates test failed. Response list doesn't match expected list.")
        sys.exit(1)
    print("Deleted-item-updates test passed...")


def test_updates():
    print("Testing updates:")
    invalid_date_for_updates()
    no_date_for_updates()
    no_updates()
    no_folder_updates()
    no_updates_for_deleted_item()
    print("Updates tests passed.\n")


""""=========/history========="""


def upload_test_file():
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    batch = {
        "items": [
            {
                "type": "FILE",
                "id": file_id,
                "parentId": None,
                "size": 100,
                "url": "my_file"
            }
        ],
        "updateDate": "2022-09-15T16:54:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def delete_test_file():
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"

    params = urllib.parse.urlencode({
        "date": "2022-09-15T16:58:00.000Z"
    })
    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def invalid_date_start():
    # dateStart не соответствует ISO 8601 --> 400
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    upload_test_file()

    params = urllib.parse.urlencode({
        "dateStart": "после дождичка в четверг",
        "dateEnd": "2022-09-15T23:00:00Z"
    })
    status, response = request(
        f"/node/{file_id}/history?{params}", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Invalid-date-start test passed...")
    delete_test_file()


def invalid_date_end():
    # dateEnd не соответствует ISO 8601 --> 400
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    upload_test_file()

    params = urllib.parse.urlencode({
        "dateStart": "2022-09-15T10:00:00Z",
        "dateEnd": "после дождичка в четверг"
    })
    status, response = request(
        f"/node/{file_id}/history?{params}", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Invalid-date-end test passed...")
    delete_test_file()


def start_after_end():
    # dateStart позже dateEnd --> 400
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    upload_test_file()

    params = urllib.parse.urlencode({
        "dateStart": "2022-09-15T23:00:00Z",
        "dateEnd": "2022-09-15T12:00:00Z"
    })
    status, response = request(
        f"/node/{file_id}/history?{params}", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Start-after-end test passed...")
    delete_test_file()


def start_without_end():
    # в задании сказано выдать либо историю в рамках [from, to), либо за все время
    # поэтому dateStart без dateEnd --> 400
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    upload_test_file()

    params = urllib.parse.urlencode({
        "dateStart": "2022-09-15T12:00:00Z",
    })
    status, response = request(
        f"/node/{file_id}/history?{params}", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Start-without-end test passed...")
    delete_test_file()


def end_without_start():
    # в задании сказано выдать либо историю в рамках [from, to), либо за все время
    # поэтому dateEnd без dateStart --> 400
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    upload_test_file()

    params = urllib.parse.urlencode({
        "dateEnd": "2022-09-15T18:00:00Z"
    })
    status, response = request(
        f"/node/{file_id}/history?{params}", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("End-without-start test passed...")
    delete_test_file()


def id_not_found_for_history():
    # ненайденный id --> 404
    upload_test_file()

    params = urllib.parse.urlencode({
        "dateStart": "2022-09-15T12:00:00Z",
        "dateEnd": "2022-09-15T23:00:00Z"
    })
    status, response = request(
        f"/node/'MyBrandNewId'/history?{params}", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Id-not-found test passed...")
    delete_test_file()


def no_history():
    # нет обновленных за данный период элементов - выдаем [] --> 200
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    upload_test_file()

    params = urllib.parse.urlencode({
        "dateStart": "1000-01-01T12:00:00Z",
        "dateEnd": "2000-01-01T12:00:00Z"
    })
    status, response = request(
        f"/node/{file_id}/history?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = []
    if response != expected:
        print("No-history test failed. Response list doesn't match expected list.")
        sys.exit(1)
    print("No-history test passed...")
    delete_test_file()


def all_time_history():
    # запрос без dateStart и dateEnd выдает историю за все время --> 200
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    upload_test_file()

    status, response = request(
        f"/node/{file_id}/history", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = [
        {
            "id": file_id,
            "type": "FILE",
            "url": "my_file",
            "parentId": None,
            "size": 100,
            "date": "2022-09-15T16:54:00.000Z"
        }
    ]
    if response != expected:
        print("All-time-history test failed. Response list doesn't match expected list.")
        sys.exit(1)
    print("All-time-history test passed...")
    delete_test_file()


def folder_with_deleted_item():
    # должна появиться запись об уменьшении размера папки, в которой лежал удаленный файл --> 200
    file_id = "f5c8380d-fd22-4040-8817-9e0eb6b1ee3e"
    folder_id = "072cdf36-340e-4007-853a-af3197080f18"

    batch = {
        "items": [
            {
                "type": "FOLDER",
                "id": folder_id,
                "parentId": None
            },
            {
                "type": "FILE",
                "id": file_id,
                "parentId": folder_id,
                "size": 100,
                "url": "my_file"
            }
        ],
        "updateDate": "2022-09-15T19:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=batch)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    params = urllib.parse.urlencode({
        "date": "2022-09-15T19:04:00.000Z"
    })
    status, _ = request(f"/delete/{file_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, response = request(
        f"/node/{folder_id}/history", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected = [
        {
            'size': 100,
            'id': '072cdf36-340e-4007-853a-af3197080f18',
            'type': 'FOLDER',
            'url': None,
            'parentId': None,
            'date': '2022-09-15T19:00:00.000Z'
        },
        {
            'size': 0,
            'id': '072cdf36-340e-4007-853a-af3197080f18',
            'type': 'FOLDER',
            'url': None,
            'parentId': None,
            'date': '2022-09-15T19:04:00.000Z'
        }
    ]
    if response != expected:
        print("Folder-with-deleted-item test failed. Response list doesn't match expected list.")
        sys.exit(1)
    print("Folder-with-deleted-item test passed...")

    # удаляем из БД пустую папку
    params = urllib.parse.urlencode({
        "date": "2022-09-15T19:23:00.000Z"
    })
    status, _ = request(f"/delete/{folder_id}?{params}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"


def test_history():
    print("Testing history:")
    invalid_date_start()
    invalid_date_end()
    start_after_end()
    start_without_end()
    end_without_start()
    id_not_found_for_history()
    no_history()
    all_time_history()
    folder_with_deleted_item()
    print("History tests passed.")


def main():
    test_import()
    test_delete()
    test_nodes()
    test_updates()
    test_history()


if __name__ == "__main__":
    main()
