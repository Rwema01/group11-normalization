# Stage 5: Fourth Normal Form (4NF) Explanation

## 1. What multi-valued dependencies (MVDs) did you find?
Multi-valued dependencies exist when an attribute $X$ multi-determines independent sets of attributes $Y$ and $Z$ ($X \twoheadrightarrow Y$ and $X \twoheadrightarrow Z$):
1. **Worker-related MVDs**: A worker has multiple independent multi-valued attributes:
   * `WorkerID ->-> Skill`
   * `WorkerID ->-> Certification`
   These are independent of each other (a worker's certifications do not determine or depend on their skills).
2. **Project-related MVDs**: A project is associated with multiple independent sets:
   * `ProjectID ->-> WorkerID`
   * `ProjectID ->-> MaterialID` (and SupplierID)
   * `ProjectID ->-> EquipmentID`
   These are independent of each other (the workers assigned to a project do not depend on the equipment used, etc.).

## 2. How did you resolve them?
We resolved them by separating these independent multi-valued facts into separate tables:
* Workers: Decomposed into `worker_skills` and `worker_certifications`.
* Projects: Decomposed into `project_workers`, `project_materials`, and `project_equipment`.

Because these independent multi-valued facts are completely isolated in their own junction tables, the database contains no non-trivial multi-valued dependencies. Therefore, the design is in **4NF**.
