# 3NF Explanation - Group 11 | Big3 Construction Dataset

## Transitive Dependencies Found

| Non-Key Determinant | Dependent Attributes | Fix |
|---|---|---|
| `ClientName` | ClientPhone, ClientEmail, ClientCity | Extracted → `clients` table |
| `SupervisorName` | SupervisorPhone | Extracted → `supervisors` table |
| `WorkerName` | WorkerPhone, WorkerHourlyRate | Extracted → `workers` table |
| `SupplierName` | SupplierCity | Extracted → `suppliers` table |
| `MaterialName` | MaterialUnitCost | Extracted → `materials` table |
| `EquipmentName` | EquipmentRentalCost | Extracted → `equipment` table |

## New Tables Created (14 total)

| Table | Primary Key | Foreign Keys |
|---|---|---|
| `projects` | ProjectID | ClientID → clients, SupervisorID → supervisors |
| `clients` | ClientID | - |
| `supervisors` | SupervisorID | - |
| `workers` | WorkerID | - |
| `suppliers` | SupplierID | - |
| `materials` | MaterialID | - |
| `equipment` | EquipmentID | - |
| `project_workers` | (ProjectID, WorkerID) | → projects, → workers |
| `project_suppliers` | (ProjectID, SupplierID) | → projects, → suppliers |
| `project_materials` | (ProjectID, MaterialID) | → projects, → materials |
| `project_equipment` | (ProjectID, EquipmentID) | → projects, → equipment |
| `worker_skills` | (WorkerID, Skill) | → workers |
| `worker_certifications` | (WorkerID, Certification) | → workers |
| `supplier_phones` | (SupplierID, Phone) | → suppliers |

## Why This Is 3NF

- All tables are already in 2NF (no partial dependencies).
- No non-key attribute determines another non-key attribute in any table.
- e.g. in `projects`, every column depends only on `ProjectID`, not on `ClientID` or `SupervisorID`.
- e.g. in `materials`, `MaterialUnitCost` depends only on `MaterialID`, not on which project uses it.
- All relationships are preserved through foreign keys, no data is lost.