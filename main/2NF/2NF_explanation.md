# Stage 2: Second Normal Form (2NF) Explanation

## 1. Which tables had composite keys?
In 1NF, the single flat table had a massive composite primary key:
`(ProjectID, WorkerName, Skill, Certification, SupplierPhone, MaterialSupplied, EquipmentUsed)`

## 2. Which columns depended only on part of a composite key?
There were extensive partial dependencies (non-key columns depending on a subset of the composite key):
1. **Project details** (`ProjectName`, `ProjectType`, etc.) depended only on `ProjectID`.
2. **Worker details** (`WorkerPhone`, `WorkerHourlyRate`) depended only on `WorkerName`.
3. **Supplier details** (`SupplierCity`) depended only on `SupplierName`.
4. **Material Unit Cost** depended on `(ProjectID, SupplierName, MaterialSupplied)`.
5. **Equipment Rental Cost** depended on `(ProjectID, EquipmentUsed)`.

## 3. Which data did you move into separate tables?
To resolve all partial dependencies, we decomposed the table into **9 separate tables**:
1. `projects.csv`: Contains project information.
2. `workers.csv`: Contains worker attributes.
3. `worker_skills.csv`: Many-to-many relationship of workers and skills.
4. `worker_certifications.csv`: Many-to-many relationship of workers and certifications.
5. `project_workers.csv`: Many-to-many project assignment of workers.
6. `suppliers.csv`: Contains supplier details.
7. `supplier_phones.csv`: Many-to-many relationship of suppliers and phone numbers.
8. `project_materials.csv`: Ternary relationship linking projects, suppliers, materials, and their unit costs.
9. `project_equipment.csv`: Relationship linking projects, equipment, and rental costs.

*Note: Transitive dependencies (such as Client details depending on ClientName in the projects table, and Supervisor details depending on SupervisorName in the projects table) are retained inside projects.csv since they do not violate 2NF (they are not partial dependencies).*

## 4. What primary keys and foreign keys did you introduce?
| Table | Primary Key | Foreign Key | References |
| :--- | :--- | :--- | :--- |
| `projects.csv` | `ProjectID` | None | - |
| `workers.csv` | `WorkerName` | None | - |
| `worker_skills.csv` | `(WorkerName, Skill)` | `WorkerName` | `workers.WorkerName` |
| `worker_certifications.csv` | `(WorkerName, Certification)` | `WorkerName` | `workers.WorkerName` |
| `project_workers.csv` | `(ProjectID, WorkerName)` | `ProjectID`, `WorkerName` | `projects.ProjectID`, `workers.WorkerName` |
| `suppliers.csv` | `SupplierName` | None | - |
| `supplier_phones.csv` | `(SupplierName, SupplierPhone)` | `SupplierName` | `suppliers.SupplierName` |
| `project_materials.csv` | `(ProjectID, SupplierName, MaterialSupplied)` | `ProjectID`, `SupplierName` | `projects.ProjectID`, `suppliers.SupplierName` |
| `project_equipment.csv` | `(ProjectID, EquipmentUsed)` | `ProjectID` | `projects.ProjectID` |

## 5. Why is your design now in 2NF?
A table is in 2NF if it is in 1NF and contains no partial dependencies. 
* Tables with single-attribute primary keys (`projects`, `workers`, `suppliers`) cannot have partial dependencies.
* Junction tables without non-key attributes (`worker_skills`, `worker_certifications`, `project_workers`, `supplier_phones`) cannot violate 2NF.
* Tables with composite keys and non-key attributes (`project_materials`, `project_equipment`) have their non-key attributes (`MaterialUnitCost`, `EquipmentRentalCost`) dependent on the entire composite key.
