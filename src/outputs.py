import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    # чтобы не обращаться дважды к атрибуту объекта в условиях if, elif
    # сохраняю значение в переменную.
    output = cli_args.output
    # Если функция main.py вызывается с аргументом -p,
    # то данные выводятся в формате prettytable
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        # вывод данных в файл
        file_output(results, cli_args)
    # Если нет такого аргумента, то данные выводятся в "сыром" виде.
    else:
        default_output(results)


def default_output(results):
    for row in results:
        print(row)


def pretty_output(results):
    table = PrettyTable()
    # Для заголовков используем первый элемент списка.
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formated = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formated}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
