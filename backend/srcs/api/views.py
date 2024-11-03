from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

class BaseAPIView(View):
    """
    A base API view that serves different pages as JSON responses,
    with optional authentication requirements.

    Attributes:
        pages_config (dict): Configuration for each page, specifying the template
            to render and whether authentication is required.
        page (str): The identifier for the specific page to render.
    """

    pages_config = {
        'home': {'template': 'home.html', 'auth_required': False},
        'profile': {'template': 'profile.html', 'auth_required': True},
        'login': {'template': 'login.html', 'auth_required': False},
    }

    page = None

    def get(self, request):
        """
        Handles GET requests and returns the content of the requested page
        as a JSON response. If the page requires authentication, checks the
        user's login status and redirects to the login page if unauthenticated.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            JsonResponse: Contains the HTML content of the page, or an error message
                if the page is not found or if the user is not authenticated.
        """
    
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
    """
    A view for the 'home' page.
    Inherits from BaseAPIView and sets the page attribute to 'home'.
    """

    page = 'home'


class LoginView(BaseAPIView):
    """
    A view for the 'login' page.\n
    Inherits from BaseAPIView and sets the page attribute to 'login'.
    """

    page = 'login'


class ProfileView(BaseAPIView):
    """
    A view for the 'profile' page.
    Inherits from BaseAPIView and sets the page attribute to 'profile'.
    
    Methods:
        get(request): Overrides the base get method to allow retrieving
            a profile parameter from the request's query string.
    """
    
    page = 'profile'

    def get(self, request):
        #? /profile/?profile=exemple
        profile = request.GET.get('profile')
        print("profile:", profile)
        return super().get(request)