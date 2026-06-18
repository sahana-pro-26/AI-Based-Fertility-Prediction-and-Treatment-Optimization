import os
import json
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Try common locations for a Kaggle-style IVF CSV or fall back to the repo sample
possible_paths = []
env_path = os.environ.get('IVF_CSV')
if env_path:
    possible_paths.append(env_path)
possible_paths += [
    os.path.join(BASE_DIR, '..', 'ivf_kaggle.csv'),
    os.path.join(BASE_DIR, '..', 'IVF.csv'),
    os.path.join(BASE_DIR, '..', 'IVF_data.csv'),
    os.path.join(BASE_DIR, 'ivf_data.csv')
]

data_path = None
for p in possible_paths:
    if p and os.path.exists(p) and os.path.getsize(p) > 0:
        data_path = p
        break

if data_path is None:
    raise FileNotFoundError(f"No IVF dataset found. Searched: {possible_paths}")

print(f"Loading IVF dataset from: {data_path}")
df = pd.read_csv(data_path)

# Expected feature order used by the web form
expected = [
    'age','weight','height','periods','pcos','stress','smoking','pregnancy',
    'years','activity','disease','fertility_test','issues','IVF_Success'
]

# Build a mapping from expected -> actual column name (case-insensitive match)
cols = {col.lower(): col for col in df.columns}
mapping = {}
for exp in expected:
    found = None
    # exact (case-insensitive)
    for actual in df.columns:
        if actual.strip().lower() == exp.lower():
            found = actual
            break
    if not found:
        # contains
        for actual in df.columns:
            if exp.lower() in actual.strip().lower():
                found = actual
                break
    if not found:
        mapping[exp] = None
    else:
        mapping[exp] = found

missing = [k for k,v in mapping.items() if v is None]
if 'IVF_Success' in missing:
    print('Available columns:', df.columns.tolist())
    raise ValueError('Target column IVF_Success not found in dataset; please provide a column named IVF_Success or one that includes "ivf" and "success"')

# Keep only rows where target is not null
df = df[df[mapping['IVF_Success']].notna()].copy()

# Encode helper
def encode_series(name, s):
    if pd.api.types.is_numeric_dtype(s):
        return s.fillna(0)
    s2 = s.astype(str).str.strip().str.lower()
    if name == 'periods':
        return s2.apply(lambda x: 1 if 'regular' in x or x == '1' else 0)
    if name in ('pcos','smoking','pregnancy','fertility_test'):
        return s2.apply(lambda x: 1 if x in ('yes','1','true','y','yes ') else 0)
    if name == 'stress':
        return s2.apply(lambda x: 0 if 'low' in x or x=='0' else 1 if 'med' in x or x=='1' else 2)
    if name == 'activity':
        return s2.apply(lambda x: 1 if 'active' in x or 'moderate' in x or x=='1' else 0)
    if name == 'disease':
        # maintain app logic where Yes -> risk (0), No -> 1
        return s2.apply(lambda x: 0 if x in ('yes','1','true') else 1)
    if name == 'issues':
        return s2.apply(lambda x: 1 if 'none' in x else 0)
    if name == 'years':
        return pd.to_numeric(s, errors='coerce').fillna(0)
    # fallback numeric coercion
    return pd.to_numeric(s, errors='coerce').fillna(0)

# Construct training DataFrame in expected order
train_cols = []
for exp in expected[:-1]:
    actual = mapping.get(exp)
    if actual is None:
        raise ValueError(f"Required feature '{exp}' not found in dataset. Available: {list(df.columns)}")
    train_cols.append((exp, actual))

X_parts = []
for exp, actual in train_cols:
    X_parts.append(encode_series(exp, df[actual]))

X = pd.concat(X_parts, axis=1)
X.columns = [t[0] for t in train_cols]
y = encode_series('IVF_Success', df[mapping['IVF_Success']])

# Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model and feature list
model_path = os.path.join(BASE_DIR, "ivf_model.pkl")
joblib.dump(model, model_path)
with open(os.path.join(BASE_DIR, 'ivf_features.json'), 'w') as fh:
    json.dump(list(X.columns), fh)

print("MODEL CREATED SUCCESSFULLY using", data_path)

