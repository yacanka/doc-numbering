# Numarator

Numarator, tanımlı formatlardan atomik ve izlenebilir belge numaraları üreten Django REST + Vue uygulamasıdır.

- Tarayıcı arayüzü API'si: `/api/v1/`
- Dış uygulamalar için özel API: `/api/private/v1/`
- OpenAPI şeması: `/api/schema/`
- Swagger arayüzü: `/api/docs/`

Dış uygulama entegrasyonunun kimlik doğrulama, endpoint, idempotency, hata ve güvenlik ayrıntıları için [Özel API entegrasyon rehberine](docs/private-api.md) bakın.

## Yerel geliştirme

macOS/Linux üzerinde kök dizinden:

```bash
./start-dev.sh
```

Windows üzerinde:

```bat
start-dev.bat
```

Başlatıcı backend bağımlılıklarını ve frontend paketlerini kurar, Django kontrollerini/migration'ları çalıştırır ve iki servisi başlatır.
