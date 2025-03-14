#!/usr/bin/env python3
"""
KeyLogger Pro - Başlatıcı
Config dosyasındaki ayarlarla programı başlatır.
"""

import os
import sys
import configparser
import main
import time

def ensure_data_directory():
    """Data klasörünün var olduğundan emin ol."""
    # Mevcut dizini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Config dosyasını oku
    config_path = os.path.join(script_dir, "config.ini")
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        try:
            config.read(config_path, encoding='utf-8')
            if 'Output' in config and 'output_file' in config['Output']:
                output_file = config['Output']['output_file']
                # Çıktı dizinini al
                output_dir = os.path.dirname(output_file)
                if output_dir:
                    # Dizini oluştur
                    full_output_dir = os.path.join(script_dir, output_dir)
                    os.makedirs(full_output_dir, exist_ok=True)
                    print(f"Log dizini: {full_output_dir}")
        except Exception as e:
            print(f"Config dosyası okunurken hata: {e}")
    
    # Varsayılan data klasörünü de oluştur
    data_dir = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f"Varsayılan data dizini: {data_dir}")

if __name__ == "__main__":
    # Çalışma dizinini script'in bulunduğu dizin olarak ayarla
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Çalışma dizini: {script_dir}")
    
    # Config dosyasını yükle
    config_path = os.path.join(script_dir, "config.ini")
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        try:
            config.read(config_path, encoding='utf-8')
            # Başlangıç gecikmesi
            startup_delay = config.getint('General', 'startup_delay', fallback=0)
            if startup_delay > 0:
                print(f"Program {startup_delay} saniye sonra başlayacak...")
                time.sleep(startup_delay)
        except Exception as e:
            print(f"Config dosyası okunurken hata: {e}")
    
    # Data klasörünün var olduğundan emin ol
    ensure_data_directory()
    
    # Ana programı çalıştır
    sys.argv = [sys.argv[0], "--config", config_path]
    sys.exit(main.main()) 