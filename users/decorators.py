from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'role') or request.user.role not in ['manager', 'admin']:
            messages.error(request, 'У вас нет прав для доступа к этой странице.')
            return redirect('product_list')
        return view_func(request, *args, **kwargs)
    return wrapper
