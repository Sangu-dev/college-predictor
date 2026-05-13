import camelot
import pandas as pd

pdf_path = "PROF_CODE_E_R_30082025kannada.pdf"

# Extract tables using camelot
tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")

all_data = []

for table in tables:
    df = table.df

    if len(df.columns) >= 4:
        try:
            df = df.iloc[:, :4]  # take first 4 columns
            df.columns = ["college", "branch", "category", "cutoff_rank"]
            all_data.append(df)
        except:
            continue

if len(all_data) == 0:
    print("❌ No tables extracted. PDF is too complex.")
else:
    final_df = pd.concat(all_data, ignore_index=True)

    # Clean
    final_df = final_df.dropna()
    final_df.to_csv("kcet_cutoffs.csv", index=False)

    print("✅ Dataset created successfully!")