import pandas as pd

# Read the raw CSV
df = pd.read_csv('big3_construction_raw_data.csv')

# Function to explode multi-valued columns
def explode_column(df, col_name, new_col_name, sep='|'):
    """Split a column with separator and create new rows."""
    # Split the column
    df[col_name] = df[col_name].str.split(sep)
    # Explode to create new rows
    df = df.explode(col_name)
    # Rename the column
    df = df.rename(columns={col_name: new_col_name})
    return df

# Step 1: Explode WorkerSkills
df_1nf = explode_column(df.copy(), 'WorkerSkills', 'Skill')

# Step 2: Explode WorkerCertifications
df_1nf = explode_column(df_1nf, 'WorkerCertifications', 'Certification')

# Step 3: Explode SupplierPhones
df_1nf = explode_column(df_1nf, 'SupplierPhones', 'SupplierPhone')

# Step 4: Explode MaterialSupplied and MaterialUnitCost (they are linked)
# Create a function to handle paired data
def explode_paired_columns(df, col1, col2, new_col1, new_col2, sep='|'):
    """Split two paired columns and create new rows."""
    # Split both columns
    df[col1] = df[col1].str.split(sep)
    df[col2] = df[col2].str.split(sep)
    
    # Create list of tuples
    df['temp'] = df.apply(lambda row: list(zip(row[col1], row[col2])), axis=1)
    df = df.explode('temp')
    
    # Split the tuples back into columns
    df[new_col1] = df['temp'].apply(lambda x: x[0])
    df[new_col2] = df['temp'].apply(lambda x: x[1])
    
    # Drop temporary columns
    df = df.drop(columns=[col1, col2, 'temp'])
    return df

df_1nf = explode_paired_columns(df_1nf, 'MaterialSupplied', 'MaterialUnitCost', 
                                 'MaterialSupplied', 'MaterialUnitCost')

# Step 5: Explode EquipmentUsed and EquipmentRentalCost (they are linked)
df_1nf = explode_paired_columns(df_1nf, 'EquipmentUsed', 'EquipmentRentalCost',
                                 'EquipmentUsed', 'EquipmentRentalCost')

# Save the 1NF table
df_1nf.to_csv('1NF_table.csv', index=False)

print("✅ 1NF transformation complete!")
print(f"Rows before: {len(df)}, Rows after: {len(df_1nf)}")