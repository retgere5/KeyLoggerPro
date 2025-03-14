#!/usr/bin/env python3
"""
KeyLogger Pro - Log Okuyucu
Log dosyalarını okumak için komut satırı aracı.
"""

import os
import sys
import argparse
import traceback

# Modül arama yolunu düzelt
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate_key, decrypt_data

def read_file(file_path, encrypted=True, password="default_key"):
    """Log dosyasını oku ve içeriği döndür."""
    if not os.path.exists(file_path):
        return "Dosya bulunamadı: " + file_path
    
    # Dosya boyutunu kontrol et
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return "Dosya boş"
    
    try:
        if encrypted:
            # Şifrelenmiş dosyayı oku
            key = generate_key(password)
            with open(file_path, 'rb') as f:
                content = f.read().split(b'\n')
                
            decrypted_content = []
            error_count = 0
            
            for line in content:
                if line.strip():
                    try:
                        decrypted_line = decrypt_data(line, key)
                        decrypted_content.append(decrypted_line)
                    except Exception as e:
                        # Şifre çözülemedi - hata sayısını artır
                        error_count += 1
                        if error_count < 5:  # Sadece ilk birkaç hatayı göster
                            print(f"Satır çözülemedi: {e}")
            
            if not decrypted_content:
                if error_count > 0:
                    return f"Dosyanın şifresi çözülemedi. {error_count} satır çözülemedi. Şifre doğru mu? Dosya gerçekten şifrelenmiş mi?"
                else:
                    return "Dosya içeriği boş veya okunamadı."
                        
            return '\n'.join(decrypted_content)
        else:
            # Şifrelenmemiş dosyayı oku
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if not content.strip():
                    return "Dosya içeriği boş"
                return content
    except Exception as e:
        error_details = traceback.format_exc()
        return f"Hata: {str(e)}\n\nDetaylar:\n{error_details}"

def save_to_file(content, output_path):
    """İçeriği dosyaya kaydet."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Hata: {str(e)}")
        return False

def main():
    """Komut satırı arayüzü."""
    parser = argparse.ArgumentParser(description='KeyLogger Pro - Log dosyalarını oku')
    parser.add_argument('file', help='Okunacak log dosyası')
    parser.add_argument('--password', '-p', default="default_key", 
                        help='Şifre çözmek için kullanılacak parola')
    parser.add_argument('--output', '-o', help='Çıktı dosyası (belirtilmezse ekrana yazdırır)')
    parser.add_argument('--no-encrypt', action='store_true', help='Dosyanın şifrelenmemiş olduğunu belirt')
    
    args = parser.parse_args()
    
    # Dosya uzantısına göre şifreleme durumunu otomatik belirle
    encrypted = not args.no_encrypt
    if args.file.lower().endswith('.txt') and not args.no_encrypt:
        print("Not: .txt uzantılı dosya için şifreleme otomatik olarak devre dışı bırakıldı.")
        print("Dosya şifreliyse --no-encrypt parametresini kullanmayın.")
        encrypted = False
    
    content = read_file(args.file, encrypted, args.password)
    
    if args.output:
        if save_to_file(content, args.output):
            print(f"Log dosyası kaydedildi: {args.output}")
        else:
            print("Dosya kaydedilemedi.")
    else:
        print("\n" + "="*50 + " LOG İÇERİĞİ " + "="*50)
        print(content)
        print("="*120)

if __name__ == "__main__":
    sys.exit(main()) 