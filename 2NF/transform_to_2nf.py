import os
import pandas as pd

def transform_to_2nf():
    # Ensure 2NF output directory exists
    output_dir = '2NF'
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the 1NF table
    df = pd.read_csv('1NF_table.csv')
    print(f"Loaded 1NF table with {len(df)} rows and {len(df.columns)} columns.")
    
    # Define the 9 target tables with their columns and key columns for deduplication
    tables_config = {
        'projects.csv': {
            'columns': [
                'ProjectID', 'ProjectName', 'ProjectType', 'StartDate', 'EndDate', 
                'SiteAddress', 'SiteCity', 'SiteState', 'ClientName', 'ClientPhone', 
                'ClientEmail', 'ClientCity', 'SupervisorName', 'SupervisorPhone'
            ],
            'pk': ['ProjectID']
        },
        'workers.csv': {
            'columns': ['WorkerName', 'WorkerPhone', 'WorkerHourlyRate'],
            'pk': ['WorkerName']
        },
        'worker_skills.csv': {
            'columns': ['WorkerName', 'Skill'],
            'pk': ['WorkerName', 'Skill']
        },
        'worker_certifications.csv': {
            'columns': ['WorkerName', 'Certification'],
            'pk': ['WorkerName', 'Certification']
        },
        'project_workers.csv': {
            'columns': ['ProjectID', 'WorkerName'],
            'pk': ['ProjectID', 'WorkerName']
        },
        'suppliers.csv': {
            'columns': ['SupplierName', 'SupplierCity'],
            'pk': ['SupplierName']
        },
        'supplier_phones.csv': {
            'columns': ['SupplierName', 'SupplierPhone'],
            'pk': ['SupplierName', 'SupplierPhone']
        },
        'project_materials.csv': {
            'columns': ['ProjectID', 'SupplierName', 'MaterialSupplied', 'MaterialUnitCost'],
            'pk': ['ProjectID', 'SupplierName', 'MaterialSupplied']
        },
        'project_equipment.csv': {
            'columns': ['ProjectID', 'EquipmentUsed', 'EquipmentRentalCost'],
            'pk': ['ProjectID', 'EquipmentUsed']
        }
    }
    
    # Decompose and save each table
    for filename, config in tables_config.items():
        cols = config['columns']
        pk = config['pk']
        
        # Select columns and drop duplicates based on the primary key
        sub_df = df[cols].drop_duplicates(subset=pk).dropna(subset=pk)
        
        # Sort values for consistency and readability
        sub_df = sub_df.sort_values(by=pk)
        
        # Save to CSV
        output_path = os.path.join(output_dir, filename)
        sub_df.to_csv(output_path, index=False)
        print(f"Generated {output_path} ({len(sub_df)} rows)")

if __name__ == '__main__':
    transform_to_2nf()
    print("[2NF] Decomposition complete!")
