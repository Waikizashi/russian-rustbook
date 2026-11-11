# Сборка и проверка

## Требования

- Python 3.11.8+.
- Pandoc 3.x для проверки Markdown и сборки EPUB.
- mdBook 0.5.4 для сайта.
- EPUBCheck и Java 17+ для проверки стандарта электронного издания.
- Дополнительно PyMuPDF для PDF и Rust 1.85+ для программ дополнения.

Установка генератора сайта: `cargo install mdbook --version 0.5.4 --locked`. В CI используется проверенный SHA-256 официального бинарного релиза mdBook.

В CI Pandoc 3.13 и EPUBCheck 5.4.0 устанавливаются из официальных архивов GitHub с закреплёнными SHA-256, без зависимости от зеркал Ubuntu. На Linux x86-64 ту же установку можно выполнить локально (Java должна быть установлена отдельно):

```sh
python3 scripts/install_ebook_tools.py
export PATH="$PWD/.tools/bin:$PATH"
```

## Основная книга

```sh
python3 scripts/check_book.py
python3 scripts/check_language.py
python3 -m unittest discover -s tests -v
mdbook build
python3 scripts/build_ebooks.py
python3 scripts/verify_epub.py
epubcheck dist/The_Rust_Programming_Language_RU_2026.epub
```

Первый скрипт автоматически сравнивает 111 файлов, 542 заголовка и 958 блоков кода/вывода с контрольными данными официального commit из `upstream.json`. Ссылки и исходные изображения проверяются локально. Завершающий перевод строки у кодового блока нормализуется при сериализации Markdown; содержимое строк сохраняется.

Сайт создаётся в `book/`. EPUB, единый Markdown и ZIP Markdown с изображениями — в `dist/`; пользовательские файлы копируются в `downloads/`.

## PDF

```sh
python3 -m pip install 'PyMuPDF==1.26.6'
python3 scripts/build_pdf.py
```

PDF строится из того же EPUB. Переносятся оглавление и ссылки, добавляются номера страниц, автоматически проверяется выход текста за границы страницы. Предварительные изображения для визуальной проверки находятся в `dist/pdf-preview/`.

## Дополнение

```sh
cd extras/bits-bytes
python3 scripts/check.py
cargo test --workspace --all-targets --locked
python3 scripts/run_examples.py
python3 scripts/run_examples.py --release
python3 scripts/prepare_book.py
mdbook build
```

Для общего сайта сборка дополнения размещается в `book/extras/bits-bytes/`. Исходники и нумерация основной книги сохраняются отдельно от дополнения.

После сборки обеих частей выполните `python3 scripts/check_site.py`: проверяются фактические пути и якоря сгенерированных HTML-файлов.

## GitHub Actions и публикация

`ci.yml` проверяет основную книгу, EPUB и код дополнения. `pages.yml` собирает обе части сайта и публикует их через GitHub Pages. Для Pages требуется выбрать GitHub Actions как источник в настройках репозитория.

`upstream.yml` по расписанию сравнивает текущий HEAD официального репозитория с `upstream.json` и сохраняет отчёт. Он не заменяет перевод автоматически. Содержательные изменения оригинала нужно проверить и перевести перед обновлением контрольных данных.

`release.yml` при теге `v*` публикует пользовательские файлы из `downloads/` и контрольные суммы в GitHub Releases. Создание репозитория, включение Pages и выпуск тега — отдельные действия; наличие workflow не означает, что они уже выполнены.
