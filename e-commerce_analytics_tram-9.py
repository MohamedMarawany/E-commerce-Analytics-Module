import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

# Task 1: Data Cleaning
def clean_and_preprocess_dataset():
    dataset = pd.read_csv("data.csv", encoding='ISO-8859-1')
    dataset["InvoiceDate"] = pd.to_datetime(dataset["InvoiceDate"])
    dataset = dataset.drop(dataset[(dataset["Quantity"] < 0) | (dataset["UnitPrice"] < 0)].index)
    dataset['CustomerID'] = dataset['CustomerID'].fillna('Unknown')
    dataset["TotalPrice"] = dataset["Quantity"] * dataset["UnitPrice"]
    return dataset

# Task 2: Exploratory Data Analysis (EDA)
def exploratory_data_analysis(dataset):
    print("Statistical summary:\n", dataset.describe())
    product_analysis = dataset.groupby("Description").agg(
        total_quantity=("Quantity", "sum"),
        total_revenue=("TotalPrice", "sum"),
        number_of_transactions=("InvoiceNo", "nunique")
    ).reset_index()
    top_10_products = product_analysis.sort_values(by="total_quantity", ascending=False).head(10)
    print("Top 10 products by Quantity:\n", top_10_products)

# Task 3: Time Series Analysis
def time_series_analysis(dataset):
    sales_by_month = dataset.resample('M', on='InvoiceDate')['TotalPrice'].sum()
    highest_sales_month = sales_by_month.idxmax()
    lowest_sales_month = sales_by_month.idxmin()
    highest_sales = sales_by_month.max()
    lowest_sales = sales_by_month.min()

    plt.figure(figsize=(10, 6))
    sales_by_month.plot(kind='line', marker='o', linestyle='-', color='green', linewidth=2)
    plt.title("Sales Distribution by Month")
    plt.xlabel("Month")
    plt.ylabel("Sales")
    plt.xticks(rotation=45)
    plt.annotate(f'Highest Sales\n({highest_sales_month}, {highest_sales})',
                 xy=(sales_by_month.idxmax(), highest_sales),
                 xytext=(sales_by_month.idxmax(), highest_sales + 2000),
                 arrowprops=dict(facecolor='green', arrowstyle='->'))
    plt.annotate(f'Lowest Sales\n({lowest_sales_month}, {lowest_sales})',
                 xy=(sales_by_month.idxmin(), lowest_sales),
                 xytext=(sales_by_month.idxmin(), lowest_sales - 2000),
                 arrowprops=dict(facecolor='red', arrowstyle='->'))
    plt.tight_layout()
    plt.show()


# Task 4: RFM Analysis
def RFM_analysis_customer_segmentation(dataset):
    recency = dataset.groupby("CustomerID")["InvoiceDate"].max()
    recency = (dataset["InvoiceDate"].max() - recency).dt.days
    frequency = dataset.groupby("CustomerID")["InvoiceNo"].size()
    monetary = dataset.groupby("CustomerID")["TotalPrice"].sum()
    rfm = pd.DataFrame({'Recency': recency, 'Frequency': frequency, 'Monetary': monetary})
    rfm['Recency_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
    rfm['Frequency_Score'] = pd.qcut(rfm['Frequency'], 4, labels=[1, 2, 3, 4])
    rfm['Monetary_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
    rfm['RFM_Score'] = rfm['Recency_Score'].astype(int) + rfm['Frequency_Score'].astype(int) + rfm['Monetary_Score'].astype(int)

    def segment_customer(rfm_score):
        if rfm_score >= 9:
            return 'High'
        elif 5 <= rfm_score < 9:
            return 'Medium'
        else:
            return 'Low'

    rfm['Segment'] = rfm['RFM_Score'].apply(segment_customer)
    print(rfm[['Recency', 'Frequency', 'Monetary', 'RFM_Score', 'Segment']])
    return rfm['Segment']

# Task 5: Product Category Analysis
def extract_product_category_from_description(dataset):
    dataset['Category'] = dataset['Description'].str.split().str[-2:].str.join(' ')
    category_revenue = dataset.groupby('Category')['TotalPrice'].sum()
    plt.figure(figsize=(10, 6))
    category_revenue.nlargest(5).sort_values().plot(kind='barh', color='deepskyblue')
    plt.title('Top 5 Categories by Revenue')
    plt.xlabel('Total Revenue')
    plt.ylabel('Category')
    plt.grid(True)
    plt.show()

# Task 6: Geographical Analysis
def geographical_analysis(dataset):
    total_revenue_by_country = dataset.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False)
    top_10_countries = total_revenue_by_country.head(10)
    plt.figure(figsize=(10, 6))
    top_10_countries.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Countries by Revenue')
    plt.xlabel('Country')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return top_10_countries

# Task 7: Customer Behavior Analysis
def customer_behavior_analysis(dataset):
    order_quantity_data = dataset.groupby("InvoiceNo")["Quantity"].sum()
    plt.figure(figsize=(9, 6))
    plt.subplot(2, 2, 1)
    sns.histplot(order_quantity_data, color='g', bins=30)
    plt.xlabel('Quantity')
    plt.ylabel('Frequency')
    plt.title('Distribution of Order Quantities')

    plt.subplot(2, 2, 2)
    sns.scatterplot(data=dataset, x='Quantity', y='TotalPrice', color='blue')
    plt.xlabel('Quantity')
    plt.ylabel('Total Price')
    plt.title('Scatter Plot of Quantity vs Total Price')

    dataset['DayOfWeek'] = dataset['InvoiceDate'].dt.day_name()
    avg_daily_sales = dataset.groupby('DayOfWeek')['TotalPrice'].mean().reindex(
        ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])

    plt.subplot(2, 2, 3)
    sns.lineplot(avg_daily_sales, marker="o")
    sns.barplot(avg_daily_sales)
    plt.title("Sales Distribution by Day")
    plt.xlabel("Days")
    plt.ylabel("Sales")
    plt.tight_layout()
    plt.show()

# Task 8: Moving Average Forecast
def moving_average_forecast(dataset):
    dataset['day_date'] = dataset['InvoiceDate'].dt.strftime("%Y-%m-%d")
    daily_sales = dataset.groupby('day_date')['TotalPrice'].sum().reset_index()
    daily_sales['day_date'] = pd.to_datetime(daily_sales['day_date'])
    daily_sales['7-Day MA'] = daily_sales['TotalPrice'].rolling(window=7).mean()
    data_last_3_months = daily_sales.tail(90)

    plt.figure(figsize=(12, 6))
    plt.plot(data_last_3_months['day_date'], data_last_3_months['TotalPrice'], label='Actual Sales', marker='o')
    plt.plot(data_last_3_months['day_date'], data_last_3_months['7-Day MA'], label='7-Day Moving Average', linestyle='--', color='orange')
    plt.title('Actual Sales vs 7-Day Moving Average (Last 3 Months)')
    plt.xlabel('Date')
    plt.ylabel('Sales')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

# Task 9: Summary Dashboard Creation
def create_summary_dashboard(dataset):
    monthly_sales = dataset.resample('M', on='InvoiceDate')['TotalPrice'].sum()
    top_products = dataset.groupby('Description')['TotalPrice'].sum().nlargest(5).reset_index()
    customer_segments = RFM_analysis_customer_segmentation(dataset).value_counts().reset_index()
    customer_segments.columns = ['CustomerSegment', 'Count']
    top_countries = dataset.groupby('Country')['TotalPrice'].sum().nlargest(5).reset_index()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].plot(monthly_sales, marker='o', color='blue')
    axes[0, 0].set_title('Monthly Sales Trend')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Sales')

    axes[0, 1].barh(top_products['Description'], top_products['TotalPrice'], color='orange')
    axes[0, 1].set_title('Top 5 Products by Revenue')
    axes[0, 1].set_xlabel('Revenue')
    axes[0, 1].set_ylabel('Product')

    axes[1, 0].bar(customer_segments['CustomerSegment'], customer_segments['Count'], color='green')
    axes[1, 0].set_title('Customer Segmentation')
    axes[1, 0].set_xlabel('Segment')
    axes[1, 0].set_ylabel('Count')

    axes[1, 1].bar(top_countries['Country'], top_countries['TotalPrice'], color='purple')
    axes[1, 1].set_title('Top 5 Countries by Revenue')
    axes[1, 1].set_xlabel('Country')
    axes[1, 1].set_ylabel('Revenue')
    axes[1, 1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()
# Task 10: Optimize Data Processing
def calculate_spending_loops(dataset):
    start_time = time.time()
    result = {}
    for _, row in dataset.iterrows():
        customer = row["CustomerID"]
        total_spend = dataset["Quantity"] * dataset["UnitPrice"]
        if customer in result:
            result[customer] += total_spend
        else:
            result[customer] = total_spend
    elapsed_time = time.time() - start_time
    return result, elapsed_time


def calculate_spending_vectorized(df):
    start_time = time.time()
    result = df.groupby("CustomerID")["TotalPrice"].sum()
    elapsed_time = time.time() - start_time
    return result, elapsed_time


def compare_methods(df, n):
    loop_result, loop_time = calculate_spending_loops(df[0:n])
    vectorized_result, vectorized_time = calculate_spending_vectorized(df[0:n])
    # Print performance comparison
    print(f"Time taken using loops: {loop_time:.2f} seconds for {n} records")
    print(f"Time taken using vectorized operations: {vectorized_time:.2f} seconds for {n} records")



if __name__ == '__main__':
    dataset = clean_and_preprocess_dataset()
    exploratory_data_analysis(dataset)
    time_series_analysis(dataset)
    RFM_analysis_customer_segmentation(dataset)
    extract_product_category_from_description(dataset)
    geographical_analysis(dataset)
    customer_behavior_analysis(dataset)
    moving_average_forecast(dataset)
    create_summary_dashboard(dataset)
    compare_methods(dataset, 1000)
