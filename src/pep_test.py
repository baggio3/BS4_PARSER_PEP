import requests_cache
from bs4 import BeautifulSoup
# from urllib.parse import urljoin
import re
# from pathlib import Path
from tqdm import tqdm
from prettytable import PrettyTable


PEP_URL = 'https://peps.python.org/'


def pep():
    session = requests_cache.CachedSession()
    session.cache.clear()
    response = session.get(PEP_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    num_section = soup.find('section', attrs={'id': 'numerical-index'})
    table_tag = num_section.find('table', attrs={'class': 'pep-zero-table docutils align-default'})
    body_tag = table_tag.find('tbody')
    tr_tag = body_tag.find_all('tr', attrs={'class': re.compile(r'row-(odd|even)')})
    results = [('status', 'pep number',  'PEP Title','authors', 'Python version')]
    for pep in tqdm(tr_tag):
        status_tag = pep.find('abbr')
        status_info = status_tag.text
        version_tag = pep.find('a', attrs={'class': 'pep reference internal'})
        short_link = version_tag['href']
        title_pep = version_tag['title']
        td_tags = pep. find_all('td')
        author_name = td_tags[3].text
        if td_tags[-1].text:
            working_python_version = td_tags[-1].text
        else:
            working_python_version = ''
        results.append([status_info, short_link, title_pep, author_name, working_python_version])
    return results
    

if __name__ == '__main__':
    pep_table = PrettyTable()
    pep_table.field_names = pep()[0]
    pep_table.add_rows(pep()[1:])
    print(pep_table)
    

        # version_a_tag = find_tag(section, 'a')
        # href = version_a_tag['href']
        # version_link = urljoin(whats_new_url, href)
        # response = get_response(session, version_link)
        # if response is None:
        #     continue
        # soup = BeautifulSoup(response.text, 'lxml')
        # h1 = find_tag(soup, 'h1')
        # dl = find_tag(soup, 'dl')
        # dl_text = dl.text.replace('\n', ' ')
        # results.append([version_link, h1.text, dl_text])




    # for section in main_section_tag.find_all('section'):
    #     if section.find('table', attrs={'class': 'pep-zero-table docutils align-default'}):
    #         table_tag = section.find('table', attrs={'class': 'pep-zero-table docutils align-default'})
    #         for tag in table_tag.find_all('tr', attrs={'class': re.compile(r'row-(odd|even)')}):
    #             # print(type(tag))
    #             # tr_tag = tag.find_all('tr', attrs={'class': re.compile(r'row-(odd|even)')})
    #             td_tag = tag.find_all('td')

    #             # print(td_tag)

    #             # status_tag = td_tag.find('title')
    #             link_tag = td_tag.find('href')
    #             # pep_num = td_tag.find('title')

    #             print(link_tag)
    #         # print(table_tag) 
    #     # section_tags = section.find('section')
    #     # table_tag = section_tags.find(
    # #         'div',
    # #         attrs={'class': 'table-wrapper'}
    # #     )
    # #     tr_class = table_tag.find('tr', attrs={'class': re.compile(r'row-(odd|even)')})
    # #     print(*tr_class)