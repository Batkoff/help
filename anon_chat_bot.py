# - *- coding: utf- 8 - *-
import sys
import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


dialogs = {}  # Словарь диалогов (id: собеседник) все int
wait = []  # Список ожидания, состоящий из id
vk_session = vk_api.VkApi(token="токен")  # Токен группы
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, "id группы")  # id группы с ботом
for event in longpoll.listen():  # Обработка событий longpoll
    log = open('log.txt', 'a')  # Создание или открытие файла log.txt
    if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка события, является ли оно сообщением
        if event.message.text != '':  # Отбрасываем сообщения с пустым текстом
            if event.from_user:  # Если сообщение от группы (может быть еще в беседе)
                log.write(f'Сообщение {event.message.text} от {event.message.from_id}\n')  # Запись в лог
                if event.message.text.lower() == '!стоп':  # Проверка: не является ли сообщение командой
                    log.write(f'Диалог {event.message.from_id} с {dialogs[event.message.from_id]} остановлен\n')
                    # Запись в лог
                    vk.messages.send(user_id=dialogs[event.message.from_id], random_id=get_random_id(),
                                     message='Диалог остановлен')  # Уведомление остановившему
                    vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                     message='Диалог остановлен')  # Уведомление собеседнику
                    del dialogs[dialogs[event.message.from_id]]  # Чистка в словаре диалогов, следующая строка также
                    del dialogs[event.message.from_id]
                elif event.message.text.lower() == '!отменапоиска' and event.message.from_id in wait:
                    # Проверка: не является ли сообщение командой и находится ли человек в очереди, чтобы из нее выйти
                    log.write(f'{event.message.from_id} вышел из очереди ожидания\n')  # Запись в лог
                    vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                     message='Вы удалены из очереди')  # Уведомление
                    del wait[wait.index(event.message.from_id)]  # Удаление из очереди
                elif event.message.text.lower() == '!диалог' and event.message.from_id not in wait and \
                        event.message.from_id not in dialogs:
                    # Проверка: не является ли сообщение командой и на не нахождение в очереди ожидания и в диалогах
                    if not wait:  # Если список ожидания пуст
                        vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                         message='Вы в очереди ожидания')  # Уведомление
                        wait.append(event.message.from_id)  # Добавление в список ожидания
                        log.write(f'{event.message.from_id} добавлен в очередь\n')  # Запись в лог
                    else:  # Если в списке ожидания кто то есть
                        dialogs[event.message.from_id] = wait[0]  # Запись в словарь Написавший: ожидающий
                        dialogs[wait[0]] = event.message.from_id  # Запись в словарь Ожидающий: написавший
                        vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                         message='Диалог начат, для остановки пишите !стоп')  # Уведомление
                        vk.messages.send(user_id=wait[0], random_id=get_random_id(),
                                         message='Диалог начат, для остановки пишите !стоп')  # Уведомление
                        log.write(f'Начат диалог {event.message.from_id} c {wait[0]}\n')  # Запись в лог
                        del wait[0]  # Убираем ожидающего из очереди
                elif event.message.text.lower() == 'диалоги' and event.message.from_id == ('int id админа'):
                    # Проверка: не является ли сообщение командой и проверка на id написавшего
                    if dialogs:  # Если в диалогах кто то есть
                        vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                         message=' '.join([f'|{i[0]} с {i[1]}|' for i in dialogs.items()]))
                        # Распаковываем словарь диалогов и приводим кортежи к str
                    else:  # Если в диалогах никого есть
                        vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                         message='Диалогов нет')  # Сообщение админу
                    log.write(f'Админ посмотрел диалоги\n')  # Запись в лог
                elif event.message.text.lower() == 'очередь' and event.message.from_id == ('int id админа'):
                    # Проверка: не является ли сообщение командой и проверка на id написавшего
                    if wait:  # Если в очереди кто то есть
                        vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                         message=' '.join(list(map(str, wait))))
                        # Переводим int(id) в str и превращаем список в строку и отправляем админу
                    else:  # Если в очереди никого нет
                        vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                         message='Очередь пустая')  # Сообщение админу
                    log.write(f'Админ проверил список ожидания\n')  # Запись в лог
                elif event.message.from_id in wait:  # Если пишет челик из очереди ожидания
                    log.write(f'{event.message.from_id} пишет из очереди ожидания\n')  # Запись в лог
                    vk.messages.send(user_id=wait[0], random_id=get_random_id(),
                                     message='Вы в очереди ожидание, ждите, для выхода из '
                                             'очереди напишите !отменапоиска')  # Сообщение
                elif event.message.from_id not in dialogs:  # Если человек не в диалогах (выше проверка и на очередь)
                    vk.messages.send(user_id=event.message.from_id, random_id=get_random_id(),
                                     message='Чтобы начать чат с анонимным собеседником - напишите !диалог')
                    # Пишем стартовое сообщение
                    log.write(f'Отправлено стартовое сообщение для {event.message.from_id}\n')  # Запись в лог
                elif event.message.from_id in dialogs:  # Если человек в диалогах
                    vk.messages.send(user_id=dialogs[event.message.from_id], random_id=get_random_id(),
                                     message=event.message.text)
                    # Пишем сообщение с его текстом его собеседнику из словаря, ключ - id написавшего
                    log.write(f'Отправлено сообщение {event.message.from_id} к {dialogs[event.message.from_id]}\n')
                    # Запись в лог
    log.close()  # Закрытие лога
