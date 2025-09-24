from django.http import HttpResponseForbidden
from functools import wraps

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Требуется авторизация.")
        if request.user.role not in ['manager', 'admin']:
            return HttpResponseForbidden("Доступ запрещен. Требуются права менеджера.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
