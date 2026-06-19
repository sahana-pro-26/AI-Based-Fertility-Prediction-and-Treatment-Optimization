import pickle
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'pcos_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'pcos_scaler.pkl')

def train_pcos_model():
    """Train PCOS prediction model from CSV data"""
    try:
        # Try multiple possible paths for the CSV file
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'CLEAN- PCOS SURVEY SPREADSHEET.csv'),
            os.path.join(os.path.dirname(__file__), '..', 'PCOS_data.csv'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'CLEAN- PCOS SURVEY SPREADSHEET.csv'),
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if csv_path is None:
            print("CSV file not found in expected locations")
            return None, None
        
        df = pd.read_csv(csv_path)
        
        # Map column names - handle spaces and special characters
        # The target variable is "Have you been diagnosed with PCOS/PCOD?"
        target_col = 'Have you been diagnosed with PCOS/PCOD?'
        
        # Select features for prediction
        feature_columns = [
            'Age (in Years)',
            'Weight (in Kg)',
            'Have you gained weight recently?',
            'Do you have excessive body/facial hair growth ?',
            'Do have hair loss/hair thinning/baldness ?',
            'Do you have pimples/acne on your face/jawline ?',
            'Do you experience mood swings ?',
            'Are your periods regular ?'
        ]
        
        # Check if all columns exist
        available_columns = [col for col in feature_columns if col in df.columns]
        print(f"Using columns: {available_columns}")
        
        if len(available_columns) < 5:
            print(f"Not enough feature columns found. Found {len(available_columns)}, need at least 5")
            print(f"Available columns: {df.columns.tolist()}")
            return None, None
        
        X = df[available_columns].copy()
        # Clean/convert columns to numeric where possible
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce')
            # fallback mapping for yes/no string columns
            if X[col].isna().sum() > 0:
                s = df[col].astype(str).str.strip().str.lower()
                if s.isin(['yes','no','1','0','true','false']).any():
                    X[col] = s.map({'yes':1,'true':1,'1':1,'no':0,'false':0,'0':0}).fillna(0)
                else:
                    X[col] = X[col].fillna(0)

        y = pd.to_numeric(df[target_col], errors='coerce').fillna(0)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train_scaled, y_train)
        
        # Save model and scaler
        pickle.dump(model, open(MODEL_PATH, 'wb'))
        pickle.dump(scaler, open(SCALER_PATH, 'wb'))
        
        print("PCOS model trained and saved successfully!")
        return model, scaler
        
    except Exception as e:
        print(f"Error training model: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def get_pcos_prediction(age, weight, weight_gain, facial_hair, hair_loss, acne, mood_swings, period_regularity):
    """
    Predict PCOS status using trained model
    """

    try:
        # Load model and scaler
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            train_pcos_model()

        model = pickle.load(open(MODEL_PATH, 'rb'))
        scaler = pickle.load(open(SCALER_PATH, 'rb'))

        # Prepare features
        # The training data uses 1 for regular periods and 0 for irregular periods,
        # so we pass period_regularity directly.
        features = np.array([[
            age,
            weight,
            weight_gain,
            facial_hair,
            hair_loss,
            acne,
            mood_swings,
            period_regularity
        ]])

        # Scale features
        features_scaled = scaler.transform(features)

        # Random Forest prediction and probability
        prediction = int(model.predict(features_scaled)[0])
        proba = model.predict_proba(features_scaled)[0]
        pcos_prob = float(proba[1]) * 100
        confidence = float(max(proba)) * 100

        if prediction == 1:
            status = "PCOS Detected"
        elif pcos_prob >= 40:
            status = "At Risk"
        else:
            status = "PCOS Not Detected"

        return {
            'prediction': int(prediction),
            'has_pcos': int(prediction == 1),
            'status': status,
            'confidence': round(confidence, 2),
            'pcos_probability': round(pcos_prob, 2)
        }

    except Exception as e:
        print(f"Error making prediction: {e}")
        return {
            'prediction': 0,
            'has_pcos': 0,
            'status': 'PCOS Not Detected',
            'confidence': 0,
            'pcos_probability': 0,
            'error': str(e)
        }