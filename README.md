### Вступительное задание в ШБР Яндекса 2022

#### *Выполнила Зинаида Будилова*

###### *Язык: Python 3.7*

### Запуск
В нормальной ситуации приложение всегда запущено, в том числе после перезагрузки контейнера.
Запуск приложения при перезагрузке настроен с помощью *systemd*, см. файл `/etc/systemd/system/my_project_flask.service`.

В случае необходимости, приложение можно запустить командой `sudo python3 /home/ubuntu/yandex_project/disk/main.py`.
Тесты запускаются аналогично: нужно выполнить файл `unit_test.py` в папке `yandex_project`.

### Струкутура проекта
Код проекта расположен в директории `yandex_project/disk/`.

Основной файл с *flask*-приложением - `main.py`.
Модули с постфиксом `_funcs.py` содержат вспомогательные функции для каждой из задач. 
Модуль `validation.py` содержит функции для проверки корректности данных.

В подпапке `db/` находится файл, создающий структуру базы данных - `schema.py` 
- и сама база `database.db`.

Юнит-тесты, условие задания и ридми лежат вне директории с кодом, в папке `yandex_project/`.  

### Технологии, библиотеки
Веб-приложение выполнено в фреймворке *Flask*.
База данных создана с помощью расширения *flask_sqlalchemy*.

Для работы с датами в ISO-формате использован модуль *dateutil.parser*, 
а валидность даты проверяется регулярным выражением (*re*).
Тип данных - FILE или FOLDER - реализован как класс *enum*.
Для перевода данных в формат *json* используется одноименная библиотека.
Для работы с файловой системой - *os*. 

Так как сроки выполнения проекта строго ограничены, а технические мощности, наоборот,
предоставлены в избытке, я выбрала именно *Flask* - единственный немного знакомый мне фреймворк.
Сравнивать множество библиотек в поисках самой эффективной означало бы не успеть к дедлайну.

### Выполнение задач
В приложении реализованы все описанные в `openapi.yaml` функции - и базовые, и дополнительные.
Проверяется корректность входных данных.

Выполнены технические требования: 
Сервис развернут на адресе `0.0.0.0:80`.
Данные сохраняются при перезапуске.
Сервис автоматически перезапускается при рестарте контейнера. 
Время выполнения `test_all()` базовой версии юнит-тестов - около 0.3s real time, 0.06s user time, 0.02s sys time. 

Сервис может обрабатывать малое количество запросов одновременно, 
так как дефолтный параметр приложения *Flask* - `app.run(threaded=True)`.
Большой поток одновременных запросов приложение не выдержит, поскольку отдельный WSGI-сервер не используется.

### Тесты
Приложение проходит все тесты из базовой версии `unit_test.py`, 
однако пришлось поменять в этой программе значение `API_BASEURL` 
с некорректного `http://localhost:8080` на требуемый заданием `http://localhost:80`.


