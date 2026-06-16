# Stage 2: Second Normal Form (2NF) Explanation

This document explains the normalization process applied to convert the 1NF table into Second Normal Form (2NF).

---

## 1. Which tables had composite keys?

In 1NF, all database attributes were stored in a single flat table (`1NF_table.csv`). This table required a massive composite primary key to uniquely identify each row:

*   **Primary Key in 1NF**: `(ProjectID, WorkerName, Skill, Certification, SupplierPhone, MaterialSupplied, EquipmentUsed)`

Since there was only one table, it was the only table with a composite key.

---

## 2. Which columns depended only on part of a composite key?

There were extensive partial dependencies in the 1NF table where non-key attributes depended on a proper subset of the composite key:

1.  **Project Details**:
    *   `ProjectName`, `ProjectType`, `StartDate`, `EndDate`, `SiteAddress`, `SiteCity`, `SiteState`, `ClientName`, `ClientPhone`, `ClientEmail`, `ClientCity`, `SupervisorName`, `SupervisorPhone`
    *   *Dependency*: These columns depend strictly on **`ProjectID`**, which is only a part of the 1NF composite key.
2.  **Worker Details**:
    *   `WorkerPhone`, `WorkerHourlyRate`
    *   *Dependency*: These columns depend strictly on **`WorkerName`**, which is only a part of the 1NF composite key.
3.  **Supplier Details**:
    *   `SupplierCity`
    *   *Dependency*: This column depends strictly on **`SupplierName`**, which is only a part of the 1NF composite key.
4.  **Material Details**:
    *   `MaterialUnitCost`
    *   *Dependency*: This column depends on **`(ProjectID, SupplierName, MaterialSupplied)`**, which is only a part of the 1NF composite key. (Unit costs vary by project and supplier, so they cannot depend on material name alone).
5.  **Equipment Details**:
    *   `EquipmentRentalCost`
    *   *Dependency*: This column depends on **`(ProjectID, EquipmentUsed)`**, which is only a part of the 1NF composite key. (Rental costs vary by project, so they cannot depend on equipment name alone).

---

## 3. Which data did you move into separate tables?

To resolve these partial dependencies, we extracted the entities and relationship details into **9 separate tables**:

1.  **`projects.csv`**: Contains project-level attributes.
2.  **`workers.csv`**: Contains worker-specific attributes.
3.  **`worker_skills.csv`**: Links workers to their skills (resolving the multi-valued worker skills attribute).
4.  **`worker_certifications.csv`**: Links workers to their certifications (resolving the multi-valued worker certifications attribute).
5.  **`project_workers.csv`**: Links workers to the construction projects they are assigned to.
6.  **`suppliers.csv`**: Contains supplier-level attributes.
7.  **`supplier_phones.csv`**: Links suppliers to their phone numbers (resolving the multi-valued supplier phone attribute).
8.  **`project_materials.csv`**: Links projects to the materials supplied by specific suppliers and records their unit costs.
9.  **`project_equipment.csv`**: Links projects to the rented equipment and records their rental costs.

---

## 4. What primary keys and foreign keys did you introduce?

We established clear primary and foreign key relationships to connect the entities:

| Table | Primary Key (PK) | Foreign Key (FK) | References |
| :--- | :--- | :--- | :--- |
| **`projects.csv`** | `ProjectID` | None | N/A |
| **`workers.csv`** | `WorkerName` | None | N/A |
| **`worker_skills.csv`** | `(WorkerName, Skill)` | `WorkerName` | `workers.WorkerName` |
| **`worker_certifications.csv`** | `(WorkerName, Certification)` | `WorkerName` | `workers.WorkerName` |
| **`project_workers.csv`** | `(ProjectID, WorkerName)` | `ProjectID`<br>`WorkerName` | `projects.ProjectID`<br>`workers.WorkerName` |
| **`suppliers.csv`** | `SupplierName` | None | N/A |
| **`supplier_phones.csv`** | `(SupplierName, SupplierPhone)` | `SupplierName` | `suppliers.SupplierName` |
| **`project_materials.csv`** | `(ProjectID, SupplierName, MaterialSupplied)` | `ProjectID`<br>`SupplierName` | `projects.ProjectID`<br>`suppliers.SupplierName` |
| **`project_equipment.csv`** | `(ProjectID, EquipmentUsed)` | `ProjectID` | `projects.ProjectID` |

---

## 5. Why is your design now in 2NF?

A database is in **Second Normal Form (2NF)** when:
1.  It is in First Normal Form (1NF) — *satisfied, all attributes are atomic, and rows are uniquely identifiable*.
2.  It contains **no partial dependencies** — *every non-key attribute is fully functionally dependent on the entire primary key, not a subset of it*.

Our decomposed schema satisfies 2NF for the following reasons:
*   **Single-Column Primary Keys**: The tables `projects.csv`, `workers.csv`, and `suppliers.csv` have single-column primary keys (`ProjectID`, `WorkerName`, and `SupplierName` respectively). Since their keys cannot be split, a partial dependency is mathematically impossible.
*   **Relationship Tables with No Non-Key Columns**: The tables `worker_skills.csv`, `worker_certifications.csv`, `project_workers.csv`, and `supplier_phones.csv` consist entirely of key columns that form the composite primary key. Because they have no non-key columns, they cannot violate 2NF.
*   **Composite Keys with Non-Key Columns**:
    *   In `project_materials.csv`, the non-key attribute `MaterialUnitCost` is determined by the *whole* composite key `(ProjectID, SupplierName, MaterialSupplied)`. It cannot depend on a subset like `MaterialSupplied` because the same material (e.g., Concrete) has different costs across different projects and suppliers.
    *   In `project_equipment.csv`, the non-key attribute `EquipmentRentalCost` is determined by the *whole* composite key `(ProjectID, EquipmentUsed)`. It cannot depend on `EquipmentUsed` alone because equipment rental costs vary by project.

By moving partially dependent attributes into separate tables focused on single entities or complete composite relationships, we have completely resolved all partial dependencies.
