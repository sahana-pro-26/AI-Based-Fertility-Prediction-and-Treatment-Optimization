from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def pcos(request):
    return render(request, 'pcos.html')

