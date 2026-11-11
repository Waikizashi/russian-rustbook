# Отчёт о сборке The Rust Programming Language — русский перевод

Дата актуальности исходников и сборки: **30 сентября 2026 года**. Последние commit обоих репозиториев повторно проверены командой `git ls-remote origin HEAD` в день сборки.

- Официальный оригинал: https://github.com/rust-lang/book — `1500248d8f230566e4ec9f27fcbb8fe9e2898ab1` (commit от 2 сентября 2026 года).
- Основа русского перевода: https://github.com/rust-lang-ru/book — `1bec6512e7475b20919b6266dc8596ba71298ff9`.
- Версия, указанная в текущей книге: **Rust 1.98.0**, **edition 2024**.
- Авторы оригинала: Steve Klabnik, Carol Nichols, Chris Krycho и сообщество Rust.
- Это неофициальная русская сборка, подготовленная на основе существующего перевода с переводом новых и изменённых фрагментов. Оригинальные уведомления и лицензии MIT / Apache-2.0 включены в EPUB. Код, комментарии в коде и вывод программ оставлены на языке оригинала.

## Сопоставление

Официальное оглавление содержит **111 файлов глав, разделов и приложений**, в том числе **21 основную главу**. Относительно английских исходников, по которым выполнялся существующий русский перевод, **102 файла изменились**, **7 файлов главы об асинхронности отсутствовали**, **2 файла исходного текста не изменились**. Изменения включают как содержательные дополнения, так и заголовки, ссылки, номера глав и листингов. Это число файлов, а не число полностью переписанных глав.

Сохранён подходящий русский перевод неизменённых фрагментов. Новая глава об асинхронном программировании переведена полностью. В остальных частях вручную восстановлены и обновлены 460 блоков текста и заголовков; дополнительно синхронизированы технические имена, ссылки и номера листингов. Все блоки кода взяты из текущего официального оригинала, включая раскрытые включения из каталога `listings`.

Основные содержательные обновления:

- Новое предисловие Бек Рамбул; актуальные авторы, версия Rust и редакция 2024.
- Асинхронность: async/await, future, задачи, каналы, конкурентное ожидание, потоки значений, `Future`, `Stream`, `StreamExt`, `Pin` и `Unpin`, сочетание асинхронности с потоками выполнения.
- `let...else`, уточнения владения, присваивания и деструктуризации кортежных структур.
- Обновлённый пример игры: `rand` 0.10.1, `rand::rng`, `RngExt`, `random_range`.
- Обновлённые тесты и проект `minigrep`; итератор, возвращаемый из функции поиска; рабочие пространства Cargo с `resolver = "3"`.
- Небезопасный Rust: операторы `&raw const` / `&raw mut`, блоки `unsafe` внутри небезопасных функций, `unsafe extern`, отдельные безопасные функции FFI, `#[unsafe(no_mangle)]`, доступ к изменяемым статическим переменным, комментарии `SAFETY` и Miri.
- Совместимость типажей с `dyn`, возврат разных замыканий, завершение пула потоков через `Vec::drain`.

Перечисленные возможности являются новыми или изменёнными **относительно основы русского перевода**; это не утверждение, что все они впервые появились в Rust 1.98.

## Проверки EPUB

| Проверка | Результат |
|---|---|
| Официальный порядок глав и разделов | Все 111 файлов, без пропусков и перестановок |
| Внутренние заголовки | Все 542 заголовка; уровни и идентификаторы сопоставлены автоматически с текущим оригиналом |
| Код | Все 958 блоков посимвольно совпадают с раскрытыми текущими официальными примерами |
| Иллюстрации | Все 28 встроены в EPUB |
| Внутренние ссылки и ресурсы | Проверено 1117; битых ссылок 0 |
| Крупные английские фрагменты прозы | Автоматический поиск не выявил; код, имена собственные и юридические тексты исключены из проверки |
| ZIP, XML, manifest, spine | Проверки пройдены |
| UTF-8 и кириллица | Корректно извлекаются; 758678 кириллических символов в независимом импорте |
| Независимое открытие | Pandoc открыл EPUB; MuPDF также открыл и разбил книгу на 704 страниц при выбранном размере страницы |
| Визуальная проверка | Просмотрены страницы титула, установки и раздела о типажах async; кириллица, ссылки и код отображаются корректно |
| Оглавление | EPUB Navigation Document со всеми заголовками; дополнительное NCX для совместимости |
| DRM | Отсутствует |
| EPUBCheck | Не установлен в среде; результат EPUBCheck не заявляется |

Автоматические проверки не заменяют профессиональную редактуру перевода. На физических Kindle и в приложениях KOReader, Calibre, Apple Books и Google Play Books файл отдельно не тестировался. Использован обычный EPUB 3 с изменяемым размером текста, XHTML/CSS и дополнительным NCX. Для Kindle EPUB следует передавать через Send to Kindle; справка Amazon: https://kdp.amazon.com/en_US/help/topic/G200641240 .

PDF — дополнительная версия с фиксированной разбивкой на 704 страницы, 113 закладками оглавления и 921 перенесённой ссылкой. Просмотрены выборочные страницы; автоматическая проверка всех страниц не выявила текстовых фрагментов за границами страницы. Markdown поставляется также архивом вместе с иллюстрациями; для полностью автономного чтения Markdown распакуйте архив с сохранением каталога `img`.

## Файлы и контрольные суммы

- `The_Rust_Programming_Language_RU_2026.epub` — 1,476,830 байт; SHA-256 `bdbab387f01fdc644d871b16f9f30b4f5d1edd7a044c364fb2d1a90f3ec6ddc0`.
- `The_Rust_Programming_Language_RU_2026.md` — 2,150,009 байт; SHA-256 `9d14a1a9047caea26e6d530dcb9e7fc7ee25476cb69338e584b87da75c32e4f6`.
- `The_Rust_Programming_Language_RU_2026.pdf` — 8,976,352 байт; SHA-256 `8b5fa4b24176667cafcff6af8d2eafdc2b5da60b52fb41005a9cb95b1325a1ec`.
- `The_Rust_Programming_Language_RU_2026_Markdown.zip` — 1,299,084 байт; SHA-256 `bb33c2497574914a96f3a043502642867810bc3d01cacbc2d7dd58953fd3ed18`.

## Подробное сопоставление файлов

| Официальный файл | Файл русского перевода | Статус | Ручных блоков |
|---|---|---|---|
| `title-page.md` | `title-page.md` | Актуализирован | 2 |
| `foreword.md` | `foreword.md` | Актуализирован | 7 |
| `ch00-00-introduction.md` | `ch00-00-introduction.md` | Актуализирован | 5 |
| `ch01-00-getting-started.md` | `ch01-00-getting-started.md` | Актуализирован | 0 |
| `ch01-01-installation.md` | `ch01-01-installation.md` | Актуализирован | 7 |
| `ch01-02-hello-world.md` | `ch01-02-hello-world.md` | Актуализирован | 8 |
| `ch01-03-hello-cargo.md` | `ch01-03-hello-cargo.md` | Актуализирован | 2 |
| `ch02-00-guessing-game-tutorial.md` | `ch02-00-guessing-game-tutorial.md` | Актуализирован | 11 |
| `ch03-00-common-programming-concepts.md` | `ch03-00-common-programming-concepts.md` | Актуализирован | 1 |
| `ch03-01-variables-and-mutability.md` | `ch03-01-variables-and-mutability.md` | Актуализирован | 2 |
| `ch03-02-data-types.md` | `ch03-02-data-types.md` | Актуализирован | 15 |
| `ch03-03-how-functions-work.md` | `ch03-03-how-functions-work.md` | Актуализирован | 4 |
| `ch03-04-comments.md` | `ch03-04-comments.md` | Актуализирован | 0 |
| `ch03-05-control-flow.md` | `ch03-05-control-flow.md` | Актуализирован | 7 |
| `ch04-00-understanding-ownership.md` | `ch04-00-understanding-ownership.md` | Без изменений в английском источнике | 0 |
| `ch04-01-what-is-ownership.md` | `ch04-01-what-is-ownership.md` | Актуализирован | 6 |
| `ch04-02-references-and-borrowing.md` | `ch04-02-references-and-borrowing.md` | Актуализирован | 1 |
| `ch04-03-slices.md` | `ch04-03-slices.md` | Актуализирован | 5 |
| `ch05-00-structs.md` | `ch05-00-structs.md` | Актуализирован | 0 |
| `ch05-01-defining-structs.md` | `ch05-01-defining-structs.md` | Актуализирован | 5 |
| `ch05-02-example-structs.md` | `ch05-02-example-structs.md` | Актуализирован | 3 |
| `ch05-03-method-syntax.md` | `ch05-03-method-syntax.md` | Актуализирован | 2 |
| `ch06-00-enums.md` | `ch06-00-enums.md` | Актуализирован | 0 |
| `ch06-01-defining-an-enum.md` | `ch06-01-defining-an-enum.md` | Актуализирован | 3 |
| `ch06-02-match.md` | `ch06-02-match.md` | Актуализирован | 2 |
| `ch06-03-if-let.md` | `ch06-03-if-let.md` | Актуализирован | 14 |
| `ch07-00-managing-growing-projects-with-packages-crates-and-modules.md` | `ch07-00-managing-growing-projects-with-packages-crates-and-modules.md` | Актуализирован | 1 |
| `ch07-01-packages-and-crates.md` | `ch07-01-packages-and-crates.md` | Актуализирован | 0 |
| `ch07-02-defining-modules-to-control-scope-and-privacy.md` | `ch07-02-defining-modules-to-control-scope-and-privacy.md` | Актуализирован | 1 |
| `ch07-03-paths-for-referring-to-an-item-in-the-module-tree.md` | `ch07-03-paths-for-referring-to-an-item-in-the-module-tree.md` | Актуализирован | 0 |
| `ch07-04-bringing-paths-into-scope-with-the-use-keyword.md` | `ch07-04-bringing-paths-into-scope-with-the-use-keyword.md` | Актуализирован | 5 |
| `ch07-05-separating-modules-into-different-files.md` | `ch07-05-separating-modules-into-different-files.md` | Актуализирован | 0 |
| `ch08-00-common-collections.md` | `ch08-00-common-collections.md` | Актуализирован | 0 |
| `ch08-01-vectors.md` | `ch08-01-vectors.md` | Актуализирован | 0 |
| `ch08-02-strings.md` | `ch08-02-strings.md` | Актуализирован | 7 |
| `ch08-03-hash-maps.md` | `ch08-03-hash-maps.md` | Актуализирован | 2 |
| `ch09-00-error-handling.md` | `ch09-00-error-handling.md` | Актуализирован | 0 |
| `ch09-01-unrecoverable-errors-with-panic.md` | `ch09-01-unrecoverable-errors-with-panic.md` | Актуализирован | 5 |
| `ch09-02-recoverable-errors-with-result.md` | `ch09-02-recoverable-errors-with-result.md` | Актуализирован | 3 |
| `ch09-03-to-panic-or-not-to-panic.md` | `ch09-03-to-panic-or-not-to-panic.md` | Актуализирован | 6 |
| `ch10-00-generics.md` | `ch10-00-generics.md` | Актуализирован | 0 |
| `ch10-01-syntax.md` | `ch10-01-syntax.md` | Актуализирован | 0 |
| `ch10-02-traits.md` | `ch10-02-traits.md` | Актуализирован | 9 |
| `ch10-03-lifetime-syntax.md` | `ch10-03-lifetime-syntax.md` | Актуализирован | 9 |
| `ch11-00-testing.md` | `ch11-00-testing.md` | Актуализирован | 0 |
| `ch11-01-writing-tests.md` | `ch11-01-writing-tests.md` | Актуализирован | 11 |
| `ch11-02-running-tests.md` | `ch11-02-running-tests.md` | Актуализирован | 2 |
| `ch11-03-test-organization.md` | `ch11-03-test-organization.md` | Актуализирован | 4 |
| `ch12-00-an-io-project.md` | `ch12-00-an-io-project.md` | Актуализирован | 2 |
| `ch12-01-accepting-command-line-arguments.md` | `ch12-01-accepting-command-line-arguments.md` | Актуализирован | 0 |
| `ch12-02-reading-a-file.md` | `ch12-02-reading-a-file.md` | Актуализирован | 1 |
| `ch12-03-improving-error-handling-and-modularity.md` | `ch12-03-improving-error-handling-and-modularity.md` | Актуализирован | 16 |
| `ch12-04-testing-the-librarys-functionality.md` | `ch12-04-testing-the-librarys-functionality.md` | Актуализирован | 7 |
| `ch12-05-working-with-environment-variables.md` | `ch12-05-working-with-environment-variables.md` | Актуализирован | 2 |
| `ch12-06-writing-to-stderr-instead-of-stdout.md` | `ch12-06-writing-to-stderr-instead-of-stdout.md` | Актуализирован | 1 |
| `ch13-00-functional-features.md` | `ch13-00-functional-features.md` | Актуализирован | 0 |
| `ch13-01-closures.md` | `ch13-01-closures.md` | Актуализирован | 10 |
| `ch13-02-iterators.md` | `ch13-02-iterators.md` | Актуализирован | 1 |
| `ch13-03-improving-our-io-project.md` | `ch13-03-improving-our-io-project.md` | Актуализирован | 5 |
| `ch13-04-performance.md` | `ch13-04-performance.md` | Актуализирован | 3 |
| `ch14-00-more-about-cargo.md` | `ch14-00-more-about-cargo.md` | Актуализирован | 0 |
| `ch14-01-release-profiles.md` | `ch14-01-release-profiles.md` | Актуализирован | 0 |
| `ch14-02-publishing-to-crates-io.md` | `ch14-02-publishing-to-crates-io.md` | Актуализирован | 10 |
| `ch14-03-cargo-workspaces.md` | `ch14-03-cargo-workspaces.md` | Актуализирован | 7 |
| `ch14-04-installing-binaries.md` | `ch14-04-installing-binaries.md` | Актуализирован | 1 |
| `ch14-05-extending-cargo.md` | `ch14-05-extending-cargo.md` | Актуализирован | 0 |
| `ch15-00-smart-pointers.md` | `ch15-00-smart-pointers.md` | Актуализирован | 0 |
| `ch15-01-box.md` | `ch15-01-box.md` | Актуализирован | 5 |
| `ch15-02-deref.md` | `ch15-02-deref.md` | Актуализирован | 6 |
| `ch15-03-drop.md` | `ch15-03-drop.md` | Актуализирован | 1 |
| `ch15-04-rc.md` | `ch15-04-rc.md` | Актуализирован | 4 |
| `ch15-05-interior-mutability.md` | `ch15-05-interior-mutability.md` | Актуализирован | 7 |
| `ch15-06-reference-cycles.md` | `ch15-06-reference-cycles.md` | Актуализирован | 3 |
| `ch16-00-concurrency.md` | `ch16-00-concurrency.md` | Актуализирован | 1 |
| `ch16-01-threads.md` | `ch16-01-threads.md` | Актуализирован | 3 |
| `ch16-02-message-passing.md` | `ch16-02-message-passing.md` | Актуализирован | 9 |
| `ch16-03-shared-state.md` | `ch16-03-shared-state.md` | Актуализирован | 5 |
| `ch16-04-extensible-concurrency-sync-and-send.md` | `ch16-04-extensible-concurrency-sync-and-send.md` | Актуализирован | 5 |
| `ch17-00-async-await.md` | `—` | Новый раздел, переведён полностью | 0 |
| `ch17-01-futures-and-syntax.md` | `—` | Новый раздел, переведён полностью | 0 |
| `ch17-02-concurrency-with-async.md` | `—` | Новый раздел, переведён полностью | 0 |
| `ch17-03-more-futures.md` | `—` | Новый раздел, переведён полностью | 0 |
| `ch17-04-streams.md` | `—` | Новый раздел, переведён полностью | 0 |
| `ch17-05-traits-for-async.md` | `—` | Новый раздел, переведён полностью | 0 |
| `ch17-06-futures-tasks-threads.md` | `—` | Новый раздел, переведён полностью | 0 |
| `ch18-00-oop.md` | `ch17-00-oop.md` | Актуализирован | 1 |
| `ch18-01-what-is-oo.md` | `ch17-01-what-is-oo.md` | Актуализирован | 2 |
| `ch18-02-trait-objects.md` | `ch17-02-trait-objects.md` | Актуализирован | 3 |
| `ch18-03-oo-design-patterns.md` | `ch17-03-oo-design-patterns.md` | Актуализирован | 12 |
| `ch19-00-patterns.md` | `ch18-00-patterns.md` | Актуализирован | 0 |
| `ch19-01-all-the-places-for-patterns.md` | `ch18-01-all-the-places-for-patterns.md` | Актуализирован | 3 |
| `ch19-02-refutability.md` | `ch18-02-refutability.md` | Актуализирован | 3 |
| `ch19-03-pattern-syntax.md` | `ch18-03-pattern-syntax.md` | Актуализирован | 15 |
| `ch20-00-advanced-features.md` | `ch19-00-advanced-features.md` | Актуализирован | 0 |
| `ch20-01-unsafe-rust.md` | `ch19-01-unsafe-rust.md` | Актуализирован | 27 |
| `ch20-02-advanced-traits.md` | `ch19-03-advanced-traits.md` | Актуализирован | 6 |
| `ch20-03-advanced-types.md` | `ch19-04-advanced-types.md` | Актуализирован | 4 |
| `ch20-04-advanced-functions-and-closures.md` | `ch19-05-advanced-functions-and-closures.md` | Актуализирован | 13 |
| `ch20-05-macros.md` | `ch19-06-macros.md` | Актуализирован | 6 |
| `ch21-00-final-project-a-web-server.md` | `ch20-00-final-project-a-web-server.md` | Актуализирован | 4 |
| `ch21-01-single-threaded.md` | `ch20-01-single-threaded.md` | Актуализирован | 6 |
| `ch21-02-multithreaded.md` | `ch20-02-multithreaded.md` | Актуализирован | 16 |
| `ch21-03-graceful-shutdown-and-cleanup.md` | `ch20-03-graceful-shutdown-and-cleanup.md` | Актуализирован | 6 |
| `appendix-00.md` | `appendix-00.md` | Без изменений в английском источнике | 0 |
| `appendix-01-keywords.md` | `appendix-01-keywords.md` | Актуализирован | 1 |
| `appendix-02-operators.md` | `appendix-02-operators.md` | Актуализирован | 18 |
| `appendix-03-derivable-traits.md` | `appendix-03-derivable-traits.md` | Актуализирован | 1 |
| `appendix-04-useful-development-tools.md` | `appendix-04-useful-development-tools.md` | Актуализирован | 8 |
| `appendix-05-editions.md` | `appendix-05-editions.md` | Актуализирован | 3 |
| `appendix-06-translation.md` | `appendix-06-translation.md` | Актуализирован | 7 |
| `appendix-07-nightly-rust.md` | `appendix-07-nightly-rust.md` | Актуализирован | 3 |
