import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas as stc
from streamlit_js_eval import streamlit_js_eval as sje
from model import model, predictor
from datetime import datetime
import psycopg2

try:
    conn = psycopg2.connect(database = "mnistdb", 
                        user = "postgres", 
                        host= 'localhost',
                        password = "post_admin",
                        port = 5432)
    
    # print("Database connected successfully.")
except Exception as e:
    st.write("Database connection failed.\n")
    st.write(e)
    raise

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