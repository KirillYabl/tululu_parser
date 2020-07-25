# Tululu parser

This code is the console parser [tululu.org](http://tululu.org/) - a free library with electronic books. 

### How to install

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
    
### How to use

Open command line (in windows `Win+R` and write `cmd` and `Ok`). Go to directory with program or write in cmd:

```sh
python parse_tululu_category.py
```

You can use next params with program:

`--start_page` - Category has many pages of books, this param specifies the start page of the parsing. `default=1`

`--end_page` - End page for parsing, inclusive. `default=1`

`--category_id` - Id of books category. `default=55` (science fiction).
You can get category_id from [tululu.org](http://tululu.org/), the page with books category looks like `http://tululu.org/l{category_id}`

`--dest_folder` - Folder where text files and images will be created. The folder will be created if it doesn't exist.

`--skip_imgs` - Flag, if set, then images will not be saved.

`--skip_txt` - Flag, if set, then txt files will not be saved.

`--json_path` - The file name or path to the file where the parsing result will be written. 
If the file name does not exist, it will be created. If the folder in the file path does not exist, an error occurs.
File have next structure:
```json
[
    {
        "title": "BOOK_TITLE",
        "author": "AUTHOR",
        "image_src": "IMAGE_FILEPATH",
        "book_path": "BOOK_FILEPATH",
        "comments": ["COMMENT", ..., "COMMENT"],
        "genres": ["GENRE", ..., "GENRE"]
    },
    ...,
    {
        "title": "BOOK_TITLE",
        "author": "AUTHOR",
        "image_src": "IMAGE_FILEPATH",
        "book_path": "BOOK_FILEPATH",
        "comments": ["COMMENT", ..., "COMMENT"],
        "genres": ["GENRE", ..., "GENRE"]
    }
]
```

`--help` - Program description and help

For example, this command will analyze pages 2 through 6, and only images will be saved. A new data folder will be created if it does not exist.
```sh
python parse_tululu_category --start_page 2 --end_page 6 --skip_txt --dest_folder data
```

### References

- [tululu.org](http://tululu.org/)

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
