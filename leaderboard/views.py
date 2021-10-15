from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views import View

from leaderboard.services import UserService


class HomeView(View):
    """
    This view displays the home page
    """

    template_name = 'home.html'
    page_name = 'home'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Get the home page

        :param request: The request made to the server
        """
        return render(request, self.template_name, {'page_name': self.page_name})


class LeaderboardView(View):
    """
    This view displays the leaderboard page
    """

    template_name = 'leaderboard.html'
    page_name = 'leaderboard'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Get the leaderboard page

        :param request: The request made to the server
        """
        return render(
            request,
            self.template_name,
            {'page_name': self.page_name, 'users': UserService.get_user_rankings()},
        )
