from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from rest_framework.views import APIView
from srcs.user.models import CustomUser as User
from srcs.community.models import Blocked, Friend, Messages
from srcs.game.models import Match, Matchs, Tournament
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import requests

class BaseSSRView(APIView):
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
        'pong1v1': {'template': 'pong1v1.html', 'auth_required': True},
        'pong2v2': {'template': 'pong2v2.html', 'auth_required': True},
        'puissance4': {'template': 'puissance4.html', 'auth_required': True},
        'tournament': {'template': 'tournament.html', 'auth_required': True},
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

    matchs = None

    pong = None
    puissance4 = None
    
    messages = None

    def requests(self, url):
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()

            data = response.json()
            print(data)
            return data
        except requests.exceptions.RequestException as e:
            print(str(e))
            return None

    def get_game_stats(self, games, mode):
        win = 0
        defeat = 0
        winrate = 0
        if games is not None:

            if mode in ['1v1', 'ai', 'puissance4']:
                for game in games:
                    if game.user1 == self.user and game.user1_score > game.user2_score:
                        win += 1
                    elif game.user2 == self.user and game.user2_score > game.user1_score:
                        win += 1
                    else:
                        defeat += 1
            elif mode == '2v2':
                for game in games:
                    if (game.user1 == self.user or game.user2 == self.user) and game.team1_score > game.team2_score:
                        win += 1
                    elif (game.user3 == self.user or game.user4 == self.user) and game.team2_score > game.team1_score:
                        win += 1
                    else:
                        defeat += 1

            total_matches = win + defeat
            winrate = round((win / total_matches * 100), 2) if total_matches > 0 else 0

        return {"win": win, "defeat": defeat, "winrate": winrate, 'matchs': games}

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
            return Response({'html': "<p>404: NOT FOUND</p>"}, status=status.HTTP_404_NOT_FOUND)

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
            'matchs': self.matchs,
            'pong': self.pong,
            'puissance4': self.puissance4,
            'user_status': self.user_status,
            'messages': self.messages,
        }

        # Check if the page requires authentication
        if page_config['auth_required'] and not request.user.is_authenticated:
            page_config = self.pages_config['login']
            self.context['error_message'] = 'You need to login to have access to this page.'
            html_content = render(request, page_config['template'], self.context).content.decode("utf-8")
            return Response({'html': html_content}, status=status.HTTP_200_OK)
        else:
            html_content = render(request, page_config['template'], self.context).content.decode("utf-8")

        # print(html_content)  #* DEBUG
        return Response({'html': html_content}, status=status.HTTP_200_OK)


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
        self.all_users = User.objects.exclude(username='AI.').order_by('-elo')
        return super().get(request)


class WaitingView(BaseSSRView):
    """
    A view for the 'waiting' page.
    Inherits from BaseSSRView and sets the page attribute to 'waiting'.
    """

    page = 'waiting'
    def get(self, request, *args, **kwargs):
        game_mode = kwargs.get('game_mode')
        queue_type = kwargs.get('queue_type')
        if game_mode == 'private':
            self.friend = Friend.objects.filter(Q(id=int(queue_type)) & Q(user1=request.user) | Q(user2=request.user)).first()
            if self.friend is None:
                self.error_message = 'You can\'t have access to this party.'
                self.page = 'play'
                return super().get(request)
        return super().get(request)


class GameView(BaseSSRView):
    """
    A view for the 'waiting' page.
    Inherits from BaseSSRView and sets the page attribute to 'waiting'.
    """

    page = 'pong1v1'

    def get(self, request, *args, **kwargs):
        game = kwargs.get('game')
        matchId = kwargs.get('id')
        matchMode = kwargs.get('mode')

        if (game == 'puissance4'):
            self.matchs = Match.objects.filter((Q(id=matchId) & Q(game='puissance4_1v1')) & (Q(user1=request.user) | Q(user2=request.user))).first()
            print(self.matchs)

            if self.matchs is not None and self.matchs.user1_score < 1 and self.matchs.user2_score < 1:
                self.page = 'puissance4'
                return super().get(request)
            self.error_message = 'You can\'t have access to this party.'
            self.page = 'play'
            return super().get(request)

        elif (matchMode == '1v1' or matchMode == 'AI'):
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
            if self.matchs is not None and self.matchs.team1_score < 5 and self.matchs.team2_score < 5:
                self.page = 'pong2v2'
                return super().get(request)
            else:
                self.page = 'play'
                self.error_message = 'You can\'t have access to this party.'
                return super().get(request)
    
        elif (matchMode == 'tournament'):
            self.matchs = Tournament.objects.filter(Q(id=matchId) & Q(user1=request.user) | Q(user2=request.user) | Q(user3=request.user) | Q(user4=request.user)).first()
            if self.matchs is not None and self.matchs.winner is None:
                self.page = 'tournament'
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
        friend = Friend.objects.filter(id=id).first()
        if (friend is None or (friend.user1 != request.user and friend.user2 != request.user)):
            self.page = 'community'
            self.error_message = 'You can\'t access to this page'
            self.all_users = User.objects.exclude(id=request.user.id)
        else: #* load messages history
            self.friend = friend
            self.messages = Messages.objects.filter(friend_id=id).order_by('created_at')
        self.user = request.user
        return super().get(request)


class LoginView(BaseSSRView):
    """
    A view for the 'login' page.
    Inherits from BaseSSRView and sets the page attribute to 'login'.
    """

    page = 'login'


class RegisterView(BaseSSRView):
    """
    A view for the 'register' page.
    Inherits from BaseSSRView and sets the page attribute to 'register'.
    """

    page = 'register'


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
        if profile and profile[-1] == '/':
            profile = profile[:-1]
        user = User.objects.filter(username=profile).first()
        # print("profile:", profile) #* Debug
        # print(user) #* Debug
        if user is None:
            user = request.user

        friend = Friend.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id)).first()
        blocked = Blocked.objects.filter(user1=request.user.id, user2=user.id).first()
        self.friend = friend if friend and friend.status else None
        self.friend_request = friend and (friend.user1 == request.user or friend.status)
        self.blocked = blocked
        self.user = user

        pong_1v1 = Match.objects.filter(
            Q(game='pong_1v1') & (Q(user1=user) | Q(user2=user))
        ).order_by('-created_at').all()

        pong_ai = Match.objects.filter(
            Q(game='pong_ai') & (Q(user1=user) | Q(user2=user))
        ).order_by('-created_at').all()

        pong_2v2 = Matchs.objects.filter(
            Q(game='pong_2v2') & (Q(user1=user) | Q(user2=user) | Q(user3=user) | Q(user4=user))
        ).order_by('-created_at').all()

        puissance4_1v1 = Match.objects.filter(
            Q(game='puissance4_1v1') & (Q(user1=user) | Q(user2=user))
        ).order_by('-created_at').all()

        self.pong = {
            "1v1": self.get_game_stats(pong_1v1, '1v1'),
            "2v2": self.get_game_stats(pong_2v2, '2v2'),
            "ai": self.get_game_stats(pong_ai, 'ai')
        }

        self.puissance4 = {
            "1v1": self.get_game_stats(puissance4_1v1, 'puissance4')
        }

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
