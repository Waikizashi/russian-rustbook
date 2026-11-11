<a id="how-to-write-tests"></a>

## Как писать тесты

Тесты - это функции Rust, которые проверяют, что не тестовый код работает ожидаемым образом. Содержимое тестовых функций обычно выполняет следующие три действия:

- Установка любых необходимых данных или состояния.
- Запуск кода, который вы хотите проверить.
- Утверждение, что результаты являются теми, которые вы ожидаете.

Давайте рассмотрим функции предоставляемые в Rust специально для написания тестов, которые выполнят все эти действия, включая атрибут `test`, несколько макросов и атрибут `should_panic`.

<span id="the-anatomy-of-a-test-function"></span>

<a id="structuring-test-functions"></a>

### Структура тестовых функций

В простейшем случае в Rust тест - это функция, аннотированная атрибутом `test`. Атрибуты представляют собой метаданные о фрагментах кода Rust; один из примеров атрибут `derive`, который мы использовали со структурами в главе 5. Чтобы превратить функцию в тестирующую функцию добавьте `#[test]` в строку перед `fn`. Когда вы запускаете тесты командой `cargo test`, Rust создаёт бинарный модуль выполняющий функции аннотированные атрибутом test и сообщающий о том, успешно или нет прошла каждая тестирующая функция.

Когда мы создаём новый проект библиотеки с помощью Cargo, то в нём автоматически генерируется тестовый модуль с тест-функцией для нас. Этот модуль даст вам шаблон для написания ваших тестов, так что вам не нужно искать точную структуру и синтаксис тестовых функций каждый раз, когда вы начинаете новый проект. Вы можете добавить столько дополнительных тестовых функций и столько тестовых модулей, сколько захотите!

Мы исследуем некоторые аспекты работы тестов, экспериментируя с шаблонным тестом сгенерированным для нас, без реального тестирования любого кода. Затем мы напишем некоторые реальные тесты, которые вызывают некоторый написанный код и убедимся в его правильном поведении. Мы рассмотрим некоторые аспекты работы тестов, поэкспериментируем с шаблонным тестом, прежде чем приступать к фактическому тестированию любого кода. Затем мы напишем несколько реальных тестов, которые вызывают некоторый написанный нами код и проверяют, что его поведение правильное.

Давайте создадим новый библиотечный проект под названием `adder`, который складывает два числа:

``` console
$ cargo new adder --lib
     Created library `adder` project
$ cd adder
```

Содержимое файла *src/lib.rs* вашей библиотеки `adder` должно выглядеть как в листинге 11-1.

Файл: `src/lib.rs`

``` rust
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

Листинг 11-1: Код, автоматически сгенерированный `cargo new`

Файл начинается с примера функции `add`, чтобы нам было что тестировать.

Пока сосредоточимся только на функции `it_works`. Обратите внимание на аннотацию `#[test]`: этот атрибут обозначает тестовую функцию, и программа запуска тестов знает, что её нужно выполнить как тест. В модуле `tests` могут быть и вспомогательные функции, подготавливающие общие сценарии или выполняющие повторяющиеся операции. Поэтому мы всегда должны указывать, какие функции являются тестами.

В теле примера макрос `assert_eq!` проверяет, что `result`, содержащий результат вызова `add` с аргументами 2 и 2, равен 4. Это образец обычного теста. Запустим его и убедимся, что он проходит.

Команда `cargo test` выполнит все тесты в выбранном проекте и сообщит о результатах как в листинге 11-2:

``` console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.57s
     Running unittests src/lib.rs (target/debug/deps/adder-01ad14159ff659ab)

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Листинг 11-2: Вывод информации о работе автоматически сгенерированных тестов

Cargo скомпилировал и выполнил тест. Мы видим строку `running 1 test`. Следующая строка показывает имя сгенерированной тестовой функции, называемой `tests::it_works`, и результат запуска этого теста равный `ok`. Текст `test result: ok.` означает, что все тесты пройдены успешно и часть вывода `1 passed; 0 failed` сообщает общее количество тестов, которые прошли или были ошибочными.

Можно пометить тест как игнорируемый, чтобы он не выполнялся в конкретном случае; мы рассмотрим это в разделе [“Игнорирование некоторых тестов, если их специально не запрашивать”](ch11-02-running-tests.md#ignoring-tests-unless-specifically-requested) позже в этой главе. Поскольку в данный момент мы этого не сделали, в сводке показано, что `0 ignored`. Мы также можем передать аргумент команде `cargo test` для запуска только тех тестов, имя которых соответствует строке; это называется *фильтрацией*, и мы рассмотрим это в разделе [“Запуск подмножества тестов по имени”](ch11-02-running-tests.md#running-a-subset-of-tests-by-name). Мы также не фильтровали выполняемые тесты, поэтому в конце сводки показано, что `0 filtered out`.

Статистика `0 measured` предназначена для тестов производительности. На момент написания этой статьи такие тесты доступны только в ночной сборке Rust. Посмотрите [документацию о тестах производительности](https://doc.rust-lang.org/unstable-book/library-features/test.html), чтобы узнать больше.

Следующая часть вывода тестов начинается с `Doc-tests adder` - это информация о тестах в документации. У нас пока нет тестов документации, но Rust может компилировать любые примеры кода, которые находятся в API документации. Такая возможность помогает поддерживать документацию и код в синхронизированном состоянии. Мы поговорим о написании тестов документации в секции [“Комментарии документации как тесты”](ch14-02-publishing-to-crates-io.md#documentation-comments-as-tests) Главы 14. Пока просто проигнорируем часть `Doc-tests` вывода.

Давайте начнём настраивать тест в соответствии с нашими собственными потребностями. Сначала поменяем название нашего теста `it_works` на `exploration`, вот так:

Файл: src/lib.rs

``` rust
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exploration() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

Снова выполним команду `cargo test`. Вывод показывает наименование нашей тест-функции - `exploration` вместо `it_works`:

``` console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.59s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::exploration ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Добавим ещё один тест, но в этот раз специально сделаем так, чтобы этот новый тест не отработал! Тест терпит неудачу, когда что-то паникует в тестируемой функции. Каждый тест запускается в новом потоке и когда главный поток видит, что тестовый поток упал, то помечает тест как завершившийся аварийно. Мы говорили о простейшем способе вызвать панику в главе 9, используя для этого известный макрос `panic!`. Введём код тест-функции `another`, как в файле *src/lib.rs* из листинга 11-3.

Файл: `src/lib.rs`

``` rust
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exploration() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }

    #[test]
    fn another() {
        panic!("Make this test fail");
    }
}
```

Листинг 11-3: Добавление второго теста, который завершится ошибкой, потому что мы вызываем `panic!` макрос

Запустим команду `cargo test`. Вывод результатов показан в листинге 11-4, который сообщает, что тест `exploration` пройден, а `another` нет:

``` console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.72s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 2 tests
test tests::another ... FAILED
test tests::exploration ... ok

failures:

---- tests::another stdout ----

thread 'tests::another' (6019162) panicked at src/lib.rs:17:9:
Make this test fail
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::another

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Листинг 11-4. Результаты теста, когда один тест пройден, а другой нет

Вместо `ok`, строка `test tests::another` сообщает `FAILED`. Две новые секции появились между отдельными результатами и сводкой: в первом отображается подробная причина каждого сбоя теста. В данном случае тест `tests::another` не сработал, потому что `Make this test fail`, произошло в строке 10 файла *src/lib.rs*. В следующем разделе перечисляют имена всех не пройденных тестов, что удобно, когда есть много тестов и много подробных результатов неудачных тестов. Мы можем использовать имя не пройденного теста для его дальнейшей отладки; мы больше поговорим о способах запуска тестов в разделе [“Контролирование хода выполнения тестов”](ch11-02-running-tests.md#controlling-how-tests-are-run).

Итоговая строка отображается в конце: общий результат нашего тестирования `FAILED`. У нас один тест пройден и один тест завершён аварийно.

Теперь, когда вы увидели, как выглядят результаты теста при разных сценариях, давайте рассмотрим другие макросы полезные в тестах, кроме `panic!`.

<span id="checking-results-with-the-assert-macro"></span>

<a id="checking-results-with-assert"></a>

### Проверка результатов с помощью `assert!`

Макрос `assert!` доступен из стандартной библиотеки и является удобным, когда вы хотите проверить что некоторое условие в тесте вычисляется в значение `true`. Мы передаём в макрос `assert!` аргумент, который вычисляется в логическое значение. Если оно `true`, то ничего не происходит и тест считается пройденным. Если же значение вычисляется в `false`, то макрос `assert!` вызывает макрос `panic!`, чтобы вызвать сбой теста. Использование макроса `assert!` помогает проверить, что код функционирует как ожидалось.

В главе 5, листинге 5-15, мы использовали структуру `Rectangle` и метод `can_hold`, который повторён в листинге 11-5. Давайте поместим этот код в файл *src/lib.rs* и напишем несколько тестов для него используя макрос `assert!`.

Файл: `src/lib.rs`

``` rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}
```

Листинг 11-5: Использование структуры `Rectangle` и её метода can_hold из главы 5

Метод `can_hold` возвращает логическое значение, что означает, что он является идеальным вариантом использования в макросе `assert!`. В листинге 11-6 мы пишем тест, который выполняет метод `can_hold` путём создания экземпляра `Rectangle` шириной 8 и высотой 7 и убеждаемся, что он может содержать другой экземпляр `Rectangle` имеющий ширину 5 и высоту 1.

Файл: `src/lib.rs`

``` rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn larger_can_hold_smaller() {
        let larger = Rectangle {
            width: 8,
            height: 7,
        };
        let smaller = Rectangle {
            width: 5,
            height: 1,
        };

        assert!(larger.can_hold(&smaller));
    }
}
```

Листинг 11-6: Тест для метода `can_hold`, который проверяет что больший прямоугольник действительно может содержать меньший

Также, в модуле `tests` обратите внимание на новую добавленную строку `use super::*;`. Модуль `tests` является обычным и подчиняется тем же правилам видимости, которые мы обсуждали в главе 7 [“Пути для ссылки на элементы внутри дерева модуля”](ch07-03-paths-for-referring-to-an-item-in-the-module-tree.md). Так как этот модуль `tests` является внутренним, нужно подключить тестируемый код из внешнего модуля в область видимости внутреннего модуля с тестами. Для этого используется глобальное подключение, так что все что определено во внешнем модуле становится доступным внутри `tests` модуля.

Мы назвали наш тест `larger_can_hold_smaller` и создали два нужных экземпляра `Rectangle`. Затем вызвали макрос `assert!` и передали результат вызова `larger.can_hold(&smaller)` в него. Это выражение должно возвращать `true`, поэтому наш тест должен пройти. Давайте выясним!

``` console
$ cargo test
   Compiling rectangle v0.1.0 (file:///projects/rectangle)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/rectangle-6584c4561e48942e)

running 1 test
test tests::larger_can_hold_smaller ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests rectangle

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Тест проходит. Теперь добавим другой тест, в этот раз мы попытаемся убедиться, что меньший прямоугольник не может содержать больший прямоугольник:

Файл: src/lib.rs

``` rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn larger_can_hold_smaller() {
        // --snip--
    }

    #[test]
    fn smaller_cannot_hold_larger() {
        let larger = Rectangle {
            width: 8,
            height: 7,
        };
        let smaller = Rectangle {
            width: 5,
            height: 1,
        };

        assert!(!smaller.can_hold(&larger));
    }
}
```

Поскольку правильный результат функции `can_hold` в этом случае `false`, то мы должны инвертировать этот результат, прежде чем передадим его в `assert!` макро. Как результат, наш тест пройдёт, если `can_hold` вернёт `false`:

``` console
$ cargo test
   Compiling rectangle v0.1.0 (file:///projects/rectangle)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/rectangle-6584c4561e48942e)

running 2 tests
test tests::larger_can_hold_smaller ... ok
test tests::smaller_cannot_hold_larger ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests rectangle

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Два теста работают. Теперь проверим, как отреагируют тесты, если мы добавим ошибку в код. Давайте изменим реализацию метода `can_hold` заменив одно из логических выражений знак сравнения с “больше чем” на противоположный “меньше чем” при сравнении ширины:

``` rust
// --snip--
impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width < other.width && self.height > other.height
    }
}
```

Запуск тестов теперь производит следующее:

``` console
$ cargo test
   Compiling rectangle v0.1.0 (file:///projects/rectangle)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/rectangle-6584c4561e48942e)

running 2 tests
test tests::larger_can_hold_smaller ... FAILED
test tests::smaller_cannot_hold_larger ... ok

failures:

---- tests::larger_can_hold_smaller stdout ----

thread 'tests::larger_can_hold_smaller' (6020788) panicked at src/lib.rs:28:9:
assertion failed: larger.can_hold(&smaller)
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::larger_can_hold_smaller

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Наши тесты нашли ошибку! Так как в тесте `larger.width` равно 8 и `smaller.width` равно 5 сравнение ширины в методе `can_hold` возвращает результат `false`, поскольку число 8 не меньше чем 5.

<span id="testing-equality-with-the-assert_eq-and-assert_ne-macros"></span>

<a id="testing-equality-with-assert_eq-and-assert_ne"></a>

### Проверка равенства с помощью `assert_eq!` и `assert_ne!`

Общим способом проверки функциональности является использование сравнения результата тестируемого кода и ожидаемого значения, чтобы убедиться в их равенстве. Для этого можно использовать макрос `assert!`, передавая ему выражение с использованием оператора `==`. Важно также знать, что кроме этого стандартная библиотека предлагает пару макросов `assert_eq!` и `assert_ne!`, чтобы сделать тестирование более удобным. Эти макросы сравнивают два аргумента на равенство или неравенство соответственно. Макросы также печатают два значения входных параметров, если тест завершился ошибкой, что позволяет легче увидеть *почему* тест ошибочен. Противоположно этому, макрос `assert!` может только отобразить, что он вычислил значение `false` для выражения `==`, но не значения, которые привели к результату `false`.

В листинге 11-7, мы напишем функцию `add_two`, которая прибавляет к входному параметру `2` и возвращает значение. Затем, протестируем эту функцию с помощью макроса `assert_eq!`:

Файл: `src/lib.rs`

``` rust
pub fn add_two(a: u64) -> u64 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_adds_two() {
        let result = add_two(2);
        assert_eq!(result, 4);
    }
}
```

Листинг 11-7: Тестирование функции `add_two` с помощью макроса `assert_eq!`

Проверим, что тесты проходят!

``` console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.58s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::it_adds_two ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Создадим переменную `result` с результатом `add_two(2)`. Затем передадим `result` и `4` в макрос `assert_eq!`. Строка вывода этого теста — `test tests::it_adds_two ... ok`; слово `ok` означает, что тест пройден!

Давайте введём ошибку в код, чтобы увидеть, как она выглядит, когда тест, который использует `assert_eq!` завершается ошибкой. Измените реализацию функции `add_two`, чтобы добавлять `3`:

``` rust
pub fn add_two(a: u64) -> u64 {
    a + 3
}
```

Попробуем выполнить данный тест ещё раз:

``` console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::it_adds_two ... FAILED

failures:

---- tests::it_adds_two stdout ----

thread 'tests::it_adds_two' (6020955) panicked at src/lib.rs:12:9:
assertion `left == right` failed
  left: 5
 right: 4
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::it_adds_two

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Тест обнаружил ошибку! `tests::it_adds_two` завершился неудачно, а сообщение показывает, что не выполнилась проверка `left == right`, и приводит значения `left` и `right`. Это помогает начать отладку: аргумент `left`, содержащий результат `add_two(2)`, равен `5`, а аргумент `right` — `4`. Представьте, насколько это полезно, когда тестов много.

В некоторых языках и тестовых фреймворках параметры проверки равенства называются `expected` и `actual`, и порядок аргументов важен. В Rust они называются `left` и `right`, а порядок ожидаемого и полученного значения несущественен. Можно написать `assert_eq!(4, result)` и получить такое же сообщение `` assertion `left == right` failed ``.

Макрос `assert_ne!` сработает успешно, если входные параметры не равны друг другу и завершится с ошибкой, если значения равны. Этот макрос наиболее полезен в тех случаях, когда мы не знаем заранее, каким значение *будет*, но знаем точно, каким оно *не может* быть. К примеру, если тестируется функция, которая гарантировано изменяет входные данные определённым образом, но способ изменения входного параметра зависит от дня недели, в который запускаются тесты, что лучший способ проверить правильность работы такой функции - это сравнить и убедиться, что выходное значение функции не должно быть равным входному значению.

В своей работе макросы `assert_eq!` и `assert_ne!` неявным образом используют операторы `==` и `!=` соответственно. Когда проверка не срабатывает, макросы печатают значения аргументов с помощью отладочного форматирования и это означает, что значения сравниваемых аргументов должны реализовать типажи `PartialEq` и `Debug`. Все примитивные и большая часть типов стандартной библиотеки Rust реализуют эти типажи. Для структур и перечислений, которые вы реализуете сами будет необходимо реализовать типаж `PartialEq` для сравнения значений на равенство или неравенство. Для печати отладочной информации в виде сообщений в строку вывода консоли необходимо реализовать типаж `Debug`. Так как оба типажа являются выводимыми типажами, как упоминалось в листинге 5-12 главы 5, то эти типажи можно реализовать добавив аннотацию `#[derive(PartialEq, Debug)]` к определению структуры или перечисления. Смотрите больше деталей в Appendix C [“Выводимые типажи”](appendix-03-derivable-traits.md) про эти и другие выводимые типажи.

<a id="adding-custom-failure-messages"></a>

### Создание сообщений об ошибках

Также можно добавить пользовательское сообщение как дополнительный аргумент макросов для печати в сообщении об ошибке теста `assert!`, `assert_eq!`, и `assert_ne!`. Любые аргументы, указанные после обязательных аргументов, далее передаются в макрос `format!` (он обсуждается в разделе [“Конкатенация с помощью оператора `+` или макроса format!”](ch08-02-strings.md#concatenating-with-or-format)), так что вы можете передать форматированную строку, которая содержит `{}` для заполнителей и значения, заменяющие эти заполнители. Пользовательские сообщения полезны для пояснения того, что означает утверждение (assertion); когда тест завершается неудачей, у вас будет лучшее представление о том, в чем проблема с кодом.

Например, есть функция, которая приветствует человека по имени и мы хотим протестировать эту функцию. Мы хотим чтобы передаваемое ей имя выводилось в консоль:

Файл: src/lib.rs

``` rust
pub fn greeting(name: &str) -> String {
    format!("Hello {name}!")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn greeting_contains_name() {
        let result = greeting("Carol");
        assert!(result.contains("Carol"));
    }
}
```

Требования к этой программе ещё не были согласованы и мы вполне уверены, что текст `Hello` в начале приветствия ещё изменится. Мы решили, что не хотим обновлять тест при изменении требований, поэтому вместо проверки на точное равенство со значением возвращённым из `greeting`, мы просто будем проверять, что вывод содержит текст из входного параметра.

Давайте внесём ошибку в этот код, изменив `greeting` так, чтобы оно не включало `name` и увидим, как выглядит сбой этого теста:

``` rust
pub fn greeting(name: &str) -> String {
    String::from("Hello!")
}
```

Запуск этого теста выводит следующее:

``` console
$ cargo test
   Compiling greeter v0.1.0 (file:///projects/greeter)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.91s
     Running unittests src/lib.rs (target/debug/deps/greeter-170b942eb5bf5e3a)

running 1 test
test tests::greeting_contains_name ... FAILED

failures:

---- tests::greeting_contains_name stdout ----

thread 'tests::greeting_contains_name' (6021143) panicked at src/lib.rs:12:9:
assertion failed: result.contains("Carol")
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::greeting_contains_name

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Сообщение содержит лишь информацию о том что сравнение не было успешным и в какой строке это произошло. В данном случае, более полезный текст сообщения был бы, если бы также выводилось значение из функции `greeting`. Изменим тестирующую функцию так, чтобы выводились пользовательское сообщение форматированное строкой с заменителем и фактическими данными из кода `greeting`:

``` rust
    #[test]
    fn greeting_contains_name() {
        let result = greeting("Carol");
        assert!(
            result.contains("Carol"),
            "Greeting did not contain name, value was `{result}`"
        );
    }
```

После того, как выполним тест ещё раз мы получим подробное сообщение об ошибке:

``` console
$ cargo test
   Compiling greeter v0.1.0 (file:///projects/greeter)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.93s
     Running unittests src/lib.rs (target/debug/deps/greeter-170b942eb5bf5e3a)

running 1 test
test tests::greeting_contains_name ... FAILED

failures:

---- tests::greeting_contains_name stdout ----

thread 'tests::greeting_contains_name' (6021333) panicked at src/lib.rs:12:9:
Greeting did not contain name, value was `Hello!`
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::greeting_contains_name

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Мы можем увидеть значение, которое мы на самом деле получили в тестовом выводе, что поможет нам отлаживать произошедшее, а не то, что мы ожидали.

<a id="checking-for-panics-with-should_panic"></a>

### Проверка с помощью макроса `should_panic`

В дополнение к проверке того, что наш код возвращает правильные, ожидаемые значения, важным также является проверить, что наш код обрабатывает ошибки, которые мы ожидаем. Например, рассмотрим тип `Guess` который мы создали в главе 9, листинга 9-13. Другой код, который использует `Guess` зависит от гарантии того, что `Guess` экземпляры будут содержать значения только от 1 до 100. Мы можем написать тест, который гарантирует, что попытка создать экземпляр `Guess` со значением вне этого диапазона вызывает панику.

Для этого добавим тестовой функции атрибут `should_panic`. Тест проходит, если код функции паникует, и не проходит, если паники нет.

Листинг 11-8 показывает тест, который проверяет, что условия ошибки `Guess::new` произойдут, когда мы их ожидаем их.

Файл: `src/lib.rs`

``` rust
pub struct Guess {
    value: i32,
}

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 || value > 100 {
            panic!("Guess value must be between 1 and 100, got {value}.");
        }

        Guess { value }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic]
    fn greater_than_100() {
        Guess::new(200);
    }
}
```

Листинг 11-8: Проверка того, что условие вызовет макрос `panic!`

Атрибут `#[should_panic]` следует после `#[test]` и до объявления тестовой функции. Посмотрим на вывод результата, когда тест проходит:

``` console
$ cargo test
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.58s
     Running unittests src/lib.rs (target/debug/deps/guessing_game-57d70c3acb738f4d)

running 1 test
test tests::greater_than_100 - should panic ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests guessing_game

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Выглядит хорошо! Теперь давайте внесём ошибку в наш код, убрав условие о том, что функция `new` будет паниковать если значение больше 100:

``` rust
// --snip--
impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!("Guess value must be between 1 and 100, got {value}.");
        }

        Guess { value }
    }
}
```

Когда мы запустим тест в листинге 11-8, он потерпит неудачу:

``` console
$ cargo test
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.62s
     Running unittests src/lib.rs (target/debug/deps/guessing_game-57d70c3acb738f4d)

running 1 test
test tests::greater_than_100 - should panic ... FAILED

failures:

---- tests::greater_than_100 stdout ----
note: test did not panic as expected at src/lib.rs:21:8

failures:
    tests::greater_than_100

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Мы получаем не очень полезное сообщение в этом случае, но когда мы смотрим на тестирующую функцию, мы видим, что она `#[should_panic]`. Аварийное выполнение, которое мы получили означает, что код в тестирующей функции не вызвал паники.

Тесты, которые используют `should_panic` могут быть неточными, потому что они только указывают, что код вызвал панику. Тест с атрибутом `should_panic` пройдёт, даже если тест паникует по причине, отличной от той, которую мы ожидали. Чтобы сделать тесты с `should_panic` более точными, мы можем добавить необязательный параметр `expected` для атрибута `should_panic`. Такая детализация теста позволит удостовериться, что сообщение об ошибке содержит предоставленный текст. Например, рассмотрим модифицированный код для `Guess` в листинге 11-9, где `new` функция паникует с различными сообщениями в зависимости от того, является ли значение слишком маленьким или слишком большим.

Файл: `src/lib.rs`

``` rust
// --snip--

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!(
                "Guess value must be greater than or equal to 1, got {value}."
            );
        } else if value > 100 {
            panic!(
                "Guess value must be less than or equal to 100, got {value}."
            );
        }

        Guess { value }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "less than or equal to 100")]
    fn greater_than_100() {
        Guess::new(200);
    }
}
```

Листинг 11-9: Проверка `panic!` на наличие в его сообщении указанной подстроки

Этот тест пройдёт, потому что значение, которое мы поместили для `should_panic` в параметр атрибута `expected` является подстрокой сообщения, с которым функция `Guess::new` вызывает панику. Мы могли бы указать полное, ожидаемое сообщение для паники, в этом случае это будет `Guess value must be less than or equal to 100, got 200`. То что вы выберите для указания как ожидаемого параметра у `should_panic` зависит от того, какая часть сообщения о панике уникальна или динамична, насколько вы хотите, чтобы ваш тест был точным. В этом случае достаточно подстроки из сообщения паники, чтобы гарантировать выполнение кода в тестовой функции `else if value > 100` .

Чтобы увидеть, что происходит, когда тест `should_panic` неуспешно завершается с сообщением `expected`, давайте снова внесём ошибку в наш код, поменяв местами `if value < 1` и `else if value > 100` блоки:

``` rust
        if value < 1 {
            panic!(
                "Guess value must be less than or equal to 100, got {value}."
            );
        } else if value > 100 {
            panic!(
                "Guess value must be greater than or equal to 1, got {value}."
            );
        }
```

На этот раз, когда мы выполним `should_panic` тест, он потерпит неудачу:

``` console
$ cargo test
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/guessing_game-57d70c3acb738f4d)

running 1 test
test tests::greater_than_100 - should panic ... FAILED

failures:

---- tests::greater_than_100 stdout ----

thread 'tests::greater_than_100' (6021675) panicked at src/lib.rs:12:13:
Guess value must be greater than or equal to 1, got 200.
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
note: panic did not contain expected string
      panic message: "Guess value must be greater than or equal to 1, got 200."
 expected substring: "less than or equal to 100"

failures:
    tests::greater_than_100

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Сообщение об ошибке указывает, что этот тест действительно вызвал панику, как мы и ожидали, но сообщение о панике не включено ожидаемую строку `less than or equal to 100`. Сообщение о панике, которое мы получили в этом случае, было `Guess value must be greater than or equal to 1, got 200` Теперь мы можем начать выяснение, где ошибка!

<a id="using-resultt-e-in-tests"></a>

### Использование `Result<T, E>` в тестах

Пока что мы написали тесты, которые паникуют, когда терпят неудачу. Мы также можем написать тесты которые используют `Result<T, E>`! Вот тест из листинга 11-1, переписанный с использованием `Result<T, E>` и возвращающий `Err` вместо паники:

``` rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() -> Result<(), String> {
        let result = add(2, 2);

        if result == 4 {
            Ok(())
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }
}
```

Функция `it_works` теперь имеет возвращаемый тип `Result<(), String>`. В теле функции, вместо вызова макроса `assert_eq!`, мы возвращаем `Ok(())` когда тест успешно выполнен и `Err` со `String` внутри, когда тест не проходит.

Написание тестов так, чтобы они возвращали `Result<T, E>` позволяет использовать оператор “вопросительный знак” в теле тестов, который может быть удобным способом писать тесты, которые должны выполниться не успешно, если какая-либо операция внутри них возвращает вариант ошибки `Err`.

Вы не можете использовать аннотацию `#[should_panic]` в тестах, использующих `Result<T, E>`. Чтобы утверждать, что операция возвращает вариант `Err`, *не* используйте оператор вопросительного знака для значения `Result<T, E>`. Вместо этого используйте `assert!(value.is_err())`.

Теперь, когда вы знаете несколько способов написания тестов, давайте взглянем на то, что происходит при запуске тестов и исследуем разные опции используемые с командой `cargo test`.
