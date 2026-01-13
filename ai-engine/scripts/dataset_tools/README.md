# Dataset Manager - Smart Factory Safety Monitoring

Pipeline otomatis untuk konversi dan validasi dataset Computer Vision berstandar industri.

## 🎯 Fitur Utama

- ✅ Konversi XML (Pascal VOC) ke YOLO format
- ✅ Merge multi-source dataset (Roboflow + Kaggle)
- ✅ Auto-split train/valid/test (70/20/10)
- ✅ Visual validation dengan bounding box
- ✅ Statistik lengkap per-dataset

## 📦 Struktur Dataset

```
Dataset_Manager/
├── source_roboflow/          # Dataset Roboflow (sudah YOLO format)
│   ├── train/
│   ├── valid/
│   ├── test/
│   └── data_construction.yaml
├── source_kaggle/            # Dataset Kaggle (XML format)
│   ├── *.xml
│   └── *.png
├── converted_kaggle_yolo/    # Hasil konversi (auto-generated)
├── merged_dataset/           # Dataset final (auto-generated)
└── validation_visual/        # Sampel visual (auto-generated)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Konversi XML ke YOLO

```bash
python xml_to_yolo_converter.py
```

**Output:**
- `converted_kaggle_yolo/labels/` - Anotasi YOLO format
- `converted_kaggle_yolo/images/` - Gambar yang sudah dikonversi

### 3. Merge Dataset

```bash
python merge_datasets.py
```

**Output:**
- `merged_dataset/train/` - 70% data
- `merged_dataset/valid/` - 20% data
- `merged_dataset/test/` - 10% data
- `merged_dataset/data.yaml` - Config untuk training

### 4. Validasi Visual

```bash
python visual_validator.py
```

**Output:**
- `validation_visual/train/` - Sampel train dengan bbox
- `validation_visual/valid/` - Sampel valid dengan bbox
- `validation_visual/test/` - Sampel test dengan bbox
- `validation_visual/legend.png` - Legend warna per kelas

## 📋 Label Mapping

| Kaggle XML | Roboflow Construction | Class ID | Color |
|------------|----------------------|----------|-------|
| `helmet` | `Hardhat` | 0 | 🟢 Green |
| `head` | `NO-Hardhat` | 2 | 🔴 Red |

**Full Class List (10 kelas):**
0. Hardhat
1. Mask
2. NO-Hardhat
3. NO-Mask
4. NO-Safety Vest
5. Person
6. Safety Cone
7. Safety Vest
8. machinery
9. vehicle

## ⚠️ Important Notes

### 1. Koordinat Normalisasi
Format YOLO menggunakan koordinat normalized [0-1]:
```
class_id x_center y_center width height
```

### 2. Empty Annotations
File `.txt` kosong = negative sample (background), bukan error!

### 3. Verifikasi Visual WAJIB
Sebelum training, **SELALU** cek hasil di `validation_visual/`:
- ✅ Bbox alignment benar
- ✅ Label class sesuai
- ✅ Tidak ada koordinat meleset

## 📊 Expected Output

```
📊 MERGE SUMMARY
================================================================
TRAIN:
  Roboflow: 3,000 files
  Kaggle:   3,500 files
  Total:    6,500 files

VALID:
  Roboflow: 500 files
  Kaggle:   1,000 files
  Total:    1,500 files

TEST:
  Roboflow: 200 files
  Kaggle:   500 files
  Total:    700 files

🎯 GRAND TOTAL: 8,700 images
```

## 🎨 Visual Validation Preview

Setelah run `visual_validator.py`, cek folder `validation_visual/`:
- Bbox hijau = Hardhat (aman)
- Bbox merah = NO-Hardhat (bahaya)
- Legend lengkap di `legend.png`

## 🔧 Troubleshooting

**Q: "Image not found" error?**  
A: Pastikan file .png/.jpg ada di folder yang sama dengan .xml

**Q: Bbox meleset?**  
A: Bug di normalisasi koordinat. Cek ulang w/h gambar di XML

**Q: Class ID tidak dikenali?**  
A: Tambahkan mapping di `LABEL_MAPPING` di converter

## 📝 Training Next

```bash
# Gunakan data.yaml hasil merge
yolo train model=yolov8n.pt data=merged_dataset/data.yaml epochs=100
```

## 🏗️ Architecture Reference

Proyek ini mengikuti blueprint **Smart Factory/Safety Monitoring** dengan:
- Multi-camera ingestion ready (Golang layer)
- Real-time inference optimized (Python + TensorRT)
- Edge-cloud hybrid deployment capable

---

**Created for**: Industry-grade CV pipeline  
**Dataset Sources**: Roboflow Universe + Kaggle Hard Hat Workers  
**Format**: YOLOv8 compatible
