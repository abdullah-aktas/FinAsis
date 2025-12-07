# -*- coding: utf-8 -*-
"""
FinAsis Artırılmış Gerçeklik (AR) Modülü
Temizlenmiş ve fonksiyonel yapılandırma.
"""

import cv2
import numpy as np
import threading
import time
import os
import mediapipe as mp
from ursina import *  # noqa: F403
from scipy.spatial.transform import Rotation


class ARManager:
    def __init__(self, use_aruco=True, show_camera=True, camera_index=0, marker_size=6):
        self.use_aruco = use_aruco
        self.show_camera = show_camera
        self.camera_index = camera_index
        self.marker_size = marker_size

        self.cap = None
        self.camera_texture = None
        self.camera_entity = None
        self.is_running = False

        self.markers = {}
        self.ar_nesneleri = []
        self.ar_etkilesimleri = []

        self.camera_matrix = np.array(
            [[1000.0, 0.0, 320.0], [0.0, 1000.0, 240.0], [0.0, 0.0, 1.0]]
        )
        self.dist_coeffs = np.zeros((4, 1))

        if self.use_aruco:
            self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
            self.aruco_params = cv2.aruco.DetectorParameters_create()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7
        )

    def start(self):
        if self.cap:
            return True

        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("Kamera açılamadı!")
            self.cap = None
            return False

        if self.show_camera:
            ret, frame = self.cap.read()
            if ret:
                self.create_camera_background(*frame.shape[1::-1])

        self.is_running = True
        threading.Thread(target=self._process_camera, daemon=True).start()
        return True

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None

        if self.camera_entity:
            destroy(self.camera_entity)  # noqa: F405
            self.camera_entity = None

        self.hands.close()
        cv2.destroyAllWindows()

    def create_camera_background(self, width, height):
        self.camera_texture = Texture(width=width, height=height)  # noqa: F405
        self.camera_entity = Entity(  # noqa: F405
            model="quad",
            texture=self.camera_texture,
            scale=(16 / 9, 1, 1),
            position=(0, 0, 2),
            billboard=True,
            double_sided=True,
        )

    def _process_camera(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.use_aruco:
                self._detect_aruco_markers(frame)
            else:
                self._detect_color_markers(frame)

            if self.show_camera and self.camera_texture:
                invoke(
                    setattr, self.camera_texture, "set_data", frame_rgb
                )  # noqa: F405
            time.sleep(0.01)

    def _detect_aruco_markers(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )
        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, self.camera_matrix, self.dist_coeffs
            )
            for i, marker_id in enumerate(ids.flatten()):
                tvec, rvec = tvecs[i][0], rvecs[i][0]
                rot_mat, _ = cv2.Rodrigues(rvec)
                position = Vec3(tvec[0], tvec[2], -tvec[1]) * 0.01  # noqa: F405
                self._update_marker_entity(marker_id, position, rot_mat)

    def _detect_color_markers(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        colors = {
            "red": ([0, 100, 100], [10, 255, 255], 1),
            "green": ([50, 100, 100], [70, 255, 255], 2),
            "blue": ([110, 100, 100], [130, 255, 255], 3),
            "yellow": ([25, 100, 100], [35, 255, 255], 4),
        }
        for lower, upper, marker_id in colors.values():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.dilate(cv2.erode(mask, None, iterations=2), None, iterations=2)
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if contours:
                c = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(c)
                if area > 500:
                    M = cv2.moments(c)
                    cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                    h, w = frame.shape[:2]
                    rel_x = (cx - w / 2) / (w / 2)
                    rel_y = (h / 2 - cy) / (h / 2)
                    rel_z = 0.5 * (1 - np.sqrt(area) / np.sqrt(w * h / 2))
                    position = Vec3(rel_x * 5, rel_y * 5, -rel_z * 10)  # noqa: F405
                    self._update_marker_entity(marker_id, position)

    def _update_marker_entity(self, marker_id, position, rotation_matrix=None):
        invoke(
            self.on_marker_detected, marker_id, position, rotation_matrix
        )  # noqa: F405

    def on_marker_detected(self, marker_id, position, rotation_matrix=None):
        if marker_id not in self.markers:
            self.markers[marker_id] = Entity(  # noqa: F405
                model="cube", color=color.random_color(), scale=0.5  # noqa: F405
            )
        entity = self.markers[marker_id]
        entity.position = position
        if rotation_matrix is not None:
            quat = Rotation.from_matrix(rotation_matrix).as_quat()
            entity.rotation = Quat(quat[3], quat[0], quat[1], quat[2])  # noqa: F405

    def register_marker(self, marker_id, entity):
        self.markers[marker_id] = entity

    def load_camera_calibration(self, file_path):
        if not os.path.exists(file_path):
            return False
        try:
            data = np.load(file_path)
            self.camera_matrix = data["camera_matrix"]
            self.dist_coeffs = data["dist_coeffs"]
            return True
        except Exception as e:
            print(f"Kalibrasyon hatası: {str(e)}")
            return False

    def el_takibi(self):
        if not self.cap:
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                points = [
                    (int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0]))
                    for landmark in hand.landmark
                ]
                self.etkilesim_kontrol(points)
        return frame

    def etkilesim_kontrol(self, parmak_konumlari):
        for nesne in self.ar_nesneleri:
            if nesne["durum"] != "aktif":
                continue
            for parmak in parmak_konumlari:
                if self.cakisma_kontrol(parmak, nesne["konum"]):
                    self.ar_etkilesimleri.append(
                        {
                            "nesne": nesne,
                            "etkilesim_tipi": "dokunma",
                            "zaman": time.time(),
                        }
                    )

    def cakisma_kontrol(self, parmak, konum):
        return np.linalg.norm(np.array(parmak) - np.array(konum)) < 50

    def ar_nesne_ekle(self, nesne_tipi, konum, olcek):
        self.ar_nesneleri.append(
            {"tip": nesne_tipi, "konum": konum, "olcek": olcek, "durum": "aktif"}
        )

    def ar_nesne_guncelle(self):
        pass  # Geliştirilebilir animasyon/metin/güncellemeler

    def _tum_sistemleri_guncelle(self):
        """Tüm sistem güncellemelerini sırayla çalıştırır."""
        self.update_market_research()
        self.update_competition_analysis()
        self.update_financial_reports()
        self.update_strategic_planning()
        self.update_production_system()
        self.update_hr_system()
        self.update_marketing_system()
        self.update_rnd_system()
        self.update_economy()
        self.update_quest_system()
        self.update_training_system()
        self.update_quality_system()
        self.update_sustainability_system()
        self.update_crisis_system()
        self.update_international_trade()
        self.update_digital_transformation()
        self.update_innovation_system()
        self.update_crm_system()
        self.update_scm_system()
        self.update_pm_system()
        self.update_fr_system()
        self.update_health_system()
        self.update_exercise_system()

    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        current_time = time.time()
        if not self.game_state["is_paused"]:
            (current_time - self.game_state["current_time"]) * self.game_state[
                "game_speed"
            ]
            self.game_state["current_time"] = current_time
            self._tum_sistemleri_guncelle()
            # Otomatik kayıt
            if (
                current_time - self.game_state["last_save_time"]
                >= self.game_state["save_interval"]
            ):
                self.save_game()
                self.game_state["last_save_time"] = current_time
            self.update_ui()
            self.check_notifications()
            if self.multiplayer["is_online"]:
                self.update_multiplayer()
