# Язык программирования Rust

[Язык программирования Rust](title-page.md)
[Предисловие](foreword.md)
[Введение](ch00-00-introduction.md)

- [Начало работы](ch01-00-getting-started.md)
  - [Установка](ch01-01-installation.md)
  - [Привет, мир!](ch01-02-hello-world.md)
  - [Привет, Cargo!](ch01-03-hello-cargo.md)

- [Программируем игру в загадки](ch02-00-guessing-game-tutorial.md)

- [Общие концепции программирования](ch03-00-common-programming-concepts.md)
  - [Переменные и изменяемость](ch03-01-variables-and-mutability.md)
  - [Типы Данных](ch03-02-data-types.md)
  - [Функции](ch03-03-how-functions-work.md)
  - [Комментарии](ch03-04-comments.md)
  - [Управляющие конструкции](ch03-05-control-flow.md)

- [Понимание Владения](ch04-00-understanding-ownership.md)
  - [Что такое владение?](ch04-01-what-is-ownership.md)
  - [Ссылки и заимствование](ch04-02-references-and-borrowing.md)
  - [Тип срезы](ch04-03-slices.md)

- [Использование структур для структурирования связанных данных](ch05-00-structs.md)
  - [Определение и инициализация структур](ch05-01-defining-structs.md)
  - [Пример использования структур](ch05-02-example-structs.md)
  - [Методы](ch05-03-method-syntax.md)

- [Перечисления и сопоставление с образцом](ch06-00-enums.md)
  - [Определение перечисления](ch06-01-defining-an-enum.md)
  - [Управляющая конструкция match](ch06-02-match.md)
  - [Краткое управление потоком выполнения с if let и let...else](ch06-03-if-let.md)

- [Пакеты, крейты и модули](ch07-00-managing-growing-projects-with-packages-crates-and-modules.md)
  - [Пакеты и крейты](ch07-01-packages-and-crates.md)
  - [Управление областью видимости и доступом с помощью модулей](ch07-02-defining-modules-to-control-scope-and-privacy.md)
  - [Пути для ссылки на элемент в дереве модулей](ch07-03-paths-for-referring-to-an-item-in-the-module-tree.md)
  - [Подключение путей в область видимости с помощью ключевого слова use](ch07-04-bringing-paths-into-scope-with-the-use-keyword.md)
  - [Разделение модулей на разные файлы](ch07-05-separating-modules-into-different-files.md)

- [Общие коллекции](ch08-00-common-collections.md)
  - [Хранение списков значений в векторах](ch08-01-vectors.md)
  - [Хранение закодированного текста UTF-8 в строках](ch08-02-strings.md)
  - [Хранение ключей со связанными значениями в HashMap](ch08-03-hash-maps.md)

- [Обработка ошибок](ch09-00-error-handling.md)
  - [Неустранимые ошибки с макросом panic!](ch09-01-unrecoverable-errors-with-panic.md)
  - [Исправимые ошибки с Result](ch09-02-recoverable-errors-with-result.md)
  - [panic! или не panic!](ch09-03-to-panic-or-not-to-panic.md)

- [Обобщённые типы, типажи и время жизни](ch10-00-generics.md)
  - [Обобщённые типы данных](ch10-01-syntax.md)
  - [Определение общего поведения с помощью типажей](ch10-02-traits.md)
  - [Валидация ссылок при помощи времён жизни<a name="validating-references-with-lifetimes"></a>](ch10-03-lifetime-syntax.md)

- [Написание автоматизированных тестов](ch11-00-testing.md)
  - [Как писать тесты](ch11-01-writing-tests.md)
  - [Контролирование хода выполнения тестов](ch11-02-running-tests.md)
  - [Организация тестов](ch11-03-test-organization.md)

- [Проект с вводом/выводом (I/O): создание консольного приложения](ch12-00-an-io-project.md)
  - [Принятие аргументов командной строки](ch12-01-accepting-command-line-arguments.md)
  - [Чтение файла](ch12-02-reading-a-file.md)
  - [Рефакторинг для улучшения модульности и обработки ошибок](ch12-03-improving-error-handling-and-modularity.md)
  - [Добавление возможностей через разработку на основе тестов](ch12-04-testing-the-librarys-functionality.md)
  - [Работа с переменными окружения](ch12-05-working-with-environment-variables.md)
  - [Направление ошибок в стандартный поток ошибок](ch12-06-writing-to-stderr-instead-of-stdout.md)

- [Функциональные возможности языка: итераторы и замыкания](ch13-00-functional-features.md)
  - [Замыкания](ch13-01-closures.md)
  - [Обработка последовательности элементов с помощью итераторов](ch13-02-iterators.md)
  - [Улучшение нашего проекта с вводом/выводом](ch13-03-improving-our-io-project.md)
  - [Производительность циклов и итераторов](ch13-04-performance.md)

- [Больше о Cargo и Crates.io](ch14-00-more-about-cargo.md)
  - [Настройка сборок с профилями релизов](ch14-01-release-profiles.md)
  - [Публикация библиотеки в Crates.io](ch14-02-publishing-to-crates-io.md)
  - [Рабочие пространства Cargo](ch14-03-cargo-workspaces.md)
  - [Установка двоичных файлов с помощью cargo install](ch14-04-installing-binaries.md)
  - [Расширение Cargo пользовательскими командами](ch14-05-extending-cargo.md)

- [Умные указатели](ch15-00-smart-pointers.md)
  - [Использование Box<T> для ссылки на данные в куче](ch15-01-box.md)
  - [Работа с умными указателями как с обычными ссылками](ch15-02-deref.md)
  - [Запуск кода при очистке с помощью типажа Drop](ch15-03-drop.md)
  - [Rc<T> — умный указатель с подсчётом ссылок](ch15-04-rc.md)
  - [RefCell<T> и шаблон внутренней изменяемости](ch15-05-interior-mutability.md)
  - [Ссылочные зацикливания могут приводить к утечке памяти](ch15-06-reference-cycles.md)

- [Многопоточность без страха](ch16-00-concurrency.md)
  - [Использование потоков для одновременного выполнения кода](ch16-01-threads.md)
  - [Передача данных между потоками с помощью сообщений](ch16-02-message-passing.md)
  - [Многопоточное разделяемое состояние](ch16-03-shared-state.md)
  - [Расширяемое конкурентное выполнение с Send и Sync](ch16-04-extensible-concurrency-sync-and-send.md)

- [Основы асинхронного программирования: async, await, future и потоки значений](ch17-00-async-await.md)
  - [Future и асинхронный синтаксис](ch17-01-futures-and-syntax.md)
  - [Конкурентное выполнение с помощью async](ch17-02-concurrency-with-async.md)
  - [Возврат управления среде выполнения](ch17-03-more-futures.md)
  - [Потоки значений: последовательности future](ch17-04-streams.md)
  - [Подробнее о типажах для асинхронного программирования](ch17-05-traits-for-async.md)
  - [Объединяем всё вместе: future, задачи и потоки](ch17-06-futures-tasks-threads.md)

- [Возможности объектно-ориентированного программирования](ch18-00-oop.md)
  - [Характеристики объектно-ориентированных языков](ch18-01-what-is-oo.md)
  - [Абстрагирование общего поведения с помощью объектов типажей](ch18-02-trait-objects.md)
  - [Реализация объектно-ориентированного шаблона проектирования](ch18-03-oo-design-patterns.md)

- [Шаблоны и сопоставление](ch19-00-patterns.md)
  - [Все случаи, где могут быть использованы шаблоны](ch19-01-all-the-places-for-patterns.md)
  - [Возможность опровержения: может ли шаблон не совпадать](ch19-02-refutability.md)
  - [Синтаксис шаблонов](ch19-03-pattern-syntax.md)

- [Расширенные возможности](ch20-00-advanced-features.md)
  - [Unsafe Rust](ch20-01-unsafe-rust.md)
  - [Продвинутые типажи](ch20-02-advanced-traits.md)
  - [Продвинутые типы](ch20-03-advanced-types.md)
  - [Продвинутые функции и замыкания](ch20-04-advanced-functions-and-closures.md)
  - [Макросы](ch20-05-macros.md)

- [Финальный проект: создание многопоточного веб-сервера](ch21-00-final-project-a-web-server.md)
  - [Создание однопоточного веб-сервера](ch21-01-single-threaded.md)
  - [От однопоточного сервера к многопоточному](ch21-02-multithreaded.md)
  - [Мягкое завершение работы и очистка](ch21-03-graceful-shutdown-and-cleanup.md)

- [Дополнительная информация](appendix-00.md)
  - [Приложение A: Ключевые слова](appendix-01-keywords.md)
  - [Приложение B: Операторы и обозначения](appendix-02-operators.md)
  - [Приложение C: Типажи с автоматической реализацией](appendix-03-derivable-traits.md)
  - [Приложение D: Полезные инструменты разработки](appendix-04-useful-development-tools.md)
  - [Приложение E: Редакции](appendix-05-editions.md)
  - [Приложение F: Переводы книги](appendix-06-translation.md)
  - [Приложение G: Как создаётся Rust и что такое Nightly Rust](appendix-07-nightly-rust.md)

---

# Дополнения

- [Биты, байты и двоичные данные](supplement.md)
