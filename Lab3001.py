import os
import csv
from datetime import datetime
import shutil

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
        # Проверка директории
        if not os.path.exists(directory_path):
            print(f"Директория '{directory_path}' не существует!")
            return False, None

        if not os.path.isdir(directory_path):
            print(f"'{directory_path}' не является директорией!")
            return False, None

        # Ввод полного пути к файлу
        full_path = os.path.join(directory_path, filename)

        # Проверка существования файла
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

    # Ввод пути к директории
    user_dir = input("\nВведите путь к директории (или нажмите Enter для пропуска): ").strip()
    if not user_dir:
        print("Путь не указан. Будут сгенерированы примерные данные.")
        return None

    # Подсчет количества файлов в директории
    files_count, error_msg = count_files_in_directory(user_dir)
    if error_msg:
        print(error_msg)
    else:
        print(f"Количество файлов в директории: {files_count}")

    # Ввод имени файла для проверки
    filename = input("Введите имя файла для проверки с указанием формата файла .csv: ").strip()
    if not filename:
        print("Имя файла не указано. Будут сгенерированы примерные данные.")
        return None

    # Проверка наличия файла
    file_exists, full_path = check_file_in_directory(user_dir, filename)

    if file_exists:
        print(f"Файл найден: {full_path}")
        return full_path
    else:
        print(f"Файл '{filename}' отсутствует в директории '{user_dir}'")
        print("Будут сгенерированы примерные данные.")
        return None


class BankVisits:
    def __init__(self, filename='data.csv', use_generated_data=False):
        self.filename = filename
        self.use_generated_data = use_generated_data
        self.data = []  # Список словарей с данными
        self.headers = ['№', 'ФИО', 'Дата и время', 'Тип обращения']
        self.is_loaded = False  # Флаг для отслеживания загрузки

    def parse_csv_line(self, line):
        if line.startswith('\ufeff'):
            line = line[1:]
        # Разделение по точке с запятой
        return [item.strip() for item in line.split(';')]

    def read_from_file(self, custom_path=None):
        # Генерация данных
        if self.use_generated_data:
            print(f"\nГенерируем примерные данные...")
            self.data = self.generate_sample_data()
            print(f"Сгенерировано записей: {len(self.data)}")
            self.is_loaded = True
            return

        file_to_read = custom_path if custom_path else self.filename

        # Если данные уже загружены, повторно не загружаются
        if self.is_loaded:
            return

        try:
            with open(file_to_read, 'r', encoding='utf-8-sig') as file:
                # Читаем заголовки
                header_line = file.readline().strip()
                headers = self.parse_csv_line(header_line)

                # Проверяем соответствие заголовков
                expected_headers = ['№', 'ФИО', 'Дата и время', 'Тип обращения']
                if headers != expected_headers:
                    header_mapping = {}
                    for i, expected in enumerate(expected_headers):
                        if i < len(headers):
                            header_mapping[headers[i]] = expected
                else:
                    header_mapping = {h: h for h in headers}

                # Чтение данных
                self.data = []
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue

                    values = self.parse_csv_line(line)

                    # Словарь записи
                    record = {}
                    for i, header in enumerate(headers):
                        if i < len(values):
                            mapped_header = header_mapping.get(header, header)
                            record[mapped_header] = values[i]

                    if '№' in record:
                        try:
                            record['№'] = int(record['№'])
                        except:
                            record['№'] = line_num

                    self.data.append(record)

            print(f"\nДанные успешно загружены из файла '{file_to_read}'")
            print(f"Загружено записей: {len(self.data)}")
            self.is_loaded = True

        except FileNotFoundError:
            print(f"\nФайл '{file_to_read}' не найден.")
            print(f"Генерируем примерные данные...")
            self.data = self.generate_sample_data()
            print(f"Сгенерировано записей: {len(self.data)}")
            self.is_loaded = True
        except Exception as e:
            print(f"\nОшибка при чтении файла: {e}")
            print(f"Генерируем примерные данные...")
            self.data = self.generate_sample_data()
            print(f"Сгенерировано записей: {len(self.data)}")
            self.is_loaded = True

    def generate_sample_data(self):
        sample_data = [
            {'№': 1, 'ФИО': 'Иванчук И.И.', 'Дата и время': '2026-04-15 10:30', 'Тип обращения': 'консультация'},
            {'№': 2, 'ФИО': 'Петренко П.П.', 'Дата и время': '2026-04-15 11:45', 'Тип обращения': 'ипотека'},
            {'№': 3, 'ФИО': 'Сидоров С.С.', 'Дата и время': '2026-04-15 09:15', 'Тип обращения': 'вклад'},
            {'№': 4, 'ФИО': 'Андрейченко А.А.', 'Дата и время': '2026-04-16 14:20', 'Тип обращения': 'консультация'},
            {'№': 5, 'ФИО': 'Бориско Б.Б.', 'Дата и время': '2026-04-16 16:30', 'Тип обращения': 'консультация'},
            {'№': 6, 'ФИО': 'Васильева В.В.', 'Дата и время': '2026-04-17 12:00', 'Тип обращения': 'консультация'},
            {'№': 7, 'ФИО': 'Григорьевич Г.Г.', 'Дата и время': '2026-04-17 13:45', 'Тип обращения': 'счёт'},
            {'№': 8, 'ФИО': 'Дмитриенко Д.Д.', 'Дата и время': '2026-04-18 10:00', 'Тип обращения': 'консультация'},
            {'№': 9, 'ФИО': 'Егороц Е.Е.', 'Дата и время': '2026-04-18 11:30', 'Тип обращения': 'консультация'},
            {'№': 10, 'ФИО': 'Жуковский Ж.Ж.', 'Дата и время': '2026-04-18 15:15', 'Тип обращения': 'вклад'}
        ]
        return sample_data

    def save_to_file(self, filename=None):
        save_filename = filename or self.filename

        try:
            with open(save_filename, 'w', encoding='utf-8-sig', newline='') as file:
                # Запись заголовков через ;
                file.write(';'.join(self.headers) + '\n')

                # Запись данных
                for record in self.data:
                    line = ';'.join([
                        str(record.get('№', '')),
                        record.get('ФИО', ''),
                        record.get('Дата и время', ''),
                        record.get('Тип обращения', '')
                    ])
                    file.write(line + '\n')

            print(f"Данные успешно сохранены в файл '{save_filename}'")

        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")

    def display_data(self, data=None, title="Данные"):
        if data is None:
            data = self.data

        if not data:
            print("Нет данных для отображения")
            return

        print(f"\n{title}:")
        print(f"{'№':<5} {'ФИО':<25} {'Дата и время':<20} {'Тип обращения':<20}")

        for record in data:
            print(f"{record.get('№', 'N/A'):<5} {record.get('ФИО', 'N/A'):<25} {record.get('Дата и время', 'N/A'):<20} {record.get('Тип обращения', 'N/A'):<20}")

        print(f"\nВсего записей: {len(data)}")

    def sort_by_string_field(self, field='ФИО', reverse=False):
        if not self.data or field not in self.data[0]:
            return self.data
        return sorted(self.data, key=lambda x: str(x.get(field, '')), reverse=reverse)

    def sort_by_numeric_field(self, field='№', reverse=False):
        if not self.data or field not in self.data[0]:
            return self.data
        return sorted(self.data, key=lambda x: int(x.get(field, 0)), reverse=reverse)

    def filter_by_criteria(self, field, value, operator='eq'):
        filtered = []

        for record in self.data:
            record_value = record.get(field, '')

            if not record_value:
                continue

            if operator == 'eq':  # равно
                if str(record_value) == str(value):
                    filtered.append(record)
            elif operator == 'gt':  # больше
                if field == '№' and int(record_value) > int(value):
                    filtered.append(record)
                elif field == 'Дата и время' and str(record_value) > str(value):
                    filtered.append(record)
            elif operator == 'lt':  # меньше
                if field == '№' and int(record_value) < int(value):
                    filtered.append(record)
                elif field == 'Дата и время' and str(record_value) < str(value):
                    filtered.append(record)
            elif operator == 'contains':  # содержит подстроку
                if str(value).lower() in str(record_value).lower():
                    filtered.append(record)

        return filtered

    def demonstrate_operations(self):
        print("Обработка CSV-файла. Сортировка и фильтрация")

        # Чтение данных из файла
        self.read_from_file()

        if not self.data:
            print("Нет данных для обработки")
            return

        # Сортировка по строковому полю (ФИО)
        sorted_by_name = self.sort_by_string_field('ФИО')
        self.display_data(sorted_by_name, "Сортировка по ФИО (А-Я)")

        sorted_by_name_desc = self.sort_by_string_field('ФИО', reverse=True)
        self.display_data(sorted_by_name_desc, "Сортировка по ФИО (Я-А)")

        # Сортировка по числовому полю (№)
        sorted_by_num = self.sort_by_numeric_field('№')
        self.display_data(sorted_by_num, "Сортировка по номеру (возрастание)")

        sorted_by_num_desc = self.sort_by_numeric_field('№', reverse=True)
        self.display_data(sorted_by_num_desc, "Сортировка по номеру (убывание)")

        # Фильтрация по критерию
        print("Фильтрация по критериям")

        # Фильтр по типу обращения
        consultation_visits = self.filter_by_criteria('Тип обращения', 'консультация', 'eq')
        self.display_data(consultation_visits, "Посещения с типом 'консультация'")

        # Фильтр по номеру > 5
        visits_gt_5 = self.filter_by_criteria('№', 5, 'gt')
        self.display_data(visits_gt_5, "Посещения с номером > 5")

        # Фильтр по ФИО, содержащим 'ов'
        visits_with_ov = self.filter_by_criteria('ФИО', 'ов', 'contains')
        self.display_data(visits_with_ov, "Посещения с ФИО, содержащими 'ов'")

        # Фильтр по дате
        visits_after_date = self.filter_by_criteria('Дата и время', '2026-03-16', 'gt')
        self.display_data(visits_after_date, "Посещения после 2026-03-16")


def add_new_visits(bank_visits):
    print("Добавление новых записей")

    while True:
        print("\nДобавление новой записи:")

        # Определяем следующий номер
        next_num = max([record.get('№', 0) for record in bank_visits.data] + [0]) + 1

        # Ввод ФИО
        fio = input("Введите ФИО (или 'стоп' для завершения): ").strip()
        if fio.lower() == 'стоп':
            break

        # Ввод даты и времени
        datetime_str = input("Введите дату и время (ДД.ММ.ГГГГ ЧЧ:ММ): ").strip()

        # Ввод типа обращения
        visit_type = input("Введите тип обращения (кредит/вклад/платеж/консультация): ").strip()

        # Создаем новую запись
        new_record = {
            '№': next_num,
            'ФИО': fio,
            'Дата и время': datetime_str,
            'Тип обращения': visit_type
        }

        # Добавляем в данные
        bank_visits.data.append(new_record)
        print(f"Запись №{next_num} добавлена!")

        # Спрашиваем, продолжать ли
        continue_add = input("\nДобавить еще? (да/нет): ").strip().lower()
        if continue_add != 'да':
            break

    # Сохраняем обновленные данные
    if len(bank_visits.data) > 0:
        if input("\nСохранить изменения в файл? (да/нет): ").strip().lower() == 'да':
            filename = input("Имя файла для сохранения (Enter для текущего файла): ").strip()
            if not filename:
                filename = bank_visits.filename
            bank_visits.save_to_file(filename)


def main():
    print("Лабораторная работа №3. Работа с файлами")
    print("Вариант 7: История посещений банка")

    # Проверка наличия файла в директории
    found_file_path = demonstrate_directory_work()

    # Работа с CSV файлом
    if found_file_path:
        file_to_use = found_file_path
        print(f"\nИспользуем найденный файл: {file_to_use}")
        bank_visits = BankVisits(file_to_use, use_generated_data=False)
    else:
        print(f"\nФайл не указан. Генерируем примерные данные...")
        bank_visits = BankVisits(use_generated_data=True)

    bank_visits.demonstrate_operations()

    # Добавление новых данных
    if bank_visits.data:
        if input("\nХотите добавить новые записи? (да/нет): ").strip().lower() == 'да':
            add_new_visits(bank_visits)
    else:
        print("Нет данных для обработки")

    print("\n")
    print("Обработка CSV успешно завершена!")


if __name__ == "__main__":
    main()