<a id="appendix-d-useful-development-tools"></a>

## Приложение D: Полезные инструменты разработки

В этом дополнении мы расскажем про часто используемые средства разработки, предоставляемые Rust. Мы рассмотрим автоматическое форматирование, быстрый путь исправления предупреждений, линтер, и интеграцию с IDE.

<a id="automatic-formatting-with-rustfmt"></a>

### Автоматическое форматирование с `rustfmt`

Инструмент `rustfmt` переформатирует ваш код в соответствии со стилем кода сообщества. Многие совместные проекты используют `rustfmt`, чтобы предотвратить споры о том, какой стиль использовать при написании Rust: все форматируют свой код с помощью этого инструмента.

По умолчанию Rust устанавливается вместе с `rustfmt`, поэтому программы `rustfmt` и `cargo-fmt` уже должны быть в вашей системе. Эти команды похожи на `rustc` и `cargo`: `rustfmt` предоставляет более тонкий контроль, а `cargo-fmt` понимает соглашения проектов Cargo. Чтобы отформатировать любой проект Cargo, выполните:

``` console
$ cargo fmt
```

Эта команда отформатирует весь код на языке Rust в текущем крейте. Будет изменён только стиль кода, семантика останется прежней. Для большей информации о `rustfmt`, смотрите [документацию](https://github.com/rust-lang/rustfmt).

<a id="fix-your-code-with-rustfix"></a>

### Исправление кода с `rustfix`

Инструмент rustfix включён в установку Rust и может автоматически исправлять предупреждения компилятора с очевидным способом исправления проблемы, скорее всего, подходящим вам. Вероятно, вы уже видели предупреждения компилятора. Например, рассмотрим этот код:

Файл: src/main.rs

``` rust
fn main() {
    let mut x = 42;
    println!("{x}");
}
```

Здесь мы объявляем переменную `x` изменяемой, но нигде её не изменяем. Rust предупреждает об этом:

``` console
$ cargo build
   Compiling myprogram v0.1.0 (file:///projects/myprogram)
warning: variable does not need to be mutable
 --> src/main.rs:2:9
  |
2 |     let mut x = 0;
  |         ----^
  |         |
  |         help: remove this `mut`
  |
  = note: `#[warn(unused_mut)]` on by default
```

Предупреждение предлагает удалить `mut`. Инструмент `rustfix` может автоматически применить эту рекомендацию по команде `cargo fix`:

``` console
$ cargo fix
    Checking myprogram v0.1.0 (file:///projects/myprogram)
      Fixing src/main.rs (1 fix)
    Finished dev [unoptimized + debuginfo] target(s) in 0.59s
```

Когда посмотрим в *src/main.rs* снова, мы увидим что `cargo fix` изменил наш код:

Файл: src/main.rs

``` rust
fn main() {
    let x = 42;
    println!("{x}");
}
```

Теперь переменная `x` неизменяема, и предупреждение больше не появляется.

Также Вы можете использовать команду `cargo fix` для перемещения вашего кода между различными редакциями Rust. Редакции будут рассмотрены в дополнении Д.

<a id="more-lints-with-clippy"></a>

### Больше проверок с Clippy

Clippy — набор диагностических проверок, анализирующих код, помогающих находить распространённые ошибки и улучшать программы Rust. Clippy входит в стандартную установку Rust.

Для запуска проверок Clippy’s для проекта Cargo, введите следующее:

``` console
$ cargo clippy
```

Например, скажем что Вы хотите написать программу, в которой будет использоваться приближенная математическая константа, такая как число Пи, как в следующей программе:

Файл: `src/main.rs`

``` rust
fn main() {
    let x = 3.1415;
    let r = 8.0;
    println!("the area of the circle is {}", x * r * r);
}
```

Запуск `cargo clippy` для этого проекта вызовет следующую ошибку:

``` text
error: approximate value of `f{32, 64}::consts::PI` found
 --> src/main.rs:2:13
  |
2 |     let x = 3.1415;
  |             ^^^^^^
  |
  = note: `#[deny(clippy::approx_constant)]` on by default
  = help: consider using the constant directly
  = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#approx_constant
```

Эта ошибка сообщает, что в Rust уже есть более точная константа `PI` и использование её сделает программу правильнее. Следует изменить код, воспользовавшись `PI`.

Следующий код не вызывает ни ошибок, ни предупреждений Clippy:

Файл: `src/main.rs`

``` rust
fn main() {
    let x = std::f64::consts::PI;
    let r = 8.0;
    println!("the area of the circle is {}", x * r * r);
}
```

Для большей информации о Clippy смотрите [документацию](https://github.com/rust-lang/rust-clippy).

<a id="ide-integration-using-rust-analyzer"></a>

### Интеграция с IDE с помощью `rust-analyzer`

Чтобы облегчить интеграцию с IDE, сообщество Rust рекомендует использовать [`rust-analyzer`](https://rust-analyzer.github.io). Этот инструмент представляет собой набор ориентированных на компилятор утилит, которые используют [Language Server Protocol](http://langserver.org/), который является спецификацией для взаимодействия IDE и языков программирования друг с другом. Разные клиенты могут использовать `rust-analyzer`, например [подключаемый модуль анализатора Rust для Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer).

Посетите домашнюю страницу проекта `rust-analyzer` для получения инструкций по установке, затем установите поддержку языкового сервера в конкретной среде IDE. Ваша IDE получит такие возможности, как автозаполнение, переход к определению и встроенные ошибки.
