# Stage 4: Boyce-Codd Normal Form (BCNF) Explanation

## 1. What functional dependencies did you check?
We checked all functional dependencies in each table:
* `projects`: `ProjectID` is the primary key and determines all other attributes.
* `clients`: `ClientID` determines all client attributes.
* `supervisors`: `SupervisorID` determines all supervisor attributes.
* `workers`: `WorkerID` determines all worker attributes.
* `suppliers`: `SupplierID` determines all supplier attributes.
* `project_materials`: `(ProjectID, MaterialID)` determines `SupplierID` and `MaterialUnitCost`. The determinant is the candidate key.
* `project_equipment`: `(ProjectID, EquipmentID)` determines `EquipmentRentalCost`. The determinant is the candidate key.
* Junction tables (`project_workers`, `project_suppliers`, `worker_skills`, `worker_certifications`, `supplier_phones`): Contain only key attributes and have no non-trivial dependencies.

## 2. Why does this design satisfy BCNF?
A relation is in BCNF if for every functional dependency $X \rightarrow Y$, $X$ is a superkey. In our corrected design:
1. Every determinant in every table is a candidate key.
2. The transitive and partial dependencies have been completely resolved.
3. No non-key attribute determines a candidate key or part of a candidate key.
