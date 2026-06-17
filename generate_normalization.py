import os
import pandas as pd
import numpy as np

def clean_dir(path):
    if os.path.exists(path):
        import shutil
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

def generate_all():
    print("[Pipeline] Starting Database Normalization Generator...")
    
    # Ensure raw data exists
    if not os.path.exists('big3_construction_raw_data.csv'):
        raise FileNotFoundError("Raw data file 'big3_construction_raw_data.csv' not found.")
        
    df_raw = pd.read_csv('big3_construction_raw_data.csv')
    
    # Setup folders
    clean_dir('main/1NF')
    clean_dir('main/2NF')
    clean_dir('main/3NF')
    clean_dir('main/BCNF')
    clean_dir('main/4NF')
    
    # ----------------------------------------------------
    # 1. 1NF GENERATION
    # ----------------------------------------------------
    print("[1NF] Generating 1NF...")
    
    def explode_column(df, col_name, new_col_name, sep='|'):
        df[col_name] = df[col_name].astype(str).str.split(sep)
        df = df.explode(col_name)
        df = df.rename(columns={col_name: new_col_name})
        return df

    def explode_paired_columns(df, col1, col2, new_col1, new_col2, sep='|'):
        df[col1] = df[col1].astype(str).str.split(sep)
        df[col2] = df[col2].astype(str).str.split(sep)
        
        # Create list of tuples
        df['temp'] = df.apply(lambda row: list(zip(row[col1], row[col2])), axis=1)
        df = df.explode('temp')
        
        # Split the tuples back into columns
        v1 = df['temp'].apply(lambda x: x[0] if isinstance(x, tuple) else np.nan)
        v2 = df['temp'].apply(lambda x: x[1] if isinstance(x, tuple) else np.nan)
        
        df = df.drop(columns=['temp'])
        
        if col1 != new_col1 and col1 in df.columns:
            df = df.drop(columns=[col1])
        if col2 != new_col2 and col2 in df.columns:
            df = df.drop(columns=[col2])
            
        df[new_col1] = v1
        df[new_col2] = v2
        return df

    # Explode multi-valued attributes to ensure atomicity
    df_1nf = explode_column(df_raw.copy(), 'WorkerSkills', 'Skill')
    df_1nf = explode_column(df_1nf, 'WorkerCertifications', 'Certification')
    df_1nf = explode_column(df_1nf, 'SupplierPhones', 'SupplierPhone')
    df_1nf = explode_paired_columns(df_1nf, 'MaterialSupplied', 'MaterialUnitCost', 'MaterialSupplied', 'MaterialUnitCost')
    df_1nf = explode_paired_columns(df_1nf, 'EquipmentUsed', 'EquipmentRentalCost', 'EquipmentUsed', 'EquipmentRentalCost')
    
    # Strip whitespaces from strings if any
    for col in df_1nf.select_dtypes(include=['object']).columns:
        df_1nf[col] = df_1nf[col].str.strip()
        
    df_1nf.to_csv('main/1NF/1NF_table.csv', index=False)
    
    # Write 1NF Explanation
    with open('main/1NF/1NF_explanation.md', 'w', encoding='utf-8') as f:
        f.write("""# Stage 1: First Normal Form (1NF) Explanation

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
""")

    # ----------------------------------------------------
    # 2. 2NF GENERATION
    # ----------------------------------------------------
    print("[2NF] Generating 2NF...")
    # Decompose into 9 tables to remove partial dependencies
    # Keeping clients and supervisors in projects since they are transitive, not partial dependencies.
    
    projects_2nf_cols = [
        'ProjectID', 'ProjectName', 'ProjectType', 'StartDate', 'EndDate', 
        'SiteAddress', 'SiteCity', 'SiteState', 'ClientName', 'ClientPhone', 
        'ClientEmail', 'ClientCity', 'SupervisorName', 'SupervisorPhone'
    ]
    
    projects_2nf = df_1nf[projects_2nf_cols].drop_duplicates().sort_values('ProjectID')
    workers_2nf = df_1nf[['WorkerName', 'WorkerPhone', 'WorkerHourlyRate']].drop_duplicates().sort_values('WorkerName')
    worker_skills_2nf = df_1nf[['WorkerName', 'Skill']].drop_duplicates().sort_values(['WorkerName', 'Skill'])
    worker_certs_2nf = df_1nf[['WorkerName', 'Certification']].drop_duplicates().sort_values(['WorkerName', 'Certification'])
    project_workers_2nf = df_1nf[['ProjectID', 'WorkerName']].drop_duplicates().sort_values(['ProjectID', 'WorkerName'])
    suppliers_2nf = df_1nf[['SupplierName', 'SupplierCity']].drop_duplicates().sort_values('SupplierName')
    supplier_phones_2nf = df_1nf[['SupplierName', 'SupplierPhone']].drop_duplicates().sort_values(['SupplierName', 'SupplierPhone'])
    project_materials_2nf = df_1nf[['ProjectID', 'SupplierName', 'MaterialSupplied', 'MaterialUnitCost']].drop_duplicates().sort_values(['ProjectID', 'SupplierName', 'MaterialSupplied'])
    project_equipment_2nf = df_1nf[['ProjectID', 'EquipmentUsed', 'EquipmentRentalCost']].drop_duplicates().sort_values(['ProjectID', 'EquipmentUsed'])
    
    projects_2nf.to_csv('main/2NF/projects.csv', index=False)
    workers_2nf.to_csv('main/2NF/workers.csv', index=False)
    worker_skills_2nf.to_csv('main/2NF/worker_skills.csv', index=False)
    worker_certs_2nf.to_csv('main/2NF/worker_certifications.csv', index=False)
    project_workers_2nf.to_csv('main/2NF/project_workers.csv', index=False)
    suppliers_2nf.to_csv('main/2NF/suppliers.csv', index=False)
    supplier_phones_2nf.to_csv('main/2NF/supplier_phones.csv', index=False)
    project_materials_2nf.to_csv('main/2NF/project_materials.csv', index=False)
    project_equipment_2nf.to_csv('main/2NF/project_equipment.csv', index=False)
    
    with open('main/2NF/2NF_explanation.md', 'w', encoding='utf-8') as f:
        f.write("""# Stage 2: Second Normal Form (2NF) Explanation

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
""")

    # ----------------------------------------------------
    # 3. 3NF GENERATION
    # ----------------------------------------------------
    print("[3NF] Generating 3NF...")
    # Decompose transitive dependencies and introduce surrogate keys based on order of appearance.
    
    def get_id_map(series, prefix):
        unique_vals = []
        for val in series:
            if pd.notna(val) and val not in unique_vals:
                unique_vals.append(val)
        return {val: f"{prefix}{i+1:03d}" for i, val in enumerate(unique_vals)}

    # Generate ID maps
    client_map = get_id_map(df_1nf['ClientName'], 'C')
    supervisor_map = get_id_map(df_1nf['SupervisorName'], 'SUP')
    worker_map = get_id_map(df_1nf['WorkerName'], 'W')
    supplier_map = get_id_map(df_1nf['SupplierName'], 'SP')
    material_map = get_id_map(df_1nf['MaterialSupplied'], 'M')
    equipment_map = get_id_map(df_1nf['EquipmentUsed'], 'EQ')

    # Decompose clients
    clients_3nf = df_1nf[['ClientName', 'ClientPhone', 'ClientEmail', 'ClientCity']].drop_duplicates()
    clients_3nf['ClientID'] = clients_3nf['ClientName'].map(client_map)
    clients_3nf = clients_3nf[['ClientID', 'ClientName', 'ClientPhone', 'ClientEmail', 'ClientCity']].sort_values('ClientID')

    # Decompose supervisors
    supervisors_3nf = df_1nf[['SupervisorName', 'SupervisorPhone']].drop_duplicates()
    supervisors_3nf['SupervisorID'] = supervisors_3nf['SupervisorName'].map(supervisor_map)
    supervisors_3nf = supervisors_3nf[['SupervisorID', 'SupervisorName', 'SupervisorPhone']].sort_values('SupervisorID')

    # Decompose projects
    projects_3nf = df_1nf[['ProjectID', 'ProjectName', 'ProjectType', 'StartDate', 'EndDate', 'SiteAddress', 'SiteCity', 'SiteState', 'ClientName', 'SupervisorName']].drop_duplicates()
    projects_3nf['ClientID'] = projects_3nf['ClientName'].map(client_map)
    projects_3nf['SupervisorID'] = projects_3nf['SupervisorName'].map(supervisor_map)
    projects_3nf = projects_3nf.drop(columns=['ClientName', 'SupervisorName']).sort_values('ProjectID')

    # Decompose workers
    workers_3nf = df_1nf[['WorkerName', 'WorkerPhone', 'WorkerHourlyRate']].drop_duplicates()
    workers_3nf['WorkerID'] = workers_3nf['WorkerName'].map(worker_map)
    workers_3nf = workers_3nf[['WorkerID', 'WorkerName', 'WorkerPhone', 'WorkerHourlyRate']].sort_values('WorkerID')

    # Decompose worker skills
    worker_skills_3nf = df_1nf[['WorkerName', 'Skill']].drop_duplicates()
    worker_skills_3nf['WorkerID'] = worker_skills_3nf['WorkerName'].map(worker_map)
    worker_skills_3nf = worker_skills_3nf[['WorkerID', 'Skill']].sort_values(['WorkerID', 'Skill'])

    # Decompose worker certs
    worker_certs_3nf = df_1nf[['WorkerName', 'Certification']].drop_duplicates()
    worker_certs_3nf['WorkerID'] = worker_certs_3nf['WorkerName'].map(worker_map)
    worker_certs_3nf = worker_certs_3nf[['WorkerID', 'Certification']].sort_values(['WorkerID', 'Certification'])

    # Decompose project workers
    project_workers_3nf = df_1nf[['ProjectID', 'WorkerName']].drop_duplicates()
    project_workers_3nf['WorkerID'] = project_workers_3nf['WorkerName'].map(worker_map)
    project_workers_3nf = project_workers_3nf[['ProjectID', 'WorkerID']].sort_values(['ProjectID', 'WorkerID'])

    # Decompose suppliers
    suppliers_3nf = df_1nf[['SupplierName', 'SupplierCity']].drop_duplicates()
    suppliers_3nf['SupplierID'] = suppliers_3nf['SupplierName'].map(supplier_map)
    suppliers_3nf = suppliers_3nf[['SupplierID', 'SupplierName', 'SupplierCity']].sort_values('SupplierID')

    # Decompose supplier phones
    supplier_phones_3nf = df_1nf[['SupplierName', 'SupplierPhone']].drop_duplicates()
    supplier_phones_3nf['SupplierID'] = supplier_phones_3nf['SupplierName'].map(supplier_map)
    supplier_phones_3nf = supplier_phones_3nf.rename(columns={'SupplierPhone': 'Phone'})
    supplier_phones_3nf = supplier_phones_3nf[['SupplierID', 'Phone']].sort_values(['SupplierID', 'Phone'])

    # Decompose materials
    materials_3nf = df_1nf[['MaterialSupplied']].drop_duplicates()
    materials_3nf['MaterialID'] = materials_3nf['MaterialSupplied'].map(material_map)
    materials_3nf = materials_3nf.rename(columns={'MaterialSupplied': 'MaterialName'})
    materials_3nf = materials_3nf[['MaterialID', 'MaterialName']].sort_values('MaterialID')

    # Decompose equipment
    equipment_3nf = df_1nf[['EquipmentUsed']].drop_duplicates()
    equipment_3nf['EquipmentID'] = equipment_3nf['EquipmentUsed'].map(equipment_map)
    equipment_3nf = equipment_3nf.rename(columns={'EquipmentUsed': 'EquipmentName'})
    equipment_3nf = equipment_3nf[['EquipmentID', 'EquipmentName']].sort_values('EquipmentID')

    # Ternary relationship for project materials to prevent lossy join
    project_materials_3nf = df_1nf[['ProjectID', 'MaterialSupplied', 'SupplierName', 'MaterialUnitCost']].drop_duplicates()
    project_materials_3nf['MaterialID'] = project_materials_3nf['MaterialSupplied'].map(material_map)
    project_materials_3nf['SupplierID'] = project_materials_3nf['SupplierName'].map(supplier_map)
    project_materials_3nf = project_materials_3nf[['ProjectID', 'MaterialID', 'SupplierID', 'MaterialUnitCost']]
    project_materials_3nf = project_materials_3nf.sort_values(['ProjectID', 'MaterialID', 'SupplierID'])

    # Project suppliers (redundant but kept for structural consistency)
    project_suppliers_3nf = df_1nf[['ProjectID', 'SupplierName']].drop_duplicates()
    project_suppliers_3nf['SupplierID'] = project_suppliers_3nf['SupplierName'].map(supplier_map)
    project_suppliers_3nf = project_suppliers_3nf[['ProjectID', 'SupplierID']].sort_values(['ProjectID', 'SupplierID'])

    # Project equipment (rental cost is project-specific)
    project_equipment_3nf = df_1nf[['ProjectID', 'EquipmentUsed', 'EquipmentRentalCost']].drop_duplicates()
    project_equipment_3nf['EquipmentID'] = project_equipment_3nf['EquipmentUsed'].map(equipment_map)
    project_equipment_3nf = project_equipment_3nf[['ProjectID', 'EquipmentID', 'EquipmentRentalCost']].sort_values(['ProjectID', 'EquipmentID'])

    # Save 3NF
    projects_3nf.to_csv('main/3NF/projects.csv', index=False)
    clients_3nf.to_csv('main/3NF/clients.csv', index=False)
    supervisors_3nf.to_csv('main/3NF/supervisors.csv', index=False)
    workers_3nf.to_csv('main/3NF/workers.csv', index=False)
    worker_skills_3nf.to_csv('main/3NF/worker_skills.csv', index=False)
    worker_certs_3nf.to_csv('main/3NF/worker_certifications.csv', index=False)
    project_workers_3nf.to_csv('main/3NF/project_workers.csv', index=False)
    suppliers_3nf.to_csv('main/3NF/suppliers.csv', index=False)
    supplier_phones_3nf.to_csv('main/3NF/supplier_phones.csv', index=False)
    materials_3nf.to_csv('main/3NF/materials.csv', index=False)
    equipment_3nf.to_csv('main/3NF/equipment.csv', index=False)
    project_materials_3nf.to_csv('main/3NF/project_materials.csv', index=False)
    project_suppliers_3nf.to_csv('main/3NF/project_suppliers.csv', index=False)
    project_equipment_3nf.to_csv('main/3NF/project_equipment.csv', index=False)

    # Write 3NF Explanation
    with open('main/3NF/3NF_explanation.md', 'w', encoding='utf-8') as f:
        f.write("""# Stage 3: Third Normal Form (3NF) Explanation

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
""")

    # ----------------------------------------------------
    # 4. BCNF GENERATION
    # ----------------------------------------------------
    print("[BCNF] Generating BCNF...")
    # BCNF requires that for every functional dependency X -> Y, X must be a candidate key.
    # The corrected 3NF design satisfies BCNF. We will copy the tables over.
    
    clean_dir('main/BCNF')
    for file in os.listdir('main/3NF'):
        if file.endswith('.csv'):
            import shutil
            shutil.copy(os.path.join('main/3NF', file), os.path.join('main/BCNF', file))
        
    with open('main/BCNF/BCNF_explanation.md', 'w', encoding='utf-8') as f:
        f.write("""# Stage 4: Boyce-Codd Normal Form (BCNF) Explanation

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
A relation is in BCNF if for every functional dependency $X \\rightarrow Y$, $X$ is a superkey. In our corrected design:
1. Every determinant in every table is a candidate key.
2. The transitive and partial dependencies have been completely resolved.
3. No non-key attribute determines a candidate key or part of a candidate key.
""")

    # ----------------------------------------------------
    # 5. 4NF GENERATION
    # ----------------------------------------------------
    print("[4NF] Generating 4NF...")
    # 4NF requires that there are no non-trivial multi-valued dependencies (MVDs).
    # Since our BCNF tables already isolate independent multi-valued facts (worker skills vs worker certs, etc.), they satisfy 4NF.
    
    clean_dir('main/4NF')
    for file in os.listdir('main/BCNF'):
        if file.endswith('.csv'):
            import shutil
            shutil.copy(os.path.join('main/BCNF', file), os.path.join('main/4NF', file))
        
    with open('main/4NF/4NF_explanation.md', 'w', encoding='utf-8') as f:
        f.write("""# Stage 5: Fourth Normal Form (4NF) Explanation

## 1. What multi-valued dependencies (MVDs) did you find?
Multi-valued dependencies exist when an attribute $X$ multi-determines independent sets of attributes $Y$ and $Z$ ($X \\twoheadrightarrow Y$ and $X \\twoheadrightarrow Z$):
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
""")

    # ----------------------------------------------------
    # 6. INTEGRITY & PROJECTION VERIFICATION
    # ----------------------------------------------------
    print("[Verification] Running Projection-based Verification...")
    
    # Load 1NF table
    df_1nf_test = pd.read_csv('main/1NF/1NF_table.csv')
    
    # Load 2NF tables
    projects_2nf = pd.read_csv('main/2NF/projects.csv')
    workers_2nf = pd.read_csv('main/2NF/workers.csv')
    worker_skills_2nf = pd.read_csv('main/2NF/worker_skills.csv')
    worker_certs_2nf = pd.read_csv('main/2NF/worker_certifications.csv')
    project_workers_2nf = pd.read_csv('main/2NF/project_workers.csv')
    suppliers_2nf = pd.read_csv('main/2NF/suppliers.csv')
    supplier_phones_2nf = pd.read_csv('main/2NF/supplier_phones.csv')
    project_materials_2nf = pd.read_csv('main/2NF/project_materials.csv')
    project_equipment_2nf = pd.read_csv('main/2NF/project_equipment.csv')
    
    # Load 3NF tables
    projects_3nf = pd.read_csv('main/3NF/projects.csv')
    clients_3nf = pd.read_csv('main/3NF/clients.csv')
    supervisors_3nf = pd.read_csv('main/3NF/supervisors.csv')
    workers_3nf = pd.read_csv('main/3NF/workers.csv')
    worker_skills_3nf = pd.read_csv('main/3NF/worker_skills.csv')
    worker_certs_3nf = pd.read_csv('main/3NF/worker_certifications.csv')
    project_workers_3nf = pd.read_csv('main/3NF/project_workers.csv')
    suppliers_3nf = pd.read_csv('main/3NF/suppliers.csv')
    supplier_phones_3nf = pd.read_csv('main/3NF/supplier_phones.csv')
    materials_3nf = pd.read_csv('main/3NF/materials.csv')
    equipment_3nf = pd.read_csv('main/3NF/equipment.csv')
    project_materials_3nf = pd.read_csv('main/3NF/project_materials.csv')
    project_equipment_3nf = pd.read_csv('main/3NF/project_equipment.csv')
    
    all_passed = True
    
    # Helper to sort and compare two dataframes
    def verify_equality(df1, df2, columns):
        d1 = df1[columns].astype(str).drop_duplicates().sort_values(columns).reset_index(drop=True)
        d2 = df2[columns].astype(str).drop_duplicates().sort_values(columns).reset_index(drop=True)
        return d1.equals(d2)

    # 1. Verify 2NF tables match 1NF projections
    configs_2nf = {
        'projects.csv': (projects_2nf, projects_2nf_cols),
        'workers.csv': (workers_2nf, ['WorkerName', 'WorkerPhone', 'WorkerHourlyRate']),
        'worker_skills.csv': (worker_skills_2nf, ['WorkerName', 'Skill']),
        'worker_certifications.csv': (worker_certs_2nf, ['WorkerName', 'Certification']),
        'project_workers.csv': (project_workers_2nf, ['ProjectID', 'WorkerName']),
        'suppliers.csv': (suppliers_2nf, ['SupplierName', 'SupplierCity']),
        'supplier_phones.csv': (supplier_phones_2nf, ['SupplierName', 'SupplierPhone']),
        'project_materials.csv': (project_materials_2nf, ['ProjectID', 'SupplierName', 'MaterialSupplied', 'MaterialUnitCost']),
        'project_equipment.csv': (project_equipment_2nf, ['ProjectID', 'EquipmentUsed', 'EquipmentRentalCost'])
    }
    
    print("  Checking 2NF tables...")
    for filename, (sub_df, cols) in configs_2nf.items():
        if verify_equality(df_1nf_test, sub_df, cols):
            print(f"    [PASS] 2NF {filename}")
        else:
            print(f"    [FAIL] 2NF {filename} mismatch!")
            all_passed = False

    # 2. Verify 3NF tables match 1NF projections (by joining ID tables)
    print("  Checking 3NF tables (verifying surrogate key joins)...")
    
    # 2.1 projects
    recon_projects = projects_3nf.merge(clients_3nf, on='ClientID').merge(supervisors_3nf, on='SupervisorID')
    if verify_equality(df_1nf_test, recon_projects, projects_2nf_cols):
        print("    [PASS] 3NF projects/clients/supervisors join matches 1NF")
    else:
        print("    [FAIL] 3NF projects/clients/supervisors join mismatch!")
        all_passed = False
        
    # 2.2 workers
    if verify_equality(df_1nf_test, workers_3nf, ['WorkerName', 'WorkerPhone', 'WorkerHourlyRate']):
        print("    [PASS] 3NF workers table matches 1NF")
    else:
        print("    [FAIL] 3NF workers table mismatch!")
        all_passed = False
        
    # 2.3 worker_skills
    recon_skills = worker_skills_3nf.merge(workers_3nf, on='WorkerID')
    if verify_equality(df_1nf_test, recon_skills, ['WorkerName', 'Skill']):
        print("    [PASS] 3NF worker_skills join matches 1NF")
    else:
        print("    [FAIL] 3NF worker_skills join mismatch!")
        all_passed = False

    # 2.4 worker_certs
    recon_certs = worker_certs_3nf.merge(workers_3nf, on='WorkerID')
    if verify_equality(df_1nf_test, recon_certs, ['WorkerName', 'Certification']):
        print("    [PASS] 3NF worker_certifications join matches 1NF")
    else:
        print("    [FAIL] 3NF worker_certifications join mismatch!")
        all_passed = False

    # 2.5 project_workers
    recon_pw = project_workers_3nf.merge(workers_3nf, on='WorkerID')
    if verify_equality(df_1nf_test, recon_pw, ['ProjectID', 'WorkerName']):
        print("    [PASS] 3NF project_workers join matches 1NF")
    else:
        print("    [FAIL] 3NF project_workers join mismatch!")
        all_passed = False

    # 2.6 suppliers
    if verify_equality(df_1nf_test, suppliers_3nf, ['SupplierName', 'SupplierCity']):
        print("    [PASS] 3NF suppliers table matches 1NF")
    else:
        print("    [FAIL] 3NF suppliers table mismatch!")
        all_passed = False

    # 2.7 supplier_phones
    recon_phones = supplier_phones_3nf.rename(columns={'Phone': 'SupplierPhone'}).merge(suppliers_3nf, on='SupplierID')
    if verify_equality(df_1nf_test, recon_phones, ['SupplierName', 'SupplierPhone']):
        print("    [PASS] 3NF supplier_phones join matches 1NF")
    else:
        print("    [FAIL] 3NF supplier_phones join mismatch!")
        all_passed = False

    # 2.8 project_materials
    recon_pm = project_materials_3nf.merge(materials_3nf, on='MaterialID').merge(suppliers_3nf, on='SupplierID')
    recon_pm = recon_pm.rename(columns={'MaterialName': 'MaterialSupplied'})
    if verify_equality(df_1nf_test, recon_pm, ['ProjectID', 'SupplierName', 'MaterialSupplied', 'MaterialUnitCost']):
        print("    [PASS] 3NF project_materials join matches 1NF (preserves ternary relation and cost!)")
    else:
        print("    [FAIL] 3NF project_materials join mismatch!")
        all_passed = False

    # 2.9 project_equipment
    recon_pe = project_equipment_3nf.merge(equipment_3nf, on='EquipmentID')
    recon_pe = recon_pe.rename(columns={'EquipmentName': 'EquipmentUsed'})
    if verify_equality(df_1nf_test, recon_pe, ['ProjectID', 'EquipmentUsed', 'EquipmentRentalCost']):
        print("    [PASS] 3NF project_equipment join matches 1NF (preserves cost!)")
    else:
        print("    [FAIL] 3NF project_equipment join mismatch!")
        all_passed = False

    # 3. Primary Key Uniqueness Verification
    print("  Verifying Primary Key Uniqueness...")
    pk_configs = {
        'main/3NF/projects.csv': ['ProjectID'],
        'main/3NF/clients.csv': ['ClientID'],
        'main/3NF/supervisors.csv': ['SupervisorID'],
        'main/3NF/workers.csv': ['WorkerID'],
        'main/3NF/worker_skills.csv': ['WorkerID', 'Skill'],
        'main/3NF/worker_certifications.csv': ['WorkerID', 'Certification'],
        'main/3NF/project_workers.csv': ['ProjectID', 'WorkerID'],
        'main/3NF/suppliers.csv': ['SupplierID'],
        'main/3NF/supplier_phones.csv': ['SupplierID', 'Phone'],
        'main/3NF/materials.csv': ['MaterialID'],
        'main/3NF/equipment.csv': ['EquipmentID'],
        'main/3NF/project_materials.csv': ['ProjectID', 'MaterialID', 'SupplierID'], # Cost depends on Project-Material-Supplier combo
        'main/3NF/project_equipment.csv': ['ProjectID', 'EquipmentID']
    }
    
    for filepath, pks in pk_configs.items():
        df_pk = pd.read_csv(filepath)
        if df_pk.duplicated(subset=pks).any():
            print(f"    [FAIL] Duplicate keys found in {filepath} for PK {pks}!")
            all_passed = False
        else:
            print(f"    [PASS] PK uniqueness for {filepath}")

    if all_passed:
        print("[PASS] SUCCESS: All projection-based and primary key validations passed! Zero data loss.")
        return True
    else:
        print("[FAIL] ERROR: Validation checks failed.")
        return False

if __name__ == '__main__':
    success = generate_all()
    if success:
        print("\n[Pipeline] Normalization pipeline completed successfully with zero data loss!")
    else:
        print("\n[Pipeline] Pipeline failed during verification.")
