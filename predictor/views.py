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
    return render(request, 'score.html')

def recommend(request):
    return render(request, 'recommend.html')
