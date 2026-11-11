<a id="cargo-workspaces"></a>

## Рабочие пространства Cargo

В главе 12 мы создали пакет, который включал в себя бинарный и библиотечный крейты. По мере развития вашего проекта может возникнуть ситуация, когда библиотечный крейт будет становиться все больше, и вы захотите разделить ваш пакет на несколько библиотечных крейтов. Cargo предоставляет функциональность под названием *workspaces*, которая помогает управлять несколькими взаимосвязанными пакетами, которые разрабатываются в тандеме.

<a id="creating-a-workspace"></a>

### Создание рабочего пространства

*Workspace* - это набор пакетов, которые используют один и тот же *Cargo.lock* и директорию для хранения результатов компиляции. Давайте создадим проект с использованием *workspace* - мы будем использовать тривиальный код, чтобы сосредоточиться на структуре рабочего пространства. Существует несколько способов структурировать рабочую область, но мы покажем только один из них. У нас будет рабочая область, содержащая двоичный файл и две библиотеки. Двоичный файл, который обеспечивает основную функциональность, будет зависеть от двух библиотек. Одна библиотека предоставит функцию `add_one`, а вторая - `add_two`. Эти три крейта будут частью одного *workspace*. Начнём с создания каталога для рабочего окружения:

``` console
$ mkdir add
$ cd add
```

Затем в каталоге *add* создадим *Cargo.toml* с настройками всего рабочего пространства. Раздела `[package]` в нём не будет: вместо него файл начинается с `[workspace]`, куда можно добавлять участников. Также явно выберем новейшую версию алгоритма разрешения зависимостей Cargo, задав `resolver` равным `"3"`:

Файл: Cargo.toml

``` toml
[workspace]
resolver = "3"
```

Затем мы создадим исполняемый крейт `adder`, запустив команду `cargo new` в каталоге *add*:

``` console
$ cargo new adder
     Created binary (application) `adder` package
      Adding `adder` as member of workspace at `file:///projects/add`
```

Вызов `cargo new` внутри рабочего пространства также автоматически добавляет созданный пакет в ключ `members` раздела `[workspace]` корневого *Cargo.toml*:

``` toml
[workspace]
resolver = "3"
members = ["adder"]
```

На этом этапе мы можем создать рабочее пространство, запустив команду `cargo build`. Файлы в каталоге *add* должны выглядеть следующим образом:

``` text
├── Cargo.lock
├── Cargo.toml
├── adder
│   ├── Cargo.toml
│   └── src
│       └── main.rs
└── target
```

Рабочая область содержит на верхнем уровне один каталог *target*, в который будут помещены скомпилированные артефакты; пакет `adder` не имеет собственного каталога *target*. Даже если мы запустим `cargo build` из каталога *adder*, скомпилированные артефакты все равно окажутся в *add/target*, а не в *add/adder/target*. Cargo так определил директорию *target* в рабочем пространстве, потому что крейты в рабочем пространстве должны зависеть друг от друга. Если бы каждый крейт имел свой собственный каталог *target*, каждому крейту пришлось бы перекомпилировать каждый из других крейтов в рабочем пространстве, чтобы поместить артефакты в свой собственный каталог *target*. Благодаря совместному использованию единого каталога *target* крейты могут избежать ненужной перекомпиляции.

<a id="creating-the-second-package-in-the-workspace"></a>

### Добавление второго крейта в рабочее пространство

Создадим ещё один пакет рабочего пространства, `add_one`. Сгенерируем новый библиотечный крейт с этим именем:

``` console
$ cargo new add_one --lib
     Created library `add_one` package
      Adding `add_one` as member of workspace at `file:///projects/add`
```

Теперь корневой *Cargo.toml* содержит путь *add_one* в списке `members`:

Файл: Cargo.toml

``` toml
[workspace]
resolver = "3"
members = ["adder", "add_one"]
```

Ваш каталог *add* должен теперь иметь следующие каталоги и файлы:

``` text
├── Cargo.lock
├── Cargo.toml
├── add_one
│   ├── Cargo.toml
│   └── src
│       └── lib.rs
├── adder
│   ├── Cargo.toml
│   └── src
│       └── main.rs
└── target
```

В файле *add_one/src/lib.rs* добавим функцию `add_one`:

Файл: add_one/src/lib.rs

``` rust
pub fn add_one(x: i32) -> i32 {
    x + 1
}
```

Теперь мы можем сделать так, чтобы пакет `adder` с нашим исполняемым файлом зависел от пакета `add_one`, содержащего нашу библиотеку. Сначала нам нужно добавить зависимость пути от `add_one` в *adder/Cargo.toml*.

Файл: adder/Cargo.toml

``` toml
[dependencies]
add_one = { path = "../add_one" }
```

Cargo не исходит из того, что крейты в рабочем пространстве могут зависеть друг от друга, поэтому нам необходимо явно указать отношения зависимости.

Теперь воспользуемся функцией `add_one` из крейта `add_one` в крейте `adder`. Откройте *adder/src/main.rs* и измените `main`, добавив вызов `add_one`, как в листинге 14-7.

Файл: `adder/src/main.rs`

``` rust
fn main() {
    let num = 10;
    println!("Hello, world! {num} plus one is {}!", add_one::add_one(num));
}
```

Листинг 14-7: Использование функционала библиотечного крейта `add_one` в крейте `adder`

Давайте соберём рабочее пространство, запустив команду `cargo build` в каталоге верхнего уровня *add*!

``` console
$ cargo build
   Compiling add_one v0.1.0 (file:///projects/add/add_one)
   Compiling adder v0.1.0 (file:///projects/add/adder)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.22s
```

Чтобы запустить бинарный крейт из каталога *add*, нам нужно указать какой пакет из рабочей области мы хотим использовать с помощью аргумента `-p` и названия пакета в команде `cargo run`:

``` console
$ cargo run -p adder
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/adder`
Hello, world! 10 plus one is 11!
```

Запуск кода из *adder/src/main.rs*, который зависит от `add_one`.

<span id="depending-on-an-external-package-in-a-workspace"></span>

<a id="depending-on-an-external-package"></a>

### Зависимость от внешнего пакета

Обратите внимание, что рабочая область имеет один единственный файл *Cargo.lock* на верхнем уровне, а не содержит *Cargo.lock* в каталоге каждого крейта. Это гарантирует, что все крейты используют одну и ту же версию всех зависимостей. Если мы добавим пакет `rand` в файлы *adder/Cargo.toml* и *add_one/Cargo.toml*, Cargo сведёт их оба к одной версии `rand` и запишет её в один *Cargo.lock*. Если заставить все крейты в рабочей области использовать одни и те же зависимости, то это будет означать, что крейты всегда будут совместимы друг с другом. Давайте добавим крейт `rand` в раздел `[dependencies]` в файле *add_one/Cargo.toml*, чтобы мы могли использовать крейт `rand` в крейте `add_one`:

Файл: add_one/Cargo.toml

``` toml
[dependencies]
rand = "0.10.1"
```

Теперь мы можем добавить `use rand;` в файл *add_one/src/lib.rs* и сделать сборку рабочего пространства, запустив `cargo build` в каталоге *add*, что загрузит и скомпилирует `rand` крейт:

``` console
$ cargo build
    Updating crates.io index
  Downloaded rand v0.10.1
   --snip--
   Compiling rand v0.10.1
   Compiling add_one v0.1.0 (file:///projects/add/add_one)
warning: unused import: `rand`
 --> add_one/src/lib.rs:1:5
  |
1 | use rand;
  |     ^^^^
  |
  = note: `#[warn(unused_imports)]` (part of `#[warn(unused)]`) on by default

warning: `add_one` (lib) generated 1 warning (run `cargo fix --lib -p add_one` to apply 1 suggestion)
   Compiling adder v0.1.0 (file:///projects/add/adder)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.95s
```

Файл *Cargo.lock* верхнего уровня теперь содержит информацию о зависимости `add_one` к крейту `rand`. Тем не менее, не смотря на то что `rand` использован где-то в рабочем пространстве, мы не можем использовать его в других крейтах рабочего пространства, пока не добавим крейт `rand` в отдельные *Cargo.toml* файлы. Например, если мы добавим `use rand;` в файл *adder/src/main.rs* крейта `adder`, то получим ошибку:

``` console
$ cargo build
  --snip--
   Compiling adder v0.1.0 (file:///projects/add/adder)
error[E0432]: unresolved import `rand`
 --> adder/src/main.rs:2:5
  |
2 | use rand;
  |     ^^^^ no external crate `rand`
```

Чтобы исправить это, отредактируйте файл *Cargo.toml* для пакета `adder` и укажите, что `rand` также является его зависимостью. При сборке пакета `adder` `rand` будет добавлен в список зависимостей для `adder` в *Cargo.lock*, но никаких дополнительных копий `rand` загружено не будет. Cargo позаботился о том, чтобы все крейты во всех пакетах рабочей области, использующих пакет `rand`, использовали одну и ту же версию, экономя нам место и гарантируя, что все крейты в рабочей области будут совместимы друг с другом.

Если крейты рабочего пространства указывают несовместимые версии одной зависимости, Cargo разрешит каждую из них, но всё равно постарается использовать как можно меньше разных версий.

<a id="adding-a-test-to-a-workspace"></a>

### Добавление теста в рабочее пространство

В качестве ещё одного улучшения давайте добавим тест функции `add_one::add_one` в `add_one`:

Файл: add_one/src/lib.rs

``` rust
pub fn add_one(x: i32) -> i32 {
    x + 1
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        assert_eq!(3, add_one(2));
    }
}
```

Теперь запустите `cargo test` в каталоге верхнего уровня *add*. Запуск `cargo test` в рабочем пространстве, структурированном подобно этому, запустит тесты для всех крейтов в рабочем пространстве:

``` console
$ cargo test
   Compiling add_one v0.1.0 (file:///projects/add/add_one)
   Compiling adder v0.1.0 (file:///projects/add/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.20s
     Running unittests src/lib.rs (target/debug/deps/add_one-93c49ee75dc46543)

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/debug/deps/adder-3a47283c568d2b6a)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests add_one

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Первая секция вывода показывает, что тест `it_works` в крейте `add_one` прошёл. Следующая секция показывает, что в крейте `adder` не было обнаружено ни одного теста, а последняя секция показывает, что в крейте `add_one` не было найдено ни одного теста документации.

Мы также можем запустить тесты для одного конкретного крейта в рабочем пространстве из каталог верхнего уровня с помощью флага `-p` и указанием имени крейта для которого мы хотим запустить тесты:

``` console
$ cargo test -p add_one
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.00s
     Running unittests src/lib.rs (target/debug/deps/add_one-93c49ee75dc46543)

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests add_one

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Эти выходные данные показывают, что выполнение `cargo test` запускает только тесты для крейта `add_one` и не запускает тесты крейта `adder`.

Если вы соберётесь опубликовать крейты из рабочего пространства на [crates.io](https://crates.io/), каждый крейт будет необходимо будет опубликовать отдельно. Подобно `cargo test`, мы можем опубликовать конкретный крейт из нашей рабочей области, используя флаг `-p` и указав имя крейта, который мы хотим опубликовать.

Для дополнительной практики добавьте крейт `add_two` в данное рабочее пространство аналогичным способом, как делали с крейт `add_one` !

По мере роста проекта рассмотрите возможность использования рабочих областей: легче понять небольшие, отдельные компоненты, чем один большой кусок кода. Кроме того, хранение крейтов в рабочем пространстве может облегчить координацию между крейтами, если они часто изменяются параллельно.
