use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use base64::{decode_config, encode_config, URL_SAFE};
use openssl::symm::{Cipher, Crypter, Mode};
use openssl::hash::MessageDigest;
use openssl::pkey::PKey;
use openssl::sign::Signer;
use openssl::error::ErrorStack;
use serde_derive::{Deserialize, Serialize};
use std::env;
use dotenv::dotenv;

pub struct CryptoModule {
    aes_key: Vec<u8>,
    hmac_key: Vec<u8>,
    iv: Vec<u8>,
}

impl CryptoModule {
    pub fn new(aes_key: &str, hmac_key: &str, iv: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let aes_key = decode_config(aes_key, URL_SAFE)?;
        let hmac_key = decode_config(hmac_key, URL_SAFE)?;
        let iv = decode_config(iv, URL_SAFE)?;

        Ok(CryptoModule { aes_key, hmac_key, iv })
    }

    pub fn encrypt_data(&self, data: &[u8]) -> Result<String, ErrorStack> {
        let cipher = Cipher::aes_256_cbc();
        let mut crypter = Crypter::new(cipher, Mode::Encrypt, &self.aes_key, Some(&self.iv))?;
        crypter.pad(true);

        let mut ciphertext = vec![0; data.len() + cipher.block_size()];
        let mut count = crypter.update(data, &mut ciphertext)?;
        count += crypter.finalize(&mut ciphertext[count..])?;

        ciphertext.truncate(count);
        Ok(encode_config(&ciphertext, URL_SAFE))
    }

    pub fn decrypt_data(&self, encrypted_data: &str) -> Result<String, Box<dyn std::error::Error>> {
        let encrypted_data = decode_config(encrypted_data, URL_SAFE)?;
        let cipher = Cipher::aes_256_cbc();
        let mut crypter = Crypter::new(cipher, Mode::Decrypt, &self.aes_key, Some(&self.iv))?;
        crypter.pad(true);

        let mut decrypted_data = vec![0; encrypted_data.len() + cipher.block_size()];
        let mut count = crypter.update(&encrypted_data, &mut decrypted_data)?;
        count += crypter.finalize(&mut decrypted_data[count..])?;

        decrypted_data.truncate(count);
        Ok(String::from_utf8(decrypted_data)?)
    }

    pub fn calculate_hmac(&self, data: &[u8]) -> Result<String, ErrorStack> {
        let pkey = PKey::hmac(&self.hmac_key)?;
        let mut signer = Signer::new(MessageDigest::sha256(), &pkey)?;
        signer.update(data)?;
        let hmac = signer.sign_to_vec()?;

        Ok(encode_config(&hmac, URL_SAFE))
    }
}

#[derive(Deserialize)]
struct EncryptData {
    data: String,
}

#[derive(Deserialize)]
struct DecryptData {
    encrypted_data: String,
}

#[derive(Deserialize)]
struct HmacData {
    data: String,
}

#[derive(Serialize)]
struct ResponseMessage {
    message: String,
}

async fn encrypt_endpoint(data: web::Json<EncryptData>) -> impl Responder {
    let crypto = get_crypto_module().unwrap();
    match crypto.encrypt_data(data.data.as_bytes()) {
        Ok(encrypted) => HttpResponse::Ok().json(ResponseMessage { message: encrypted }),
        Err(e) => HttpResponse::InternalServerError().body(format!("Error: {:?}", e)),
    }
}

async fn decrypt_endpoint(data: web::Json<DecryptData>) -> impl Responder {
    let crypto = get_crypto_module().unwrap();
    match crypto.decrypt_data(&data.encrypted_data) {
        Ok(decrypted) => HttpResponse::Ok().json(ResponseMessage { message: decrypted }),
        Err(e) => HttpResponse::InternalServerError().body(format!("Error: {:?}", e)),
    }
}

async fn hmac_endpoint(data: web::Json<HmacData>) -> impl Responder {
    let crypto = get_crypto_module().unwrap();
    match crypto.calculate_hmac(data.data.as_bytes()) {
        Ok(hmac) => HttpResponse::Ok().json(ResponseMessage { message: hmac }),
        Err(e) => HttpResponse::InternalServerError().body(format!("Error: {:?}", e)),
    }
}

fn get_crypto_module() -> Result<CryptoModule, Box<dyn std::error::Error>> {
    dotenv().ok();
    let aes_key = env::var("AES_KEY")?;
    let hmac_key = env::var("HMAC_KEY")?;
    let iv = env::var("IV")?;
    CryptoModule::new(&aes_key, &hmac_key, &iv)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/encrypt", web::post().to(encrypt_endpoint))
            .route("/decrypt", web::post().to(decrypt_endpoint))
            .route("/hmac", web::post().to(hmac_endpoint))
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}
