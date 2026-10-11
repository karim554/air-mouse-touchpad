#!/usr/bin/env python3
"""
Air Mouse TOUCHPAD - ماوس بالكاميرا بأسلوب التاتش باد (Relative Mode)

الفكرة: إيدك = صباعك على التاتش باد.
    - بتحرّك المؤشر بالـ "فرق في الحركة" مش بمكان إيدك في الكاميرا.
    - رفع الصباع (تفتح إيدك / تقفلها) = رفع الصباع من التاتش باد -> المؤشر بيقف وتقدر ترجّع إيدك لمكان مريح.
    - حركة بطيئة = دقة عالية (تضغط على أزرار يوتيوب الصغيرة)، حركة سريعة = المؤشر بيعدّي الشاشة بسرعة (Acceleration).

التثبيت (Windows):
    pip install opencv-python mediapipe==0.10.14 pyautogui numpy pycaw comtypes

الإيماءات:
    ☝  السبابة فقط ................. تحريك المؤشر (تاتش باد)
    🤏 Tap: قرصة إبهام+سبابة سريعة .. كليك شمال   (قرصتين سريعتين = دبل كليك = فل سكرين يوتيوب)
    🤏 قرصة وتمسك .................. دراج (سحب)
    🤏 Tap: قرصة إبهام+وسطى ........ كليك يمين
    ✌  سبابة + وسطى ................ سكرول (فوق/تحت)
    🤟 سبابة + وسطى + بنصر .......... تحكم في الصوت
    ✊ قبضة 1 ثانية ................. Play/Pause
    🤙 إبهام + خنصر 0.8 ثانية ....... كتم
    🖐 كف مفتوح 1.5 ثانية ........... تشغيل/إيقاف الماوس

الكيبورد: T تشغيل/إيقاف | SPACE Play/Pause | M كتم | [ ] سرعة المؤشر | + - حساسية القرصة
          V تصغير/تكبير نافذة الكاميرا | H مساعدة | Q أو ESC خروج
"""

import math
import os
import time
from collections import Counter, deque
from types import SimpleNamespace

import cv2
import mediapipe as mp
import numpy as np
import pyautogui

# ============================ الإعدادات ============================
CAM_INDEX = 0
CAM_W, CAM_H = 640, 480
PREVIEW_SIZE = (480, 360)       # حجم نافذة الكاميرا (V لتصغيرها)
MINI_SIZE = (320, 240)

# --- المؤشر (تاتش باد) ---
SENSITIVITY = 1.6               # سرعة المؤشر الأساسية (بتتعدل بـ [ ])
MIN_GAIN = 0.7                  # مضاعف الحركة البطيئة (أقل = دقة أعلى)
ACCEL = 1.0                     # شدة التسارع مع السرعة
MAX_GAIN = 3.2                  # أقصى مضاعف
FILTER_MIN_CUTOFF = 1.2         # أقل = تنعيم أكتر وقت الثبات (بيمنع الرعشة)
FILTER_BETA = 4.0               # أعلى = استجابة أسرع وقت الحركة السريعة
CLICK_LOCK = 0.25               # ثواني تثبيت المؤشر بعد الكليك (بيضمن الدبل كليك)

# --- الكليك ---
PINCH_ON = 0.30                 # بتتعدل بـ + / - (أعلى = أسهل)
PINCH_RELEASE_RATIO = 1.45
PINCH_CONFIRM_FRAMES = 2
DRAG_HOLD = 0.40                # مسك القرصة أكتر من كده = دراج

# --- السكرول والصوت ---
SCROLL_GAIN = 12000             # 120 = نوتش واحد
SCROLL_DEADZONE = 0.003
NATURAL_SCROLL = False          # True = إيدك فوق -> الصفحة تنزل (زي الموبايل)
VOL_RANGE = 0.35

# --- ثبات الإيماءات ---
GESTURE_WINDOW = 3
GESTURE_NEED = 2

# --- إيماءات المسك ---
TOGGLE_HOLD = 1.5
PLAY_HOLD = 1.0
MUTE_HOLD = 0.8
ACTION_COOLDOWN = 1.2

pyautogui.FAILSAFE = False      # اخرج بـ Q أو ESC
pyautogui.PAUSE = 0
SCREEN_W, SCREEN_H = pyautogui.size()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

GREEN, RED, YELLOW, WHITE, CYAN, ORANGE, GRAY = (
    (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 255, 255), (255, 255, 0), (0, 165, 255), (140, 140, 140))
WIN = "Air Mouse TOUCHPAD"


# ============================ دوال مساعدة ============================
def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def put(img, text, org, color=WHITE, scale=0.55, thick=1):
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 2, cv2.LINE_AA)
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def open_camera():
    cap = None
    if os.name == "nt":
        cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # أقل تأخير
    return cap


class OneEuro:
    """فلتر One-Euro: بيشيل الرعشة وقت الثبات من غير ما يأخّر الحركة السريعة."""

    def __init__(self, min_cutoff, beta, d_cutoff=1.0):
        self.mc, self.beta, self.dc = min_cutoff, beta, d_cutoff
        self.reset()

    def reset(self):
        self.x_prev, self.dx_prev, self.t_prev = None, 0.0, None

    @staticmethod
    def _alpha(cutoff, dt):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, x, t):
        if self.x_prev is None:
            self.x_prev, self.t_prev = x, t
            return x
        dt = max(t - self.t_prev, 1e-3)
        dx = (x - self.x_prev) / dt
        a_d = self._alpha(self.dc, dt)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev
        a = self._alpha(self.mc + self.beta * abs(dx_hat), dt)
        x_hat = a * x + (1 - a) * self.x_prev
        self.x_prev, self.dx_prev, self.t_prev = x_hat, dx_hat, t
        return x_hat


class Fingers:
    """حالة كل صباع (مرفوع/مقفول) مع Hysteresis عشان ما يرجّش."""
    UP = (1.15, 1.25, 1.25, 1.25, 1.25)
    DOWN = (1.0, 1.05, 1.05, 1.05, 1.05)

    def __init__(self):
        self.s = [False] * 5

    def update(self, lm):
        w = lm[0]
        ratios = [dist(lm[4], lm[17]) / max(dist(lm[3], lm[17]), 1e-6)]
        for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
            ratios.append(dist(w, lm[tip]) / max(dist(w, lm[pip]), 1e-6))
        for k, r in enumerate(ratios):
            if r > self.UP[k]:
                self.s[k] = True
            elif r < self.DOWN[k]:
                self.s[k] = False
        return list(self.s), ratios


def classify(s):
    t, i, m, r, p = s
    if i and m and r and p:
        return "PALM"
    if i and m and r:
        return "THREE"
    if i and m:
        return "PEACE"
    if i:
        return "POINT"
    if t and p and not (m or r):
        return "SHAKA"
    if not (i or m or r or p):
        return "FIST"
    return "OTHER"


# ============================ التحكم في الصوت ============================
class Volume:
    """pycaw لو متاح (دقيق) وإلا مفاتيح الكيبورد (كل ضغطة ≈ 2%)."""

    def __init__(self):
        self.ep = None
        self.est = 50.0
        self.muted = False
        try:
            from pycaw.pycaw import AudioUtilities
            dev = AudioUtilities.GetSpeakers()
            if hasattr(dev, "EndpointVolume"):
                self.ep = dev.EndpointVolume
            else:
                from ctypes import POINTER, cast
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import IAudioEndpointVolume
                iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.ep = cast(iface, POINTER(IAudioEndpointVolume))
            self.est = self.ep.GetMasterVolumeLevelScalar() * 100
            self.muted = bool(self.ep.GetMute())
        except Exception:
            self.ep = None

    @property
    def precise(self):
        return self.ep is not None

    def get(self):
        if self.ep is not None:
            try:
                self.est = self.ep.GetMasterVolumeLevelScalar() * 100
            except Exception:
                pass
        return self.est

    def set(self, level):
        level = float(max(0, min(100, level)))
        if self.ep is not None:
            try:
                self.ep.SetMasterVolumeLevelScalar(level / 100.0, None)
                self.est = level
                return
            except Exception:
                pass
        steps = int(round((level - self.est) / 2))
        if steps:
            pyautogui.press("volumeup" if steps > 0 else "volumedown", presses=abs(steps), interval=0)
            self.est = max(0, min(100, self.est + steps * 2))

    def toggle_mute(self):
        if self.ep is not None:
            try:
                self.muted = not bool(self.ep.GetMute())
                self.ep.SetMute(1 if self.muted else 0, None)
                return self.muted
            except Exception:
                pass
        pyautogui.press("volumemute")
        self.muted = not self.muted
        return self.muted


# ============================ البرنامج الرئيسي ============================
def main():
    cap = open_camera()
    if not cap.isOpened():
        raise SystemExit("مش قادر أفتح الكاميرا. جرّب CAM_INDEX = 1")

    hands = mp_hands.Hands(max_num_hands=1, model_complexity=1,
                           min_detection_confidence=0.7, min_tracking_confidence=0.6)
    vol = Volume()
    fingers = Fingers()

    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN, *PREVIEW_SIZE)
    try:
        cv2.setWindowProperty(WIN, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        pass

    st = SimpleNamespace(
        enabled=True, sens=SENSITIVITY, pinch_on=PINCH_ON,
        fx=OneEuro(FILTER_MIN_CUTOFF, FILTER_BETA), fy=OneEuro(FILTER_MIN_CUTOFF, FILTER_BETA),
        prev=None, rem=(0.0, 0.0), lock_until=0.0, moving=False,
        active=None, pinch_start=0.0, dragging=False, cand=None, cand_n=0,
        scroll_y=None, scroll_acc=0.0, vol_ref_y=None, vol_ref=0.0,
        hold_g=None, hold_t0=0.0, fired=None, last_action=0.0,
        flash=("", WHITE, 0.0), hist=deque(maxlen=GESTURE_WINDOW),
        show_help=True, mini=False, vol_show_until=0.0, mode="-", ratios=None, anchor=None,
    )
    HOLDS = {"PALM": TOGGLE_HOLD, "FIST": PLAY_HOLD, "SHAKA": MUTE_HOLD}

    def flash(msg, color=YELLOW, dur=0.8):
        st.flash = (msg, color, time.time() + dur)

    def lift():
        """رفع الصباع من التاتش باد: المؤشر بيقف والمرجع بيتصفّر (مفيش قفزات)."""
        st.prev = None
        st.rem = (0.0, 0.0)
        st.fx.reset()
        st.fy.reset()
        st.moving = False

    def release_all():
        if st.dragging:
            pyautogui.mouseUp(button=st.active or "left")
        st.dragging = False
        st.active = None
        st.cand, st.cand_n = None, 0
        lift()

    def toggle_mouse():
        release_all()
        st.enabled = not st.enabled
        flash("MOUSE ON" if st.enabled else "MOUSE OFF", GREEN if st.enabled else RED, 1.2)

    def play_pause():
        pyautogui.press("playpause")
        flash("PLAY / PAUSE", CYAN)

    def mute():
        m = vol.toggle_mute()
        flash("MUTED" if m else "UNMUTED", ORANGE)
        st.vol_show_until = time.time() + 1.5

    def pointer(lm, now):
        """حركة نسبية (Relative) + فلتر + تسارع = إحساس التاتش باد."""
        ax = 0.7 * lm[5].x + 0.3 * lm[8].x
        ay = 0.7 * lm[5].y + 0.3 * lm[8].y
        st.anchor = (ax, ay)
        fx, fy = st.fx(ax, now), st.fy(ay, now)
        st.moving = True
        if st.prev is None:
            st.prev = (fx, fy, now)
            return
        ox, oy, ot = st.prev
        dt = max(now - ot, 1e-3)
        dx, dy = fx - ox, (fy - oy) * 0.75            # 0.75 = نسبة الكاميرا 4:3
        st.prev = (fx, fy, now)
        speed = math.hypot(dx, dy) / dt
        mult = min(MIN_GAIN + ACCEL * speed, MAX_GAIN)
        k = SCREEN_W * st.sens * mult
        mx, my = dx * k + st.rem[0], dy * k + st.rem[1]
        ix, iy = int(mx), int(my)
        st.rem = (mx - ix, my - iy)
        if ix or iy:
            cx, cy = pyautogui.position()
            pyautogui.moveTo(min(max(cx + ix, 0), SCREEN_W - 1),
                             min(max(cy + iy, 0), SCREEN_H - 1), _pause=False)

    def detect_pinch(d_idx, d_mid, idx_ext, mid_ext):
        on = st.pinch_on
        off = on * PINCH_RELEASE_RATIO
        if st.active == "left":
            return "left" if d_idx < off else None
        if st.active == "right":
            return "right" if d_mid < off else None
        if idx_ext and d_idx < on and d_idx <= d_mid:
            return "left"
        if mid_ext and d_mid < on and d_idx > on * 1.5:
            return "right"
        return None

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            now = time.time()
            res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            st.anchor = None

            if res.multi_hand_landmarks:
                hl = res.multi_hand_landmarks[0]
                lm = hl.landmark
                mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)

                palm = max(dist(lm[0], lm[9]), 1e-6)
                up, ratios = fingers.update(lm)
                d_idx = dist(lm[4], lm[8]) / palm
                d_mid = dist(lm[4], lm[12]) / palm
                idx_ext, mid_ext = ratios[1] > 1.0, ratios[2] > 1.0
                st.ratios = (d_idx, d_mid)

                # مؤشرات القرصة على الصورة
                for tip, d, label in ((8, d_idx, "L"), (12, d_mid, "R")):
                    p1 = (int(lm[4].x * w), int(lm[4].y * h))
                    p2 = (int(lm[tip].x * w), int(lm[tip].y * h))
                    r = d / st.pinch_on
                    col = GREEN if r < 1 else (YELLOW if r < 1.8 else GRAY)
                    if r < 1.8:
                        cv2.line(frame, p1, p2, col, 2)
                        cv2.circle(frame, ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2), 8, col, -1)
                        put(frame, label, (p2[0] + 8, p2[1] - 8), col, 0.5, 1)

                # ---------- القرصة ----------
                pinch = None
                if st.enabled:
                    raw = detect_pinch(d_idx, d_mid, idx_ext, mid_ext)
                    if st.active is None:
                        if raw and raw == st.cand:
                            st.cand_n += 1
                        else:
                            st.cand, st.cand_n = raw, (1 if raw else 0)
                        pinch = st.cand if (raw and st.cand_n >= PINCH_CONFIRM_FRAMES) else None
                    else:
                        pinch = raw

                gesture = classify(up)
                if not pinch and st.active is None:
                    st.hist.append(gesture)
                top, cnt = Counter(st.hist).most_common(1)[0] if st.hist else ("OTHER", 0)
                stable = top if cnt >= GESTURE_NEED else "OTHER"

                # ---------- إيماءات المسك ----------
                if st.fired is not None and stable != st.fired:
                    st.fired = None
                if (stable in HOLDS and (st.enabled or stable == "PALM")
                        and not pinch and st.active is None):
                    if st.hold_g != stable:
                        st.hold_g, st.hold_t0 = stable, now
                    if st.fired != stable and now - st.last_action > ACTION_COOLDOWN:
                        prog = min((now - st.hold_t0) / HOLDS[stable], 1.0)
                        cv2.rectangle(frame, (10, h - 28), (210, h - 12), (60, 60, 60), -1)
                        cv2.rectangle(frame, (10, h - 28), (10 + int(200 * prog), h - 12), CYAN, -1)
                        put(frame, stable, (220, h - 14), CYAN)
                        if prog >= 1.0:
                            {"PALM": toggle_mouse, "FIST": play_pause, "SHAKA": mute}[stable]()
                            st.fired, st.last_action = stable, now
                else:
                    st.hold_g = None

                # ---------- تنفيذ الإجراءات ----------
                if not st.enabled:
                    st.mode = "OFF"
                    lift()
                elif pinch:
                    if st.active is None:
                        st.active, st.pinch_start = pinch, now
                    if not st.dragging and now - st.pinch_start > DRAG_HOLD:
                        pyautogui.mouseDown(button=st.active)
                        st.dragging = True
                        flash("DRAG " + st.active.upper(), ORANGE, 0.6)
                    if st.dragging:
                        pointer(lm, now)
                        st.mode = "DRAG " + st.active.upper()
                    else:
                        lift()                     # المؤشر ثابت لحد ما نعرف كليك ولا دراج
                        st.mode = "PINCH " + st.active.upper()
                    st.scroll_y = st.vol_ref_y = None
                else:
                    if st.active is not None:      # القرصة اتفتحت
                        btn = st.active
                        if st.dragging:
                            pyautogui.mouseUp(button=btn)
                            flash("DROP", ORANGE, 0.5)
                        else:
                            pyautogui.click(button=btn)
                            flash("LEFT CLICK" if btn == "left" else "RIGHT CLICK",
                                  GREEN if btn == "left" else CYAN, 0.6)
                        st.active, st.dragging = None, False
                        st.cand, st.cand_n = None, 0
                        st.lock_until = now + CLICK_LOCK
                        lift()
                        st.mode = "CLICK"
                    elif now < st.lock_until:
                        lift()
                    elif stable == "POINT" and d_idx > st.pinch_on * 1.35:
                        pointer(lm, now)
                        st.mode = "MOVE"
                        st.scroll_y = st.vol_ref_y = None
                    elif stable == "POINT":
                        lift()                     # صباعك قرّب من الإبهام: ثبّت المؤشر للكليك
                        st.mode = "READY"
                    elif stable == "PEACE":
                        lift()
                        y = lm[9].y
                        if st.scroll_y is not None:
                            dy = y - st.scroll_y
                            if abs(dy) > SCROLL_DEADZONE:
                                st.scroll_acc += (dy if NATURAL_SCROLL else -dy) * SCROLL_GAIN
                                n = int(st.scroll_acc)
                                if n:
                                    pyautogui.scroll(n)
                                    st.scroll_acc -= n
                        st.scroll_y, st.vol_ref_y = y, None
                        st.mode = "SCROLL"
                    elif stable == "THREE":
                        lift()
                        y = lm[9].y
                        if st.vol_ref_y is None:
                            st.vol_ref_y, st.vol_ref = y, vol.get()
                        vol.set(st.vol_ref + (st.vol_ref_y - y) / VOL_RANGE * 100.0)
                        st.vol_show_until = now + 1.5
                        st.scroll_y = None
                        st.mode = "VOLUME"
                    else:
                        lift()
                        st.scroll_y = st.vol_ref_y = None
                        st.mode = "LIFTED" if stable in ("PALM", "FIST", "SHAKA") else "..."
            else:
                release_all()
                st.scroll_y = st.vol_ref_y = None
                st.hold_g, st.fired = None, None
                st.hist.clear()
                st.ratios = None
                st.mode = "NO HAND" if st.enabled else "OFF"

            # ============================ HUD ============================
            if st.anchor:
                ap = (int(st.anchor[0] * w), int(st.anchor[1] * h))
                cv2.circle(frame, ap, 10, GREEN if st.moving else GRAY, 2)

            put(frame, "MOUSE: " + ("ON" if st.enabled else "OFF"), (10, 24),
                GREEN if st.enabled else RED, 0.7, 2)
            put(frame, "Mode: " + st.mode, (10, 48), WHITE, 0.55)
            info = f"Speed {st.sens:.1f} | Click sens {st.pinch_on:.2f}"
            if st.ratios:
                info += f" | L {st.ratios[0]:.2f}  R {st.ratios[1]:.2f}"
            put(frame, info, (10, 68), (190, 190, 190), 0.42)

            if now < st.vol_show_until or st.mode == "VOLUME":
                lvl = vol.get()
                bx, by0, by1 = w - 36, 90, h - 50
                cv2.rectangle(frame, (bx, by0), (bx + 18, by1), (60, 60, 60), -1)
                fy_ = int(by1 - (by1 - by0) * lvl / 100.0)
                cv2.rectangle(frame, (bx, fy_), (bx + 18, by1), RED if vol.muted else GREEN, -1)
                put(frame, "MUTE" if vol.muted else f"{int(lvl)}%", (bx - 8, by0 - 8),
                    RED if vol.muted else WHITE, 0.5, 1)
                if not vol.precise:
                    put(frame, "(approx)", (bx - 30, by1 + 16), (180, 180, 180), 0.4, 1)

            msg, col, until = st.flash
            if now < until:
                (tw, _), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                put(frame, msg, ((w - tw) // 2, 110), col, 1.0, 2)

            if st.show_help:
                lines = ["Point = move like a touchpad (open/close hand = lift finger)",
                         "Tap thumb+index = Left | thumb+middle = Right | hold = Drag",
                         "2 fingers = Scroll | 3 fingers = Volume",
                         "Fist 1s = Play/Pause | Shaka 0.8s = Mute | Palm 1.5s = ON/OFF",
                         "T toggle | SPACE play | M mute | [ ] speed | +/- click | V size | H help"]
                y0 = h - 104
                ov = frame.copy()
                cv2.rectangle(ov, (0, y0 - 16), (w, h - 34), (0, 0, 0), -1)
                frame = cv2.addWeighted(ov, 0.45, frame, 0.55, 0)
                for k, ln in enumerate(lines):
                    put(frame, ln, (8, y0 + k * 16), (220, 220, 220), 0.4, 1)

            cv2.imshow(WIN, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            elif key == ord("t"):
                toggle_mouse()
            elif key == ord(" "):
                play_pause()
            elif key == ord("m"):
                mute()
            elif key == ord("]"):
                st.sens = min(4.0, st.sens + 0.2)
            elif key == ord("["):
                st.sens = max(0.4, st.sens - 0.2)
            elif key in (ord("+"), ord("=")):
                st.pinch_on = min(0.60, st.pinch_on + 0.02)
            elif key in (ord("-"), ord("_")):
                st.pinch_on = max(0.12, st.pinch_on - 0.02)
            elif key == ord("v"):
                st.mini = not st.mini
                cv2.resizeWindow(WIN, *(MINI_SIZE if st.mini else PREVIEW_SIZE))
            elif key == ord("h"):
                st.show_help = not st.show_help
    finally:
        release_all()
        hands.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
