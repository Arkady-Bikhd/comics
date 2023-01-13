# Публикация комиксов

Сервис используется для публикации Вконтакте комиксов [Рэндела Манро](https://xkcd.com).


## Как установить
1. Создать группу Вконтакте, в которой будут выкладываться комиксы, и получить group_id.
2. Создать приложение Вконтакте.
3. Получить ключ доступа пользователя.
4. Полученные данные присвоить переменной окружения в файле ".env".

```python
VK_ACCESS_TOKEN=ВАШ_КЛЮЧ_ДОСТУПА
VK_GROUP_ID=ID_ГРУППЫ
```

3. Установить зависимости.

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Рекомендуется использовать [virtualenv/env](https://docs.python.org/3/library/venv.html) для изоляции проекта.

## Как использовать

Для использования сервиса необходимо запустить:

```
python comics.py
```

## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
