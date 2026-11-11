<a id="reference"></a>

# Шпаргалка и источники

<a id="cheatsheet"></a>

## Шпаргалка

| Задача | Приём |
|---|---|
| Установить флаг | `x \|= MASK` |
| Сбросить флаг | `x &= !MASK` |
| Переключить флаг | `x ^= MASK` |
| Есть хотя бы один | `(x & MASK) != 0` |
| Есть все | `(x & MASK) == MASK` |
| Есть неизвестные биты | `(x & !KNOWN) != 0` |
| Извлечь поле | `(x >> SHIFT) & MASK` |
| Проверить диапазон преобразования | `u8::try_from(value)` |
| Проверить числовое сложение | `checked_add` |
| Проверить величину сдвига | `checked_shl`, `checked_shr` |
| Записать число фиксированным порядком | `to_be_bytes`, `to_le_bytes` |
| Прочитать число | `from_be_bytes`, `from_le_bytes` |
| Безопасно взять часть буфера | `slice.get(range)` |
| Проверить UTF-8 без копии | `std::str::from_utf8` |
| Посчитать байты текста | `str.len()` |
| Прочитать ровно N байтов | `Read::read_exact` |
| Записать все байты | `Write::write_all` |

`checked_shl` проверяет допустимость **сдвига**, а не сохранность значения. `capacity` не равно `len`. `char` не равно байту или графемному кластеру. Native endian не задаёт переносимого формата. CRC не является проверкой подлинности.

<a id="glossary"></a>

## Термины

| Термин | Смысл |
|---|---|
| Бит | Двоичная цифра, 0 или 1 |
| Байт | Восемь битов в используемой здесь модели |
| Старший / младший бит | Позиция с большим / меньшим весом |
| Hex | Шестнадцатеричная запись |
| Маска | Набор выбранных битовых позиций |
| Флаг | Отдельное логическое свойство в битовом поле |
| Endianness | Порядок байтов многобайтового значения |
| Buffer | Область, содержащая последовательность данных |
| Slice | Срез; заимствованное представление последовательности |
| Payload | Полезная нагрузка сообщения |
| Parser | Код, разбирающий данные по правилам формата |
| Framing | Правило выделения сообщений в потоке |
| Alignment | Выравнивание значения в памяти |
| Padding | Байты заполнения между полями или в конце |
| Varint | Целое в представлении переменной длины |
| CRC | Семейство циклических контрольных сумм |

<a id="next"></a>

## Где продолжать

Если чтение байтов стало понятным, следующим шагом может быть конкретный формат: простой заголовок изображения, собственный лог событий или небольшое сетевое сообщение. Начинай со спецификации и нескольких вручную рассчитанных примеров. При разборе чужого формата используй его точные правила; похожие названия полей и алгоритмов не гарантируют совместимости.

Для сложного production-протокола полезны генераторы сериализации и существующие реализации. Даже тогда знания о длинах, кодировках и границах сообщений помогают найти ошибки и понять ограничения.

<a id="sources"></a>

## Первичные источники

Технические правила сверены 30 сентября 2026 года. Текст дополнения и его учебные примеры написаны самостоятельно; это не перевод отдельной официальной книги. Ссылки ниже позволяют проверить правила и получить подробный справочник.

1. [The Rust Programming Language](https://doc.rust-lang.org/book/): исходный маршрут изучения языка; главы 3, 4, 8, 9, 11 и 20.
2. [The Rust Reference: числовые литералы](https://doc.rust-lang.org/reference/expressions/literal-expr.html#integer-literal-expressions).
3. [The Rust Reference: операторы и числовые приведения](https://doc.rust-lang.org/reference/expressions/operator-expr.html).
4. [The Rust Reference: расположение типов в памяти](https://doc.rust-lang.org/reference/type-layout.html).
5. [The Rust Reference: неопределённое поведение и недопустимые значения](https://doc.rust-lang.org/reference/behavior-considered-undefined.html).
6. [Стандартная библиотека: `u8`](https://doc.rust-lang.org/std/primitive.u8.html), [`u16`](https://doc.rust-lang.org/std/primitive.u16.html), [`u32`](https://doc.rust-lang.org/std/primitive.u32.html), [`u64`](https://doc.rust-lang.org/std/primitive.u64.html), [`i8`](https://doc.rust-lang.org/std/primitive.i8.html), [`f32`](https://doc.rust-lang.org/std/primitive.f32.html).
7. [Стандартная библиотека: форматирование](https://doc.rust-lang.org/std/fmt/index.html).
8. [Стандартная библиотека: `Vec`](https://doc.rust-lang.org/std/vec/struct.Vec.html) и [срезы](https://doc.rust-lang.org/std/primitive.slice.html).
9. [Стандартная библиотека: `char`](https://doc.rust-lang.org/std/primitive.char.html), [`str`](https://doc.rust-lang.org/std/primitive.str.html), [`String`](https://doc.rust-lang.org/std/string/struct.String.html), [`from_utf8`](https://doc.rust-lang.org/std/str/fn.from_utf8.html).
10. [Cargo Book: профили и проверки переполнения](https://doc.rust-lang.org/cargo/reference/profiles.html#overflow-checks).
11. [Стандартная библиотека: `Read`](https://doc.rust-lang.org/std/io/trait.Read.html), [`Write`](https://doc.rust-lang.org/std/io/trait.Write.html), [`BufReader`](https://doc.rust-lang.org/std/io/struct.BufReader.html), [`TcpStream`](https://doc.rust-lang.org/std/net/struct.TcpStream.html), [`UdpSocket`](https://doc.rust-lang.org/std/net/struct.UdpSocket.html).
12. [Unicode: UTF-8, UTF-16, UTF-32 и BOM](https://www.unicode.org/faq/utf_bom.html).
13. [NIST: двоичные префиксы](https://physics.nist.gov/cuu/Units/binary.html).
14. [RFC 4648: Base16, Base32 и Base64](https://www.rfc-editor.org/rfc/rfc4648.html).
15. [RFC 9293: TCP](https://www.rfc-editor.org/rfc/rfc9293.html).
16. [Protocol Buffers: двоичное кодирование](https://protobuf.dev/programming-guides/encoding/).
17. [RFC 1952: gzip и пример вычисления CRC](https://www.rfc-editor.org/rfc/rfc1952.html).

Документация на сайтах обновляется со временем. При работе с более старым компилятором проверяй пометки о версии стабилизации конкретного API. Внешние страницы не включены целиком в EPUB; сам материал и код не требуют подключения к ним.
