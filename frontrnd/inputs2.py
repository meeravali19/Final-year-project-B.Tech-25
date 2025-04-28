import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import os


def main():
    # Load the XGBoost model
    model = xgb.Booster()
    model.load_model("xgboost_model.json")

    # Class index to label mapping
    class_mapping = {
        0: 'BENIGN',
        1: 'DrDoS_DNS',
        2: 'DrDoS_LDAP',
        3: 'DrDoS_MSSQL',
        4: 'DrDoS_NTP',
        5: 'DrDoS_NetBIOS',
        6: 'DrDoS_SNMP',
        7: 'DrDoS_SSDP'
    }

    st.title("DDoS Detection from Test Dataset")

    # Define feature column names
    important_columns = [
        'Flow Duration', 'Flow Bytes/s', 'Flow Packets/s', 'Total Fwd Packets',
        'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
        'Fwd Packet Length Mean', 'Bwd Packet Length Mean', 'Max Packet Length',
        'Min Packet Length', 'Packet Length Std', 'Flow IAT Mean', 'Flow IAT Std',
        'Flow IAT Max', 'Flow IAT Min', 'SYN Flag Count', 'ACK Flag Count',
        'RST Flag Count', 'PSH Flag Count', 'FIN Flag Count', 'URG Flag Count',
        'Subflow Fwd Packets', 'Subflow Bwd Packets', 'Subflow Fwd Bytes',
        'Subflow Bwd Bytes', 'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
        'Active Mean', 'Active Std', 'Idle Mean', 'Idle Std'
    ]

    # Input for file path
    st.subheader("Enter the full path to your test CSV file:")
    file_path = st.text_input("Test Dataset Path", placeholder="e.g., C:/Users/you/Desktop/test.csv")

    if st.button("Predict"):
        if not os.path.isfile(file_path):
            st.error("Invalid file path! Please check and try again.")
            return

        try:
            df = pd.read_csv(file_path)

            # Check if required columns are present
            if not all(col in df.columns for col in important_columns):
                st.error("Dataset does not contain all required columns.")
                st.write("Missing columns:", list(set(important_columns) - set(df.columns)))
                return

            # Use a randomly selected row for prediction
            input_row = df[important_columns].sample(n=1, random_state=None)
            # Get the label of the randomly selected row
            selected_row_label = df.loc[input_row.index, 'Label'].values[0]
            input_row_x = input_row.iloc[0]
            input_df = pd.DataFrame([input_row_x])
            dmatrix = xgb.DMatrix(input_df)
            prediction = model.predict(dmatrix)

            # Map prediction to class
            predicted_class_index = int(np.round(prediction[0]))
            predicted_class_name = class_mapping.get(predicted_class_index, "Unknown")

            # Output
            st.success(f"Predicted Class: {predicted_class_name} (Index: {predicted_class_index})")
            st.subheader("Randomly Selected Row Used for Prediction:")
            st.dataframe(input_row)
            st.write(f"Actual Label: {selected_row_label}")

        except Exception as e:
            st.error("Something went wrong while processing the file.")
            st.exception(e)


if __name__ == "__main__":
    main()
