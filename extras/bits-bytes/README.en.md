# Bits, Bytes, and Binary Data in Rust

A practical **Russian-language companion** to [The Rust Programming Language](https://doc.rust-lang.org/book/). It connects integer representation, bitwise operations, UTF-8, endianness, binary parsing, and stream framing through runnable examples and a small binary format.

**[Read in Russian](README.md) · [Start reading](docs/00-about.md) · [Contribute](CONTRIBUTING.md)**

The material contains 12 numbered sections, 27 standalone Rust programs, exercises with solutions, a quick reference, and a complete standard-library-only codec called Byte Note. It assumes basic Rust syntax, slices, `Option`, and `Result`.

## Run

Requirements: Rust 1.85+ (edition 2024), Cargo, and Python 3.11+.

```sh
python3 scripts/check.py
python3 scripts/run_examples.py
cargo test --workspace --locked
cargo run -p byte-note --example demo
```

## Build the documentation

```sh
cargo install mdbook --version 0.5.4 --locked
python3 scripts/prepare_book.py
mdbook build
```

Pandoc is required to export EPUB and a single Markdown document with `python3 scripts/build_ebooks.py`. See [build documentation](docs/BUILDING.md).

This is an independent community project, not an official Rust publication. Initiated and maintained by [Evgenii Panarin](https://github.com/Waikizashi); the initial draft was developed with ChatGPT assistance. Corrections and technical review are welcome. See [provenance](PROVENANCE.md).

Text and code are available under the [MIT license](LICENSE).
