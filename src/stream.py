import os
import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas as stc
from streamlit_js_eval import streamlit_js_eval as sje
from model import model, predictor
import time
from datetime import datetime
import psycopg2


def connect_to_db():
    a = 0
    conn = None
    while a < 5:
        try:
            conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "mnistdb"),
            user=os.getenv("DB_USER", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            password=os.getenv("DB_PASSWORD", "post_admin"),
            port=int(os.getenv("DB_PORT", 5432))
            )
            # print("Database connected successfully.")
            return conn
        except Exception as e:
            a += 1
            print("Retrying DB connection...")
            time.sleep(2)
    
    st.write("Database connection failed.\n")
    raise Exception(e)

try:
    conn = connect_to_db()
except Exception as e:
    print("Error: ",e)

#create table
with conn:
    with conn.cursor() as cur:
        try:
            cur.execute(
            """
            CREATE TABLE IF NOT EXISTS prediction_logs(
            prediction INTEGER NOT NULL, 
            confidence NUMERIC(3,2) NOT NULL, 
            groundTruth INTEGER NOT NULL,
            submissionStamp VARCHAR(20) NOT NULL 
            );
            """)
        except Exception as e:
            print("Table creation failed.")
            print(e)

st.header("Hand-drawn Number Recognition Model (MNIST)")

drawing_mode = "freedraw"
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 6)
stroke_color = "white"
bg_color = "#000"
realtime_update = st.sidebar.checkbox("Update in realtime", True)

window_width = sje(js_expressions='screen.width', key = 'SCR')

# Create a canvas component
with st.form('number_guessing_form'):
        canvas_result = stc(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        update_streamlit=realtime_update,
        height = int(0.25*window_width),
        width= int(0.25*window_width),
        drawing_mode=drawing_mode,
        point_display_radius= 0,
        key="canvas"
        )
        
         
        ground_truth = str(st.number_input('Enter True Value Here:', min_value=0, max_value=9, value=None, step=1 ))
        
        st.form_submit_button('Submit') 
# Three things done after submit button: Calculate res, POST to db, Update table.

if canvas_result.image_data is not None:
    res: tuple = predictor(canvas_result.image_data)
    timestamp = '{date:%Y-%m-%d %H:%M:%S}'.format( date=datetime.now() )
    
    res = res + (int(ground_truth), timestamp,)
    
    prediction, confidence = res[0], res[1]
    
    st.write("prediction: ",str(prediction) )
    st.write("confidence: ", str(confidence*100), "%")

    
    #res can now be POST to the Postgre DB
    with conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO prediction_logs (prediction, confidence, groundTruth, submissionStamp)
                    VALUES (%s, %s, %s, %s);""", (res[0], res[1], res[2], res[3])
                    )
                #Rerun select query and update table
                cur.execute("SELECT * FROM prediction_logs;")
                view = cur.fetchall()
                
            
            except Exception as e:
                st.write("Table Insertion failed.")
                print(e)

#Create table view
view = pd.DataFrame()
with conn:
    with conn.cursor() as cur:
        try:
            cur.execute("SELECT * FROM prediction_logs;")
            view = cur.fetchall()
            col_names = [title[0] for title in cur.description]
            view = pd.DataFrame(view, columns=col_names).iloc[::-1]
            

        except Exception as e:
            st.write("Falied to get Table View.")
            print(e)

st.dataframe(view)