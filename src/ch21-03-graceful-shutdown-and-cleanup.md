<a id="graceful-shutdown-and-cleanup"></a>

## Мягкое завершение работы и очистка

Листинг 21-20 асинхронно отвечает на запросы с помощью использования пула потоков, как мы и хотели. Мы получаем некоторые предупреждения про `workers`, `id` и поля `thread`, которые мы не используем напрямую, что напоминает нам о том, что мы не освобождаем все ресурсы. Когда мы используем менее элегантный метод остановки основного потока клавишной комбинацией <span class="keystroke">ctrl-c</span>, все остальные потоки также немедленно останавливаются, даже если они находятся в середине обработки запроса.

Далее, реализуем типаж `Drop` для вызова `join` у каждого потока в пуле, чтобы они могли завершить запросы, над которыми они работают, перед закрытием. Затем мы реализуем способ сообщить потокам, что они должны перестать принимать новые запросы и завершить работу. Чтобы увидеть этот код в действии, мы изменим наш сервер так, чтобы он принимал только два запроса, после чего корректно завершал работу пула потоков.

Заметьте: ничто из дальнейшего не затрагивает части кода, отвечающие за выполнение замыканий. Поэтому всё осталось бы таким же, если бы пул потоков использовался асинхронной средой выполнения.

<a id="implementing-the-drop-trait-on-threadpool"></a>

### Реализация типажа `Drop` для `ThreadPool`

Давайте начнём с реализации `Drop` у нашего пула потоков. Когда пул удаляется, все наши потоки должны объединиться (join), чтобы убедиться, что они завершают свою работу. В листинге 21-22 показана первая попытка реализации `Drop`, код пока не будет работать.

Файл: `src/lib.rs`

``` rust
impl Drop for ThreadPool {
    fn drop(&mut self) {
        for worker in &mut self.workers {
            println!("Shutting down worker {}", worker.id);

            worker.thread.join().unwrap();
        }
    }
}
```

Листинг 21-22: Присоединение (Joining) каждого потока, когда пул потоков выходит из области видимости

Сначала мы пройдёмся по каждому `worker` из пула потоков. Для этого мы используем `&mut` с `self`, потому что нам нужно иметь возможность изменять `worker`. Для каждого обработчика мы выводим сообщение о том, что он завершает работу, а затем вызываем `join` у потока этого обработчика. Для случаев, когда вызов `join` не удался, мы используем `unwrap`, чтобы заставить Rust запаниковать и перейти в режим грубого завершения работы.

Ошибка получаемая при компиляции этого кода:

``` console
$ cargo check
    Checking hello v0.1.0 (file:///projects/hello)
error[E0507]: cannot move out of `worker.thread` which is behind a mutable reference
  --> src/lib.rs:52:13
   |
52 |             worker.thread.join().unwrap();
   |             ^^^^^^^^^^^^^ ------ `worker.thread` moved due to this method call
   |             |
   |             move occurs because `worker.thread` has type `JoinHandle<()>`, which does not implement the `Copy` trait
   |
note: `std::thread::JoinHandle::<T>::join` takes ownership of the receiver `self`, which moves `worker.thread`
  --> /rustc/58cf8f9c35b355199727627d07ae34a4e2846d67/library/std/src/thread/join_handle.rs:149:16

For more information about this error, try `rustc --explain E0507`.
error: could not compile `hello` (lib) due to 1 previous error
```

Ошибка говорит нам, что мы не можем вызвать `join`, потому что у нас есть только изменяемое заимствование каждого `worker`, а `join` забирает во владение свой аргумент. Чтобы решить эту проблему, нам нужно извлечь поток из экземпляра `Worker`, который владеет `thread`, чтобы `join` мог его использовать. Мы сделали это в листинге 18-15: теперь, когда `Worker` хранит в себе `Option<thread::JoinHandle<()>>`, мы можем воспользоваться методом `take` у `Option`, чтобы извлечь значение из варианта `Some`, тем самым оставляя на его месте `None`. Другими словами, в рабочем состоянии `Worker` будет использовать вариант `Some` содержащий `thread`, а когда мы захотим завершить `Worker`, мы заменим `Some` на `None`, чтобы у `Worker` не было потока для работы.

Однако такая потребность возникает только при уничтожении `Worker`. Взамен нам пришлось бы иметь дело с `Option<thread::JoinHandle<()>>` при каждом обращении к `worker.thread`. В идиоматичном Rust `Option` используется часто, но если вы оборачиваете в него заведомо присутствующее значение лишь для обхода подобного ограничения, стоит поискать другой подход, делающий код чище и менее подверженным ошибкам.

Здесь есть более удачная альтернатива — метод `Vec::drain`. Он принимает диапазон удаляемых из вектора элементов и возвращает их итератор. Диапазон `..` удаляет из вектора все значения.

Поэтому обновим реализацию `drop` для `ThreadPool` следующим образом:

Файл: `src/lib.rs`

``` rust
impl Drop for ThreadPool {
    fn drop(&mut self) {
        for worker in self.workers.drain(..) {
            println!("Shutting down worker {}", worker.id);

            worker.thread.join().unwrap();
        }
    }
}
```

Это устраняет ошибку компиляции и не требует других изменений. Учтите: `drop` может вызываться во время паники, и `unwrap` тоже способен вызвать панику. Такая двойная паника немедленно завершает программу и прерывает очистку ресурсов. Для учебного примера это допустимо, но в рабочем коде так делать не рекомендуется.

<a id="signaling-to-the-threads-to-stop-listening-for-jobs"></a>

### Сигнализация потокам прекратить прослушивание получения задач

Теперь, после всех внесённых нами изменений, код компилируется без каких-либо предупреждений. Но плохая новость в том, что этот код всё ещё не работает так, как мы этого хотим. Причина заключается в логике замыканий, запускаемых потоками экземпляров Worker: в данный момент мы вызываем join, но это не приводит к завершению потоков, так как они находятся в бесконечном цикле, ожидая новую задачу. Если мы попытаемся удалить ThreadPool в текущей реализации drop, основной поток навсегда заблокируется в ожидании завершения первого потока из пула.

Чтобы решить эту проблему, нам нужно будет изменить реализацию `drop` в `ThreadPool`, а затем внести изменения в цикл `Worker` .

Сначала изменим `drop` у `ThreadPool`, чтобы явно уничтожить `sender` до ожидания завершения потоков. Изменения показаны в листинге 21-23. В отличие от случая с потоком, здесь действительно нужен `Option`, позволяющий извлечь `sender` из `ThreadPool` с помощью `Option::take`.

Файл: `src/lib.rs`

``` rust
pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: Option<mpsc::Sender<Job>>,
}
// --snip--
impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        // --snip--

        ThreadPool {
            workers,
            sender: Some(sender),
        }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);

        self.sender.as_ref().unwrap().send(job).unwrap();
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        drop(self.sender.take());

        for worker in self.workers.drain(..) {
            println!("Shutting down worker {}", worker.id);

            worker.thread.join().unwrap();
        }
    }
}
```

Листинг 21-23. Явное удаление `sender` перед ожиданием завершения рабочих потоков

Удаление `sender` закрывает канал, что указывает на то, что сообщения больше не будут отправляться. Когда это произойдёт, все вызовы `recv`, выполняемые рабочими процессами в бесконечном цикле, вернут ошибку. В листинге 21-24 мы меняем цикл `Worker` для корректного выхода из него в этом случае, что означает, что потоки завершатся, когда реализация `drop` `ThreadPool` вызовет для них `join`.

Файл: `src/lib.rs`

``` rust
impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || {
            loop {
                let message = receiver.lock().unwrap().recv();

                match message {
                    Ok(job) => {
                        println!("Worker {id} got a job; executing.");

                        job();
                    }
                    Err(_) => {
                        println!("Worker {id} disconnected; shutting down.");
                        break;
                    }
                }
            }
        });

        Worker { id, thread }
    }
}
```

Листинг 21-24: Явный выход из цикла, когда `recv` возвращает ошибку

Чтобы увидеть этот код в действии, давайте изменим `main`, чтобы принимать только два запроса, прежде чем корректно завершить работу сервера как показано в листинге 21-25.

Файл: `src/main.rs`

``` rust
fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(4);

    for stream in listener.incoming().take(2) {
        let stream = stream.unwrap();

        pool.execute(|| {
            handle_connection(stream);
        });
    }

    println!("Shutting down.");
}
```

Код 21-25. Выключение сервера после обслуживания двух запросов с помощью выхода из цикла

Вы бы не хотели, чтобы реальный веб-сервер отключался после обслуживания только двух запросов. Этот код всего лишь демонстрирует, что корректное завершение работы и освобождение ресурсов находятся в рабочем состоянии.

Метод `take` определён в типаже `Iterator` и ограничивает итерацию максимум первыми двумя элементами. `ThreadPool` выйдет из области видимости в конце `main` и будет запущена его реализация `drop`.

Запустите сервер с `cargo run` и сделайте три запроса. Третий запрос должен выдать ошибку и в терминале вы должны увидеть вывод, подобный следующему:

``` console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.41s
     Running `target/debug/hello`
Worker 0 got a job; executing.
Shutting down.
Shutting down worker 0
Worker 3 got a job; executing.
Worker 1 disconnected; shutting down.
Worker 2 disconnected; shutting down.
Worker 3 disconnected; shutting down.
Worker 0 disconnected; shutting down.
Shutting down worker 1
Shutting down worker 2
Shutting down worker 3
```

Вы возможно увидите другой порядок рабочих потоков и напечатанных сообщений. Мы можем увидеть, как этот код работает по сообщениям: “работники” номер 0 и 3 получили первые два запроса. Сервер прекратил принимать соединения после второго подключения, а реализация `Drop` для `ThreadPool` начинает выполняется ещё тогда, когда как работник 3 даже не приступил к выполнению своей работы. Удаление `sender` отключает все рабочие потоки от канала и просит их завершить работу. Каждый рабочий поток при отключении печатает сообщение, а затем пул потоков вызывает `join`, чтобы дождаться, пока каждый из рабочих потоков завершится.

Обратите внимание на один интересный аспект этого конкретного запуска: ThreadPool удалил `sender`, и прежде чем какой-либо из работников получил ошибку, мы попытались присоединить (join) рабочий поток с номером 0. Рабочий поток 0 ещё не получил ошибку от `recv`, поэтому основной поток заблокировался, ожидания завершения потока работника 0. Тем временем, работник 3 получил задание, а затем каждый из рабочих потоков получил ошибку. Когда рабочий поток 0 завершился, основной поток ждал окончания завершения выполнения остальных рабочих потоков. В этот момент все они вышли из своих циклов и остановились.

Примите поздравления! Теперь мы завершили проект; у нас есть базовый веб-сервер, использующий пул потоков для асинхронных ответов. Мы можем выполнить корректное завершение работы сервера, очистив все потоки в пуле.

Вот полный код для справки:

Файл: `src/main.rs`

``` rust
use hello::ThreadPool;
use std::{
    fs,
    io::{BufReader, prelude::*},
    net::{TcpListener, TcpStream},
    thread,
    time::Duration,
};

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(4);

    for stream in listener.incoming().take(2) {
        let stream = stream.unwrap();

        pool.execute(|| {
            handle_connection(stream);
        });
    }

    println!("Shutting down.");
}

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&stream);
    let request_line = buf_reader.lines().next().unwrap().unwrap();

    let (status_line, filename) = match &request_line[..] {
        "GET / HTTP/1.1" => ("HTTP/1.1 200 OK", "hello.html"),
        "GET /sleep HTTP/1.1" => {
            thread::sleep(Duration::from_secs(5));
            ("HTTP/1.1 200 OK", "hello.html")
        }
        _ => ("HTTP/1.1 404 NOT FOUND", "404.html"),
    };

    let contents = fs::read_to_string(filename).unwrap();
    let length = contents.len();

    let response =
        format!("{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}");

    stream.write_all(response.as_bytes()).unwrap();
}
```

Файл: `src/lib.rs`

``` rust
use std::{
    sync::{Arc, Mutex, mpsc},
    thread,
};

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: Option<mpsc::Sender<Job>>,
}

type Job = Box<dyn FnOnce() + Send + 'static>;

impl ThreadPool {
    /// Create a new ThreadPool.
    ///
    /// The size is the number of threads in the pool.
    ///
    /// # Panics
    ///
    /// The `new` function will panic if the size is zero.
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();

        let receiver = Arc::new(Mutex::new(receiver));

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }

        ThreadPool {
            workers,
            sender: Some(sender),
        }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);

        self.sender.as_ref().unwrap().send(job).unwrap();
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        drop(self.sender.take());

        for worker in &mut self.workers {
            println!("Shutting down worker {}", worker.id);

            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || {
            loop {
                let message = receiver.lock().unwrap().recv();

                match message {
                    Ok(job) => {
                        println!("Worker {id} got a job; executing.");

                        job();
                    }
                    Err(_) => {
                        println!("Worker {id} disconnected; shutting down.");
                        break;
                    }
                }
            }
        });

        Worker {
            id,
            thread: Some(thread),
        }
    }
}
```

Мы могли бы сделать ещё больше! Если вы хотите продолжить совершенствование этого проекта, вот несколько идей:

- Добавьте больше документации в `ThreadPool` и его публичные методы.
- Добавьте тесты для функционала, реализуемого библиотекой.
- Замените вызовы `unwrap` на более устойчивую обработку ошибок.
- Используйте `ThreadPool` для выполнения некоторых других задач, помимо обслуживания веб-запросов.
- На [crates.io](https://crates.io/) найдите крейт для работы с пулами потоков и на его основе реализуйте аналогичный веб-сервер. Затем сравните его API и надёжность с реализованным нами пулом потоков.

<a id="summary"></a>

## Итоги

Отличная работа! Вы сделали это к концу книги! Мы хотим поблагодарить вас за то, что присоединились к нам в этом путешествии по языку Rust. Теперь вы готовы реализовать свои собственные проекты на Rust и помочь с проектами другим людям. Имейте в виду, что сообщество Rust разработчиков довольно гостеприимно, они с удовольствием постараются помочь вам с любыми трудностями, с которыми вы можете столкнуться в своём путешествии по Rust.
