"""
Face detection and facial landmark extraction module.
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple, Dict
import config


class FaceDetector:
    """Detects faces and extracts facial landmarks / regions."""

    def __init__(self, use_mediapipe: bool = True):
        self.use_mediapipe = use_mediapipe
        self.mp_face_mesh = None
        self.face_mesh = None
        self.face_cascade = None

        if use_mediapipe:
            try:
                import mediapipe as mp
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                )
                self.mp_drawing = mp.solutions.drawing_utils
                print("[INFO] Using MediaPipe Face Mesh")
            except ImportError:
                print("[WARN] MediaPipe not found, falling back to Haar Cascade")
                self.use_mediapipe = False

        if not self.use_mediapipe:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + config.FACE_CASCADE_PATH
            )
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + config.EYE_CASCADE_PATH
            )

    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect the primary face in the image. Returns (x, y, w, h)."""
        if self.use_mediapipe:
            return self._detect_face_mediapipe(image)
        else:
            return self._detect_face_haar(image)

    def _detect_face_mediapipe(self, image: np.ndarray) -> Optional[Tuple]:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        h, w = image.shape[:2]
        landmarks = results.multi_face_landmarks[0]

        xs = [lm.x * w for lm in landmarks.landmark]
        ys = [lm.y * h for lm in landmarks.landmark]

        x_min = int(min(xs))
        y_min = int(min(ys))
        x_max = int(max(xs))
        y_max = int(max(ys))

        padding = 20
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(w, x_max + padding)
        y_max = min(h, y_max + padding)

        return (x_min, y_min, x_max - x_min, y_max - y_min)

    def _detect_face_haar(self, image: np.ndarray) -> Optional[Tuple]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
        )
        if len(faces) == 0:
            return None

        # Return the largest face
        areas = [w * h for (x, y, w, h) in faces]
        idx = np.argmax(areas)
        return tuple(faces[idx])

    def get_facial_regions(self, image: np.ndarray) -> Optional[Dict]:
        """
        Extract facial regions: forehead, cheeks, nose, chin, under-eyes.
        """
        if self.use_mediapipe:
            return self._get_regions_mediapipe(image)
        else:
            return self._get_regions_haar(image)

    def _get_regions_mediapipe(self, image: np.ndarray) -> Optional[Dict]:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        h, w = image.shape[:2]
        landmarks = results.multi_face_landmarks[0]

        def lm_point(idx):
            lm = landmarks.landmark[idx]
            return (int(lm.x * w), int(lm.y * h))

        # Key landmark indices (MediaPipe Face Mesh)
        # Forehead: landmarks around top of face
        # Nose tip: 1, Nose bridge: 6
        # Left cheek: 234, Right cheek: 454
        # Chin: 152
        # Left eye: 33, 133  Right eye: 362, 263
        # Under left eye: 111, 117  Under right eye: 340, 346

        regions = {}

        # ── Forehead ──
        forehead_center = lm_point(10)
        forehead_left = lm_point(67)
        forehead_right = lm_point(297)
        fw = abs(forehead_right[0] - forehead_left[0])
        fh = int(fw * 0.4)
        fx = forehead_left[0]
        fy = max(0, forehead_center[1] - fh)
        regions["forehead"] = (fx, fy, fw, fh)

        # ── Left Cheek ──
        lc = lm_point(234)
        nose_l = lm_point(48)
        cw = abs(nose_l[0] - lc[0])
        ch = int(cw * 0.8)
        regions["left_cheek"] = (lc[0], lc[1] - ch // 2, cw, ch)

        # ── Right Cheek ──
        rc = lm_point(454)
        nose_r = lm_point(278)
        cw2 = abs(rc[0] - nose_r[0])
        ch2 = int(cw2 * 0.8)
        regions["right_cheek"] = (nose_r[0], rc[1] - ch2 // 2, cw2, ch2)

        # ── Nose ──
        nose_top = lm_point(6)
        nose_bottom = lm_point(1)
        nose_left = lm_point(48)
        nose_right = lm_point(278)
        nw = abs(nose_right[0] - nose_left[0])
        nh = abs(nose_bottom[1] - nose_top[1])
        regions["nose"] = (nose_left[0], nose_top[1], nw, nh)

        # ── Chin ──
        chin = lm_point(152)
        chin_left = lm_point(172)
        chin_right = lm_point(397)
        chinw = abs(chin_right[0] - chin_left[0])
        chinh = int(chinw * 0.5)
        regions["chin"] = (chin_left[0], chin[1] - chinh // 2, chinw, chinh)

        # ── Under Left Eye ──
        ule1 = lm_point(111)
        ule2 = lm_point(117)
        ulew = abs(ule2[0] - ule1[0]) + 20
        uleh = 25
        regions["under_left_eye"] = (
            min(ule1[0], ule2[0]) - 10,
            min(ule1[1], ule2[1]),
            ulew, uleh
        )

        # ── Under Right Eye ──
        ure1 = lm_point(340)
        ure2 = lm_point(346)
        urew = abs(ure2[0] - ure1[0]) + 20
        ureh = 25
        regions["under_right_eye"] = (
            min(ure1[0], ure2[0]) - 10,
            min(ure1[1], ure2[1]),
            urew, ureh
        )

        # Clamp all regions to image bounds
        for key in regions:
            x, y, rw, rh = regions[key]
            x = max(0, x)
            y = max(0, y)
            rw = min(rw, w - x)
            rh = min(rh, h - y)
            regions[key] = (x, y, rw, rh)

        return regions

    def _get_regions_haar(self, image: np.ndarray) -> Optional[Dict]:
        face = self.detect_face(image)
        if face is None:
            return None

        x, y, w, h = face
        regions = {}

        # Approximate regions based on face bounding box proportions
        regions["forehead"] = (
            x + w // 4, y, w // 2, h // 5
        )
        regions["left_cheek"] = (
            x, y + h // 3, w // 3, h // 3
        )
        regions["right_cheek"] = (
            x + 2 * w // 3, y + h // 3, w // 3, h // 3
        )
        regions["nose"] = (
            x + w // 3, y + h // 4, w // 3, h // 3
        )
        regions["chin"] = (
            x + w // 4, y + 3 * h // 4, w // 2, h // 4
        )
        regions["under_left_eye"] = (
            x + w // 8, y + h // 4, w // 4, h // 10
        )
        regions["under_right_eye"] = (
            x + 5 * w // 8, y + h // 4, w // 4, h // 10
        )

        return regions

    def get_face_mask(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Create a mask for the face region."""
        if self.use_mediapipe:
            return self._get_face_mask_mediapipe(image)
        else:
            face = self.detect_face(image)
            if face is None:
                return None
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            x, y, w, h = face
            cx, cy = x + w // 2, y + h // 2
            cv2.ellipse(mask, (cx, cy), (w // 2, h // 2), 0, 0, 360, 255, -1)
            return mask

    def _get_face_mask_mediapipe(self, image: np.ndarray) -> Optional[np.ndarray]:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        h, w = image.shape[:2]
        landmarks = results.multi_face_landmarks[0]

        # Face oval indices in MediaPipe
        face_oval_indices = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361,
            288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
            150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54,
            103, 67, 109, 10
        ]

        points = []
        for idx in face_oval_indices:
            lm = landmarks.landmark[idx]
            points.append((int(lm.x * w), int(lm.y * h)))

        mask = np.zeros((h, w), dtype=np.uint8)
        pts = np.array(points, dtype=np.int32)
        cv2.fillConvexPoly(mask, pts, 255)

        return mask

    def draw_regions(self, image: np.ndarray,
                     regions: Dict) -> np.ndarray:
        """Draw facial regions on the image for visualization."""
        result = image.copy()
        colors = {
            "forehead": (0, 255, 0),
            "left_cheek": (255, 0, 0),
            "right_cheek": (255, 0, 0),
            "nose": (0, 255, 255),
            "chin": (255, 255, 0),
            "under_left_eye": (0, 0, 255),
            "under_right_eye": (0, 0, 255),
        }

        for region_name, (x, y, w, h) in regions.items():
            color = colors.get(region_name, (128, 128, 128))
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                result, region_name, (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1
            )

        return result