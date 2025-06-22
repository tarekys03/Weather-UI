import streamlit as st
import pandas as pd
import requests
import numpy as np
from io import BytesIO

API_URL = "https://weather-api-ltyb.onrender.com//predict/"

st.title("🌦️ Weather Fault Classifier")

st.write("""
Upload your own CSV or generate a sample weather dataset for fault analysis.  
Columns required: **Temperature, Humidity, Barometer, Windspeed, Rain, Light**
""")

uploaded_file = st.file_uploader("📁 Choose a CSV file", type="csv")

# -------------------------------
# Function to generate sample data
# -------------------------------
def generate_sample_data(num_rows=20):
    data = {
        "Temperature": np.random.uniform(-5, 35, num_rows),
        "Humidity": np.random.uniform(10, 60, num_rows),
        "Barometer": np.random.uniform(20, 35, num_rows),
        "Windspeed": np.random.uniform(0, 25, num_rows),
        "Rain": np.random.uniform(0, 5, num_rows),
        "Light": np.random.uniform(100, 800, num_rows),
    }
    df = pd.DataFrame(data)
    return df

# -------------------------------
# Function to analyze data via API
# -------------------------------
def analyze_data_via_api(df):
    try:
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        files = {"file": ("sample.csv", csv_buffer, "text/csv")}
        response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            result = response.json()
            df_result = pd.DataFrame(result["records"])
            return df_result, None
        else:
            return None, response.json()["detail"]

    except Exception as e:
        return None, str(e)

# -------------------------------
# Generate + Analyze Sample Data
# -------------------------------
if st.button("🧪 Generate & Analyze Sample Data"):
    with st.spinner("Generating and analyzing..."):
        sample_df = generate_sample_data()
        st.subheader("📝 Generated Sample Data")
        st.dataframe(sample_df)

        result_df, error = analyze_data_via_api(sample_df)

        if error:
            st.error(f"❌ Error: {error}")
        else:
            st.success("✅ Analysis Complete")

            st.subheader("🔍 Full Predictions")
            st.dataframe(result_df)

            st.subheader("🚨 Abnormal Readings Only")
            abnormal_df = result_df[
                (result_df['Temp_Fault'] != "Normal") |
                (result_df['Humidity_Fault'] != "Normal") |
                (result_df['Barometer_Fault'] != "Normal") |
                (result_df['Wind_Fault'] != "Calm") |
                (result_df['Rain_Fault'] != "No Rain") |
                (result_df['Light_Fault'] != "Normal")
            ]
            st.dataframe(abnormal_df)

            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Predictions as CSV", data=csv, file_name="sample_predictions.csv", mime='text/csv')

# -------------------------------
# Analyze Uploaded File
# -------------------------------
if uploaded_file is not None:
    st.success("✅ File uploaded!")

    if st.button("🔍 Analyze Uploaded File"):
        with st.spinner("Analyzing uploaded file..."):
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            result = response.json()
            df_result = pd.DataFrame(result["records"])

            st.subheader("🔍 Full Predictions")
            st.dataframe(df_result)

            st.subheader("🚨 Abnormal Readings Only")
            abnormal_df = df_result[
                (df_result['Temp_Fault'] != "Normal") |
                (df_result['Humidity_Fault'] != "Normal") |
                (df_result['Barometer_Fault'] != "Normal") |
                (df_result['Wind_Fault'] != "Calm") |
                (df_result['Rain_Fault'] != "No Rain") |
                (df_result['Light_Fault'] != "Normal")
            ]
            st.dataframe(abnormal_df)

            csv = df_result.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Predictions as CSV", data=csv, file_name="uploaded_predictions.csv", mime='text/csv')
        else:
            st.error(f"❌ Error {response.status_code}: {response.json()['detail']}")
