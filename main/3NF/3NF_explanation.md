# Stage 3: Third Normal Form (3NF) Explanation

## 1. What transitive dependencies did you find?
Transitive dependency exists when a non-key attribute determines another non-key attribute:
1. `ProjectID -> ClientName -> (ClientPhone, ClientEmail, ClientCity)`
2. `ProjectID -> SupervisorName -> SupervisorPhone`
3. `ProjectID -> WorkerName -> (WorkerPhone, WorkerHourlyRate)`
4. `ProjectID -> SupplierName -> SupplierCity`
5. `(ProjectID, MaterialName) -> SupplierName -> SupplierCity`

## 2. How did you resolve them?
We extracted the transitive dependencies into their own tables and introduced surrogate key IDs (`ClientID`, `SupervisorID`, `WorkerID`, `SupplierID`, `MaterialID`, `EquipmentID`) to identify the entities:
1. **`clients.csv`**: Identified by `ClientID`.
2. **`supervisors.csv`**: Identified by `SupervisorID`.
3. **`workers.csv`**: Identified by `WorkerID`.
4. **`suppliers.csv`**: Identified by `SupplierID`.
5. **`materials.csv`**: Identified by `MaterialID`.
6. **`equipment.csv`**: Identified by `EquipmentID`.

We updated reference tables to use foreign keys pointing to these surrogate IDs.

## 3. Critical Fix: Non-Lossy Ternary Relationship for Materials
In previous manual 3NF designs:
* `project_materials` and `project_suppliers` were split into binary relations.
* **Bug:** This resulted in a **lossy join** where the connection of which supplier supplied which material to a project was lost.
* **Fix:** We resolved this by modeling `project_materials` as a ternary relation: `(ProjectID, MaterialID, SupplierID, MaterialUnitCost)`. This preserves the fact that BuildPro Supplies supplied Concrete to P001, and SteelWorks Inc supplied Steel Beams to P001.

## 4. Cost Location Fix
* **MaterialUnitCost** varies by project and supplier, so it is kept in `project_materials` with primary key `(ProjectID, MaterialID, SupplierID)`.
* **EquipmentRentalCost** varies by project, so it is kept in `project_equipment` with primary key `(ProjectID, EquipmentID)`.
