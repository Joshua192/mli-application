import psycopg2

try:
    conn = psycopg2.connect(database = "mnistdb", 
                        user = "postgres", 
                        host= 'localhost',
                        password = "post_admin",
                        port = 5432)
    print("Database connected successfully.")
except:
    print("Database connection failed.")

with conn:
    with conn.cursor() as cur:
        
        try:
            # cur.execute(
            # """
            # CREATE TABLE prediction_logs(
            # prediction INTEGER NOT NULL, 
            # confidence NUMERIC(3,2) NOT NULL, 
            # groundTruth INTEGER NOT NULL,
            # submissionStamp VARCHAR(20) NOT NULL 
            # );
            # """)

            print("Table created successfully")
        except Exception as e:
            print("Table creation failed.")
            print(e)
    
conn.close()