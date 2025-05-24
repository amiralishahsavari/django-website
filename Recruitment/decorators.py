# optional for getting points 
from django.shortcuts import redirect
from functools import wraps

def jobseeker_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'jobseeker'):
            return view_func(request, *args, **kwargs)
        return redirect('home')  # یا نمایش پیغام خطا
    return _wrapped_view

def employer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'employer'):
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return _wrapped_view
