import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "ivf_model.pkl")
model = joblib.load(model_path)

# load feature list saved during training (optional)
features_file = os.path.join(BASE_DIR, 'ivf_features.json')
if os.path.exists(features_file):
    try:
        import json
        with open(features_file, 'r') as fh:
            IVF_FEATURES = json.load(fh)
    except Exception:
        IVF_FEATURES = None
else:
    IVF_FEATURES = None


def _prepare_input(input_data):
    """Accept either a list/tuple (already ordered) or a dict mapping feature->value.
    If a dict is provided and `ivf_features.json` is available, produce a list in that order.
    """
    if isinstance(input_data, (list, tuple)):
        return list(input_data)
    if isinstance(input_data, dict):
        if IVF_FEATURES:
            return [input_data.get(f, 0) for f in IVF_FEATURES]
        # fallback: sort keys alphabetically
        keys = sorted(input_data.keys())
        return [input_data[k] for k in keys]
    raise ValueError('input_data must be list or dict')


def predict_ivf(input_data):
    x = _prepare_input(input_data)

    probabilities = model.predict_proba([x])[0]
    success_prob = float(probabilities[1])
    failure_prob = float(probabilities[0])
    prediction = int(model.predict([x])[0])
    confidence = float(max(success_prob, failure_prob))

    if success_prob >= 0.70:
        label = "High IVF Success"
    elif success_prob >= 0.40:
        label = "Moderate IVF Success"
    else:
        label = "Low IVF Success"

    return {
        'prediction': prediction,
        'label': label,
        'confidence': confidence,
        'success_probability': success_prob,
        'failure_probability': failure_prob
    }
