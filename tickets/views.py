# tickets/views.py
from django.shortcuts import render

def dashboard_view(request):
    # La variable 'view_class' se pasará al template base.html
    context = {
        'view_class': 'view-dashboard'
    }
    return render(request, 'dashboard.html', context)