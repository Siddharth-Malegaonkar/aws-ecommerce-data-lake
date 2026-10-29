import pandas as pd
from pathlib import Path

BUCKET_NAME = "ecommerce-data-lake-sm2026"
RAW_FILE = Path("orders.csv")

# Read raw data
df = pd.read_csv(RAW_FILE)

print("Raw records:", len(df))

# Clean column values
df.columns = df.columns.str.strip()

for column in ["customer_id", "product", "category", "city"]:
    df[column] = df[column].astype("string").str.strip()

# Convert data types
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

# Remove invalid records
df = df.dropna(
    subset=[
        "order_id",
        "order_date",
        "customer_id",
        "product",
        "category",
        "quantity",
        "unit_price",
        "city",
    ]
)

df = df.drop_duplicates(subset=["order_id"])

df = df[
    (df["quantity"] > 0) &
    (df["unit_price"] >= 0)
].copy()

# Calculate order value
df["total_amount"] = df["quantity"] * df["unit_price"]

# Save cleaned data
Path("output").mkdir(exist_ok=True)
df.to_csv("output/cleaned_orders.csv", index=False)

print("Cleaned records:", len(df))
print("Total revenue: ₹", df["total_amount"].sum())
print("Cleaned data saved to output/cleaned_orders.csv")
print(df.head())

# Save cleaned data in Parquet format
df.to_parquet("output/cleaned_orders.parquet", index=False)

print("Parquet file saved successfully!")


# Create daily sales summary
daily_sales = (
    df.groupby("order_date")
    .agg(
        total_revenue=("total_amount", "sum"),
        total_orders=("order_id", "nunique"),
        total_quantity=("quantity", "sum")
    )
    .reset_index()
)

# Save curated analytics data
daily_sales.to_parquet(
    "output/daily_sales.parquet",
    index=False
)

print("\nDaily sales summary:")
print(daily_sales)
print("\nCurated dataset saved successfully!")