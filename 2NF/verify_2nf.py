import os
import pandas as pd

def verify_2nf():
    print("Starting 2NF validation checks...")
    
    # Load 1NF table
    df_1nf = pd.read_csv('1NF_table.csv')
    
    # Load 2NF tables
    projects = pd.read_csv(os.path.join('2NF', 'projects.csv'))
    workers = pd.read_csv(os.path.join('2NF', 'workers.csv'))
    worker_skills = pd.read_csv(os.path.join('2NF', 'worker_skills.csv'))
    worker_certifications = pd.read_csv(os.path.join('2NF', 'worker_certifications.csv'))
    project_workers = pd.read_csv(os.path.join('2NF', 'project_workers.csv'))
    suppliers = pd.read_csv(os.path.join('2NF', 'suppliers.csv'))
    supplier_phones = pd.read_csv(os.path.join('2NF', 'supplier_phones.csv'))
    project_materials = pd.read_csv(os.path.join('2NF', 'project_materials.csv'))
    project_equipment = pd.read_csv(os.path.join('2NF', 'project_equipment.csv'))
    
    all_passed = True
    
    # Mappings of 2NF tables to verify
    configs = {
        'projects.csv': (projects, ['ProjectID']),
        'workers.csv': (workers, ['WorkerName']),
        'worker_skills.csv': (worker_skills, ['WorkerName', 'Skill']),
        'worker_certifications.csv': (worker_certifications, ['WorkerName', 'Certification']),
        'project_workers.csv': (project_workers, ['ProjectID', 'WorkerName']),
        'suppliers.csv': (suppliers, ['SupplierName']),
        'supplier_phones.csv': (supplier_phones, ['SupplierName', 'SupplierPhone']),
        'project_materials.csv': (project_materials, ['ProjectID', 'SupplierName', 'MaterialSupplied']),
        'project_equipment.csv': (project_equipment, ['ProjectID', 'EquipmentUsed'])
    }
    
    for filename, (sub_df, pk) in configs.items():
        cols = list(sub_df.columns)
        # Extract unique rows for those columns from the 1NF table
        df_sub = df_1nf[cols].drop_duplicates(subset=pk).dropna(subset=pk)
        
        # Sort both for comparison
        df_sub_sorted = df_sub.sort_values(by=pk).reset_index(drop=True)
        sub_df_sorted = sub_df.sort_values(by=pk).reset_index(drop=True)
        
        # Check equality
        match = df_sub_sorted.equals(sub_df_sorted)
        if match:
            print(f"  [PASS] {filename} is verified (Rows: {len(sub_df)})")
        else:
            print(f"  [FAIL] {filename} does not match 1NF data!")
            all_passed = False
            
    if all_passed:
        print("\n[SUCCESS] All 2NF tables successfully verified against 1NF base! Zero data loss.")
    else:
        print("\n[FAILED] Verification failed. Please check 2NF generation logic.")

if __name__ == '__main__':
    verify_2nf()
