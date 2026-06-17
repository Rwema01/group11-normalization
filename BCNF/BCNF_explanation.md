# BCNF Transformation - Group 11

## Overview

Boyce-Codd Normal Form (BCNF) is stricter than 3NF: **for every non-trivial functional dependency X → Y, X must be a candidate key** (superkey). We reviewed every table from the 3NF design, identified violations, decomposed the offending tables, and confirmed that all remaining tables satisfy BCNF.

## Which functional dependencies did you check?

We checked all functional dependencies (FDs) in each 3NF table:

| Table | Functional Dependencies Checked | Result |
|-------|--------------------------------|--------|
| `projects` | ProjectID → all other columns | ProjectID is PK ✓ |
| `clients` | ClientID → ClientName, ClientPhone, ClientEmail, ClientCity | ClientID is PK ✓ |
| `supervisors` | SupervisorID → SupervisorName, SupervisorPhone | SupervisorID is PK ✓ |
| `workers` | WorkerID → WorkerName, WorkerPhone, WorkerHourlyRate; WorkerName → WorkerPhone, WorkerHourlyRate | Both WorkerID and WorkerName are candidate keys ✓ |
| `project_workers` | (ProjectID, WorkerID) → (no non-key attrs) | Composite PK only ✓ |
| `worker_skills` | (WorkerID, Skill) → (no non-key attrs) | Composite PK only ✓ |
| `worker_certifications` | (WorkerID, Certification) → (no non-key attrs) | Composite PK only ✓ |
| `suppliers` | SupplierID → SupplierName, SupplierCity; SupplierName → SupplierCity | Both SupplierID and SupplierName are candidate keys ✓ |
| `supplier_phones` | (SupplierID, Phone) → (no non-key attrs); Phone → SupplierID | Phone is a candidate key ✓ |
| `project_suppliers` | (ProjectID, SupplierID) → (no non-key attrs) | Composite PK only ✓ |
| **`materials`** | **MaterialID → MaterialName, MaterialUnitCost; MaterialName → MaterialUnitCost** | **VIOLATION — see below** |
| **`equipment`** | **EquipmentID → EquipmentName, EquipmentRentalCost; EquipmentName → EquipmentRentalCost** | **VIOLATION — see below** |
| `project_materials` | (ProjectID, MaterialID) → (no non-key attrs) | Junction only — cost was missing |
| `project_equipment` | (ProjectID, EquipmentID) → (no non-key attrs) | Junction only — cost was missing |

## Did you find any determinant that was not a candidate key?

**Yes — in the `materials` and `equipment` tables from 3NF.**

### Violation 1: `materials` table

**3NF structure:** `materials(MaterialID, MaterialName, MaterialUnitCost)`

**Problematic FD:** `MaterialName → MaterialUnitCost`

In the raw data, the **same material name does not always have the same unit cost**:

| Material | Project | Unit Cost |
|----------|---------|-----------|
| Concrete | P001 | 120 |
| Concrete | P002 | 110 |
| Concrete | P005 | 130 |
| Concrete | P006 | 115 |
| Concrete | P007 | 140 |
| Steel Beams | P001, P004 | 500 |
| Steel Beams | P007 | 520 |

Storing a single `MaterialUnitCost` per `MaterialName` in the `materials` table forces one value (e.g., 120 for Concrete) and **loses the other valid costs**. The FD `MaterialName → MaterialUnitCost` is not valid in this dataset.

Even if we treated `MaterialName` as a candidate key, assigning one cost per material name would be **incorrect**. The cost is really determined by the **project–material combination**: `(ProjectID, MaterialName) → MaterialUnitCost`.

### Violation 2: `equipment` table

**3NF structure:** `equipment(EquipmentID, EquipmentName, EquipmentRentalCost)`

**Problematic FD:** `EquipmentName → EquipmentRentalCost`

The same equipment type has **different rental costs on different projects**:

| Equipment | Project | Rental Cost |
|-----------|---------|-------------|
| Crane | P001 | 5000 |
| Crane | P002 | 5500 |
| Crane | P004 | 6000 |
| Crane | P007 | 6500 |
| Bulldozer | P001 | 3000 |
| Bulldozer | P005 | 3200 |
| Mixer | P003 | 800 |
| Mixer | P005 | 1000 |
| Mixer | P006 | 900 |

Storing one `EquipmentRentalCost` per `EquipmentName` is incorrect. The rental cost depends on `(ProjectID, EquipmentName) → EquipmentRentalCost`.

## Which table or tables violated BCNF?

| Violating Table | Invalid FD | Why It Violates BCNF |
|-----------------|------------|----------------------|
| `materials` | MaterialName → MaterialUnitCost | MaterialName cannot functionally determine a single unit cost; cost varies by project |
| `equipment` | EquipmentName → EquipmentRentalCost | EquipmentName cannot functionally determine a single rental cost; cost varies by project |

All other 3NF tables already satisfied BCNF (see table above).

## How did you decompose the table or tables?

### `materials` decomposition

**Before (3NF — violates BCNF):**
```
materials(MaterialID, MaterialName, MaterialUnitCost)
project_materials(ProjectID, MaterialID)
```

**After (BCNF):**
```
materials(MaterialID, MaterialName)
project_materials(ProjectID, MaterialID, MaterialUnitCost)
```

- Removed `MaterialUnitCost` from `materials` — material identity is separate from project-specific pricing.
- Added `MaterialUnitCost` to `project_materials` — cost now depends on the full composite key `(ProjectID, MaterialID)`.

### `equipment` decomposition

**Before (3NF — violates BCNF):**
```
equipment(EquipmentID, EquipmentName, EquipmentRentalCost)
project_equipment(ProjectID, EquipmentID)
```

**After (BCNF):**
```
equipment(EquipmentID, EquipmentName)
project_equipment(ProjectID, EquipmentID, EquipmentRentalCost)
```

- Removed `EquipmentRentalCost` from `equipment`.
- Added `EquipmentRentalCost` to `project_equipment` — cost depends on `(ProjectID, EquipmentID)`.

## What candidate keys exist after decomposition?

| Table | Primary Key | Other Candidate Keys |
|-------|-------------|----------------------|
| `materials` | MaterialID | MaterialName |
| `equipment` | EquipmentID | EquipmentName |
| `project_materials` | (ProjectID, MaterialID) | None |
| `project_equipment` | (ProjectID, EquipmentID) | None |
| `workers` | WorkerID | WorkerName |
| `suppliers` | SupplierID | SupplierName |
| `supplier_phones` | (SupplierID, Phone) | Phone |
| All other tables | Same as 3NF | Unchanged |

After decomposition:
- In `materials`, the only FD is `MaterialID → MaterialName` (and `MaterialName → MaterialID`). Both determinants are candidate keys.
- In `project_materials`, the only FD is `(ProjectID, MaterialID) → MaterialUnitCost`. The determinant is the primary key.
- Same logic applies to `equipment` and `project_equipment`.

## Why is your design now in BCNF?

1. **Every determinant is a candidate key** — for each table, every functional dependency X → Y has X as a superkey.
2. **Project-specific costs are preserved** — Concrete can cost 120 on P001 and 110 on P002 without contradiction.
3. **No invalid global FDs** — we no longer claim MaterialName → MaterialUnitCost or EquipmentName → EquipmentRentalCost across the whole database.
4. **All other tables were already in BCNF** — we verified `workers` (WorkerName is a candidate key), `supplier_phones` (Phone is a candidate key), and all junction tables (keys only, no partial attributes).

## Tables Already in BCNF (No Changes Needed)

These 3NF tables were checked and **left unchanged** in BCNF:

- `projects`, `clients`, `supervisors`
- `workers`, `project_workers`
- `worker_skills`, `worker_certifications`
- `suppliers`, `supplier_phones`, `project_suppliers`

## Files Produced

```
BCNF/
  projects.csv
  clients.csv
  supervisors.csv
  workers.csv
  project_workers.csv
  worker_skills.csv
  worker_certifications.csv
  suppliers.csv
  supplier_phones.csv
  project_suppliers.csv
  materials.csv              ← MaterialUnitCost removed
  equipment.csv              ← EquipmentRentalCost removed
  project_materials.csv      ← MaterialUnitCost added
  project_equipment.csv        ← EquipmentRentalCost added
```

Generated by `normalize_2nf_bcnf.py` from the raw CSV and 3NF surrogate-key mappings.
