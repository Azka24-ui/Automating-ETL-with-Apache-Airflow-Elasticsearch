'''
=================================================
Milestone 3

Nama  : Azka Irsyad Choir
Batch : FTDS-001-RMT

Program ini dibuat untuk melakukan automatisasi transform dan load data dari PostgreSQL ke ElasticSearch. Adapun dataset yang dipakai adalah dataset balaji fast food sales.
=================================================
'''

from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from elasticsearch import Elasticsearch, helpers
import pandas as pd
from datetime import datetime, timedelta

# Default parameters
defaults_args = {
    'owner': 'Azka',
    'retry': None,
    'start_date': datetime(2024,11,1)
}

def extract(**context):

    """
    Mengekstrak data dari PostgreSQL dan menyimpannya dalam file CSV.

    Fungsi ini mengambil semua data dari tabel `table_m3` di PostgreSQL, 
    menyimpannya sebagai file CSV, dan mengirimkan lokasi file ke XCom 
    untuk diproses lebih lanjut.

    Langkah-langkah:
    1. Terhubung ke database PostgreSQL menggunakan PostgresHook.
    2. Mengambil seluruh data dari tabel `table_m3` ke dalam DataFrame.
    3. Menampilkan satu baris pertama untuk verifikasi.
    4. Menyimpan data dalam file CSV di '/opt/airflow/dags/data_mentah.csv'.
    5. Mengirim lokasi file ke XCom agar bisa digunakan oleh task berikutnya.
    """

    # Koneksi ke PostgreSQL
    source_hook = PostgresHook(postgres_conn_id="172.18.0.2")
    source_conn = source_hook.get_conn()

    # Extract data
    data_raw = pd.read_sql('SELECT * FROM table_m3', source_conn)

    # Show data
    print(data_raw.head(1))

    # Simpan data
    path = '/opt/airflow/dags/data_mentah.csv'
    data_raw.to_csv(path, index=False)

    # Lempar konteks
    context['ti'].xcom_push(key='lokasi_data', value=path)


def transform(**context):

    """
    Membersihkan dan memproses data dari PostgreSQL sebelum disimpan kembali.

    Fungsi ini mengambil data mentah dari task `extract_data`, melakukan 
    proses cleaning dan formatting, lalu menyimpannya sebagai file CSV baru 
    yang siap digunakan untuk analisis atau tahap selanjutnya dalam pipeline.

    Langkah-langkah:
    1. Mengambil lokasi file dari XCom hasil task `extract_data`.
    2. Membaca dataset ke dalam Pandas DataFrame.
    3. Menghapus kolom yang tidak relevan seperti `unnamed_10`, `unnamed_11`, dan `unnamed_12`.
    4. Menghapus baris yang mengandung total summary agar tidak mengganggu analisis.
    5. Mengubah format harga produk dan jumlah transaksi menjadi tipe numerik.
    6. Menghapus nilai yang kosong (missing values) dan data yang duplikat.
    7. Mengonversi kolom `date` menjadi format datetime agar dapat digunakan untuk analisis waktu.
    8. Menyimpan hasil data yang sudah bersih ke file CSV `/opt/airflow/dags/P2M3_azka_data_clean.csv`.

    """
    # Mengambil instance XCom
    ti = context['ti']

    # Mengambil path dari hasil Extract Task
    data_path = ti.xcom_pull(task_ids='extract_data', key='lokasi_data')

    # Load dataset
    data_raw = pd.read_csv(data_path)

    # 1. Hapus kolom yang tidak relevan
    data_clean = data_raw.drop(columns=["unnamed_10", "unnamed_11", "unnamed_12"], errors="ignore")

    # 2. Hapus baris yang mengandung total summary
    data_clean = data_clean[~data_clean["item_name"].str.contains("total", na=False, case=False)]

    # 3. Konversi harga item & transaksi ke numerik
    data_clean["item_price"] = data_clean["item_price"].replace('[\$,]', '', regex=True).astype(float)
    data_clean["transaction_amount"] = data_clean["transaction_amount"].replace('[\$,]', '', regex=True).astype(float)

    # 4. Hapus missing values & duplikat
    data_clean.dropna(inplace=True)
    data_clean.drop_duplicates(inplace=True)

    # 5. Konversi kolom date ke format datetime
    data_clean["date"] = pd.to_datetime(data_clean["date"], errors='coerce')

    # 6. Simpan data yang sudah dibersihkan
    cleaned_path = "/opt/airflow/dags/P2M3_azka_data_clean.csv"
    data_clean.to_csv(cleaned_path, index=False)

    # 7. Push path file bersih ke XCom
    ti.xcom_push(key='lokasi_data_bersih', value=cleaned_path)


def upload_to_elasticsearch(**context):

    """
    Mengunggah data yang telah dibersihkan ke Elasticsearch.

    Fungsi ini mengambil data hasil transformasi dari task `transform_data`, 
    lalu mengunggahnya ke indeks Elasticsearch agar bisa digunakan untuk analisis dan pencarian.

    Langkah-langkah:
    1. Membuat koneksi ke Elasticsearch.
    2. Mengecek apakah Elasticsearch dapat diakses.
    3. Mengambil path file dari XCom yang dihasilkan oleh task `transform_data`.
    4. Membaca data yang telah dibersihkan dari file CSV.
    5. Mengunggah setiap baris data ke indeks `milestone3_clean_data` di Elasticsearch.
    6. Menampilkan pesan keberhasilan setelah upload selesai.

    """
    es = Elasticsearch(
        "http://elasticsearch:9200",
    )
    if es.ping():
        print("Connected to Elasticsearch")
    else:
        print("Connection to Elasticsearch failed")
    
    # Mengambil objek TaskInstance untuk mengambil data dari XCom
    ti = context['ti']

    # Mengambil path data yang telah dibersihkan dari task 'transform_data' melalui XCom
    data_path = ti.xcom_pull(task_ids='transform_data', key='lokasi_data_bersih')

    # Membuat koneksi ke Elasticsearch menggunakan URL instance Elasticsearch
    es = Elasticsearch(['http://elasticsearch:9200'])

    # Membaca data yang telah dibersihkan dari file CSV
    data_clean = pd.read_csv(data_path)

    # Menentukan nama indeks untuk Elasticsearch
    index_name = "milestone3_clean_data"

    # Melakukan indexing data ke Elasticsearch
    for _, row in data_clean.iterrows():  # Iterasi melalui setiap baris data
        doc = row.to_dict()  # Mengubah baris data menjadi dictionary
        es.index(index=index_name, body=doc)  # Memasukkan data ke dalam indeks Elasticsearch

    # Menampilkan pesan keberhasilan
    print(f"Data successfully loaded to Elasticsearch index '{index_name}'.")


# Membuat objek DAG
with DAG('pipeline_milestone_3',
         description='pipeline milestone 3',
         schedule_interval='@daily',
         default_args=defaults_args,
         catchup=False) as dag:

    # Task untuk extract data
    extract_data = PythonOperator(
        task_id='extract_data',
        python_callable=extract,
        provide_context=True
    )

    # Task untuk transformasi data
    transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=transform,
        provide_context=True
    )

    # Task untuk upload ke Elasticsearch
    upload_task = PythonOperator(
        task_id='upload_to_elasticsearch',
        python_callable=upload_to_elasticsearch,
        provide_context=True
    )

    # Alur proses
    extract_data >> transform_data >> upload_task
