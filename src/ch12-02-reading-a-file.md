<a id="reading-a-file"></a>

## Чтение файла

Теперь добавим возможность чтения файла, указанного как аргумент командной строки `file_path`. Во-первых, нам нужен пример файла для тестирования: мы будем использовать файл с небольшим объёмом текста в несколько строк с несколькими повторяющимися словами. В листинге 12-3 представлено стихотворение Эмили Дикинсон, которое будет хорошо работать! Создайте файл с именем *poem.txt* в корне вашего проекта и введите стихотворение “I’m nobody! Who are you?”

Файл: `poem.txt`

``` text
I'm nobody! Who are you?
Are you nobody, too?
Then there's a pair of us - don't tell!
They'd banish us, you know.

How dreary to be somebody!
How public, like a frog
To tell your name the livelong day
To an admiring bog!
```

Листинг 12-3: Стихотворение Эмили Дикинсон - хороший пример для проверки

Текст на месте, отредактируйте *src/main.rs* и добавьте код для чтения файла, как показано в листинге 12-4.

Файл: `src/main.rs`

``` rust
use std::env;
use std::fs;

fn main() {
    // --snip--
    println!("In file {file_path}");

    let contents = fs::read_to_string(file_path)
        .expect("Should have been able to read the file");

    println!("With text:\n{contents}");
}
```

Листинг 12-4: Чтение содержимого файла указанного во втором аргументе

Во-первых, мы добавляем ещё одну инструкцию `use` чтобы подключить соответствующую часть стандартной библиотеки: нам нужен `std::fs` для обработки файлов.

В `main` новый вызов `fs::read_to_string` принимает `file_path`, открывает файл и возвращает `std::io::Result<String>` с его содержимым.

После этого, мы снова добавили временную инструкцию `println!` для печати значения `contents` после чтения файла, таким образом мы можем проверить, что программа отрабатывает до этого места.

Давайте запустим этот код с любой строкой в качестве первого аргумента командной строки (потому что мы ещё не реализовали поисковую часть) и файл *poem.txt* как второй аргумент:

``` console
$ cargo run -- the poem.txt
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/minigrep the poem.txt`
Searching for the
In file poem.txt
With text:
I'm nobody! Who are you?
Are you nobody, too?
Then there's a pair of us - don't tell!
They'd banish us, you know.

How dreary to be somebody!
How public, like a frog
To tell your name the livelong day
To an admiring bog!
```

Отлично! Этот код прочитал и затем напечатал содержимое файла. Но у программы есть несколько недостатков. Прежде всего, функция `main` решает слишком много задач: как правило функция понятнее и проще в обслуживании если она воплощает только одну идею. Другая проблема заключается в том, что мы не обрабатываем ошибки так хорошо, как могли бы. Пока наша программа небольшая, то эти недостатки не являются большой проблемой, но по мере роста программы эти недостатки будет всё труднее исправлять. Хорошей практикой является начинать рефакторинг на ранней стадии разработки программы, потому что гораздо проще рефакторить меньшие объёмы кода. Мы сделаем это далее.
