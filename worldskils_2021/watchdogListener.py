#!/usr/bin/python3

# Импорты
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from networktables import NetworkTables
from networktables.util import ntproperty
import threading
import os

# ScriptWay = "python3 /home/pi/"
# ArgWay = "/home/pi/"

#Создаём файл результата
f = open('/home/pi/patterns_result.txt', 'w')
f.close()

#Создаём поток, чтобы убедиться, что сетевая таблица подключена
cond = threading.Condition()
notified = [False]

#Создаём функцию прослушивания соединения
def connectionListener(connected, info):
    with cond:
        notified[0] = True
        cond.notify()

#Создаём экземпляр таблицы
NetworkTables.initialize(server="10.12.34.2")
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

#Ждём установления соединения
with cond:
    if not notified[0]:
        cond.wait()

#Создаём vision Table с нужными свойствами для взаимодействия с кодом "Робота"
ntMatrix = ntproperty('/Vision/Matrix', "null")
ntFindTemplates = ntproperty('/Vision/findTemplates', False)
ntPatternTemplates = ntproperty('/Vision/patternScript', "null")
ntPatternTemplates = ntproperty('/Vision/patternArgument', "null")

#Назначение таблицы для последующего использования
table = NetworkTables.getTable('Vision')

#Создаём класс для использования FileSystemEventHandler
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        try:
            file = open('./home/pi/patterns_result.txt', 'r')
            table.putString('Matrix', file.readline())
            file.close()
        except:
            pass #when file is not created yet

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='./home/pi/patterns_result.txt', recursive=False)
observer.start()

#Бесконечный цикл
while(True):
    #Проверяем свойство таблицы и при флаге "Истина" запускаем скрипт
    if table.getBoolean('findTemplates', False) == True:
        #Сбрасываем флаг
        table.putBoolean('findTemplates', False)
        #Получаем имена скриптов и аргументов
        FILE = table.getString('patternScript', "")
        ARG = table.getString('patternArgument', "")
        #Если имена не получены подставляем значения по умолчанию
        if FILE == "null" or ARG == "null":
            FILE = "/home/pi/findTemplatesOnSomePatterns.py"
            ARG = "/home/pi/W.png /home/pi/B.png /home/pi/Y.png"
        #Запускаем выполнение скрипта с аргументами 
        os.system("python3 " + FILE + " " + ARG)
    try:
        pass
    except KeyboardInterrupt:
        observer.stop()
