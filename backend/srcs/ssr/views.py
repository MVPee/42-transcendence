from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from srcs.user.models import CustomUser as User
from srcs.community.models import Blocked, Friend
from srcs.game.models import Match, Matchs
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlparse
from django.db.models import Q
from django.conf import settings
import os

class BaseSSRView(View):
    """
    A base Server Side Rendering view that serves different pages as JSON responses,
    with optional authentication requirements.

    Attributes:
        pages_config (dict): Configuration for each page, specifying the template
            to render and whether authentication is required.
        page (str): The identifier for the specific page to render.
    """

    pages_config = {
        'play': {'template': 'play.html', 'auth_required': True},
        'scoreboard': {'template': 'scoreboard.html', 'auth_required': False},
        'profile': {'template': 'profile.html', 'auth_required': True},
        'settings': {'template': 'settings.html', 'auth_required': True},
        'community': {'template': 'community.html', 'auth_required': True},
        'login': {'template': 'login.html', 'auth_required': False},
        'register': {'template': 'register.html', 'auth_required': False},
        'chat': {'template': 'chat.html', 'auth_required': True},
        'waiting': {'template': 'waiting.html', 'auth_required': True},
        'game': {'template': 'game.html', 'auth_required': True},
    }

    context = None
    page = None

    language = 'EN'

    error_message = None
    success_message = None

    user = None
    all_users = None
    all_friends = None
    all_pendings = None

    friend = None
    friend_request = None
    blocked = None

    #? Online / Offline / Absent
    user_status = None 

    matchs_1v1 = None
    winrate_1v1 = None
    average_score_1v1 = None

    matchs_2v2 = None
    winrate_2v2 = None
    average_score_2v2 = None

    def get(self, request, *args, **kwargs):
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
        
        if (request.user.is_authenticated):
            user = User.objects.filter(id=request.user.id).first()
            if user:
                user.last_connection = timezone.now()
                user.save()
                self.language = user.language

        self.context = {
            'language': self.language,
            'error_message': self.error_message,
            'success_message': self.success_message,
            'user': self.user,
            'all_users': self.all_users,
            'all_friends': self.all_friends,
            'all_pendings': self.all_pendings,
            'friend': self.friend,
            'friend_request': self.friend_request,
            'blocked': self.blocked,
            'matchs_1v1': self.matchs_1v1,
            'winrate_1v1': self.winrate_1v1,
            'average_score_1v1': self.average_score_1v1,
            'matchs_2v2': self.matchs_2v2,
            'winrate_2v2': self.winrate_2v2,
            'average_score_2v2': self.average_score_2v2,
            'user_status': self.user_status,
        }

        # Check if the page requires authentication
        if page_config['auth_required'] and not request.user.is_authenticated:
            page_config = self.pages_config['login']
            self.context['error_message'] = 'You need to login to have access to this page.'
            html_content = render(request, page_config['template'], self.context).content.decode("utf-8")
            return JsonResponse({'html': html_content})
        else:
            html_content = render(request, page_config['template'], self.context).content.decode("utf-8")

        # print(html_content)  #* DEBUG
        return JsonResponse({'html': html_content})


class PlayView(BaseSSRView):
    """
    A view for the index page.
    Inherits from BaseSSRView and sets the page attribute to 'play'.
    """

    page = 'play'


class CommunityView(BaseSSRView):
    """
    A view for the 'community' page.
    Inherits from BaseSSRView and sets the page attribute to 'community'.
    """

    page = 'community'

    def all_users_friends(self, request):
        self.all_users = User.objects.exclude(id=request.user.id).exclude(username='AI.')
        self.all_friends = Friend.objects.filter((Q(user1=request.user.id) | Q(user2=request.user.id)), status=True).all()
        self.all_pendings = Friend.objects.filter(user2=request.user.id, status=False).all()

    def get(self, request):
        self.all_users_friends(request)
        return super().get(request)
    
    def post(self, request):
        self.all_users_friends(request)
        search = request.POST.get('query', '')
        if (search):
            self.all_users = self.all_users.filter(username__icontains=search)
        return super().get(request)


class ScoreboardView(BaseSSRView):
    """
    A view for the 'community' page.
    Inherits from BaseSSRView and sets the page attribute to 'community'.
    """

    page = 'scoreboard'

    def get(self, request):
        self.all_users = User.objects.all().order_by('-elo')
        return super().get(request)


class WaitingView(BaseSSRView):
    """
    A view for the 'waiting' page.
    Inherits from BaseSSRView and sets the page attribute to 'waiting'.
    """

    page = 'waiting'


class GameView(BaseSSRView):
    """
    A view for the 'waiting' page.
    Inherits from BaseSSRView and sets the page attribute to 'waiting'.
    """

    page = 'game'

    def get(self, request, *args, **kwargs):
        matchId = kwargs.get('id')
        matchMode = kwargs.get('mode')
        print(matchMode)

        if (matchMode == '1v1' or matchMode == 'AI'):
            self.matchs = Match.objects.filter(id=matchId).first()

            if self.matchs is None \
                or (self.matchs.user1.id != request.user.id and self.matchs.user2.id != request.user.id) \
                or (self.matchs.user1_score >= 5 or self.matchs.user2_score >= 5):
                self.page = 'play'
                self.error_message = 'You can\'t have access to this party.'
                return super().get(request)

            return super().get(request)

        elif (matchMode == '2v2'):
            self.matchs = Matchs.objects.filter(Q(id=matchId) & Q(user1=request.user) | Q(user2=request.user) | Q(user3=request.user) | Q(user4=request.user)).first()
            if self.matchs is not None and self.matchs.team1_score < 5 or self.matchs.team2_score < 5:
                self.page = 'play'
                self.error_message = '2v2 is comming but not now bro.'
                return super().get(request)
            else:
                self.page = 'play'
                self.error_message = 'You can\'t have access to this party.'
                return super().get(request)



class ChatView(BaseSSRView):
    """
    A view for the 'chat' page.
    Inherits from BaseSSRView and sets the page attribute to 'chat'.
    """

    page = 'chat'

    def get(self, request, *args, **kwargs):

        id = kwargs.get('id')
        friend = Friend.objects.filter((Q(user1=request.user.id) | Q(user2=request.user.id)), status=True).first()
        if (friend is None or friend.id != id):
            self.page = 'community'
            self.error_message = 'You can\'t access to this page'
            self.all_users = User.objects.exclude(id=request.user.id)
        return super().get(request)


class LoginView(BaseSSRView):
    """
    A view for the 'login' page.
    Inherits from BaseSSRView and sets the page attribute to 'login'.
    """

    page = 'login'

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            self.success_message = 'Login successfull.'
            self.page = urlparse(request.META.get('HTTP_REFERER')).path[1:]
            if self.page == 'login': self.page = 'profile'
            self.user = request.user

            #? 1v1 MATCH
            self.matchs_1v1 = Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-created_at')

            total_matches = self.matchs_1v1.count()
            wins = sum(1 for match in self.matchs_1v1 if (match.user1 == user and match.user1_score > match.user2_score) or 
                    (match.user2 == user and match.user2_score > match.user1_score))
            self.average_score_1v1 = round((sum(match.user1_score for match in self.matchs_1v1 if match.user1 == user) + 
                                sum(match.user2_score for match in self.matchs_1v1 if match.user2 == user)) / total_matches, 2) if total_matches > 0 else 0
            self.winrate_1v1 = round((wins / total_matches * 100), 2) if total_matches > 0 else 0

            #? 2v2 MATCH
            self.matchs_2v2 = Matchs.objects.filter(Q(user1=user) | Q(user2=user) | Q(user3=user) | Q(user4=user)).order_by('-created_at')

            total_matches_2v2 = self.matchs_2v2.count()
            wins_2v2 = sum(1 for match in self.matchs_2v2 if 
                        ((match.user1 == user or match.user2 == user) and match.team1_score > match.team2_score) or 
                        ((match.user3 == user or match.user4 == user) and match.team2_score > match.team1_score))
            self.average_score_2v2 = round((sum(match.team1_score for match in self.matchs_2v2 if match.user1 == user or match.user2 == user) + 
                                            sum(match.team2_score for match in self.matchs_2v2 if match.user3 == user or match.user4 == user)) / total_matches_2v2, 2) if total_matches_2v2 > 0 else 0
            self.winrate_2v2 = round((wins_2v2 / total_matches_2v2 * 100), 2) if total_matches_2v2 > 0 else 0

            return super().get(request)
        else:
            self.error_message = 'Invalid username or password.'
            self.page = 'login'
            return super().get(request)


class RegisterView(BaseSSRView):
    """
    A view for the 'register' page.
    Inherits from BaseSSRView and sets the page attribute to 'register'.
    """

    page = 'register'

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(username=username).exists():
            self.error_message = 'Username already exists.'
            return super().get(request)

        if User.objects.filter(email=email).exists():
            self.error_message = 'Email already in use.'
            return super().get(request)

        if password != confirm_password:
            self.error_message = 'Passwords do not match.'
            return super().get(request)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            self.success_message = 'Registration successful. You are now logged in.'
            self.page = 'profile'
            self.user = request.user
            return super().get(request)
        except Exception as e:
            self.error_message = f"An error occurred: {str(e)}"
            return super().get(request)


class ProfileView(BaseSSRView):
    """
    A view for the 'profile' page.
    Inherits from BaseSSRView and sets the page attribute to 'profile'.
    
    Methods:
        get(request): Overrides the base get method to allow retrieving
            a profile parameter from the request's query string.
    """
    
    page = 'profile'

    def get(self, request):

        if not request.user.is_authenticated: return super().get(request)

        #? /profile/?profile=exemple
        profile = request.GET.get('profile')
        # print("profile:", profile) #* Debug
        user = User.objects.filter(username=profile).first()
        if user is None:
            user = request.user

        friend = Friend.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id)).first()
        blocked = Blocked.objects.filter(user1=request.user.id, user2=user.id).first()
        self.friend = friend if friend and friend.status else None
        self.friend_request = friend and (friend.user1 == request.user or friend.status)
        self.blocked = blocked
        self.user = user

        #? 1v1 MATCH
        self.matchs_1v1 = Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-created_at')

        total_matches = self.matchs_1v1.count()
        wins = sum(1 for match in self.matchs_1v1 if (match.user1 == user and match.user1_score > match.user2_score) or 
                   (match.user2 == user and match.user2_score > match.user1_score))
        self.average_score_1v1 = round((sum(match.user1_score for match in self.matchs_1v1 if match.user1 == user) + 
                            sum(match.user2_score for match in self.matchs_1v1 if match.user2 == user)) / total_matches, 2) if total_matches > 0 else 0
        self.winrate_1v1 = round((wins / total_matches * 100), 2) if total_matches > 0 else 0

        #? 2v2 MATCH
        self.matchs_2v2 = Matchs.objects.filter(Q(user1=user) | Q(user2=user) | Q(user3=user) | Q(user4=user)).order_by('-created_at')

        total_matches_2v2 = self.matchs_2v2.count()
        wins_2v2 = sum(1 for match in self.matchs_2v2 if 
                    ((match.user1 == user or match.user2 == user) and match.team1_score > match.team2_score) or 
                    ((match.user3 == user or match.user4 == user) and match.team2_score > match.team1_score))
        self.average_score_2v2 = round((sum(match.team1_score for match in self.matchs_2v2 if match.user1 == user or match.user2 == user) + 
                                        sum(match.team2_score for match in self.matchs_2v2 if match.user3 == user or match.user4 == user)) / total_matches_2v2, 2) if total_matches_2v2 > 0 else 0
        self.winrate_2v2 = round((wins_2v2 / total_matches_2v2 * 100), 2) if total_matches_2v2 > 0 else 0

        if (friend and friend.status):
            time_diff = timezone.now() - user.last_connection

            if time_diff < timedelta(minutes=2): self.user_status = "Online"
            elif time_diff < timedelta(minutes=5): self.user_status = "Away"
            else: self.user_status = "Offline"

        return super().get(request)


class SettingsView(BaseSSRView):
    """
    A view for the 'settings' page.
    Inherits from BaseSSRView and sets the page attribute to 'settings'.
    
    Methods:
        get(request): Overrides the base get method to allow retrieving
            a profile parameter from the request's query string.
    """
    
    page = 'settings'

    def get(self, request):
        self.user = request.user
        return super().get(request)


class LogoutRequest(BaseSSRView):
    """
    A view for 'logout'.
    Inherits from BaseSSRView and sets the page attribute to 'login'.
    """
    
    page = 'login'

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            self.success_message = 'Logout successfull.'
        else:
            self.error_message = 'You are not authenticated.'
        return super().get(request)


class SettingsRequest(BaseSSRView):
    """
    A view for the 'settings' page.
    Inherits from BaseSSRView and sets the page attribute to 'settings'.
    
    Methods:
        get(request): Overrides the base get method to allow retrieving
            a profile parameter from the request's query string.
    """
    
    page = 'settings'

    def post(self, request):
        self.user = request.user
        action = request.POST.get('action')
        value = request.POST.get('value')

        if action == 'avatar' and 'avatar' in request.FILES:
            new_avatar = request.FILES['avatar']
            valid_extensions = ['png', 'jpeg', 'jpg']
            if not new_avatar.name.split('.')[-1].lower() in valid_extensions:
                self.error_message = 'Invalid file format. Only PNG, JPEG, and JPG are allowed.'
                return super().get(request)

            if not new_avatar.content_type in ['image/png', 'image/jpeg']:
                self.error_message = 'Invalid file format. Only PNG, JPEG, and JPG are allowed.'
                return super().get(request)

            width, height = get_image_dimensions(new_avatar)
            if width < 50 or height < 50 or width > 256 or height > 256:
                self.error_message = 'Avatar dimensions should be between 50x50 pixels and 256x256 pixels.'
                return super().get(request)

            # Delete the old avatar if it exists and isn't the default avatar
            if self.user.avatar.name != 'avatars/profile.png':
                old_avatar_path = os.path.join(settings.MEDIA_ROOT, self.user.avatar.name)
                if os.path.isfile(old_avatar_path):
                    os.remove(old_avatar_path)

            self.user.avatar = new_avatar
            self.user.save()
            self.success_message = 'Avatar updated successfully.'
        
        elif (action == 'username' and value):
            new_username = value
            if User.objects.filter(username=new_username).exclude(id=self.user.id).exists():
                self.error_message = 'Username already taken.'
            elif self.user.username == new_username:
                self.error_message = 'You need to use your keyboard to change your username.'
            else:
                self.user.username = new_username
                self.user.save()
                self.success_message = f'Username updated successfully to {new_username}'

        elif (action == 'email' and value):
            new_email = value
            if User.objects.filter(email=new_email).exclude(id=self.user.id).exists():
                self.error_message = 'Email already taken.'
            elif self.user.email == new_email:
                self.error_message = 'You need to use your keyboard to change your email.'
            else:
                self.user.email = new_email
                self.user.save()
                self.success_message = f'Email updated successfully to {new_email}'

        elif (action == 'language' and value):
            new_language = value
            if self.user.language == new_language:
                self.error_message = 'You need to use your mouse to change your language.'
            elif new_language in ['EN', 'FR', 'DE']:
                self.user.language = new_language
                self.user.save()
                self.success_message = 'Language updated successfully.'
            else:
                self.error_message = 'Invalid language selection.'

        return super().get(request)


class FriendRequest(BaseSSRView):
    """
    Handling friend requests on the 'profile' page.
    Inherits from BaseSSRView and sets the page attribute to 'profile'.
    
    Methods:
        post(request): Processes friend requests based on the profile, action, and type parameters in the request body.
    """

    page = 'profile'
    
    def post(self, request):
        profile = request.POST.get('profile')
        type = request.POST.get('type')
        # print("FRIEND REQUEST") #* Debug
        # print("profile:", profile) #* Debug
        # print("type:", type) #* Debug

        user = User.objects.filter(username=profile).first()
        if user is None:
            user = request.user
        else:
            friend = Friend.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id) ).first()
            block = Blocked.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id) ).first()
            if type=='add':
                if block is None:
                    if friend is None: #? Create a new friend with status pending
                        friend = Friend.objects.create(user1=request.user, user2=user, status=False)
                        friend.save()
                        self.success_message = f"Sucessfuly sent a friend request to {profile}."
                    else:
                        if friend.status is True:
                            self.error_message = f"{profile} is already your friend."
                        elif friend.user1 == request.user: #? if initial friend request came from me
                            self.error_message = f"A friend request was already sent to {profile}."
                        else: #? if initial friend request did not came from me
                            self.success_message = f"You and {profile} are now friends !"
                            friend.status = True
                            friend.save()

                    self.friend = friend.status
                    self.friend_request = friend.user1 == request.user or friend.status

                else:
                    self.error_message = f"You can't send a friend request to {profile}."

            elif type=='remove':
                if friend is None:
                    self.error_message = f"{profile} is not in your friend list."
                else:
                    if friend.user1 == request.user:  #? if initial friend request came from me
                        if friend.status is False:
                            self.success_message = f"{profile} friend request sucessfuly aborted."
                        else :
                            self.success_message = f"{profile} has been removed from your friends."
                    else:
                        if friend.status is False:
                            self.error_message = f"A friend request to {profile} was never sent."

                friend.delete()
                self.friend = False
                self.friend_request = False

            self.blocked = Blocked.objects.filter(user1=request.user.id, user2=user.id).first()

        self.user = user

        self.matchs = Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-created_at')

        total_matches = self.matchs.count()
        wins = sum(1 for match in self.matchs if (match.user1 == user and match.user1_score > match.user2_score) or 
                   (match.user2 == user and match.user2_score > match.user1_score))
        self.average_score = round((sum(match.user1_score for match in self.matchs if match.user1 == user) + 
                            sum(match.user2_score for match in self.matchs if match.user2 == user)) / total_matches, 2) if total_matches > 0 else 0
        self.winrate = round((wins / total_matches * 100), 2) if total_matches > 0 else 0

        if (friend and friend.status):
            time_diff = timezone.now() - user.last_connection

            if time_diff < timedelta(minutes=2): self.user_status = "Online"
            elif time_diff < timedelta(minutes=5): self.user_status = "Away"
            else: self.user_status = "Offline"

        return super().get(request)


class BlockRequest(BaseSSRView):
    """
    Handling block requests on the 'profile' page.
    Inherits from BaseSSRView and sets the page attribute to 'profile'.
    
    Methods:
        post(request): Processes friend requests based on the profile, action, and type parameters in the request body.
    """

    page = 'profile'
    
    def post(self, request):
        profile = request.POST.get('profile')
        type = request.POST.get('type')
        # print("BLOCK REQUEST") #* Debug
        # print("profile:", profile) #* Debug
        # print("type:", type) #* Debug

        user = User.objects.filter(username=profile).first()
        if user is None:
            user = request.user
        else:
            blocked = Blocked.objects.filter(user1=request.user.id, user2=user.id).first()

            if type=='add':
                if blocked is None: 
                    new_blocked = Blocked.objects.create(user1=request.user, user2=user)
                    new_blocked.save()
                    self.success_message = f"Sucessfuly blocked {profile}."
                else:
                    self.error_message = f"{profile} is already blocked."
                #? remove the friend relation in the database if they were friend
                friend = Friend.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id) ).first()
                if (friend):
                    friend.delete()
            elif type=='remove':
                if blocked is None: 
                    self.error_message = f"{profile} was not blocked."
                else:
                    blocked.delete()
                    self.success_message = f"{profile} is not blocked anymore."

            self.friend = False 
            self.friend_request = False
            self.blocked = type=='add'
        
        self.user = user

        self.matchs = Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-created_at')

        total_matches = self.matchs.count()
        wins = sum(1 for match in self.matchs if (match.user1 == user and match.user1_score > match.user2_score) or 
                   (match.user2 == user and match.user2_score > match.user1_score))
        self.average_score = round((sum(match.user1_score for match in self.matchs if match.user1 == user) + 
                            sum(match.user2_score for match in self.matchs if match.user2 == user)) / total_matches, 2) if total_matches > 0 else 0
        self.winrate = round((wins / total_matches * 100), 2) if total_matches > 0 else 0
        
        return super().get(request)
