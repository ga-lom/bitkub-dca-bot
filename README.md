# Bitkub DCA Bot (ซื้อ BTC อัตโนมัติวันละครั้ง)

บอท Python แบบเรียบง่ายสำหรับ **ซื้อ BTC อัตโนมัติบน Bitkub วันละครั้ง** ตามเวลาที่ตั้งไว้ โดยใช้คำสั่ง **Market Order** 

> ⚠️ **คำเตือน**: โปรเจกต์นี้มีไว้เพื่อการศึกษา/ทดลองใช้งาน การซื้อขายมีความเสี่ยง คุณรับผิดชอบเงินทุนและการจัดการ API Key เองทั้งหมด

---

## บอททำอะไรได้บ้าง

- ซื้อ BTC **วันละครั้ง** ตามเวลา `DCA_TIME`
- ใช้เงิน THB จำนวน `DCA_AMOUNT_THB` ต่อครั้ง (Market Buy)
- ถ้าเงิน THB ไม่พอ → **ข้ามการซื้อ**
- บันทึก Log ลงไฟล์ `dca_bot.log` ในโฟลเดอร์โปรเจกต์
- ต้องเปิดโปรเซสค้างไว้ตลอด (บอทจะทำงานตามเวลา)

---

## ความต้องการของระบบ

- Python **3.9+** (แนะนำ)
- อินเทอร์เน็ต
- Bitkub API Key ที่มีสิทธิ์:
  - **View** (จำเป็น)
  - **Trade** (จำเป็น)

---

## ไฟล์ในโปรเจกต์

```
.
├── dca_bot.py            # โปรแกรมหลัก
├── test_connection.py    # สคริปต์ทดสอบ API ก่อนใช้งานจริง
├── requirements.txt
├── .env.example
├── bitkub-dca.service    # systemd service (สำหรับ Raspberry Pi / Linux)
├── install.sh            # สคริปต์ติดตั้งอัตโนมัติบน Raspberry Pi
├── uninstall.sh          # สคริปต์ถอนการติดตั้ง
└── README.md
```

---

## 1) สร้าง Bitkub API Key

1. ล็อกอิน https://www.bitkub.com/th/api-management
2. สร้าง API Key ใหม่ (ตั้งชื่อเช่น `DCA Bot`)
3. เปิดสิทธิ์:
   - ✅ View
   - ✅ Trade
4. เก็บ **API Key** และ **API Secret** ไว้ให้ปลอดภัย

> 🔒 ห้ามแชร์ API Secret และห้ามอัปโหลดไฟล์ `.env` ขึ้น GitHub

---

## 2) ติดตั้งและรัน (Windows)

### 2.1 ติดตั้ง Python (ทำครั้งแรกเท่านั้น)
- ดาวน์โหลด Python จาก python.org
- ตอนติดตั้งให้ติ๊ก **“Add Python to PATH”**
- เปิด **PowerShell** แล้วตรวจสอบ:
```powershell
python --version
```

### 2.2 ดาวน์โหลดโปรเจกต์
ตัวเลือก A (แนะนำ): Clone ด้วย Git
```powershell
git clone https://github.com/ga-lom/bitkub-dca-bot.git
cd bitkub-dca-bot
```

ตัวเลือก B: ดาวน์โหลด ZIP จาก GitHub → แตกไฟล์ → เปิดโฟลเดอร์ด้วย PowerShell

### 2.3 สร้าง Virtual Environment และติดตั้งไลบรารี
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2.4 ตั้งค่าไฟล์ `.env`
```powershell
copy .env.example .env
notepad .env
```

กรอกค่าตัวอย่าง:
```env
BITKUB_API_KEY=YOUR_API_KEY
BITKUB_API_SECRET=YOUR_API_SECRET
DCA_AMOUNT_THB=108 #จำนวนเงินที่จะซื้อ 
DCA_TIME=09:00 #เวลาที่จะซื้อ
SYMBOL=btc_thb
```

### 2.5 รันบอท
```powershell
python dca_bot.py
```

หยุดบอท:
```text
Ctrl + C
```

---

## 3) ติดตั้งและรัน (Linux / macOS)

### 3.1 ติดตั้งเครื่องมือพื้นฐาน (Linux)
Debian/Ubuntu:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
python3 --version
```

### 3.2 ดาวน์โหลดโปรเจกต์
```bash
git clone https://github.com/ga-lom/bitkub-dca-bot.git
cd bitkub-dca-bot
```

### 3.3 สร้าง Virtual Environment และติดตั้งไลบรารี
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.4 ตั้งค่าไฟล์ `.env`
```bash
cp .env.example .env
nano .env
```

### 3.5 รันบอท
```bash
python dca_bot.py
```

หยุดบอท:
```text
Ctrl + C
```

---

## 4) ติดตั้งบน Raspberry Pi แบบ systemd service (รัน 24/7 อัตโนมัติ)

ติดตั้งลง `/home/pi/bitkub-dca` พร้อม service ที่รีสตาร์ทเองเมื่อล่มและเริ่มอัตโนมัติเมื่อบูท:

```bash
git clone https://github.com/ga-lom/bitkub-dca-bot.git
cd bitkub-dca-bot
chmod +x install.sh
./install.sh

# ใส่ API key
nano /home/pi/bitkub-dca/.env

# ทดสอบ API ก่อนเริ่มใช้งานจริง
cd /home/pi/bitkub-dca
source venv/bin/activate
python test_connection.py
deactivate

# เริ่ม service
sudo systemctl start bitkub-dca
sudo systemctl enable bitkub-dca
```

ดู log:
```bash
journalctl -u bitkub-dca -f
tail -f /home/pi/bitkub-dca/dca_bot.log
```

ถอนการติดตั้ง: `./uninstall.sh`

---

## อธิบายค่าตั้งค่า (.env)

| ตัวแปร | ความหมาย | ตัวอย่าง |
|---|---|---|
| `BITKUB_API_KEY` | API key ของ Bitkub | `abc...` |
| `BITKUB_API_SECRET` | API secret ของ Bitkub | `def...` |
| `DCA_AMOUNT_THB` | จำนวนเงิน THB ที่จะซื้อ/วัน | `100` |
| `DCA_TIME` | เวลาที่จะซื้อ (HH:MM) | `09:00` |
| `SYMBOL` | คู่เหรียญ | `btc_thb` |

หมายเหตุ:
- โดยทั่วไปยอดซื้อขั้นต่ำควร **>= 10 THB** (ตัวบอทมีการตรวจสอบ)
- เวลา `DCA_TIME` ต้องเป็นรูปแบบ **HH:MM**
- เวลาอ้างอิงจาก **timezone ของระบบที่รันบอท** (ถ้าเวลาเพี้ยน ให้ตรวจ timezone/เวลาของเครื่อง)

---

## Logs

บอทจะเขียน log ลงไฟล์:
- `dca_bot.log`

ดู log แบบเรียลไทม์ (Linux/macOS):
```bash
tail -f dca_bot.log
```

---

## ความปลอดภัย (สำคัญ)

- แนะนำให้สร้าง **API Key แยก** สำหรับบอท
- เปิดสิทธิ์เท่าที่จำเป็น: **View + Trade**
- ห้าม commit `.env` ขึ้น GitHub
- รักษาความปลอดภัยเครื่องที่รันบอท (รหัสผ่าน/อัปเดตระบบ)

---

## แก้ปัญหาที่พบบ่อย (Troubleshooting)

### `ModuleNotFoundError` / ไลบรารีไม่เจอ
ตรวจว่าคุณ activate venv แล้ว:
- Windows: `venv\Scripts\activate`
- Linux/macOS: `source venv/bin/activate`

จากนั้นติดตั้งใหม่:
```bash
pip install -r requirements.txt
```

### Error แนว “Invalid signature” / auth ไม่ผ่าน
- ตรวจ API key/secret ใน `.env`
- ตรวจเวลา/Timezone ของเครื่องให้ถูกต้อง (เวลาคลาดเคลื่อนทำให้ signature ผิดได้)
ตั้ง timezone เป็นเวลาไทย
```bash
sudo timedatectl set-timezone Asia/Bangkok
```

### บอทไม่ซื้อ “ตรงเวลา”
- ตรวจรูปแบบ `DCA_TIME` ให้เป็น `HH:MM`
- ตรวจว่าบอทยังรันอยู่ (ไม่ปิด terminal/ไม่ถูก kill)
- เปิดดู `dca_bot.log` เพื่อหาสาเหตุ

---

## License

MIT
