from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .pcos_predictor import get_pcos_prediction, train_pcos_model
from .ivf_predictor import predict_ivf

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
        weight_change = request.POST.get('weight_change', 'No Change')
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
        weight_gain = 1 if weight_change == 'Weight Gain' else 0
        
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
            'prediction_status': result['status'],
            'message': result['status']
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

        # ----------------------------
        # CONSISTENT ENCODING (IMPORTANT)
        # ----------------------------
        input_data = [
            float(form_data['age']),
            float(form_data['weight']),
            float(form_data['height']),

            1 if form_data['periods'] == 'Regular' else 0,
            1 if form_data['pcos'] == 'Yes' else 0,

            # stress: Low=0, Medium=1, High=2
            0 if form_data['stress'] == 'Low' else 1 if form_data['stress'] == 'Medium' else 2,

            1 if form_data['smoking'] == 'Yes' else 0,
            1 if form_data['pregnancy'] == 'Yes' else 0,

            float(form_data['years']),

            1 if form_data['activity'] in ['Active', 'Moderate'] else 0,

            0 if form_data['disease'] == 'Yes' else 1,   # Yes disease = risk (0 better logic)

            1 if form_data['fertility_test'] == 'Yes' else 0,
            1 if form_data['issues'] == 'None' else 0
        ]

        # ----------------------------
        # PREDICTION
        # ----------------------------
        result = predict_ivf(input_data)
        confidence_pct = result['confidence'] * 100
        success_pct = result['success_probability'] * 100

        if result['label'] == 'High IVF Success':
            prediction = f"🟢 High IVF Success ({success_pct:.1f}% chance, {confidence_pct:.1f}% confidence)"
        elif result['label'] == 'Moderate IVF Success':
            prediction = f"🟡 Moderate IVF Success ({success_pct:.1f}% chance, {confidence_pct:.1f}% confidence)"
        else:
            prediction = f"🔴 Low IVF Success ({success_pct:.1f}% chance, {confidence_pct:.1f}% confidence)"

    return render(request, 'ivf.html', {
        'form_data': form_data,
        'prediction': prediction
    })
    
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
    if request.method == 'POST':
        try:
            # Collect form data
            age = request.POST.get('age')
            weight = request.POST.get('weight')
            pcos_status = request.POST.get('pcos_status', 'No')
            fertility_score = request.POST.get('fertility_score')

            # Convert to proper types
            try:
                age_val = int(age) if age not in (None, '') else None
            except ValueError:
                age_val = None

            try:
                weight_val = float(weight) if weight not in (None, '') else None
            except ValueError:
                weight_val = None

            try:
                score_val = int(fertility_score) if fertility_score not in (None, '') else None
            except ValueError:
                score_val = None

            # Generate recommendations based on inputs
            recommendations = []

            # Age-based recommendations
            if age_val is not None:
                if age_val < 25:
                    recommendations.append("Focus on maintaining overall health. Consider tracking your menstrual cycle and starting prenatal vitamins.")
                elif age_val < 35:
                    recommendations.append("This is an optimal fertility window. Maintain healthy lifestyle habits and regular check-ups.")
                elif age_val < 40:
                    recommendations.append("Consider fertility testing if planning pregnancy. Discuss with a specialist about your timeline.")
                else:
                    recommendations.append("Age-related fertility considerations increase. Consult with a fertility specialist for personalized guidance.")

            # Weight-based recommendations
            if weight_val is not None and age_val is not None:
                # Estimate BMI (assume average height of 165cm for recommendation purposes)
                height_m = 1.65
                bmi = weight_val / (height_m * height_m)
                if bmi < 18.5:
                    recommendations.append("Maintain a balanced diet to achieve a healthy weight. Underweight status may affect fertility.")
                elif bmi > 30:
                    recommendations.append("Consider a gradual weight management plan. Maintaining a healthy weight can improve fertility outcomes.")
                else:
                    recommendations.append("Your weight is in a healthy range. Continue balanced nutrition and regular exercise.")

            # PCOS-based recommendations
            if pcos_status == 'Yes':
                recommendations.append("PCOS management is important: maintain balanced diet, regular exercise, manage stress, and follow up with your healthcare provider for hormonal assessment.")
            else:
                recommendations.append("No PCOS detected. Continue healthy lifestyle practices and regular medical check-ups.")

            # Fertility score-based recommendations
            score_header = ''
            score_details = []
            if score_val is not None:
                if score_val <= 40:
                    score_header = 'Score 0–40'
                    score_details = [
                        'Consult a fertility specialist',
                        'Comprehensive reproductive health evaluation',
                        'Lifestyle modifications'
                    ]
                elif score_val <= 70:
                    score_header = 'Score 41–70'
                    score_details = [
                        'Regular health monitoring',
                        'Improve sleep and nutrition',
                        'Stress management techniques'
                    ]
                else:
                    score_header = 'Score 71–100'
                    score_details = [
                        'Maintain current healthy habits',
                        'Regular reproductive health checkups',
                        'Continue balanced diet and exercise'
                    ]

            # Build HTML output
            custom_message = ''
            if pcos_status == 'Yes':
                custom_message = '<p><strong>PCOS Management:</strong> Maintain balanced diet, regular exercise, and stress control. Follow up with your healthcare provider for hormonal assessment.</p>'
            else:
                custom_message = '<p><strong>General Note:</strong> No PCOS detected. Continue healthy lifestyle practices and regular check-ups.</p>'

            score_section = ''
            if score_header:
                score_items = ''.join(f'<li>{item}</li>' for item in score_details)
                score_section = f'<div><strong>{score_header}</strong><ul>{score_items}</ul></div>'

            tips_section = ('<div><strong>Key Tips:</strong>'
                            '<ul>'
                            '<li>Stay hydrated and aim for 7-8 hours of sleep every night.</li>'
                            '<li>Manage stress with mindfulness, yoga, or breathing exercises.</li>'
                            '<li>Avoid smoking, excess alcohol, and processed foods.</li>'
                            '</ul></div>')

            diet_section = ('<div><strong>Balanced Diet Recommendations:</strong>'
                            '<ul>'
                            '<li>Include lean protein daily: fish, poultry, eggs, legumes.</li>'
                            '<li>Eat plenty of fiber-rich vegetables, fruits, and whole grains.</li>'
                            '<li>Choose healthy fats such as avocado, nuts, seeds and olive oil.</li>'
                            '<li>Limit refined sugars and highly processed snacks.</li>'
                            '</ul></div>')

            exercise_section = ('<div><strong>Exercise Recommendations:</strong>'
                                '<ul>'
                                '<li>Begin with 30 minutes of moderate activity most days.</li>'
                                '<li>Use low-impact aerobic exercise like walking, swimming, or cycling.</li>'
                                '<li>Add gentle strength training 2-3 times per week.</li>'
                                '<li>Include yoga and stretching for hormonal balance and stress relief.</li>'
                                '</ul></div>')

            yoga_links = (
                '<div><strong>Yoga Tutorials:</strong>'
                '<ul>'
                '<li><a href="https://www.youtube.com/watch?v=zRWUrWPWD2Y" target="_blank" rel="noopener noreferrer">PCOS Yoga Routine - 15 Min Full Body</a></li>'
                '<li><a href="https://www.youtube.com/watch?v=YukpAFgNJM8" target="_blank" rel="noopener noreferrer">PCOS Exercise & Fitness Plan - Doctor Explained</a></li>'
                '<li><a href="https://www.youtube.com/watch?v=dxV8UjwzmPA" target="_blank" rel="noopener noreferrer">PCOS Management & Yoga Tips</a></li>'
                '</ul></div>'
            )

            # Add score-based summary to top
            if score_section:
                recommendations.insert(0, score_section)

            # Add the custom note and sections
            recommendations.append(custom_message)
            recommendations.append(tips_section)
            recommendations.append(diet_section)
            recommendations.append(exercise_section)
            recommendations.append(yoga_links)

            recommendation_text = ''.join(recommendations)

            return JsonResponse({
                'status': 'success',
                'recommendation_html': recommendation_text
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return render(request, 'recommend.html')
