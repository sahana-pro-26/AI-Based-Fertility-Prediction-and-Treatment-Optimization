from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def pcos(request):
    return render(request, 'pcos.html')

def ivf(request):
    return render(request, 'ivf.html')

def score(request):
    return render(request, 'score.html')

def recommend(request):
    return render(request, 'recommend.html')
