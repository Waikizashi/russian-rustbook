<a id="controlling-how-tests-are-run"></a>

## Контролирование хода выполнения тестов

Подобно тому, как `cargo run` выполняет компиляцию вашего кода, а затем запускает полученный двоичный файл, `cargo test` компилирует ваш код в режиме тестирования и запускает полученный бинарник с тестами. Двоичный файл, создаваемый `cargo test`, по умолчанию запускает все тесты параллельно и перехватывает вывод, генерируемый во время выполнения тестов, предотвращая их вывод на экран для облегчения чтения вывода, относящегося к результатам тестирования. Однако вы можете указать параметры командной строки, чтобы изменить это поведение по умолчанию.

Некоторые параметры командной строки предназначены для `cargo test`, а другие — для полученного исполняемого файла тестов. Сначала указываются аргументы `cargo test`, затем разделитель `--`, а после него — аргументы тестовой программы. Команда `cargo test --help` показывает параметры `cargo test`, а `cargo test -- --help` — параметры после разделителя. Они также описаны в [разделе о тестах книги *The rustc Book*](https://doc.rust-lang.org/rustc/tests/index.html).

<a id="running-tests-in-parallel-or-consecutively"></a>

### Выполнение тестов параллельно или последовательно

Когда вы запускаете несколько тестов, по умолчанию они выполняются параллельно с использованием потоков, что означает, что они завершатся быстрее, и вы быстрее получите результаты. Поскольку тесты выполняются параллельно, вы должны убедиться, что ваши тесты не зависят друг от друга или от какого-либо общего состояния, включая общее окружение, например, текущий рабочий каталог или переменные окружения.

Например, допустим, каждый из ваших тестов запускает код, который создаёт файл на диске с именем *test-output.txt* и записывает некоторые данные в этот файл. Затем каждый тест считывает данные из этого файла и утверждает, что файл содержит определённое значение, которое в каждом тесте разное. Поскольку все тесты выполняются одновременно, один из тестов может перезаписать файл в промежутке между записью и чтением файла другим тестом. Тогда второй тест потерпит неудачу, но не потому, что код неверен, а потому, что эти тесты мешали друг другу при параллельном выполнении. Одно из решений - убедиться, что каждый тест пишет в свой отдельный файл; другое решение - запускать тесты по одному.

Если вы не хотите запускать тесты параллельно или хотите более детальный контроль над количеством используемых потоков, можно установить флаг `--test-threads` и то количество потоков, которое вы хотите использовать для теста. Взгляните на следующий пример:

``` console
$ cargo test -- --test-threads=1
```

Мы устанавливаем количество тестовых потоков равным `1` , указывая программе не использовать параллелизм. Выполнение тестов с использованием одного потока займёт больше времени, чем их параллельное выполнение, но тесты не будут мешать друг другу, если они совместно используют состояние.

<a id="showing-function-output"></a>

### Демонстрация результатов работы функции

По умолчанию, если тест пройден, система управления запуска тестов блокирует вывод на печать, т.е. если вы вызовете макрос `println!` внутри кода теста и тест будет пройден, вы не увидите вывода на консоль результатов вызова `println!`. Если же тест не был пройден, все информационные сообщения, а также описание ошибки будут выведены на консоль.

Например, в коде (11-10) функция выводит значение параметра с поясняющим текстовым сообщением, а также возвращает целочисленное константное значение `10`. Далее следует тест, который имеет правильный входной параметр и тест, который имеет ошибочный входной параметр:

Файл: `src/lib.rs`

``` rust
fn prints_and_returns_10(a: i32) -> i32 {
    println!("I got the value {a}");
    10
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn this_test_will_pass() {
        let value = prints_and_returns_10(4);
        assert_eq!(value, 10);
    }

    #[test]
    fn this_test_will_fail() {
        let value = prints_and_returns_10(8);
        assert_eq!(value, 5);
    }
}
```

Листинг 11-10: Тест функции, которая использует макрос `println!`

Результат вывода на консоль команды `cargo test`:

``` console
$ cargo test
   Compiling silly-function v0.1.0 (file:///projects/silly-function)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.58s
     Running unittests src/lib.rs (target/debug/deps/silly_function-160869f38cff9166)

running 2 tests
test tests::this_test_will_fail ... FAILED
test tests::this_test_will_pass ... ok

failures:

---- tests::this_test_will_fail stdout ----
I got the value 8

thread 'tests::this_test_will_fail' (6019863) panicked at src/lib.rs:19:9:
assertion `left == right` failed
  left: 10
 right: 5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::this_test_will_fail

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

Обратите внимание, что нигде в этом выводе мы не видим сообщения `I got the value 4` , которое печатается при выполнении пройденного теста. Этот вывод был записан. Результат неудачного теста, `I got the value 8` , появляется в разделе итоговых результатов теста, который также показывает причину неудачного теста.

Если мы хотим видеть напечатанные результаты прохождения тестов, мы можем сказать Rust, чтобы он также показывал результаты успешных тестов с помощью `--show-output`.

``` console
$ cargo test -- --show-output
```

Когда мы снова запускаем тесты из Листинга 11-10 с флагом `--show-output` , мы видим следующий результат:

``` console
$ cargo test -- --show-output
   Compiling silly-function v0.1.0 (file:///projects/silly-function)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.60s
     Running unittests src/lib.rs (target/debug/deps/silly_function-160869f38cff9166)

running 2 tests
test tests::this_test_will_fail ... FAILED
test tests::this_test_will_pass ... ok

successes:

---- tests::this_test_will_pass stdout ----
I got the value 4


successes:
    tests::this_test_will_pass

failures:

---- tests::this_test_will_fail stdout ----
I got the value 8

thread 'tests::this_test_will_fail' (6022313) panicked at src/lib.rs:19:9:
assertion `left == right` failed
  left: 10
 right: 5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::this_test_will_fail

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

<a id="running-a-subset-of-tests-by-name"></a>

### Запуск подмножества тестов по имени

Бывают случаи, когда в запуске всех тестов нет необходимости и нужно запустить только несколько тестов. Если вы работаете над функцией и хотите запустить тесты, которые исследуют её работу - это было бы удобно. Вы можете это сделать, используя команду `cargo test`, передав в качестве аргумента имена тестов.

Для демонстрации, как запустить группу тестов, мы создадим группу тестов для функции `add_two` function, как показано в Листинге 11-11, и постараемся выбрать какие из них запускать.

Файл: `src/lib.rs`

``` rust
pub fn add_two(a: u64) -> u64 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_two_and_two() {
        let result = add_two(2);
        assert_eq!(result, 4);
    }

    #[test]
    fn add_three_and_two() {
        let result = add_two(3);
        assert_eq!(result, 5);
    }

    #[test]
    fn one_hundred() {
        let result = add_two(100);
        assert_eq!(result, 102);
    }
}
```

Листинг 11-11: Три теста с различными именами

Если вы выполните команду `cargo test` без уточняющих аргументов, все тесты выполнятся параллельно:

``` console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.62s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 3 tests
test tests::add_three_and_two ... ok
test tests::add_two_and_two ... ok
test tests::one_hundred ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

<a id="running-single-tests"></a>

#### Запуск одного теста

Мы можем запустить один тест с помощью указания его имени в команде `cargo test`:

``` console
$ cargo test one_hundred
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.69s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::one_hundred ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 2 filtered out; finished in 0.00s
```

Был запущен только тест с названием `one_hundred`; два других теста не соответствовали этому названию. Результаты теста с помощью вывода `2 filtered out` дают нам понять, что у нас было больше тестов, но они не были запущены.

Таким образом мы не можем указать имена нескольких тестов; будет использоваться только первое значение, указанное для `cargo test` . Но есть способ запустить несколько тестов.

<a id="filtering-to-run-multiple-tests"></a>

#### Использование фильтров для запуска нескольких тестов

Мы можем указать часть имени теста, и будет запущен любой тест, имя которого соответствует этому значению. Например, поскольку имена двух наших тестов содержат `add`, мы можем запустить эти два, запустив `cargo test add`:

``` console
$ cargo test add
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 2 tests
test tests::add_three_and_two ... ok
test tests::add_two_and_two ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out; finished in 0.00s
```

Эта команда запускала все тесты с `add` в имени и отфильтровывала тест с именем `one_hundred` . Также обратите внимание, что модуль, в котором появляется тест, становится частью имени теста, поэтому мы можем запускать все тесты в модуле, фильтруя имя модуля.

<span id="ignoring-some-tests-unless-specifically-requested"></span>

<a id="ignoring-tests-unless-specifically-requested"></a>

### Игнорирование тестов без явного запроса

Бывает, что некоторые тесты требуют продолжительного времени для своего исполнения, и вы хотите исключить их из исполнения при запуске `cargo test`. Вместо перечисления в командной строке всех тестов, которые вы хотите запускать, вы можете аннотировать тесты, требующие много времени для прогона, атрибутом `ignore`, чтобы исключить их, как показано здесь:

Файл: src/lib.rs

``` rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }

    #[test]
    #[ignore]
    fn expensive_test() {
        // code that takes an hour to run
    }
}
```

После `#[test]` мы добавляем строку `#[ignore]` в тест, который хотим исключить. Теперь, когда мы запускаем наши тесты, `it_works` запускается, а `expensive_test` игнорируется:

``` console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.60s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 2 tests
test tests::expensive_test ... ignored
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 1 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Функция `expensive_test` помечена как `ignored`. Если вы хотите выполнить только проигнорированные тесты, вы можете воспользоваться командой `cargo test -- --ignored`:

``` console
$ cargo test -- --ignored
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::expensive_test ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Управляя тем, какие тесты запускать, вы можете быть уверены, что результаты вашего `cargo test` будут быстрыми. Когда вы дойдёте до момента, где имеет смысл проверить результаты тестов `ignored`, и у вас есть время дождаться их результатов, вы можете запустить их с помощью `cargo test -- --ignored`. Если вы хотите запустить все тесты независимо от того, игнорируются они или нет, выполните `cargo test -- --include-ignored`.
