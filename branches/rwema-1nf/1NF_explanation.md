# 1NF Transformation - Group 11

## Which columns violated 1NF?

The following columns contained multiple values in a single cell (separated by `|`):

1. **WorkerSkills** - Multiple skills per worker (e.g., "Carpentry|Framing")
2. **WorkerCertifications** - Multiple certifications per worker (e.g., "OSHA|First Aid")
3. **SupplierPhones** - Multiple phone numbers per supplier (e.g., "617-555-9000|617-555-9001")
4. **MaterialSupplied** - Multiple materials per project (e.g., "Concrete|Steel")
5. **MaterialUnitCost** - Multiple costs linked to materials
6. **EquipmentUsed** - Multiple equipment per project (e.g., "Crane|Bulldozer")
7. **EquipmentRentalCost** - Multiple costs linked to equipment

Additionally, there were repeating groups where project data was duplicated for each worker.

## How did you make the values atomic?

I used Python with pandas to split the multi-valued columns:

1. **WorkerSkills** → Used `explode()` function to split each skill into separate rows
2. **WorkerCertifications** → Used `explode()` function to split each certification into separate rows
3. **SupplierPhones** → Used `explode()` function to split each phone number into separate rows
4. **MaterialSupplied + MaterialUnitCost** → Created a custom `explode_paired_columns()` function to split these together, ensuring each material keeps its correct cost
5. **EquipmentUsed + EquipmentRentalCost** → Used the same paired approach to split equipment with its rental cost

For each column, the `|` character was used as the separator. When a cell had multiple values (e.g., "Carpentry|Framing"), the script created separate rows for each value.

**Results:**
- Original rows: 15
- After 1NF: 280 rows
- All cells now contain atomic values

## Did you create new rows, new tables, or both?

I created **new rows only** for this stage. The data is still in one large table (1NF_table.csv), but now each row represents a unique atomic combination.

For example, if a worker had 2 skills and 2 certifications, that created 4 rows (2 × 2) for that worker.

I did **not** create new tables yet — that will happen in 2NF, 3NF, BCNF, and 4NF.

## What key or combination of keys identifies each row?

The composite key that uniquely identifies each row is:

**`(ProjectID, WorkerName, Skill, Certification, SupplierPhone, MaterialSupplied, EquipmentUsed)`**

This combination is unique because:
- `ProjectID` identifies the project
- `WorkerName` identifies the specific worker
- `Skill` identifies the specific skill
- `Certification` identifies the specific certification
- `SupplierPhone` identifies the supplier contact
- `MaterialSupplied` identifies the specific material
- `EquipmentUsed` identifies the specific equipment

No two rows have the exact same combination of all these fields.