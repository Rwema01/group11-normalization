# Stage 1: First Normal Form (1NF) Explanation

## Which columns violated 1NF?
The raw data contained multi-valued fields where multiple independent items were stored in a single cell separated by a pipe (`|`). These violated the 1NF requirement for atomic values:
1. **WorkerSkills** (e.g. "Carpentry|Framing")
2. **WorkerCertifications** (e.g. "OSHA|First Aid")
3. **SupplierPhones** (e.g. "617-555-9000|617-555-9001")
4. **MaterialSupplied** & **MaterialUnitCost** (paired multi-valued fields)
5. **EquipmentUsed** & **EquipmentRentalCost** (paired multi-valued fields)

Additionally, there were repeating groups of project-level and worker-level attributes.

## How did you make the values atomic?
We exploded each of the multi-valued attributes:
* Singular fields (`WorkerSkills`, `WorkerCertifications`, `SupplierPhones`) were split by `|` and exploded into separate rows.
* Paired fields (`MaterialSupplied` + `MaterialUnitCost` and `EquipmentUsed` + `EquipmentRentalCost`) were split in parallel and zipped into tuples before exploding, ensuring that each material and equipment retained its correct associated cost.

## Did you create new rows, new tables, or both?
For 1NF, we created **new rows only**. The entire dataset resides in a single, wide flat table (`1NF_table.csv`) where all cells are now atomic. This resulted in an expansion from 15 original rows to **280 rows** to cover all Cartesian combinations of independent multi-valued attributes.

## What key or combination of keys identifies each row?
Since all attributes are in a single table, the composite primary key must contain all fields that can vary independently. The composite primary key is:
`(ProjectID, WorkerName, Skill, Certification, SupplierPhone, MaterialSupplied, EquipmentUsed)`
