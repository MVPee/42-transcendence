from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

class BaseAPIView(View):
    pages_config = {
        'home': {'template': 'home.html', 'auth_required': False},
        'profile': {'template': 'profile.html', 'auth_required': True},
        'login': {'template': 'login.html', 'auth_required': False},
    }

    page = None

    def get(self, request, *args, **kwargs):
        if not self.page or self.page not in self.pages_config:
            return JsonResponse({'html': "<p>404: NOT FOUND</p>"})

        page_config = self.pages_config[self.page]

        # Check if the page requires authentication
        if page_config['auth_required'] and not request.user.is_authenticated:
            login_content = render(request, 'login.html').content.decode("utf-8")
            return JsonResponse({
                'html': login_content,
                'error': "You must be logged in to access this page."
            })

        # Render the requested page’s content
        html_content = render(request, page_config['template']).content.decode("utf-8")
        return JsonResponse({'html': html_content})


class HomeView(BaseAPIView):
    page = 'home'


class LoginView(BaseAPIView):
    page = 'login'


class ProfileView(BaseAPIView):
    page = 'profile'