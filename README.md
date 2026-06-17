# Group 11 - Database Normalization Activity

## 👥 Members
| Name | Role | Branch |
|------|------|--------|
| Karabo Innocent Pamela | Group Leader, 2NF Lead | `karabo-2nf` |
| Rwema Gisa | 1NF Lead | `rwema-1nf` |
| Sonia Wisdom Etuhoko | BCNF Lead | `sonia-bcnf` |
| Ange Umutoni | 3NF Lead | `ange-3nf` |
| Irene Wanjiru Winnie | 4NF Lead + Documentation | `irene-4nf-doc` |

## 📂 Project Structure
```text
group11-normalization/
├── README.md
├── big3_construction_raw_data.csv
├── generate_normalization.py
├── 1NF/
│   ├── 1NF_table.csv
│   ├── 1NF_explanation.md
│   ├── transform_to_1nf.py
│   └── raw_data_analysis.md
├── 2NF/
│   ├── projects.csv
│   ├── workers.csv
│   ├── worker_skills.csv
│   ├── worker_certifications.csv
│   ├── project_workers.csv
│   ├── suppliers.csv
│   ├── supplier_phones.csv
│   ├── project_materials.csv
│   ├── project_equipment.csv
│   ├── 2NF_explanation.md
│   ├── transform_to_2nf.py
│   └── verify_2nf.py
├── 3NF/
│   ├── [14 Decomposed CSV tables (projects, clients, supervisors, etc.)]
│   └── 3NF_explanation.md
├── BCNF/
│   ├── [14 BCNF-Compliant CSV tables]
│   └── BCNF_explanation.md
└── 4NF/
    ├── [14 4NF-Compliant CSV tables]
    └── 4NF_explanation.md
```

## 📋 Normalization Stages
| Stage | Description | Lead |
|-------|-------------|------|
| **1NF** | Atomic values, no repeating groups | Rwema ✅ |
| **2NF** | No partial dependencies | Karabo ✅ |
| **3NF** | No transitive dependencies | Ange ✅ |
| **BCNF** | Every determinant is a candidate key | Sonia ✅ |
| **4NF** | No multi-valued dependencies | Irene ✅ |

## 🔗 Repository
https://github.com/Rwema01/group11-normalization
