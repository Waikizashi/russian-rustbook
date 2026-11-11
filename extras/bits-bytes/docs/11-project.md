<a id="project"></a>

# 11. Практика: формат Byte Note

<a id="project-idea"></a>

## Что мы соберём

Byte Note — учебный формат одного небольшого сообщения. Он объединяет знакомые приёмы: сигнатуру, битовые поля, флаги, длину, порядок байтов, UTF-8 и CRC. Формат придуман для этого дополнения и не является стандартным сетевым протоколом.

Сообщение содержит числовой тип `kind`, два флага, номер `sequence` и полезную нагрузку. Один флаг сообщает, что нагрузка — UTF-8-текст; другой помечает сообщение как срочное. Срочность здесь только метаданные: код не задаёт ей планирование или гарантии доставки.

<a id="project-spec"></a>

## Спецификация

| Смещение | Байтов | Поле | Правило |
|---:|---:|---|---|
| 0 | 4 | Сигнатура | ASCII `BYTE`, то есть `42 59 54 45` |
| 4 | 1 | Версия и тип | Биты 7–5: версия 1; биты 4–0: `kind`, 0–31 |
| 5 | 1 | Флаги | Бит 0: UTF-8; бит 1: срочность; остальные должны быть 0 |
| 6 | 2 | Длина | Число байтов нагрузки, `u16`, big-endian, не более 4096 |
| 8 | 4 | Номер | `u32`, little-endian |
| 12 | `length` | Нагрузка | Произвольные байты; при флаге UTF-8 обязана быть корректным текстом |
| `12 + length` | 4 | CRC | CRC-32/ISO-HDLC всех предшествующих байтов, `u32`, big-endian |

Размер полного сообщения — `16 + length` байтов. Вход декодера должен содержать ровно одно сообщение. Пустая нагрузка разрешена. Несовпадающие сигнатура, версия, CRC, длина или неизвестные флаги — ошибки.

Смешение endian здесь намеренное: оно позволяет проверить, что ты читаешь правило **каждого поля**. Для собственного реального формата обычно удобнее выбрать единый порядок и уменьшить число возможностей ошибиться.

Номер — обычное значение 0–`u32::MAX`. Этот пример не определяет порядок доставки, защиту от повторов и правило перехода через максимум. Если они понадобятся, их следует отдельно добавить в протокол.

<a id="project-golden"></a>

## Разбор одного сообщения вручную

Возьмём `kind = 1`, флаг UTF-8, `sequence = 0x01020304`, текст `AЖ`. Его UTF-8-нагрузка занимает три байта: `41 D0 96`.

| Часть | Байты | Объяснение |
|---|---|---|
| Сигнатура | `42 59 54 45` | `BYTE` |
| Версия и тип | `21` | `(1 << 5) \| 1` |
| Флаги | `01` | UTF-8 включён |
| Длина | `00 03` | 3, big-endian |
| Номер | `04 03 02 01` | `0x01020304`, little-endian |
| Нагрузка | `41 D0 96` | `AЖ` в UTF-8 |
| CRC | `22 F4 2A 3A` | Контрольная сумма первых 15 байтов |

Все байты вместе:

```text
42 59 54 45 21 01 00 03 04 03 02 01 41 D0 96 22 F4 2A 3A
```

Этот вектор рассчитан также независимой реализацией CRC в Python. В тестах он проверяется отдельно от обычного цикла «закодировать и декодировать».

<a id="project-types"></a>

## Код: значения и ошибки

Полный файл `crates/byte-note/src/lib.rs` ниже показан по частям. В архиве это единая библиотека без внешних зависимостей. `Message` возвращает ссылку на нагрузку, поэтому декодирование не копирует её.

```rust
pub const MAX_PAYLOAD: usize = 4096;
pub const UTF8: u8 = 1 << 0;
pub const URGENT: u8 = 1 << 1;
const KNOWN_FLAGS: u8 = UTF8 | URGENT;
const HEADER_LEN: usize = 12;
const CRC_LEN: usize = 4;

#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    Truncated,
    Magic,
    Version,
    Kind,
    Flags,
    TooLarge,
    TrailingBytes,
    Checksum,
    Utf8,
}

#[derive(Debug, PartialEq, Eq)]
pub struct Message<'a> {
    pub kind: u8,
    pub flags: u8,
    pub sequence: u32,
    pub payload: &'a [u8],
}

impl<'a> Message<'a> {
    pub fn text(&self) -> Result<Option<&'a str>, Error> {
        if self.flags & UTF8 == 0 {
            return Ok(None);
        }
        std::str::from_utf8(self.payload)
            .map(Some)
            .map_err(|_| Error::Utf8)
    }
}
```

У ошибок нет большого механизма форматирования: для этого учебного проекта достаточно `Debug`. В пользовательском приложении добавь понятное описание через `Display` и реализацию `std::error::Error`.

<a id="project-crc"></a>

## Код: контрольная сумма

```rust
pub fn crc32(data: &[u8]) -> u32 {
    let mut crc = 0xFFFF_FFFFu32;
    for &byte in data {
        crc ^= u32::from(byte);
        for _ in 0..8 {
            crc = if crc & 1 != 0 {
                (crc >> 1) ^ 0xEDB8_8320
            } else {
                crc >> 1
            };
        }
    }
    !crc
}
```

CRC охватывает сигнатуру, заголовок и нагрузку. Собственное поле CRC в расчёт не входит. Четыре байта итогового результата записываются big-endian. Это правило записи независимо от того, в какую сторону сдвигает биты сам алгоритм CRC.

<a id="project-encode"></a>

## Код: упаковка

```rust
pub fn encode(kind: u8, flags: u8, sequence: u32, payload: &[u8]) -> Result<Vec<u8>, Error> {
    if kind > 31 {
        return Err(Error::Kind);
    }
    if flags & !KNOWN_FLAGS != 0 {
        return Err(Error::Flags);
    }
    if payload.len() > MAX_PAYLOAD {
        return Err(Error::TooLarge);
    }
    if flags & UTF8 != 0 {
        std::str::from_utf8(payload).map_err(|_| Error::Utf8)?;
    }
    let len = u16::try_from(payload.len()).map_err(|_| Error::TooLarge)?;
    let mut out = Vec::with_capacity(HEADER_LEN + payload.len() + CRC_LEN);
    out.extend_from_slice(b"BYTE");
    out.push((1 << 5) | kind);
    out.push(flags);
    out.extend_from_slice(&len.to_be_bytes());
    out.extend_from_slice(&sequence.to_le_bytes());
    out.extend_from_slice(payload);
    let checksum = crc32(&out);
    out.extend_from_slice(&checksum.to_be_bytes());
    Ok(out)
}
```

Кодировщик проверяет диапазон типа сообщения, известные флаги, лимит размера и обещанную кодировку. Только после этого он создаёт выходной буфер. Поля добавляются в порядке спецификации с явными преобразованиями endian.

Вызовы `try_from` фиксируют требование «без потерь», даже когда проверка 4096 уже доказывает, что длина помещается в `u16`. Это помогает сохранить корректность, если лимит изменится позже.

<a id="project-decode"></a>

## Код: чтение

```rust
pub fn decode(data: &[u8]) -> Result<Message<'_>, Error> {
    let header = data.get(..HEADER_LEN).ok_or(Error::Truncated)?;
    if &header[..4] != b"BYTE" {
        return Err(Error::Magic);
    }
    if header[4] >> 5 != 1 {
        return Err(Error::Version);
    }
    let kind = header[4] & 0x1F;
    let flags = header[5];
    if flags & !KNOWN_FLAGS != 0 {
        return Err(Error::Flags);
    }
    let len = usize::from(u16::from_be_bytes([header[6], header[7]]));
    if len > MAX_PAYLOAD {
        return Err(Error::TooLarge);
    }
    let crc_offset = HEADER_LEN.checked_add(len).ok_or(Error::TooLarge)?;
    let required = crc_offset.checked_add(CRC_LEN).ok_or(Error::TooLarge)?;
    if data.len() < required {
        return Err(Error::Truncated);
    }
    if data.len() > required {
        return Err(Error::TrailingBytes);
    }
    let sequence = u32::from_le_bytes([header[8], header[9], header[10], header[11]]);
    let checksum = u32::from_be_bytes([
        data[crc_offset],
        data[crc_offset + 1],
        data[crc_offset + 2],
        data[crc_offset + 3],
    ]);
    if crc32(&data[..crc_offset]) != checksum {
        return Err(Error::Checksum);
    }
    let payload = &data[HEADER_LEN..crc_offset];
    if flags & UTF8 != 0 {
        std::str::from_utf8(payload).map_err(|_| Error::Utf8)?;
    }
    Ok(Message {
        kind,
        flags,
        sequence,
        payload,
    })
}
```

Декодер доказывает наличие 12-байтового заголовка перед обращением к полям. Затем проверяет длину всего сообщения, и только после этого обращается к нагрузке и четырём байтам CRC. `checked_add` делает вычисление требуемого размера явным.

Неправильный вход возвращает ошибку. Для чтения нагрузки используются индексы, безопасность которых уже следует из проверки точной длины. Если переписать порядок этих действий, такое доказательство придётся пересмотреть.

Проверка UTF-8 выполняется только при соответствующем флаге. Байты `[0xFF, 0x00]` допустимы как бинарная нагрузка, но не как UTF-8-текст. Метод `text()` у результата позволяет различить текст и бинарные данные.

<a id="project-run"></a>

## Запуск и проверка

Из корня репозитория:

```sh
cargo test -p byte-note
cargo test -p byte-note --release
cargo run -p byte-note --example demo
```

Пример `demo` создаёт сообщение, печатает его в hex и читает обратно. Тесты находятся в `tests/codec.rs`. Они проверяют заранее заданный вектор, пустую и предельную нагрузку, усечение на каждой позиции, неизвестные флаги, неверную версию, избыток данных, повреждение CRC и неверный UTF-8 с пересчитанной CRC.

Последний тест принципиален: если просто испортить текстовый байт без обновления CRC, декодер остановится на контрольной сумме, и проверка UTF-8 останется непроверенной.

<a id="project-framing"></a>

## Передача через поток

Для одного сообщения, уже находящегося в памяти, используй `decode(&bytes)`. Для файла с несколькими сообщениями или TCP можно обернуть каждое полное сообщение в кадр из [раздела 9](09-streams.md#length-prefix): сначала внешняя длина, затем байты Byte Note.

Внешняя длина обозначает **полный** Byte Note вместе с заголовком и CRC. Внутренняя длина обозначает только нагрузку. При таком обёртывании проверяются оба ограничения; максимальное сообщение Byte Note занимает 4112 байтов.

Этот проект подходит для обучения и расширения. Он не предоставляет аутентификацию, шифрование, управление ключами, повторную доставку или сетевые дедлайны. Когда приложение потребует эти свойства, они должны быть реализованы отдельными механизмами с подходящими спецификациями.

**Попробуй расширить.** Добавь чтение нескольких сообщений из среза с возвращением остатка. Сохрани строгий декодер одного сообщения отдельно. Затем добавь новый тип нагрузки и тесты его допустимых значений, не меняя правила старых сообщений.
