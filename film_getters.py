from aiohttp import ClientSession
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import json
import typing as tp
import os


class Film(ABC):
    """
    Класс для фильма, от которого будут наследоваться классы, получающие информацию
    о фильме с Кинопоиска и Википедии
    """
    @abstractmethod
    async def get_film_info(self, session: ClientSession, film_name: str) -> tp.Dict[str, tp.Any]:
        pass


class Kinopoisk(Film):  # type: ignore
    async def get_film_info(self, session: ClientSession, film_name: str) -> tp.Dict[str, tp.Any]:
        """
        Получаем ссылку на фильм с сайта kinopoisk.ru

        :param session: cессия для асинхронного взаимодействия
        :param film_name: название фильма
        :return: результат запроса - словарь, в котором содержится ссылка на фильм
        """

        curr_params = {
            'key': os.environ.get('GOOGLE_SEARCH_KEY'),
            'cx': os.environ.get('GOOGLE_SEARCH_KINOPOISK'),
            'q': film_name
        }

        async with session.get(url=os.environ.get('GOOGLE_SEARCH_URL'),
                               params=curr_params) as response:
            result = await response.text()

        return {'film_link': json.loads(result)['items'][0]['link']}


class Wiki(Film):  # type: ignore
    async def get_film_info(self, session: ClientSession, film_name: str) -> tp.Dict[str, tp.Any]:
        """
        Получает информацию о фильме с Википедии (wikipedia.org).

        :param session: cессия для асинхронного взаимодействия
        :param film_name: название фильма
        :return: результат запроса - словарь, в котором содержится информация о фильме и
        """

        curr_params = {
            'key': os.environ.get('GOOGLE_SEARCH_KEY'),
            'cx': os.environ.get('GOOGLE_SEARCH_WIKI'),
            'q': film_name
        }

        async with session.get(url=os.environ.get('GOOGLE_SEARCH_URL', ''), params=curr_params) as response:
            result = await response.text()

        link = json.loads(result)['items'][0]['link']

        async with session.get(url=link) as response:
            wiki_html_page = await response.text()

        return {'picture': self.get_picture(wiki_html_page),
                'text_info': self.get_text_info(wiki_html_page)}

    @staticmethod
    def get_text_info(html_page: str) -> str:
        """
        Получаем текстовое описание фильма с Википедии
        :param html_page: HTML-версия страницы с Википедии
        :return: Описание фильма, полученное с этой страницы
        """
        curr_soup = BeautifulSoup(html_page, features='html.parser')
        curr_div = curr_soup.html.body.findAll('div', {'id': 'mw-content-text'})[0]
        return curr_div.findAll('p', {'class': None})[0].get_text()

    @staticmethod
    def get_picture(html_page: str) -> str:
        """
        Получаем постер фильма с Википедии
        :param html_page: HTML-версия страницы с Википедии
        :return: Постер фильма, полученное с этой страницы
        """
        curr_soup = BeautifulSoup(html_page, features='html.parser')
        curr_link = curr_soup.html.body.findAll('a', {'class': 'image'})[0]
        return curr_link.findAll('img')[0]['src'][2:]
