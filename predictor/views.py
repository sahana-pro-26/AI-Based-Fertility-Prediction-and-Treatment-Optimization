from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .pcos_predictor import get_pcos_prediction, train_pcos_model

def home(request):
    return render(request, 'index.html')

def pcos(request):
    return render(request, 'pcos.html')

@require_http_methods(["POST"])
def predict_pcos(request):
    """Handle PCOS prediction request"""
    try:
        age = int(request.POST.get('age', 0))
        weight = float(request.POST.get('weight', 0))
        menstrual_cycle = request.POST.get('irregular_period', 'Regular')
        acne_problem = request.POST.get('acne_problem', 'No')
        hair_loss = request.POST.get('hair_loss', 'No')
        hair_loss_detail = request.POST.get('hair_loss_detail', '')
        facial_hair = request.POST.get('facial_hair', 'No')
        mood_swings = request.POST.get('mood_swings', 'No')
        
        # Convert to binary values (0/1)
        period_regularity = 1 if menstrual_cycle == 'Regular' else 0
        acne_value = 1 if acne_problem == 'Yes' else 0
        hair_loss_value = 1 if hair_loss == 'Yes' else 0
        facial_hair_value = 1 if facial_hair == 'Yes' else 0
        mood_swings_value = 1 if mood_swings == 'Yes' else 0
        weight_gain = 0  # Default value (can be enhanced with additional form field)
        
        # Get prediction
        result = get_pcos_prediction(
            age=age,
            weight=weight,
            weight_gain=weight_gain,
            facial_hair=facial_hair_value,
            hair_loss=hair_loss_value,
            acne=acne_value,
            mood_swings=mood_swings_value,
            period_regularity=period_regularity
        )
        
        return JsonResponse({
            'status': 'success',
            'has_pcos': result['has_pcos'],
            'confidence': round(result['confidence'], 2),
            'pcos_probability': round(result['pcos_probability'], 2),
            'message': 'PCOS Detected' if result['has_pcos'] else 'PCOS Not Detected'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing prediction: {str(e)}'
        }, status=400)

def ivf(request):
    form_data = {}
    prediction = None

    if request.method == 'POST':
        form_data = {
            'age': request.POST.get('age', ''),
            'weight': request.POST.get('weight', ''),
            'height': request.POST.get('height', ''),
            'periods': request.POST.get('periods', ''),
            'pcos': request.POST.get('pcos', ''),
            'stress': request.POST.get('stress', ''),
            'smoking': request.POST.get('smoking', ''),
            'pregnancy': request.POST.get('pregnancy', ''),
            'years': request.POST.get('years', ''),
            'activity': request.POST.get('activity', ''),
            'disease': request.POST.get('disease', ''),
            'fertility_test': request.POST.get('fertility_test', ''),
            'issues': request.POST.get('issues', ''),
        }

        score = 0
        try:
            age = int(form_data['age'])
        except ValueError:
            age = None

        if age is not None and age < 35:
            score += 1
        if form_data['pcos'] == 'No':
            score += 1
        if form_data['periods'] == 'No':
            score += 1
        if form_data['stress'] == 'Low':
            score += 1
        if form_data['smoking'] == 'No':
            score += 1
        if form_data['pregnancy'] == 'Yes':
            score += 1
        if form_data['activity'] in ('Active', 'Moderate'):
            score += 1
        if form_data['disease'] == 'No':
            score += 1
        if form_data['fertility_test'] == 'Yes':
            score += 1
        if form_data['issues'] == 'None':
            score += 1

        prediction = 'Likely to have IVF success' if score >= 4 else 'Less likely to have IVF success'

    return render(request, 'ivf.html', {'form_data': form_data, 'prediction': prediction})

def score(request):
    # Render the fertility score page on GET.
    # Handle AJAX POST requests that return a JSON fertility score.
    if request.method == 'POST':
        try:
            # Collect form data
            age = request.POST.get('age')
            weight = request.POST.get('weight')
            height = request.POST.get('height')
            smoking = request.POST.get('smoking', 'non-smoker')
            alcohol = request.POST.get('alcohol', 'never')
            exercise = request.POST.get('exercise', 'Moderate')
            menstrual_cycle = request.POST.get('menstrual_cycle', 'Regular')
            pcos = request.POST.get('pcos', 'No')
            previous_pregnancy = request.POST.get('previous_pregnancy', 'No')
            partner_issues = request.POST.get('partner_issues', 'No')
            fertility_test = request.POST.get('fertility_test', 'No')
            medical_indicator = request.POST.get('medical_indicator', 'None')
            amh_level = request.POST.get('amh_level', '')
            thyroid_status = request.POST.get('thyroid_status', 'None')
            diabetes_status = request.POST.get('diabetes_status', 'None')

            # Normalize empty-string selects to defaults
            if not smoking:
                smoking = 'non-smoker'
            if not alcohol:
                alcohol = 'never'
            if not exercise:
                exercise = 'Moderate'
            if not menstrual_cycle:
                menstrual_cycle = 'Regular'
            if not pcos:
                pcos = 'No'
            if not previous_pregnancy:
                previous_pregnancy = 'No'
            if not partner_issues:
                partner_issues = 'No'
            if not fertility_test:
                fertility_test = 'No'
            if not medical_indicator:
                medical_indicator = 'None'

            # Scoring logic (simple, extensible)
            points = 0
            total = 11

            try:
                age_val = int(age) if age not in (None, '') else None
            except ValueError:
                age_val = None

            if age_val is not None and age_val < 35:
                points += 1

            # BMI check
            try:
                w = float(weight) if weight not in (None, '') else None
                h = float(height) if height not in (None, '') else None
                if w and h:
                    h_m = h / 100.0 if h > 3 else h
                    bmi = w / (h_m * h_m) if h_m > 0 else None
                    if bmi and 18.5 <= bmi <= 24.9:
                        points += 1
            except Exception:
                pass

            # Smoking scoring: reward non-smokers and former smokers
            if str(smoking).lower() in ('non-smoker', 'former'):
                points += 1
            # Alcohol scoring: reward never or occasional intake
            if str(alcohol).lower() in ('never', 'occasionally'):
                points += 1
            if exercise in ('Active', 'Moderate'):
                points += 1
            if menstrual_cycle == 'Regular':
                points += 1
            if pcos == 'No':
                points += 1
            if previous_pregnancy == 'Yes':
                points += 1
            if partner_issues == 'No':
                points += 1
            if fertility_test == 'Yes':
                points += 1

            if medical_indicator == 'AMH':
                try:
                    amh_val = float(amh_level) if amh_level not in (None, '') else None
                except ValueError:
                    amh_val = None
                if amh_val is not None and amh_val >= 1.0:
                    points += 1
            elif medical_indicator == 'Thyroid':
                if thyroid_status == 'Normal':
                    points += 1
            elif medical_indicator == 'Diabetes':
                if diabetes_status == 'NoHistory':
                    points += 1

            score_percent = int((points / float(total)) * 100)

            if score_percent <= 40:
                category = 'Low Fertility'
                range_label = '0–40 → Low Fertility'
                color = '#ef4444'
                message = 'Your fertility score is low; consider specialist guidance and lifestyle support.'
            elif score_percent <= 70:
                category = 'Moderate Fertility'
                range_label = '41–70 → Moderate Fertility'
                color = '#f59e0b'
                message = 'Your fertility score is moderate; maintain healthy habits and discuss next steps with a provider.'
            else:
                category = 'High Fertility'
                range_label = '71–100 → High Fertility'
                color = '#22c55e'
                message = 'Your fertility score is high; current indicators look favorable.'

            return JsonResponse({
                'status': 'success',
                'score': score_percent,
                'points': points,
                'total': total,
                'category': category,
                'range_label': range_label,
                'color': color,
                'message': message
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return render(request, 'score.html')

def recommend(request):
    return render(request, 'recommend.html')
