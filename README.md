# 🖐️ Air Mouse TOUCHPAD

**ماوس بالكاميرا بأسلوب التاتش باد** — تحكّم في الماوس والصوت والميديا (يوتيوب وغيره) بإيد واحدة من غير ما تلمس أي حاجة.

> Control your PC with one hand and a webcam: touchpad-style cursor, clicks, drag, scroll, volume, mute and media play/pause.

![Python](https://img.shields.io/badge/Python-3.9--3.12-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-green)

- [العربية](#العربية)
- [English](#english)

---

## العربية

### الفكرة

إيدك = صباعك على التاتش باد.

- المؤشر بيتحرك بـ **الفرق في حركة إيدك** (Relative Mode) مش بمكانها في الكاميرا، فمش لازم توصل بإيدك لأطراف الصورة عشان توصل لأطراف الشاشة.
- لما تفتح إيدك أو تقفلها = **رفعت الصباع من التاتش باد**: المؤشر بيقف وتقدر ترجّع إيدك لمكان مريح، ولما ترجع تشاور بيكمّل من مكانه من غير قفزات.
- **حركة بطيئة = دقة عالية** (تضغط على زراير يوتيوب الصغيرة)، **حركة سريعة = المؤشر بيعدّي الشاشة** (Acceleration).
- فلتر **One-Euro** بيشيل رعشة اليد وقت الثبات من غير ما يأخّر الحركة السريعة.

### المميزات

- تحريك المؤشر بأسلوب التاتش باد (تسارع + تنعيم متكيّف)
- كليك شمال / يمين / دبل كليك / دراج (سحب وإفلات)
- سكرول رأسي
- تحكم في مستوى الصوت (دقيق عبر `pycaw`، أو بمفاتيح الكيبورد كبديل)
- Play/Pause للميديا وكتم الصوت
- تشغيل/إيقاف الماوس بالكامل بإيماءة أو بزرار
- نافذة كاميرا صغيرة فوق باقي النوافذ مع مؤشرات بصرية (خط القرصة، شريط الصوت، رسائل الكليك)

### المتطلبات

| العنصر | التفاصيل |
|---|---|
| نظام التشغيل | Windows (الصوت الدقيق ومفاتيح الميديا والسكرول مضبوطين على ويندوز) |
| Python | 3.9 إلى 3.12 |
| الكاميرا | أي ويب كام (640×480 كفاية) |
| الإضاءة | إضاءة كويسة قدام اليد بتحسّن الدقة كتير |

### التثبيت

```powershell
pip install opencv-python mediapipe==0.10.14 pyautogui numpy pycaw comtypes
```

- `pycaw` و `comtypes` **اختياريين**: من غيرهم الصوت بيشتغل بمفاتيح الكيبورد وبيبقى تقريبي.
- ثبّت `mediapipe==0.10.14` بالظبط، لأن الإصدارات الأحدث ممكن تشيل `mp.solutions`.

> **مهم:** لو عندك أكتر من نسخة Python، ثبّت بنفس النسخة اللي هتشغّل بيها:
> ```powershell
> & <مسار-python.exe> -m pip install opencv-python mediapipe==0.10.14 pyautogui numpy pycaw comtypes
> ```

### التشغيل

```powershell
python air_mouse_touchpad.py
```

هتفتح نافذة الكاميرا. وجّه إيدك للكاميرا وابدأ.

### الإيماءات

| الإيماءة | الوظيفة |
|---|---|
| ☝️ السبابة فقط | تحريك المؤشر (تاتش باد) |
| 🤏 قرصة سريعة: إبهام + سبابة | كليك شمال |
| 🤏🤏 قرصتين سريعتين | دبل كليك (فل سكرين يوتيوب) |
| 🤏 قرصة إبهام + سبابة وتفضل ماسكها (0.4 ثانية) | دراج (سحب وإفلات) |
| 🤏 قرصة: إبهام + وسطى | كليك يمين |
| ✌️ سبابة + وسطى | سكرول (حرّك إيدك فوق/تحت) |
| 🤟 سبابة + وسطى + بنصر | تحكم في الصوت (فوق = أعلى، تحت = أوطى) |
| ✊ قبضة 1 ثانية | Play / Pause |
| 🤙 إبهام + خنصر 0.8 ثانية | كتم / إلغاء كتم |
| 🖐️ كف مفتوح 1.5 ثانية | تشغيل / إيقاف الماوس |

الإيماءات اللي بتتطلب مسك بيظهر لها شريط تقدّم أزرق على الشاشة.

### اختصارات الكيبورد (على نافذة الكاميرا)

| المفتاح | الوظيفة |
|---|---|
| `T` | تشغيل/إيقاف الماوس |
| `SPACE` | Play / Pause |
| `M` | كتم |
| `[` / `]` | تقليل / زيادة سرعة المؤشر |
| `-` / `+` | تقليل / زيادة حساسية القرصة (أعلى = أسهل) |
| `V` | تصغير / تكبير نافذة الكاميرا |
| `H` | إظهار / إخفاء المساعدة |
| `Q` أو `ESC` | خروج |

### استخدامها مع يوتيوب

1. شاور بالسبابة على الفيديو أو الزرار.
2. اعمل **Tap** سريع (إبهام + سبابة) للكليك.
3. **قرصتين سريعتين** على الفيديو = فل سكرين.
4. **قبضة ثانية** = Play/Pause حتى لو المؤشر مش على الفيديو.
5. **ثلاث صوابع** وحرّك إيدك للتحكم في الصوت.
6. **سبابة + وسطى** لسكرول التعليقات.

### الإعدادات

كل الإعدادات في أول الملف تحت `الإعدادات`:

| المتغيّر | الوظيفة | ملاحظة |
|---|---|---|
| `SENSITIVITY` | سرعة المؤشر الأساسية | بتتعدل لايف بـ `[` `]` |
| `MIN_GAIN` / `ACCEL` / `MAX_GAIN` | منحنى التسارع | قلّل `MIN_GAIN` لدقة أعلى |
| `FILTER_MIN_CUTOFF` | تنعيم وقت الثبات | قلّله (مثلاً 0.8) لو لسه فيه رعشة |
| `FILTER_BETA` | استجابة الحركة السريعة | أعلى = أسرع |
| `CLICK_LOCK` | تثبيت المؤشر بعد الكليك | بيضمن الدبل كليك |
| `PINCH_ON` | حساسية القرصة | بتتعدل لايف بـ `+` `-` |
| `DRAG_HOLD` | مدة المسك للتحول لدراج | |
| `SCROLL_GAIN` | سرعة السكرول | `120` = نوتش واحد |
| `NATURAL_SCROLL` | اتجاه السكرول | `True` = زي الموبايل |
| `VOL_RANGE` | حساسية الصوت | أقل = أسرع |
| `TOGGLE_HOLD` / `PLAY_HOLD` / `MUTE_HOLD` | مدة المسك للإيماءات | |
| `CAM_INDEX` | رقم الكاميرا | جرّب `1` لو الكاميرا مش بتفتح |

### حل المشاكل

| المشكلة | الحل |
|---|---|
| `ModuleNotFoundError: No module named 'pyautogui'` | المكتبات اتثبتت على Python تاني. ثبّت بنفس الـ Python اللي بتشغّل بيه (`python -m pip install ...`) |
| `module 'mediapipe' has no attribute 'solutions'` | ثبّت `mediapipe==0.10.14` |
| الكاميرا مش بتفتح | غيّر `CAM_INDEX` لـ `1` أو `2`، وقفل أي برنامج تاني بيستخدم الكاميرا |
| الكليك مش بيتسجل | بص على الرقمين `L` و `R` على الشاشة: لازم ينزلوا تحت `Click sens`. اضغط `+` |
| الكليك بيتفعّل لوحده | اضغط `-` |
| المؤشر فيه رعشة | قلّل `FILTER_MIN_CUTOFF` وحسّن الإضاءة |
| المؤشر بطيء أو سريع | `[` `]` أو `SENSITIVITY` |
| الصوت تقريبي وبيكتب `(approx)` | `pycaw` مش شغال. ثبّته (`pip install pycaw comtypes`) |
| Play/Pause مش بيشتغل | بيستخدم مفتاح الميديا العام، فلازم تبويب يوتيوب يكون شغّال في المتصفح |

### إزاي بيشتغل

1. **OpenCV** بيجيب الصورة من الكاميرا (ومعكوسة زي المراية).
2. **MediaPipe Hands** بيطلّع 21 نقطة لليد.
3. حالة كل صباع (مرفوع/مقفول) بتتحسب بنسبة المسافة من الرسغ، مع **Hysteresis** عشان الإيماءة ما ترجّش.
4. القرصة بتتقاس بنسبة لحجم الكف (فبتشتغل قريب أو بعيد من الكاميرا)، وبتتأكد على فريمين لمنع الكليك الغلط.
5. حركة المؤشر = فرق موضع نقطة ثابتة نسبياً في اليد → فلتر **One-Euro** → مضاعف يتغير حسب السرعة → **PyAutoGUI**.
6. الصوت عبر **pycaw** (Windows Core Audio)، والميديا عبر مفاتيح الكيبورد الخاصة بالميديا.

### تنبيهات

- `pyautogui.FAILSAFE` متقفل عشان المؤشر ما يتعلقش في زاوية الشاشة. **اخرج دايماً بـ `Q` أو `ESC`** من نافذة الكاميرا.
- لو فيه دراج شغّال والإيد اختفت من الكاميرا، الكود بيسيب الزرار تلقائياً.
- الأداء بيتأثر بالإضاءة وجودة الكاميرا وسرعة الجهاز.

---

## English

### Overview

Hand = finger on a touchpad.

- **Relative cursor movement**: the pointer follows hand *motion*, not absolute hand position, so you never have to reach the edge of the camera frame.
- **Clutch / lift**: opening or closing your hand lifts the "finger"; the cursor stops, you reposition, and continue without jumps.
- **Pointer acceleration**: slow motion for precision (small YouTube buttons), fast motion to cross the screen.
- **One-Euro filter** removes jitter at rest without adding lag during fast moves.

### Features

Touchpad-style pointer · left/right/double click · drag & drop · vertical scroll · volume control (precise via `pycaw`, keyboard-key fallback) · media play/pause · mute · global on/off gesture · always-on-top mini preview with visual feedback.

### Requirements

Windows · Python 3.9–3.12 · any webcam · decent lighting.

### Install

```powershell
pip install opencv-python mediapipe==0.10.14 pyautogui numpy pycaw comtypes
```

`pycaw`/`comtypes` are optional. Pin `mediapipe==0.10.14`; newer releases may drop `mp.solutions`. If you have several Python installs, use `python -m pip ...` with the same interpreter you run the script with.

### Run

```powershell
python air_mouse_touchpad.py
```

### Gestures

| Gesture | Action |
|---|---|
| ☝️ Index finger only | Move cursor |
| 🤏 Quick pinch: thumb + index | Left click |
| 🤏🤏 Two quick pinches | Double click (YouTube fullscreen) |
| 🤏 Pinch and hold (0.4 s) | Drag & drop |
| 🤏 Pinch: thumb + middle | Right click |
| ✌️ Index + middle | Scroll (move hand up/down) |
| 🤟 Index + middle + ring | Volume (up = louder, down = quieter) |
| ✊ Fist, 1 s | Play / Pause |
| 🤙 Thumb + pinky, 0.8 s | Mute / unmute |
| 🖐️ Open palm, 1.5 s | Mouse ON / OFF |

### Keyboard shortcuts (camera window focused)

`T` toggle · `SPACE` play/pause · `M` mute · `[` `]` cursor speed · `-` `+` pinch sensitivity · `V` mini/normal preview · `H` help · `Q`/`ESC` quit.

### Configuration

All tunables are at the top of `air_mouse_touchpad.py` (`SENSITIVITY`, `MIN_GAIN`, `ACCEL`, `MAX_GAIN`, `FILTER_MIN_CUTOFF`, `FILTER_BETA`, `CLICK_LOCK`, `PINCH_ON`, `DRAG_HOLD`, `SCROLL_GAIN`, `NATURAL_SCROLL`, `VOL_RANGE`, hold durations, `CAM_INDEX`). Cursor speed and pinch sensitivity can also be changed live with the keyboard.

### Troubleshooting

- **`No module named 'pyautogui'`** → packages were installed for a different Python; use `python -m pip install ...`.
- **`mediapipe` has no attribute `solutions`** → install `mediapipe==0.10.14`.
- **Camera won't open** → try `CAM_INDEX = 1`, close other apps using the camera.
- **Clicks not registering** → the on-screen `L`/`R` values must drop below `Click sens`; press `+`.
- **Phantom clicks** → press `-`.
- **Jittery cursor** → lower `FILTER_MIN_CUTOFF` (e.g. 0.8) and improve lighting.
- **Volume shows `(approx)`** → `pycaw` is unavailable; install `pycaw comtypes`.

### How it works

OpenCV capture → MediaPipe Hands (21 landmarks) → per-finger state with hysteresis → palm-normalized pinch detection with frame confirmation → relative cursor motion with One-Euro filtering and speed-based gain → PyAutoGUI for mouse/keyboard events; `pycaw` for master volume.

### Safety notes

PyAutoGUI's fail-safe is disabled so the cursor can't get stuck in a screen corner — **always quit with `Q`/`ESC`**. Any active drag is released automatically if the hand leaves the frame.

---

## License

اختار الرخصة المناسبة لمشروعك (مثلاً MIT) وضيفها هنا.
