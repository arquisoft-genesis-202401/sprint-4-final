FROM rust:latest AS builder

WORKDIR /app

COPY Cargo.toml ./
COPY Cargo.lock ./

RUN mkdir src
RUN echo "fn main() { println!(\"Hello, world!\"); }" > src/main.rs
RUN cargo build --release
RUN rm -rf src

COPY . .

RUN cargo build --release

# Use a Rust runtime image
FROM rust:slim

RUN apt-get update && \
    apt-get install -y openssl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/crypto_module /usr/local/bin/crypto_module

CMD ["crypto_module"]

EXPOSE 8080

ENV AES_KEY 0
ENV HMAC_KEY 0
ENV IV 0
