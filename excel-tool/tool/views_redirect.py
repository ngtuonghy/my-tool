from django.shortcuts import redirect


def redirect_to_simple(request):
    """Redirect root to simple page"""
    return redirect('tool:index')
