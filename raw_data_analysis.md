# Raw Data Analysis - Group 11

## Entities Identified
1. **Project** - Construction projects
2. **Client** - Clients who own projects
3. **Supervisor** - Supervisors managing projects
4. **Worker** - Workers assigned to projects
5. **Supplier** - Suppliers providing materials
6. **Material** - Materials used in projects
7. **Equipment** - Equipment used in projects

## 1NF Violations

### Multi-valued Columns (contain `|` separator):
| Column | Example | Problem |
|--------|---------|---------|
| WorkerSkills | "Carpentry\|Framing" | Multiple skills per worker |
| WorkerCertifications | "OSHA\|First Aid" | Multiple certifications per worker |
| SupplierPhones | "617-555-9000\|617-555-9001" | Multiple phone numbers per supplier |
| MaterialSupplied | "Concrete\|Steel" | Multiple materials per project |
| MaterialUnitCost | "120\|300" | Multiple costs per material |
| EquipmentUsed | "Crane\|Bulldozer" | Multiple equipment per project |
| EquipmentRentalCost | "5000\|3000" | Multiple costs per equipment |

### Repeating Groups:
- Project details repeated for each worker
- Client details repeated
- Supplier details repeated

### Potential Primary Keys:
- ProjectID (unique identifier for projects)
- WorkerName + ProjectID (composite key for worker assignments)
- SupplierName (unique identifier for suppliers)

## Relationships Identified
- **Project → Client**: Many-to-One (one client can have many projects)
- **Project → Supervisor**: Many-to-One (one supervisor can manage many projects)
- **Project → Worker**: Many-to-Many (workers assigned to projects)
- **Project → Supplier**: Many-to-Many (suppliers provide materials to projects)
- **Project → Equipment**: Many-to-Many (equipment used on projects)
- **Worker → Skills**: One-to-Many (worker has multiple skills)
- **Worker → Certifications**: One-to-Many (worker has multiple certifications)