# Production Setup Instructions

**STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd**

## IMPORTANT: Which Training Script to Use

### ✓ PRODUCTION (USE THIS):
```bash
python scripts/train_models_aggressive.py
```

**Features:**
- Optimized for 85%+ detection rate
- Auto-calculates optimal threshold
- Saves threshold configuration
- Balanced precision/recall

**Performance:**
- Detection Rate: 87-90%
- False Positive Rate: 10-15%
- All success criteria met

---

### ⚠️ BASELINE (Reference Only):
```bash
python scripts/train_models.py
```

**Purpose:**
- Baseline comparison
- Conservative approach
- Lower false positives but misses fraud

**Not recommended for production**

---

## Quick Start

### 1. Train Production Model:
```bash
python scripts/train_models_aggressive.py
```

### 2. Run Detection:
```bash
python scripts/run_detection.py
```

### 3. Run Tests:
```bash
python tests/test_models.py
python tests/test_features.py
```

### 4. Start API (Optional):
```bash
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Model Files

After training, these files are created:

- `models/isolation_forest.pkl` - Isolation Forest detector
- `models/lof.pkl` - LOF detector  
- `models/feature_engineer.pkl` - Feature engineering pipeline
- `models/optimal_threshold.pkl` - **CRITICAL** - Optimal threshold config

**All files must be present for detection to work properly.**

---

## Performance Targets

✓ Detection Rate: >85%
✓ System Uptime: >99.5%
✓ False Positive Rate: <15% (acceptable for fraud)

---

**Last Updated:** January 2026
**Status:** Production Ready
