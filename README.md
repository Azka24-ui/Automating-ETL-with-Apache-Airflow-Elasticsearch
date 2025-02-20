# 🚀 Milestone 3: Automating ETL with Apache Airflow & Elasticsearch

## 📌 Project Overview
This project automates the **ETL (Extract, Transform, Load)** pipeline using **Apache Airflow** to process and ingest data from **PostgreSQL** into **Elasticsearch**. The dataset used in this project is from **Balaji Fast Food Sales**, which contains transactional sales records. The goal is to efficiently manage and analyze large-scale sales data by leveraging **Airflow for orchestration** and **Elasticsearch for fast retrieval & analytics**.

🔗 **Dataset Source:** [Kaggle - Balaji Fast Food Sales](https://www.kaggle.com/datasets/ahmedhalimo/balaji-fast-food-sales)

---
## 📂 Data Pipeline Architecture
This ETL pipeline consists of the following stages:
1️⃣ **Extract**: Retrieve sales data from a PostgreSQL database.  
2️⃣ **Transform**: Clean, filter, and convert the data into a structured format.  
3️⃣ **Load**: Ingest the cleaned data into **Elasticsearch** for further analysis.  

📌 **Tools Used:**
- **Apache Airflow** → Workflow orchestration & scheduling.
- **PostgreSQL** → Source database for transaction data.
- **Elasticsearch** → Fast indexing & retrieval of sales data.
- **Kibana** → Visualization & analytics on Elasticsearch data.

---
## 🔍 Implementation Details
### 🔹 Data Extraction
The DAG extracts data from the **PostgreSQL database (`table_m3`)** and stores it as a CSV file.
- Extracted using **PostgresHook** in Airflow.
- Saves raw data to `/opt/airflow/dags/data_mentah.csv`.

### 🔹 Data Transformation
The extracted data is cleaned and transformed using Pandas:
- **Removes irrelevant columns** (`unnamed_10`, `unnamed_11`, `unnamed_12`).
- **Filters out summary rows** to avoid duplicate calculations.
- **Converts price & transaction amounts** to numerical format.
- **Handles missing values** and formats `date` to `datetime`.
- Saves cleaned data as `/opt/airflow/dags/P2M3_azka_data_clean.csv`.

### 🔹 Data Loading
The transformed data is uploaded into **Elasticsearch (`milestone3_clean_data` index)**:
- Uses `Elasticsearch` Python client for indexing.
- Each row is converted into a dictionary and ingested.
- The pipeline ensures **high availability** and **scalability** of indexed data.

---
## 📜 DAG Configuration
The Apache Airflow **DAG (`P2M3_azka_irsyad_DAG.py`)** contains:
- **Task 1 (`extract_data`)** → Extracts data from PostgreSQL.
- **Task 2 (`transform_data`)** → Cleans and processes the extracted data.
- **Task 3 (`upload_to_elasticsearch`)** → Loads the cleaned data into Elasticsearch.

The DAG runs **daily (`@daily`)**, ensuring continuous data updates.

---
## 📊 Data Schema (DDL)
The original PostgreSQL table schema is as follows:
```sql
CREATE TABLE table_m3 (
    order_id SERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    item_name TEXT NOT NULL,
    item_type TEXT NOT NULL,
    item_price TEXT NOT NULL,  
    quantity INTEGER NOT NULL,
    transaction_amount TEXT NOT NULL, 
    transaction_type TEXT NOT NULL,
    received_by TEXT NOT NULL,
    time_of_sale TEXT NOT NULL,
    unnamed_10 TEXT,  
    unnamed_11 TEXT,  
    unnamed_12 TEXT   
);
```

---
## 🛠 How to Run the Pipeline
### 🔹 1. Set Up Environment
Ensure **Docker & Apache Airflow** are installed.
```bash
# Clone the repository
$ git clone https://github.com/yourusername/airflow-etl-elasticsearch.git
$ cd airflow-etl-elasticsearch

# Start Apache Airflow using Docker Compose
$ docker-compose -f airflow_ES.yaml up -d
```

### 🔹 2. Verify DAG Execution
- Access **Airflow Web UI** at `http://localhost:8080`.
- Enable the DAG named `pipeline_milestone_3`.
- Monitor DAG execution and logs.

### 🔹 3. Verify Data in Elasticsearch
Check if data has been loaded successfully into Elasticsearch.
```bash
curl -X GET "localhost:9200/milestone3_clean_data/_search?pretty"
```

### 🔹 4. Explore Data in Kibana
- Open **Kibana** at `http://localhost:5601`.
- Create an index pattern: `milestone3_clean_data*`.
- Visualize sales trends, transaction patterns, and item popularity.

---
## 📈 Key Insights & Findings
✅ **Automated ETL process** ensures efficient data extraction, transformation, and ingestion.  
✅ **Elasticsearch improves query performance** for fast retrieval of sales data.  
✅ **Scalable solution** that can handle growing data volumes without performance degradation.  

---
## 📄 License
This project is for **educational and research purposes**.

---
## 👤 Author
**Azka Irsyad Choir**  
📧 Email: [azkairsyad24@gmail.com](mailto:azkairsyad24@gmail.com)  
🔗 LinkedIn: [linkedin.com/in/azkairsyad](https://www.linkedin.com/in/azka-irsyad-aa2509191/)  
🐱 GitHub: [github.com/azka irsyad](https://github.com/Azka24-ui) 

