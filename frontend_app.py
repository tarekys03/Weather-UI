import streamlit as st
import pandas as pd
import requests
import numpy as np
from io import BytesIO

API_URL = "https://weather-api-ltyb.onrender.com//predict/"

# إعداد صفحة Streamlit
st.set_page_config(page_title="Weather Fault Classifier", page_icon="🌦", layout="centered")

st.title("🌦 Weather Fault Classifier")

st.write("""
قم بتوليد بيانات طقس عشوائية وتحليلها للكشف عن الأعطال.  
الأعمدة المستخدمة: *Temperature, Humidity, Barometer, Windspeed, Rain, Light*
""")

# توليد بيانات الطقس الوهمية
def generate_sample_data(num_rows=20):
    data = {
        "Temperature": np.random.uniform(-5, 35, num_rows),
        "Humidity": np.random.uniform(10, 60, num_rows),
        "Barometer": np.random.uniform(20, 35, num_rows),
        "Windspeed": np.random.uniform(0, 25, num_rows),
        "Rain": np.random.uniform(0, 5, num_rows),
        "Light": np.random.uniform(100, 800, num_rows),
    }
    return pd.DataFrame(data)

# تحليل البيانات باستخدام API
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

# الزر الرئيسي لتوليد وتحليل البيانات
if st.button(" Turn ON Sensors "):
    with st.spinner("جاري توليد البيانات وتحليلها..."):
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
            if abnormal_df.empty:
                st.success("✅ لا توجد قراءات غير طبيعية")
            else:
                st.dataframe(abnormal_df)

            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Predictions as CSV",
                data=csv,
                file_name="sample_predictions.csv",
                mime='text/csv'
            )
