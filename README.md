
# Keyboard Backlight Driver For Clevo / Monster / Tuxedo Linux

**Comprehensive RGB keyboard backlight manager for Clevo, Monster and Tuxedo laptops on Linux**

An interactive terminal-based keyboard lighting manager featuring 19 effects, real-time screen/audio/microphone synchronization, CPU temperature tracking, profile management and systemd integration.

---

## Features

| Category | Details |
|---|---|
| **Standard Effects** | Static, Breathing, Wave, Reactive, Cycle, Ripple, Rain, Snake, Starlight, Radar, Vortex, Heartbeat, Fireworks, Sine Wave, Neon |
| **Sync Modes** | Screen Sync, Music Sync, Mic Sync |
| **System Tracking** | Automatic color based on CPU temperature (Cool → Blue, Hot → Red) |
| **Profile Management** | Save, load and delete named profiles |
| **Systemd** | Create, enable and manage a background service |
| **Interface** | Interactive color terminal menu |

---

## Requirements

```
python >= 3.8
brightnessctl
cava          (required for Music Sync and Mic Sync)
python-pillow (required for Screen Sync)
scrot         (required for Screen Sync on X11; grim is used on Wayland)
```

### Install Dependencies

```bash
sudo pacman -S brightnessctl cava python-pillow scrot
```

On Wayland, `grim` can be used instead of `scrot` — the tool detects it automatically.

---

## Installation

```bash
git clone https://github.com/berfinbtw/Keyboard-Backlight-Driver-For-Clevo-Monster-Tuxedo-Linux.git
cd Keyboard-Backlight-Driver-For-Clevo-Monster-Tuxedo-Linux
chmod +x kbd-rgb.py
python3 kbd-rgb.py
```

### Passwordless Access via udev Rule (Recommended)

By default, writing to the LED path requires root privileges. The following rule removes the need for `sudo`:

```bash
echo 'SUBSYSTEM=="leds", KERNEL=="rgb:kbd_backlight", RUN+="/bin/chmod a+w /sys/class/leds/rgb:kbd_backlight/multi_intensity"' \
  | sudo tee /etc/udev/rules.d/99-kbd-rgb.rules

sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Usage

```bash
python3 kbd-rgb.py
```

On startup, the tool automatically restores and applies the last saved effect.

### Daemon Mode (for Systemd)

```bash
python3 kbd-rgb.py --daemon --effect breathing --color 0 100 255 --brightness 80 --speed 0.05
```

| Argument | Description |
|---|---|
| `--effect <n>` | Effect name (e.g. `breathing`, `wave`, `cpu_temp`) |
| `--color R G B` | RGB values in the 0–255 range |
| `--brightness <0-100>` | Brightness percentage |
| `--speed <float>` | Effect speed (lower = faster; recommended: 0.01–0.15) |

---

## Effects

### Standard

| Effect | Description |
|---|---|
| `static` | Solid color |
| `breathing` | Pulsing brightness |
| `wave` | Cycling color wave |
| `reactive` | Flash and fade |
| `cycle` | Slow full-spectrum cycle |
| `ripple` | Rippling pulse |
| `rain` | Rainfall effect in blue tones |
| `snake` | Rainbow color sweep |
| `starlight` | Randomly twinkling stars |
| `radar` | Radar sweep animation |
| `vortex` | Spinning color vortex |
| `heartbeat` | Heartbeat rhythm pattern |
| `fireworks` | Random firework bursts |
| `sine_wave` | Sine-modulated brightness |
| `neon` | Neon color transitions |

### Sync Modes

| Effect | Description | Requires |
|---|---|---|
| `screen_sync` | Mirrors the dominant screen color to the keyboard | Pillow + scrot/grim |
| `music_sync` | Brightness based on audio output level | cava |
| `mic_sync` | Brightness based on microphone input level | cava |
| `cpu_temp` | Blue (cool) → Red (hot) based on CPU temperature | — |

---

## Profile Management

Profiles are stored in `~/.config/kbd-rgb/profiles.json`. From the menu you can:

- Save the current effect, color, brightness and speed as a named profile
- Load and instantly apply any saved profile
- Delete profiles you no longer need

---

## Systemd Integration

From the **"Systemd Service"** menu option you can:

1. Generate `~/.config/systemd/user/kbd-rgb.service` based on current settings
2. Enable the service — it will start automatically on login
3. View the current service status

You can also manage it manually:

```bash
systemctl --user enable --now kbd-rgb.service
systemctl --user status kbd-rgb.service
systemctl --user disable --now kbd-rgb.service
```

---

## Configuration

Active settings are automatically saved to `~/.config/kbd-rgb/config.json`:

```json
{
  "effect": "breathing",
  "color": [0, 100, 255],
  "brightness": 80,
  "speed": 0.05
}
```

---

## Supported Hardware

Any Clevo, Monster or Tuxedo based laptop that exposes the LED control path:

```
/sys/class/leds/rgb:kbd_backlight/multi_intensity
```

To verify your device is supported:

```bash
ls /sys/class/leds/rgb:kbd_backlight/
```

---




TURKCE:


# Keyboard Backlight Driver For Clevo / Monster / Tuxedo Linux

**Clevo, Monster ve Tuxedo laptop klavyeleri için kapsamlı RGB yönetim aracı**

Terminalde çalışan etkileşimli bir klavye aydınlatma yöneticisidir. 19 efekt, gerçek zamanlı ekran/ses/mikrofon senkronizasyonu, CPU sıcaklık takibi, profil yönetimi ve systemd entegrasyonu içerir.

---

## Özellikler

| Kategori | İçerik |
|---|---|
| **Standart Efektler** | Static, Breathing, Wave, Reactive, Cycle, Ripple, Rain, Snake, Starlight, Radar, Vortex, Heartbeat, Fireworks, Sine Wave, Neon |
| **Senkronizasyon** | Screen Sync, Music Sync, Mic Sync |
| **Sistem Takibi** | CPU sıcaklığına göre otomatik renk (Soğuk → Mavi, Sıcak → Kırmızı) |
| **Profil Yönetimi** | Ayarları kaydet, yükle, sil |
| **Systemd** | Arka plan servisi oluştur, etkinleştir, yönet |
| **Arayüz** | Etkileşimli renkli terminal menüsü |

---

## Gereksinimler

```
python >= 3.8
brightnessctl
cava          (Music Sync ve Mic Sync için)
python-pillow (Screen Sync için)
scrot         (Screen Sync için, Wayland'da grim kullanılır)
```

### Bağımlılıkları Kur

```bash
sudo pacman -S brightnessctl cava python-pillow scrot
```

Wayland kullanıyorsanız `scrot` yerine `grim` kurulabilir — araç otomatik olarak algılar.

---

## Kurulum

```bash
git clone https://github.com/KULLANICI_ADIN/Keyboard-Backlight-Driver-For-Clevo-Monster-Tuxedo-Linux.git
cd Keyboard-Backlight-Driver-For-Clevo-Monster-Tuxedo-Linux
chmod +x kbd-rgb.py
python3 kbd-rgb.py
```

### Şifresiz Erişim için udev Kuralı (Önerilen)

Varsayılan olarak LED yoluna root yetkisi gerekir. Aşağıdaki kural `sudo` ihtiyacını ortadan kaldırır:

```bash
echo 'SUBSYSTEM=="leds", KERNEL=="rgb:kbd_backlight", RUN+="/bin/chmod a+w /sys/class/leds/rgb:kbd_backlight/multi_intensity"' \
  | sudo tee /etc/udev/rules.d/99-kbd-rgb.rules

sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Kullanım

```bash
python3 kbd-rgb.py
```

Program başladığında son kaydedilen efekti otomatik olarak yeniden başlatır.

### Daemon Modu (Systemd için)

```bash
python3 kbd-rgb.py --daemon --effect breathing --color 0 100 255 --brightness 80 --speed 0.05
```

| Argüman | Açıklama |
|---|---|
| `--effect <isim>` | Efekt adı (örn. `breathing`, `wave`, `cpu_temp`) |
| `--color R G B` | 0–255 aralığında RGB değerleri |
| `--brightness <0-100>` | Parlaklık yüzdesi |
| `--speed <float>` | Efekt hızı (küçük = hızlı, önerilen: 0.01–0.15) |

---

## Efektler

### Standart

| Efekt | Açıklama |
|---|---|
| `static` | Sabit renk |
| `breathing` | Nefes alma efekti |
| `wave` | Renk dalgası |
| `reactive` | Flaş ve sönen ışık |
| `cycle` | Yavaş renk döngüsü |
| `ripple` | Dalgalanma |
| `rain` | Yağmur efekti (mavi tonlar) |
| `snake` | Gökkuşağı renk geçişi |
| `starlight` | Rastgele parlayan yıldızlar |
| `radar` | Radar tarama efekti |
| `vortex` | Dönen renk girdabı |
| `heartbeat` | Kalp atışı ritmi |
| `fireworks` | Havai fişek patlamaları |
| `sine_wave` | Sinüs dalgası parlaklığı |
| `neon` | Neon renk geçişleri |

### Senkronizasyon

| Efekt | Açıklama | Gereksinim |
|---|---|---|
| `screen_sync` | Ekranda baskın rengi klavyeye yansıtır | Pillow + scrot/grim |
| `music_sync` | Ses çıkışı yoğunluğuna göre tonlama | cava |
| `mic_sync` | Mikrofon giriş şiddetine göre tonlama | cava |
| `cpu_temp` | CPU sıcaklığı → Mavi (soğuk) → Kırmızı (sıcak) | — |

---

## Profil Yönetimi

Profiller `~/.config/kbd-rgb/profiles.json` dosyasında saklanır. Menü üzerinden:

- Mevcut efekt, renk, parlaklık ve hızı profil olarak kaydedin
- Kayıtlı profili tek adımda yükleyip uygulayın
- İstenmeyen profilleri silin

---

## Systemd Entegrasyonu

Menüden **"Systemd Servis"** seçeneğine girerek:

1. Mevcut ayarlara göre `~/.config/systemd/user/kbd-rgb.service` dosyası oluşturun
2. Servisi etkinleştirin — oturum açıldığında otomatik başlar
3. Servis durumunu görüntüleyin

Manuel olarak da yönetilebilir:

```bash
systemctl --user enable --now kbd-rgb.service
systemctl --user status kbd-rgb.service
systemctl --user disable --now kbd-rgb.service
```

---

## Yapılandırma

Aktif ayarlar `~/.config/kbd-rgb/config.json` dosyasına otomatik kaydedilir:

```json
{
  "effect": "breathing",
  "color": [0, 100, 255],
  "brightness": 80,
  "speed": 0.05
}
```

---

## Desteklenen Donanım

`/sys/class/leds/rgb:kbd_backlight/multi_intensity` yolunu destekleyen tüm Monster ve Clevo tabanlı laptoplar.

Doğru yolun varlığını doğrulamak için:

```bash
ls /sys/class/leds/rgb:kbd_backlight/
```

---

## Lisans

MIT
## License

MIT
