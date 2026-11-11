<a id="streams"></a>

# 9. Файлы, TCP и границы сообщений

<a id="partial-read"></a>

## `read` возвращает часть данных

Файл и TCP-поток можно читать через типаж `std::io::Read`. Его метод `read` получает буфер и возвращает число реально прочитанных байтов. Этот результат может быть меньше длины буфера, даже если данные ещё придут позже.

Использовать нужно `&buffer[..n]`, а не весь буфер. Байты после `n` не являются новым прочитанным содержимым. Если буфер непустой и `read` вернул 0, это обычно конец доступного потока. Для некоторых источников, например растущего файла, позднее могут появиться новые данные.

`read_exact` делает необходимое число чтений, чтобы заполнить весь заданный буфер. Если поток заканчивается раньше, возвращается `UnexpectedEof`. После ошибки нельзя считать буфер полноценным сообщением или надёжно предполагать, сколько байтов было прочитано.

Справка: [`Read::read`](https://doc.rust-lang.org/std/io/trait.Read.html#tymethod.read), [`Read::read_exact`](https://doc.rust-lang.org/std/io/trait.Read.html#method.read_exact).

<a id="tcp-framing"></a>

## TCP даёт поток байтов

Отправитель вызвал запись два раза: для `ABC` и `DEF`. Получатель может увидеть `A`, затем `BCDE`, затем `F`, либо все шесть байтов за один вызов. TCP сохраняет порядок байтов, но границы вызовов записи не служат границами сообщений.

Прикладная программа сама задаёт **framing** — правило выделения сообщений. Частые варианты: фиксированная длина, разделитель с правилами экранирования, заголовок с длиной. Для произвольных бинарных данных удобно записать длину, затем ровно столько байтов.

Справка: [RFC 9293, модель TCP](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2).

<a id="length-prefix"></a>

## Кадр с четырёхбайтовой длиной

В примере длина полезной нагрузки — `u32` big-endian. Лимит — 64 KiB. Нулевая длина допустима. Функция ожидает **обязательный** следующий кадр: конец потока, в том числе до заголовка, возвращает ошибку.

```rust
use std::io::{self, Read, Write};

const MAX_FRAME: usize = 64 * 1024;

fn read_frame<R: Read>(reader: &mut R) -> io::Result<Vec<u8>> {
    let mut header = [0u8; 4];
    reader.read_exact(&mut header)?;
    let len = usize::try_from(u32::from_be_bytes(header))
        .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "length"))?;
    if len > MAX_FRAME {
        return Err(io::Error::new(io::ErrorKind::InvalidData, "too large"));
    }
    let mut payload = vec![0u8; len];
    reader.read_exact(&mut payload)?;
    Ok(payload)
}

fn write_frame<W: Write>(writer: &mut W, payload: &[u8]) -> io::Result<()> {
    if payload.len() > MAX_FRAME {
        return Err(io::Error::new(io::ErrorKind::InvalidInput, "too large"));
    }
    let len = u32::try_from(payload.len())
        .map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "length"))?;
    writer.write_all(&len.to_be_bytes())?;
    writer.write_all(payload)
}

fn main() -> io::Result<()> {
    let mut wire = Vec::new();
    write_frame(&mut wire, b"ABC")?;
    write_frame(&mut wire, "Ж".as_bytes())?;
    assert_eq!(&wire[..4], &[0, 0, 0, 3]);

    let mut reader = &wire[..];
    assert_eq!(read_frame(&mut reader)?, b"ABC");
    assert_eq!(read_frame(&mut reader)?, "Ж".as_bytes());
    assert!(reader.is_empty());
    assert!(read_frame(&mut reader).is_err());
    Ok(())
}
```

Лимит проверяется **до** выделения памяти. `write_all` тоже может сделать несколько операций записи. Для `File` или `TcpStream` интерфейс функций остаётся тем же: они работают с любым подходящим `Read` и `Write`.

Справка: [`Write::write_all`](https://doc.rust-lang.org/std/io/trait.Write.html#method.write_all).

<a id="stream-eof"></a>

## Нормальный конец и оборванное сообщение

В последовательности кадров полезно различать отсутствие следующего кадра и усечение уже начавшегося. Можно прочитать один первый байт заголовка отдельным вызовом с обработкой `Interrupted`: 0 означает нормальный конец; после полученного первого байта `read_exact` дочитывает остальные три, а их отсутствие — ошибку. Интерфейс тогда может возвращать `Result<Option<Vec<u8>>, Error>`.

Простое правило «любой `UnexpectedEof` означает нормальный конец» скрывает потерю части заголовка или полезной нагрузки. Наш короткий листинг намеренно возвращает ошибку во всех таких случаях. Для production-интерфейса политику завершения нужно определить отдельно.

<a id="stream-limits"></a>

## Что ещё важно в сети

Лимит размера защищает от чрезмерного запроса памяти, но не ограничивает время ожидания. Клиент может прислать заголовок и затем перестать присылать тело. Для блокирующего `TcpStream` доступны тайм-ауты; для общего времени операции приложению может понадобиться собственный дедлайн.

`BufReader` уменьшает число обращений к нижнему источнику при мелких чтениях, но сам не выделяет сообщения. Не создавай новый `BufReader` для каждого кадра: он мог заранее прочитать часть следующего кадра в свой внутренний буфер. Сохраняй один буферизированный читатель на поток.

UDP сохраняет границы датаграмм, но их доставка и порядок не гарантированы. Слишком маленький буфер приёма может потерять часть датаграммы. Кадрирование TCP и пакетный обмен UDP требуют разных решений.

Справка: [`TcpStream`](https://doc.rust-lang.org/std/net/struct.TcpStream.html), [`BufReader`](https://doc.rust-lang.org/std/io/struct.BufReader.html), [`UdpSocket::recv`](https://doc.rust-lang.org/std/net/struct.UdpSocket.html#method.recv).

**Проверь себя.** Почему нельзя ожидать, что один `write_all` соответствует одному `read`? Зачем сначала проверять длину? Почему новый `BufReader` на каждом кадре может потерять данные?
