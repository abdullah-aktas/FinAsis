"""
FinAsis Artırılmış Gerçeklik (AR) Modülü
----------------------------------------

Bu modül, ursina oyun motoru ile artırılmış gerçeklik
özelliklerini entegre etmek için kullanılır.
"""

import cv2
import numpy as np
from ursina import *
import threading
import time
import os
import mediapipe as mp

class ARManager:
    """
    Artırılmış Gerçeklik özelliklerini yöneten sınıf.
    
    Kameradan görüntü alır, işaretçileri tespit eder ve
    3D nesneleri gerçek dünya konumlarına yerleştirir.
    """
    
    def __init__(self, use_aruco=True, show_camera=True, camera_index=0, marker_size=6):
        """
        ARManager sınıfını başlat
        
        :param use_aruco: ArUco işaretçileri kullanılacak mı (yoksa basit renk tespiti mi)
        :param show_camera: Kamera görüntüsü arka planda gösterilsin mi
        :param camera_index: Kullanılacak kamera indeksi (0: varsayılan kamera)
        :param marker_size: ArUco işaretçi boyutu (cm)
        """
        self.use_aruco = use_aruco
        self.show_camera = show_camera
        self.camera_index = camera_index
        self.marker_size = marker_size
        
        # Kamerayı başlat
        self.cap = None
        self.camera_frame = None
        self.is_running = False
        self.camera_texture = None
        self.camera_entity = None
        
        # ArUco işaretçileri
        if self.use_aruco:
            self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
            self.aruco_params = cv2.aruco.DetectorParameters_create()
        
        # İşaretçi ile ilişkili nesneler
        self.markers = {}  # {marker_id: ursina_entity}
        
        # Kalibrasyon matrisi (varsayılan)
        self.camera_matrix = np.array([
            [1000.0, 0.0, 320.0],
            [0.0, 1000.0, 240.0],
            [0.0, 0.0, 1.0]
        ])
        self.dist_coeffs = np.zeros((4, 1))  # Varsayılan distorsiyon katsayıları
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        self.ar_nesneleri = []
        self.ar_etkilesimleri = []
    
    def start(self):
        """AR modülünü başlat"""
        if self.cap is not None:
            return  # Zaten başlatılmış
        
        try:
            # Kamerayı başlat
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Kamera açılamadıysa hata ver
            if not self.cap.isOpened():
                print("Kamera açılamadı!")
                self.cap = None
                return False
            
            # Kamera arka planını oluştur
            if self.show_camera:
                ret, frame = self.cap.read()
                if ret:
                    h, w = frame.shape[:2]
                    self.create_camera_background(w, h)
            
            # Kamera okuma ve işaretçi tespiti için iş parçacığı başlat
            self.is_running = True
            self.camera_thread = threading.Thread(target=self._process_camera)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            
            return True
        
        except Exception as e:
            print(f"AR başlatma hatası: {str(e)}")
            return False
    
    def stop(self):
        """AR modülünü durdur"""
        self.is_running = False
        if self.camera_thread:
            self.camera_thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.camera_entity:
            destroy(self.camera_entity)
            self.camera_entity = None
        
        self.kapat()
    
    def create_camera_background(self, width, height):
        """
        Kamera görüntüsü için arka plan oluştur
        
        :param width: Kamera genişliği
        :param height: Kamera yüksekliği
        """
        # Kamera dokusu için boş bir texture oluştur
        self.camera_texture = Texture(width=width, height=height)
        
        # Kamera varlığını oluştur (daima kameraya bakar)
        self.camera_entity = Entity(
            model='quad',
            texture=self.camera_texture,
            scale=(16/9, 1, 1),  # 16:9 en-boy oranı
            position=(0, 0, 2),  # Kameranın önünde
            billboard=True,      # Her zaman kameraya bakar
            double_sided=True
        )
    
    def _process_camera(self):
        """Kamera görüntüsünü işler ve işaretçileri tespit eder"""
        while self.is_running:
            # Kameradan görüntü al
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            # Görüntüyü işle
            self.camera_frame = frame.copy()
            
            # İşaretçileri tespit et
            if self.use_aruco:
                self._detect_aruco_markers(frame)
            else:
                self._detect_color_markers(frame)
            
            # Kamera arka planını güncelle
            if self.show_camera and self.camera_texture:
                # RGB formatına dönüştür
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Dokuyu güncelle
                invoke(setattr, self.camera_texture, 'set_data', frame_rgb)
            
            # CPU kullanımını azaltmak için kısa bekleme
            time.sleep(0.01)
    
    def _detect_aruco_markers(self, frame):
        """
        ArUco işaretçilerini tespit et
        
        :param frame: İşlenecek kamera görüntüsü
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)
        
        # Tespit edilen işaretçileri işle
        if ids is not None:
            # Poz tahmini
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, self.camera_matrix, self.dist_coeffs
            )
            
            for i in range(len(ids)):
                marker_id = ids[i][0]
                
                # İşaretçinin pozisyonu
                tvec = tvecs[i][0]
                rvec = rvecs[i][0]
                
                # Rotasyon matrisini hesapla
                rot_mat, _ = cv2.Rodrigues(rvec)
                
                # Ursina koordinat sistemine dönüştür (Y ve Z ters)
                position = Vec3(tvec[0], tvec[2], -tvec[1]) * 0.01  # cm'den m'ye
                
                # İlişkili varlığı güncelle
                self._update_marker_entity(marker_id, position, rot_mat)
    
    def _detect_color_markers(self, frame):
        """
        Basit renk tabanlı işaretçileri tespit et (ArUco olmadığında)
        
        :param frame: İşlenecek kamera görüntüsü
        """
        # HSV formatına dönüştür
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Renkler ve marker ID'leri
        colors = {
            'red': (np.array([0, 100, 100]), np.array([10, 255, 255]), 1),
            'green': (np.array([50, 100, 100]), np.array([70, 255, 255]), 2),
            'blue': (np.array([110, 100, 100]), np.array([130, 255, 255]), 3),
            'yellow': (np.array([25, 100, 100]), np.array([35, 255, 255]), 4)
        }
        
        for color_name, (lower, upper, marker_id) in colors.items():
            # Renk maskesi
            mask = cv2.inRange(hsv, lower, upper)
            
            # Gürültüyü azalt
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            
            # Konturları bul
            contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Kontur bulunduysa
            if len(contours) > 0:
                # En büyük konturu al
                c = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(c)
                
                # Yeterince büyük mü?
                if area > 500:
                    # İşaretçinin merkezini bul
                    M = cv2.moments(c)
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    
                    # Ekranın merkezine göre pozisyon hesapla
                    h, w = frame.shape[:2]
                    rel_x = (center_x - w/2) / (w/2)  # -1 ile 1 arasında
                    rel_y = (h/2 - center_y) / (h/2)  # -1 ile 1 arasında
                    rel_z = 0.5 * (1 - np.sqrt(area) / np.sqrt(w*h/2))  # Boyuta göre tahmini derinlik
                    
                    # Koordinat sistemini ursina'ya uyarla
                    position = Vec3(rel_x * 5, rel_y * 5, -rel_z * 10)
                    
                    # İlişkili varlığı güncelle (rotasyon yok)
                    self._update_marker_entity(marker_id, position, None)
    
    def _update_marker_entity(self, marker_id, position, rotation_matrix=None):
        """
        İşaretçi ile ilişkili varlığı güncelle
        
        :param marker_id: İşaretçi kimliği
        :param position: İşaretçinin 3D pozisyonu
        :param rotation_matrix: İşaretçinin rotasyon matrisi (opsiyonel)
        """
        # İşaretçi olayını tetikle
        invoke(self.on_marker_detected, marker_id, position, rotation_matrix)
    
    def on_marker_detected(self, marker_id, position, rotation_matrix=None):
        """
        İşaretçi tespit edildiğinde çağrılan fonksiyon
        Bu fonksiyon ursina'nın ana iş parçacığında çalışır
        
        :param marker_id: İşaretçi kimliği
        :param position: İşaretçinin 3D pozisyonu
        :param rotation_matrix: İşaretçinin rotasyon matrisi (opsiyonel)
        """
        # İşaretçi henüz kaydedilmemişse oluştur
        if marker_id not in self.markers:
            # Varsayılan bir küp oluştur
            entity = Entity(
                model='cube',
                color=color.random_color(),
                scale=0.5
            )
            self.markers[marker_id] = entity
        
        # Varlığın pozisyonunu güncelle
        entity = self.markers[marker_id]
        entity.position = position
        
        # Rotasyon matrisi varsa onu da güncelle
        if rotation_matrix is not None:
            # Rotasyon matrisini quaternion'a dönüştür
            import scipy.spatial.transform
            r = scipy.spatial.transform.Rotation.from_matrix(rotation_matrix)
            quat = r.as_quat()  # x, y, z, w formatında
            
            # Ursina quaternion formatına uyarla (w, x, y, z)
            entity.rotation = Quat(quat[3], quat[0], quat[1], quat[2])
    
    def register_marker(self, marker_id, entity):
        """
        Bir işaretçi ile bir varlığı ilişkilendir
        
        :param marker_id: İşaretçi kimliği
        :param entity: Ursina varlığı
        """
        self.markers[marker_id] = entity
    
    def load_camera_calibration(self, file_path):
        """
        Kamera kalibrasyon dosyasını yükle
        
        :param file_path: Kalibrasyon dosyasının yolu
        :return: Başarı durumu
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # OpenCV formatında kalibrasyon dosyasını yükle
            calibration_data = np.load(file_path)
            self.camera_matrix = calibration_data['camera_matrix']
            self.dist_coeffs = calibration_data['dist_coeffs']
            return True
        except Exception as e:
            print(f"Kalibrasyon yükleme hatası: {str(e)}")
            return False
    
    def kamera_baslat(self):
        self.cap = cv2.VideoCapture(0)
        
    def ar_nesne_ekle(self, nesne_tipi, konum, olcek):
        ar_nesne = {
            'tip': nesne_tipi,
            'konum': konum,
            'olcek': olcek,
            'durum': 'aktif'
        }
        self.ar_nesneleri.append(ar_nesne)
        
    def el_takibi(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # El hareketlerini analiz et
                parmak_konumlari = []
                for landmark in hand_landmarks.landmark:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    parmak_konumlari.append((x, y))
                    
                # AR nesneleriyle etkileşim kontrolü
                self.etkilesim_kontrol(parmak_konumlari)
                
        return frame
        
    def etkilesim_kontrol(self, parmak_konumlari):
        for nesne in self.ar_nesneleri:
            if nesne['durum'] == 'aktif':
                # Nesne ile parmak konumlarının çakışma kontrolü
                for parmak in parmak_konumlari:
                    if self.cakisma_kontrol(parmak, nesne['konum']):
                        self.ar_etkilesimleri.append({
                            'nesne': nesne,
                            'etkilesim_tipi': 'dokunma',
                            'zaman': time.time()
                        })
                        
    def cakisma_kontrol(self, parmak_konum, nesne_konum):
        # Basit çakışma kontrolü
        mesafe = np.sqrt((parmak_konum[0] - nesne_konum[0])**2 + 
                        (parmak_konum[1] - nesne_konum[1])**2)
        return mesafe < 50  # 50 piksel mesafe eşiği
        
    def ar_nesne_guncelle(self):
        # AR nesnelerinin durumlarını güncelle
        for nesne in self.ar_nesneleri:
            if nesne['durum'] == 'aktif':
                # Nesne animasyonları ve güncellemeleri
                pass
                
    def kapat(self):
        self.cap.release()
        cv2.destroyAllWindows()

# Kullanım örneği
if __name__ == '__main__':
    app = Ursina()
    
    # AR Yöneticisini oluştur
    ar_manager = ARManager(use_aruco=True, show_camera=True)
    
    # AR'ı başlat
    ar_manager.start()
    
    # Örnek işaretçi eşleştirmesi
    box = Entity(model='cube', color=color.red, scale=0.5)
    sphere = Entity(model='sphere', color=color.blue, scale=0.5)
    
    ar_manager.register_marker(1, box)
    ar_manager.register_marker(2, sphere)
    
    # Çıkış tuşu
    def input(key):
        if key == 'escape':
            ar_manager.stop()
            application.quit()
    
    app.run() 