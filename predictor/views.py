from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def pcos(request):
    return render(request, 'pcos.html')

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
