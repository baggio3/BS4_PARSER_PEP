import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    # session = requests_cache.CachedSession()
    result = get_response(session, whats_new_url)
    if result is None:
        return
    soup = BeautifulSoup(result.text, 'lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    section_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    # В results добавили список, его содержимое станет заголовками
    # для prettytable.
    # Остальные данные будут добавляться к инициализированному списку.
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(section_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append([version_link, h1.text, dl_text])
    return results


def latest_version(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    # В results добавили список, его содержимое станет заголовками
    # для prettytable.
    # Остальные данные будут добавляться к инициализированному списку.
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append([link, version, status])
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    # session = requests_cache.CachedSession()
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    # Сформируйте путь до директории downloads.
    downloads_dir = BASE_DIR / 'downloads'
    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    num_section = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    table_tag = find_tag(num_section, 'table', attrs={'class': 'pep-zero-table docutils align-default'})
    body_tag = find_tag(table_tag, 'tbody')
    tr_tag = body_tag.find_all('tr', attrs={'class': re.compile(r'row-(odd|even)')})
    results = [('status', 'pep number',  'PEP Title', 'authors', 'Python version')]
    for pep in tqdm(tr_tag):
        status_tag = find_tag(pep, 'abbr')
        status_info = status_tag.text
        version_tag = find_tag(pep, 'a', attrs={'class': 'pep reference internal'})
        short_link = version_tag['href']
        full_link = urljoin(PEP_URL, short_link)
        title_pep = version_tag['title']
        td_tags = pep. find_all('td')
        author_name = td_tags[3].text
        if td_tags[-1].text:
            working_python_version = td_tags[-1].text
        else:
            working_python_version = ''
        results.append([status_info, full_link, title_pep, author_name, working_python_version])
    return results
    


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_version,
    'download': download,
    'pep': pep,
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы коммандной строки {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу')


if __name__ == '__main__':
    main()
