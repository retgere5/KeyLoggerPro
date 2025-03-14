# KeyLogger Pro

Python ile geliştirilmiş, gelişmiş tuş kaydedici ve sistem izleme aracı.

## Özellikler

- ⌨️ Klavye girdilerini kaydedebilme
- 📂 Veri şifreleme ve güvenli saklama
- ✉️ E-posta ile uzaktan raporlama
- ⏱️ Ayarlanabilir raporlama aralığı
- 💻 Detaylı sistem bilgisi toplama
- 🔐 Veri güvenliği ve şifreleme
- 🛡️ Güvenli dosya silme
- 🔄 Arka planda çalışma desteği
- 📊 Kullanıcı dostu log okuma araçları
- ⚙️ Yapılandırılabilir config dosyası
- 📦 Taşınabilir tek EXE dosyası oluşturma

## Proje Yapısı

```
keylogger/
├── src/           # Kaynak kod
│   ├── core.py    # Çekirdek izleme modülü
│   ├── logger.py  # Loglama modülü
│   └── utils.py   # Yardımcı fonksiyonlar ve şifreleme
├── tools/         # Yardımcı araçlar
│   ├── log_reader.py  # Komut satırı log okuyucu
│   └── log_viewer.py  # Grafiksel log görüntüleyici
├── data/          # Log verileri
├── config.ini     # Yapılandırma dosyası
├── main.py        # Ana program
├── start.py       # Başlatıcı script
├── setup.py       # EXE oluşturma scripti
└── requirements.txt
```

## Gereksinimler

- Python 3.6+
- Gerekli kütüphaneler:
  - pynput (klavye izleme)
  - psutil (sistem bilgileri)
  - cryptography (şifreleme)
  - pywin32 (Windows'ta arka planda çalışma için)
  - pyinstaller (EXE oluşturmak için)

## Kurulum

1. Depoyu klonlayın
```bash
git clone https://github.com/kullanici/KeyLoggerPro.git
cd KeyLoggerPro
```

2. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

## Kullanım

### Config Dosyası ile Kullanım

Program, `config.ini` dosyasındaki ayarları kullanarak çalışır. Bu dosyayı düzenleyerek programın davranışını değiştirebilirsiniz:

```ini
[General]
# Raporlama aralığı (saniye cinsinden)
interval = 60
# Arka planda çalıştırma (true/false)
background = false
# Sistem bilgilerini kaydet (true/false)
system_info = true

[Output]
# Log dosyasının kaydedileceği konum
output_file = data/system_log.dat
# Veriyi şifreleme (true/false)
encrypt = true
# Şifreleme parolası
password = default_key
```

Config dosyasını düzenledikten sonra programı başlatmak için:

```bash
python start.py
```

### Komut Satırı Parametreleri ile Kullanım

Config dosyasındaki ayarları geçersiz kılmak için komut satırı parametrelerini kullanabilirsiniz:

```bash
python main.py --output data/system_log.dat --interval 30 --system-info --background
```

Tüm seçenekler için yardım:
```bash
python main.py --help
```

### Tek EXE Dosyası Oluşturma

Programı taşınabilir tek bir EXE dosyasına dönüştürmek için:

```bash
python setup.py build
```

Bu komut, `dist` klasöründe çalıştırılabilir bir EXE dosyası oluşturur. Bu EXE dosyası, tüm bağımlılıkları içerir ve başka bir bilgisayara kolayca taşınabilir.

### Logları Okuma

Komut satırı aracı:
```bash
python tools/log_reader.py data/system_log.dat --no-encrypt
```

veya grafik arayüzlü okuyucu:
```bash
python tools/log_viewer.py
```

## Güvenlik

Bu uygulama verileri Fernet şifreleme (AES-128-CBC) ile şifreler. Tüm şifreli verileri çözmek için orijinal şifre gereklidir.

## Önemli Uyarı

Bu araç **SADECE EĞİTİM AMAÇLIDIR**. Başkalarının bilgisayarlarında izinsiz kullanılması yasal değildir ve etik olmayan bir davranıştır. Bu aracı yalnızca kendi sistemlerinizde ve eğitim amaçlı kullanın.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 