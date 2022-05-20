import django.db.utils
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from .business_logic.log_processing import process_log
from .business_logic.nl_processing import generate_script
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .models import Game
from .serializers import GameSerializer

NUMBER_OF_GAMES_BY_USER = 2


@csrf_exempt
def new_login(request):
    user_str = request.body.decode()
    user_json = json.loads(user_str)
    username = user_json["username"]
    password = user_json["password"]

    user = authenticate(username=username, password=password)

    if user is not None:
        return HttpResponse("login_success")
    return HttpResponse("login_failure")


@csrf_exempt
def new_register(request):
    user_str = request.body.decode()
    user_json = json.loads(user_str)
    username = user_json["username"]
    email = user_json["email"]
    password = user_json["password"]

    try:
        user = User.objects.create_user(username, email, password)
        user.save()
        return HttpResponse("register_success")
    except django.db.utils.IntegrityError:
        return HttpResponse("username_already_in_use")


class GameList(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        queryset = Game.objects.all()
        query_params = self.request.query_params
        username = query_params.get('username')
        title = query_params.get('title')
        league = query_params.get('league')
        group = query_params.get('matchGroup')
        year = query_params.get('year')
        roud = query_params.get('round')
        sort_field = query_params.get('sort')

        if username is not None:
            queryset = queryset.filter(user__username=username)
        if title is not None:
            queryset = queryset.filter(title__in=title)
        if league is not None:
            queryset = queryset.filter(league__in=league)
        if group is not None:
            queryset = queryset.filter(matchGroup__in=group)
        if year is not None:
            queryset = queryset.filter(year=year)
        if roud is not None:
            queryset = queryset.filter(round=roud)
        if sort_field is not None:
            queryset = queryset.order_by(sort_field)

        return queryset

@csrf_exempt
@api_view(['POST'])
def file_upload(request):
    # game_str = request.body.decode()
    # game_json = json.loads(game_str)
    # filename = game_json["fileName"]
    # print(filename)

    uploaded_file = request.FILES['file']
    data = request.data
    user_form = data["user"]
    title = data["title"]
    description = data["description"]
    isPublic = data["isPublic"]
    league = data["league"]
    year = data["year"]
    roud = data["round"]
    matchGroup = data["matchGroup"]

    user_games = Game.objects.get(user__username=user_form)

    if len(user_games) >= NUMBER_OF_GAMES_BY_USER:
        return Response({"error": "Reached number of games by given user."})

    game = Game(logfile=uploaded_file, title=title, description=description,
                isPublic=isPublic, league=league, year=year, round=roud, matchGroup=matchGroup)

    game.save()

    events, analytics, form, form_players = process_log(uploaded_file)
    json_response = {"events": [], "form": form, "form_players": form_players}

    # new_game = Game.objects.create(uploaded_file, )

    for event in events:
        json_response["events"].append(event.to_json())

    for timestamp in analytics:
        for team in analytics[timestamp]["teams"]:
            analytics[timestamp]["teams"][team] = analytics[timestamp]["teams"][team].to_json()
        for player in analytics[timestamp]["players"]:
            analytics[timestamp]["players"][player] = analytics[timestamp]["players"][player].to_json()
    json_response["stats"] = analytics

    response = generate_script(json_response['events'], json_response["stats"])
    print(f"{response = }")

    return Response(response)
