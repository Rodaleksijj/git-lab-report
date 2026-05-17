import os
import csv
from datetime import datetime
from typing import List, Optional, Iterator, Union


class VisitRecord:#Представление записи о посещении банка

    def __init__(self, number: int, full_name: str, datetime_str: str, visit_type: str):
        self._number = number
        self._full_name = full_name
        self._datetime = datetime_str
        self._visit_type = visit_type

    def __setattr__(self, name, value):
        # Устанавливать только "приватные" атрибуты и только через _name
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            raise AttributeError(f"Изменение атрибута '{name}' запрещено. Используйте методы класса.")

    @property
    def number(self) -> int:
        return self._number

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def datetime_str(self) -> str:
        return self._datetime

    @property
    def visit_type(self) -> str:
        return self._visit_type

    def __repr__(self) -> str:
        #Перегрузка repr
        return f"VisitRecord(№={self._number}, ФИО='{self._full_name}', Дата/время='{self._datetime}', Тип='{self._visit_type}')"

    def __str__(self) -> str:
        #Перегрузка str
        return f"{self._number:<5} {self._full_name:<25} {self._datetime:<20} {self._visit_type:<20}"

    def __eq__(self, other) -> bool:
        #Перегрузка оператора сравнения
        if not isinstance(other, VisitRecord):
            return False
        return self._number == other._number

    def to_dict(self) -> dict:
        #Преобразование в словарь для CSV
        return {
            '№': self._number,
            'ФИО': self._full_name,
            'Дата и время': self._datetime,
            'Тип обращения': self._visit_type
        }

    @staticmethod
    def from_dict(data: dict) -> 'VisitRecord':
        return VisitRecord(
            number=int(data.get('№', 0)),
            full_name=data.get('ФИО', ''),
            datetime_str=data.get('Дата и время', ''),
            visit_type=data.get('Тип обращения', '')
        )

    @staticmethod
    def get_headers() -> List[str]:
        #Возврат заголовки
        return ['№', 'ФИО', 'Дата и время', 'Тип обращения']


class BaseCollection:#Создание коллекции записей


    def __init__(self):
        self._records: List[VisitRecord] = []

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int) -> VisitRecord:
        if isinstance(index, slice):
            return self._records[index]
        # Преобразуем отрицательный индекс в положительный
        if index < 0:
            index = len(self._records) + index
        if 0 <= index < len(self._records):
            return self._records[index]
        raise IndexError(f"Индекс {index} вне диапазона")

    def __setitem__(self, index: int, value: VisitRecord):
        # Преобразуем отрицательный индекс в положительный
        if index < 0:
            index = len(self._records) + index
        if 0 <= index < len(self._records):
            self._records[index] = value
        else:
            raise IndexError(f"Индекс {index} вне диапазона")

    def __iter__(self) -> Iterator[VisitRecord]:
        return iter(self._records)

    def __contains__(self, item: VisitRecord) -> bool:
        return item in self._records

    def add(self, record: VisitRecord):
        self._records.append(record)

    def get_all(self) -> List[VisitRecord]:
        return self._records.copy()

    def clear(self):
        self._records.clear()


class BankVisitsCollection(BaseCollection):

    def __init__(self, filename: str = 'data.csv', use_generated_data: bool = False):
        super().__init__()
        self._filename = filename
        self._use_generated_data = use_generated_data
        self._is_loaded = False

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            raise AttributeError(f"Изменение атрибута '{name}' запрещено. Используйте методы класса.")

    def __repr__(self) -> str:
        return f"BankVisitsCollection(filename='{self._filename}', records_count={len(self._records)}, use_generated_data={self._use_generated_data})"

    def __str__(self) -> str:
        if not self._records:
            return "Коллекция пуста"
        result = f"Коллекция посещений банка (всего {len(self._records)} записей):\n"
        result += f"{'№':<5} {'ФИО':<25} {'Дата и время':<20} {'Тип обращения':<20}\n"
        for record in self._records:
            result += f"\n{str(record)}"
        return result

    def _parse_csv_line(self, line: str) -> List[str]:
        if line.startswith('\ufeff'):
            line = line[1:]
        return [item.strip() for item in line.split(';')]

    def read_from_file(self, custom_path: Optional[str] = None):
        if self._use_generated_data:
            print(f"\nГенерируем примерные данные...")
            self._generate_sample_data()
            print(f"Сгенерировано записей: {len(self._records)}")
            self._is_loaded = True
            return

        file_to_read = custom_path or self._filename

        if self._is_loaded:
            return

        try:
            with open(file_to_read, 'r', encoding='utf-8-sig') as file:
                header_line = file.readline().strip()
                headers = self._parse_csv_line(header_line)

                expected_headers = VisitRecord.get_headers()
                if headers != expected_headers:
                    header_mapping = {}
                    for i, expected in enumerate(expected_headers):
                        if i < len(headers):
                            header_mapping[headers[i]] = expected
                else:
                    header_mapping = {h: h for h in headers}

                self._records = []
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue

                    values = self._parse_csv_line(line)
                    record_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(values):
                            mapped_header = header_mapping.get(header, header)
                            record_dict[mapped_header] = values[i]

                    if '№' in record_dict:
                        try:
                            record_dict['№'] = int(record_dict['№'])
                        except:
                            record_dict['№'] = line_num

                    self._records.append(VisitRecord.from_dict(record_dict))

            print(f"\nДанные успешно загружены из файла '{file_to_read}'")
            print(f"Загружено записей: {len(self._records)}")
            self._is_loaded = True

        except FileNotFoundError:
            print(f"\nФайл '{file_to_read}' не найден.")
            print(f"Генерируем примерные данные...")
            self._generate_sample_data()
            print(f"Сгенерировано записей: {len(self._records)}")
            self._is_loaded = True
        except Exception as e:
            print(f"\nОшибка при чтении файла: {e}")
            print(f"Генерируем примерные данные...")
            self._generate_sample_data()
            print(f"Сгенерировано записей: {len(self._records)}")
            self._is_loaded = True

    def _generate_sample_data(self):
        sample_records = [
            VisitRecord(1, 'Иванчук И.И.', '2026-04-15 10:30', 'консультация'),
            VisitRecord(2, 'Петренко П.П.', '2026-04-15 11:45', 'ипотека'),
            VisitRecord(3, 'Сидоров С.С.', '2026-04-15 09:15', 'вклад'),
            VisitRecord(4, 'Андрейченко А.А.', '2026-04-16 14:20', 'консультация'),
            VisitRecord(5, 'Бориско Б.Б.', '2026-04-16 16:30', 'консультация'),
            VisitRecord(6, 'Васильева В.В.', '2026-04-17 12:00', 'консультация'),
            VisitRecord(7, 'Григорьевич Г.Г.', '2026-04-17 13:45', 'счёт'),
            VisitRecord(8, 'Дмитриенко Д.Д.', '2026-04-18 10:00', 'консультация'),
            VisitRecord(9, 'Егороц Е.Е.', '2026-04-18 11:30', 'консультация'),
            VisitRecord(10, 'Жуковский Ж.Ж.', '2026-04-18 15:15', 'вклад')
        ]
        self._records = sample_records

    def save_to_file(self, filename: Optional[str] = None):
        save_filename = filename or self._filename

        try:
            with open(save_filename, 'w', encoding='utf-8-sig', newline='') as file:
                file.write(';'.join(VisitRecord.get_headers()) + '\n')

                for record in self._records:
                    line = ';'.join([
                        str(record.number),
                        record.full_name,
                        record.datetime_str,
                        record.visit_type
                    ])
                    file.write(line + '\n')

            print(f"Данные успешно сохранены в файл '{save_filename}'")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")

    def display_data(self, data: Optional[List[VisitRecord]] = None, title: str = "Данные"):
        if data is None:
            data = self._records

        if not data:
            print("Нет данных для отображения")
            return

        print(f"\n{title}:")
        print(f"{'№':<5} {'ФИО':<25} {'Дата и время':<20} {'Тип обращения':<20}")

        for record in data:
            print(record)

        print(f"\nВсего записей: {len(data)}")

    def sort_by_string_field(self, field: str = 'full_name', reverse: bool = False) -> List[VisitRecord]:
        if field == 'full_name':
            return sorted(self._records, key=lambda x: x.full_name, reverse=reverse)
        elif field == 'visit_type':
            return sorted(self._records, key=lambda x: x.visit_type, reverse=reverse)
        return self._records

    def sort_by_numeric_field(self, field: str = 'number', reverse: bool = False) -> List[VisitRecord]:
        if field == 'number':
            return sorted(self._records, key=lambda x: x.number, reverse=reverse)
        return self._records

    def filter_by_criteria(self, field: str, value, operator: str = 'eq') -> List[VisitRecord]:
        filtered = []

        for record in self._records:
            if field == 'number':
                record_value = record.number
            elif field == 'full_name':
                record_value = record.full_name
            elif field == 'datetime_str':
                record_value = record.datetime_str
            elif field == 'visit_type':
                record_value = record.visit_type
            else:
                continue

            if not record_value:
                continue

            if operator == 'eq':
                if str(record_value) == str(value):
                    filtered.append(record)
            elif operator == 'gt':
                if field == 'number' and int(record_value) > int(value):
                    filtered.append(record)
                elif field == 'datetime_str' and str(record_value) > str(value):
                    filtered.append(record)
            elif operator == 'lt':
                if field == 'number' and int(record_value) < int(value):
                    filtered.append(record)
                elif field == 'datetime_str' and str(record_value) < str(value):
                    filtered.append(record)
            elif operator == 'contains':
                if str(value).lower() in str(record_value).lower():
                    filtered.append(record)

        return filtered

    def iterate_by_type(self, visit_type: str) -> Iterator[VisitRecord]:
        for record in self._records:
            if record.visit_type == visit_type:
                yield record

    def iterate_by_date_range(self, start_date: str, end_date: str) -> Iterator[VisitRecord]:
        for record in self._records:
            if start_date <= record.datetime_str <= end_date:
                yield record

    @staticmethod
    def validate_visit_type(visit_type: str) -> bool:
        valid_types = ['кредит', 'вклад', 'платеж', 'консультация', 'ипотека', 'счёт']
        return visit_type.lower() in valid_types

    @staticmethod
    def get_valid_types() -> List[str]:
        return ['кредит', 'вклад', 'платеж', 'консультация', 'ипотека', 'счёт']

    def add_new_visit(self, full_name: str, datetime_str: str, visit_type: str) -> VisitRecord:
        next_num = max([r.number for r in self._records] + [0]) + 1
        new_record = VisitRecord(next_num, full_name, datetime_str, visit_type)
        self.add(new_record)
        return new_record

    def demonstrate_operations(self):
        print("\n" + "Обработка CSV-файла. Сортировка и фильтрация")

        self.read_from_file()

        if not self._records:
            print("Нет данных для обработки")
            return

        # Демонстрация итератора
        print("\nОбработка CSV. Демонстрация итератора\nПервые 3 записи через итератор:")
        for i, record in enumerate(self):
            if i >= 3:
                break
            print(f"  {record}")

        # Демонстрация доступа по индексу
        print("\nОбработка CSV.Демонстрация доступа по индексу")
        print(f"Первая запись: {self[0]}")
        print(f"Последняя запись: {self[-1]}")

        # Демонстрация генераторов
        print("\nОбработка CSV. Демонстрация генератора (по типу 'консультация')")
        for record in self.iterate_by_type('консультация'):
            print(f"  {record}")
            break  # показываем только первую

        # Демонстрация repr
        print(f"\nОбработка CSV.Демонстрация repr")
        print(f"repr коллекции: {repr(self)}")
        print(f"repr записи: {repr(self[0])}")

        # Сортировки
        sorted_by_name = self.sort_by_string_field('full_name')
        self.display_data(sorted_by_name, " Сортировка по ФИО (А-Я)")

        sorted_by_name_desc = self.sort_by_string_field('full_name', reverse=True)
        self.display_data(sorted_by_name_desc, " Сортировка по ФИО (Я-А)")

        sorted_by_num = self.sort_by_numeric_field('number')
        self.display_data(sorted_by_num, " Сортировка по номеру (возрастание)")

        sorted_by_num_desc = self.sort_by_numeric_field('number', reverse=True)
        self.display_data(sorted_by_num_desc, " Сортировка по номеру (убывание)")

        # Фильтрация
        print("\n" + "Обработка CSV. Фильтрация по критериям")

        consultation_visits = self.filter_by_criteria('visit_type', 'консультация', 'eq')
        self.display_data(consultation_visits, "Посещения с типом 'консультация'")

        visits_gt_5 = self.filter_by_criteria('number', 5, 'gt')
        self.display_data(visits_gt_5, "Посещения с номером > 5")

        visits_with_ov = self.filter_by_criteria('full_name', 'ов', 'contains')
        self.display_data(visits_with_ov, "Посещения с ФИО, содержащими 'ов'")

        visits_after_date = self.filter_by_criteria('datetime_str', '2026-03-16', 'gt')
        self.display_data(visits_after_date, "Посещения после 2026-03-16")


# Функции для работы с директорией (оставлены без изменений)
def count_files_in_directory(directory_path):
    try:
        if not os.path.exists(directory_path):
            return 0, f"Директория '{directory_path}' не существует!"
        if not os.path.isdir(directory_path):
            return 0, f"'{directory_path}' не является директорией!"
        items = os.listdir(directory_path)
        files = [item for item in items if os.path.isfile(os.path.join(directory_path, item))]
        return len(files), None
    except PermissionError:
        return 0, f"Нет прав доступа к директории '{directory_path}'"
    except Exception as e:
        return 0, f"Ошибка при подсчете файлов: {e}"


def check_file_in_directory(directory_path, filename):
    try:
        if not os.path.exists(directory_path):
            print(f"Директория '{directory_path}' не существует!")
            return False, None
        if not os.path.isdir(directory_path):
            print(f"'{directory_path}' не является директорией!")
            return False, None
        full_path = os.path.join(directory_path, filename)
        if os.path.isfile(full_path):
            return True, full_path
        else:
            print(f"Файл '{filename}' не найден в директории '{directory_path}'")
            return False, full_path
    except PermissionError:
        print(f"Нет прав доступа к директории '{directory_path}'")
        return False, None
    except Exception as e:
        print(f"Ошибка при проверке: {e}")
        return False, None


def demonstrate_directory_work():
    print("Проверка наличия CSV-файла в директории")
    user_dir = input("\nВведите путь к директории (или нажмите Enter для пропуска): ").strip()
    if not user_dir:
        print("Путь не указан. Будут сгенерированы примерные данные.")
        return None
    files_count, error_msg = count_files_in_directory(user_dir)
    if error_msg:
        print(error_msg)
    else:
        print(f"Количество файлов в директории: {files_count}")
    filename = input("Введите имя файла для проверки с указанием формата файла .csv: ").strip()
    if not filename:
        print("Имя файла не указано. Будут сгенерированы примерные данные.")
        return None
    file_exists, full_path = check_file_in_directory(user_dir, filename)
    if file_exists:
        print(f"Файл найден: {full_path}")
        return full_path
    else:
        print(f"Файл '{filename}' отсутствует в директории '{user_dir}'")
        print("Будут сгенерированы примерные данные.")
        return None


def add_new_visits(collection: BankVisitsCollection):
    print("Добавление новых записей")

    while True:
        print("\nДобавление новой записи:")
        fio = input("Введите ФИО (или 'стоп' для завершения): ").strip()
        if fio.lower() == 'стоп':
            break
        datetime_str = input("Введите дату и время (ДД.ММ.ГГГГ ЧЧ:ММ): ").strip()
        visit_type = input("Введите тип обращения (кредит/вклад/платеж/консультация): ").strip()

        # Валидация через статический метод
        if not BankVisitsCollection.validate_visit_type(visit_type):
            print(f"Неизвестный тип обращения. Допустимые типы: {BankVisitsCollection.get_valid_types()}")
            continue

        new_record = collection.add_new_visit(fio, datetime_str, visit_type)
        print(f"Запись №{new_record.number} добавлена!")

        continue_add = input("\nДобавить еще? (да/нет): ").strip().lower()
        if continue_add != 'да':
            break

    if len(collection) > 0:
        if input("\nСохранить изменения в файл? (да/нет): ").strip().lower() == 'да':
            filename = input("Имя файла для сохранения (Enter для текущего файла): ").strip()
            if not filename:
                filename = collection._filename
            collection.save_to_file(filename)


def main():
    print("Лабораторная работа №4. Работа с классами")
    print("Вариант 7: История посещений банка")

    found_file_path = demonstrate_directory_work()

    if found_file_path:
        file_to_use = found_file_path
        print(f"\nИспользуем найденный файл: {file_to_use}")
        collection = BankVisitsCollection(file_to_use, use_generated_data=False)
    else:
        print(f"\nФайл не указан. Генерируем примерные данные...")
        collection = BankVisitsCollection(use_generated_data=True)

    collection.demonstrate_operations()

    if len(collection) > 0:
        if input("\nХотите добавить новые записи? (да/нет): ").strip().lower() == 'да':
            add_new_visits(collection)
    else:
        print("Нет данных для обработки")

    print("\nОбработка CSV успешно завершена!")


if __name__ == "__main__":
    main()def greet(name): return f'Hello {name}'
print(greet('World'))
