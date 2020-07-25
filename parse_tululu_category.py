import requests
import os
import logging
import urllib
import json
import argparse

from bs4 import BeautifulSoup
import pathvalidate
from tqdm import tqdm

logger = logging.getLogger(__name__)


class RedirectError(requests.exceptions.BaseHTTPError):
    pass


def tululu_raise_for_status(response):
    response.raise_for_status()
    group_or_status_code = response.status_code // 100
    is_redirect = group_or_status_code == 3
    if is_redirect:
        raise RedirectError


def download_file(url, filename, folder):
    """Download file from url.

    :param url: str, url with file.
    :param filename: str, name of file (with extension).
    :param folder: str, folder to save (if it does not exist, a folder will be created).
    :return: str, path to the file where the file will be saved.
    """
    response = requests.get(url, allow_redirects=False)
    tululu_raise_for_status(response)

    sanitized_folder = pathvalidate.sanitize_filepath(folder)
    os.makedirs(sanitized_folder, exist_ok=True)

    sanitized_file_name = pathvalidate.sanitize_filename(filename)

    filepath = os.path.join(folder, sanitized_file_name)
    sanitized_filepath = pathvalidate.sanitize_filepath(filepath)
    with open(sanitized_filepath, 'wb') as f:
        f.write(response.content)

    return sanitized_filepath


def get_tululu_category_page_links(category_id, page_num):
    """Get all book pages for a category from http://tululu.org

    :param category_id: int or str, id of category
    :param page_num: int or str, book page number
    :return: list, book page url list
    """
    main_site_url = 'http://tululu.org'
    urls = []
    category_page_url = urllib.parse.urljoin(main_site_url, f'l{category_id}/{page_num}')
    response = requests.get(category_page_url + '/', allow_redirects=False)
    tululu_raise_for_status(response)

    soup = BeautifulSoup(response.text, 'lxml')

    books = soup.select('div#content table.d_book')
    for book_table in books:
        url_name = book_table.select_one('a')['href']
        url = urllib.parse.urljoin(main_site_url, url_name)
        urls.append(url)

    return urls


def parse_book(book_url, books_folder_name, images_folder_name, skip_txt, skip_imgs):
    """Parsing a book from http://tululu.org

    :param book_url: str, book url
    :param books_folder_name: str, name of the folder in which the book will be saved
    :param images_folder_name: str, name of the folder where the book cover will be saved
    :param skip_txt: bool, if True text of the the book is not saved
    :param skip_imgs: bool, if True cover of the book is not saved
    :return: dict, dict with book params
    """
    main_site_url = 'http://tululu.org'
    book_id = book_url.split('/')[-2][1:]
    response = requests.get(book_url, allow_redirects=False)
    tululu_raise_for_status(response)
    soup = BeautifulSoup(response.text, 'lxml')

    book_title, author = soup.select_one('h1').text.split('::')
    book_title = book_title.strip()
    author = author.strip()

    image_src = soup.select_one('div.bookimage img')['src']
    image_path = urllib.parse.urljoin(main_site_url, image_src)
    image_filename = image_path.split('/')[-1]

    image_filepath = ''
    if not skip_imgs:
        image_filepath = download_file(
            url=image_path,
            filename=image_filename,
            folder=images_folder_name
        )

    book_filepath = ''
    if not skip_txt:
        book_filepath = download_file(
            url=f'http://tululu.org/txt.php?id={book_id}',
            filename=f'{book_id}. {book_title}.txt',
            folder=books_folder_name
        )

    comments_soup = soup.select('div.texts')
    comments = []
    for comment in comments_soup:
        comments.append(comment.select_one('span').text)

    genres_soup = soup.select('span.d_book a')
    genres = []
    for genre in genres_soup:
        genres.append(genre.text)

    book_info = {
        'title': book_title,
        'author': author,
        'image_src': image_filepath,
        'book_path': book_filepath,
        'comments': comments,
        'genres': genres
    }

    return book_info


def create_argparser():
    description = 'This code is the console parser tululu.org - a free library with electronic books.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--start_page', default=1, type=int, help='Start parsing page.')
    parser.add_argument('--end_page', default=1, type=int, help='End parsing page, inclusive.')
    parser.add_argument('--category_id', default=55, type=int, help='Id of books category.')
    parser.add_argument('--dest_folder', default='data', type=str,
                        help='The folder in which text files and images will be created.')
    parser.add_argument('--skip_imgs', action='store_const', const=True, default=False,
                        help='if set, then images will not be saved.')  # flag
    parser.add_argument('--skip_txt', action='store_const', const=True, default=False,
                        help='if set, then txt files will not be saved.')  # flag
    # argparse will validate --json_path because this type of argument will try to check file creation immediately
    json_help = 'File name or file path to the file in which the result of the parsing will be written. If the file name does not exist, it will be created. If the folder in file path does not exist, an error will occur.'
    parser.add_argument('--json_path', default='books_info.json', type=argparse.FileType(mode='w'), help=json_help)

    return parser


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s  %(message)s', level=logging.INFO)

    parser = create_argparser()
    namespace = parser.parse_args()

    books_folder_name = os.path.join(namespace.dest_folder, 'books')
    image_folder_name = os.path.join(namespace.dest_folder, 'images')
    site = 'http://tululu.org'

    end_page = max(namespace.start_page, namespace.end_page) + 1

    urls = []
    for book_page in range(namespace.start_page, end_page):
        urls += get_tululu_category_page_links(namespace.category_id, book_page)
    logger.info(f'{len(urls)} books were founded')

    books_info = []
    redirect_errors = 0
    for url in tqdm(urls):
        try:
            book_info = parse_book(
                book_url=url,
                books_folder_name=books_folder_name,
                images_folder_name=image_folder_name,
                skip_txt=namespace.skip_txt,
                skip_imgs=namespace.skip_imgs
            )
            books_info.append(book_info)
        except RedirectError:
            redirect_errors += 1

    json.dump(books_info, namespace.json_path, ensure_ascii=False)

    logger.info(f'{len(books_info)} books were downloaded')
    logger.info(f'{redirect_errors} file upload redirection exceptions')
