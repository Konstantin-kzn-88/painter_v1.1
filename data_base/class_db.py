
# -----------------------------------------------------------
# Класс предназначен для работы с локальной базой данных
#
# Класс реализует:
# - создание базы данных
# - соединение с базой данных
# - добавление ген.плана в базу данных
# - замена ген.плана в базе данных
# - обновление списка ген.планов
# - получение данных из базы данных (ген.план, данные таблицы и масштаб)
# - сохранение данных в базу данных (ген.план, данные таблицы и масштаб)
#
# (C) 2022 Kuznetsov Konstantin
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

from PySide2 import QtWidgets, QtGui, QtCore
import sqlite3 as sql
import os
from pathlib import Path


class Data_base(QtWidgets.QWidget):
    def __init__(self, db_name: str, db_path: str):
        super().__init__()
        # Путь и имя базы данных
        self.db_name = db_name
        self.db_path = db_path
        # Иконки
        path_ico = str(Path(os.getcwd()))
        main_ico = QtGui.QIcon(path_ico + '/ico/painter.png')
        self.setWindowIcon(main_ico)

    def __convertToBinaryData(self, file_path):
        # Конвертирование в BLOB
        with open(file_path, 'rb') as file:
            blobData = file.read()
        return blobData

    def db_create(self) -> tuple:
        """
        Создание новой базы данных

        При отстутсвии имени базы или пути возвращает кортеж
        из двух пустых строк (например, отсуствие имени (пустая строка), нет пути,
        база по указанному пути уже существует.

        При наличии пути и имени создает таблицу в базе данных вида:
        id, data, plan, name_plan

        :@return: tuple: db_name - имя базы данных
                         db_path - путь базы данных
        """
        # 1. Получить имя новой базы данных, если параметры не были заданы в ручную
        if self.db_name == '':
            self.db_name, status = QtWidgets.QInputDialog.getText(self, 'Создать новую базу данных',
                                                         'Введите имя новой базы данных:')

            if len(self.db_name) == 0 and status:
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("Информация")
                msg.setText("База данных не может быть с пустым названием!")
                msg.exec()
                return ('', '')
            elif status == False:
                return ('', '')

        # 2. Проверить нет ли базы данных с этим же именем по тому же пути
        if self.db_path == '':
            self.db_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выбрать путь базы данных",
                                                             str(Path(os.getcwd()))[:3],
                                                             QtWidgets.QFileDialog.ShowDirsOnly
                                                             | QtWidgets.QFileDialog.DontResolveSymlinks)

        check = os.path.exists(f"{self.db_path}/{self.db_name}.db")

        if check:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Информация")
            msg.setText("База данных с таким названием уже существует!")
            msg.exec()
            return ('', '')

        # 4. Создадим базу данных
        if self.db_path == '':
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Информация")
            msg.setText("Нужно выбрать путь сохранения!")
            msg.exec()
            return ('', '')
        else:
            print(f'{self.db_path}/{self.db_name}.db')
            with sql.connect(f'{self.db_path}/{self.db_name}.db') as connection:
                cursor = connection.cursor()
                cursor.execute("""CREATE TABLE objects(id INTEGER PRIMARY KEY, data TEXT NOT NULL,
                                                            plan BLOB NOT NULL, name_plan TEXT NOT NULL)""")

            return (self.db_name, self.db_path)


    def db_connect(self) -> tuple:
        """
        Подключение к существующей БД

        При отстутсвии имени базы или пути возвращает кортеж
        из двух пустых строк (например, отсуствие имени (пустая строка), нет пути,
        база по указанному пути уже существует.

        При наличии пути и имени создает таблицу в базе данных вида:
        id, data, plan, name_plan

        :@return: tuple: db_name - имя базы данных
                         db_path - путь базы данных
        """

        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть базу данных',
                                                     str(Path(os.getcwd()))[:3], ("Data base (*.db)"))[0]
        if path == "":
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Информация")
            msg.setText("Файл базы данных не выбран")
            msg.exec()
            return ('', '')
        file_name = QtCore.QFileInfo(path).fileName()
        file_path = QtCore.QFileInfo(path).path()
        self.db_name = file_name
        self.db_path = file_path

        return (self.db_name, self.db_path)


    def plan_add(self):
        """
         Загрузка файла картинки в базу данных
        """
        # Проверка подключения к базе данных
        # проверка базы данных
        if self.db_path != '' and self.db_name != '':

            file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть генеральный план',
                                                              str(Path(os.getcwd()))[:3], ("Images (*.jpg)"))[0]
            file_name = QtCore.QFileInfo(file_path).fileName()
            # Проверка выбран ли файл ген.плана
            if file_path == "":
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("Информация")
                msg.setText("Файл не выбран")
                msg.exec()
                return

            # Подключение к базе данных
            path_str = f'{self.db_path}/{self.db_name}'.replace("/", "//")

            with sql.connect(path_str) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT id FROM objects")
                real_id = cursor.fetchall()
                # проверка максимального id в базе
                max_id = 1 if real_id == [] else max(real_id)[0] + 1
                # SQL запрос на вставку BLOB
                sqlite_insert_blob_query = """ INSERT INTO 'objects'
                                                        ('id', 'data', 'plan', 'name_plan') VALUES (?, ?, ?, ?)"""
                # Конвертация файла в BLOB
                plan_to_blob = self.__convertToBinaryData(file_path)
                # Проготовим множество к вставке в SQL запрос
                data_tuple = (max_id, "", plan_to_blob, file_name)
                cursor.execute(sqlite_insert_blob_query, data_tuple)

        else:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Информация")
            msg.setText("База данных не подключена!")
            msg.exec()
            return


    def plan_replace(self, text: str):
        """
         Замена ген.плана
        """

        # Проверка подключения к базе данных
        # проверка базы данных
        if self.db_path != '' and self.db_name != '':

            file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть генеральный план',
                                                              str(Path(os.getcwd()))[:3], ("Images (*.jpg)"))[0]
            file_name = QtCore.QFileInfo(file_path).fileName()

            # Проверка выбран ли файл ген.плана
            if file_path == "":
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("Информация")
                msg.setText("Файл не выбран")
                msg.exec()
                return

            # Подключение к базе данных
            path_str = f'{self.db_path}/{self.db_name}'.replace("/", "//")

            with sql.connect(path_str) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM objects")
                plan_in_db = cursor.fetchall()
                # проверка наличия планов в БД
                if plan_in_db == []:
                    msg = QtWidgets.QMessageBox(self)
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setWindowTitle("Информация")
                    msg.setText("Ген.планов в базе данных нет")
                    msg.exec()
                    return
                for row in plan_in_db:
                    if str(f'{row[0]}, {row[3]}') == text:
                        # Конвертация файла в BLOB
                        plan_to_blob = self.__convertToBinaryData(file_path)
                        # Обновление данных
                        cursor.execute('UPDATE objects SET plan = ?  where id = ?', (plan_to_blob, str(row[0])))
                        cursor.execute('UPDATE objects SET name_plan = ? where id = ?', (file_name, str(row[0])))


    def plan_list_update(self, plan_list) -> None:
        """
        Обновление списка ген.планов при:
        - подключении БД
        - добавлении ген.плана
        - удалении ген.плана

        :param -plan_list type (QtWidgets.QComboBox)
        """
        if self.db_path != '' and self.db_name != '':
            path_str = f'{self.db_path}/{self.db_name}'.replace("/", "//")

            with sql.connect(path_str) as connection:

                cursor = connection.cursor()
                cursor.execute("SELECT id, name_plan FROM objects")
                plan_in_db = cursor.fetchall()

                # Очистить QtWidgets.QComboBox
                plan_list.clear()

                plan_item = []

                for row in plan_in_db:
                    name_plan = str(f'{row[0]}, {row[1]}')
                    plan_item.append(name_plan)
                if plan_item == []:
                    plan_list.addItems(["--Нет ген.планов-- "])
                else:
                    plan_list.addItems(plan_item)


    def get_plan_in_db(self, text: str):
        """
        Функция получения картинки из базы данных
        :param text - строка полученная из QComboBox (id и name_plan)
        :return image_data - list данные и BLOB формат картинки
        """
        if self.db_path != '' and self.db_name != '':
            path_str = f'{self.db_path}/{self.db_name}'.replace("/", "//")

            with sql.connect(path_str) as connection:

                cursor = connection.cursor()
                cursor.execute("SELECT * FROM objects")
                plan_in_db = cursor.fetchall()
                for row in plan_in_db:
                    if str(f'{row[0]}, {row[3]}') == text:
                        data, image_data = row[1], row[2]
                        return (data, image_data)
                return (None, None)


    def save_data_in_db(self, name_plan: str, scale_plan: str, table_widget):
        """
        Функция сохранения данных таблицы в базу данных
        :param - name_plan - наименование плана для поиска в базе данных
        :param - scale_plan - масштаб плана
        :param - table_widget - QTableWidget
        """
        if self.db_path != '' and self.db_name != '':
            # 1. Считаем данные из таблицы
            data_list = []
            count_row = 0  # начинаем с 0 строки
            for _ in range(0, table_widget.rowCount()):  # посчитаем строки
                append_list = []  # заведем пустой список для объекта
                count_col = 0  # колонка с индесом 0
                for _ in range(0, table_widget.columnCount()):  # для каждого столбца строки

                    if count_col != table_widget.columnCount() - 1:
                        var = table_widget.item(count_row, count_col).text().replace(',', '.')
                    else:
                        var = table_widget.item(count_row, count_col).text()
                    append_list.append(var)  # добавим в словарь текст ячейки
                    count_col += 1  # + 1 к столбцу
                data_list.append(append_list)  # добавим объект
                count_row += 1  # +1 к строке (новая строка если len(data_list) > 1)
            # добавим масштаб
            data_list.append(scale_plan)

            # 2. Запишем все в БД
            path_str = f'{self.db_path}/{self.db_name}'.replace("/", "//")
            with sql.connect(path_str) as connection:

                cursor = connection.cursor()
                cursor.execute("SELECT * FROM objects")
                plan_in_db = cursor.fetchall()

                for row in plan_in_db:
                    if str(f'{row[0]}, {row[3]}') == name_plan:
                        # SQL запрос на вставку
                        cursor.execute('UPDATE objects SET data = ?  where id = ?', (str(data_list), str(row[0])))

    def plan_del_in_db(self, name_plan: str):
        """
        Удаление ген.плана из БД
        :param - name_plan - наименование плана для поиска в базе данных
        """
        if self.db_path != '' and self.db_name != '':
            path_str = f'{self.db_path}/{self.db_name}'.replace("/", "//")

            with sql.connect(path_str) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT id, name_plan FROM objects")
                plan_in_db = cursor.fetchall()
                for row in plan_in_db:
                    if str(f'{row[0]}, {row[1]}') == name_plan:
                        cursor.execute('DELETE FROM objects WHERE id=?', (str(row[0]),))
