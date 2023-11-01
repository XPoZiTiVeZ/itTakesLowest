from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Games, Answers
from login.models import CustomUser
from datetime import datetime, timedelta
import uuid

def home(request):
	return render(request, 'pages/home.html')

@login_required
def newgame(request):
    if request.method == 'POST':
        if len(request.POST.get('friendlyname')) > 0 and len(request.POST.get('friendlyname')) <= 24:
            if datetime.strptime(request.POST.get('end'), '%Y-%m-%d') > datetime.today():
                if Games.objects.filter(creator=request.user.username).count() < 10:
                    game = Games(creator=CustomUser.objects.get(username=request.user.username), friendlyname=request.POST.get('friendlyname'), startdate=datetime.now().strftime('%d.%m.%Y'), enddate=request.POST.get('end'),)
                    game.save()
                    return redirect('allgames')
                else:
                    messages.error(request, 'Количество ваших игр достигло максимума, удалите игру, чтобы создать новую.')
            else:
                messages.error(request, 'Дата  окончания должна быть хотя бы на 1 день позже даты начала.')
        else:
                messages.error(request, 'Название игры слишком длинное')
    return render(request, 'pages/newgame.html', {'today':(datetime.today()+timedelta(days=1)).strftime('%Y-%m-%d')})

@login_required
def joingame(request):
    if request.method == 'POST':
        try:
            Games.objects.get(id=uuid.UUID(request.POST.get('gameid')))
        except Exception as e:
            if e == Games.DoesNotExist:
                messages.error(request, 'Игры не существует')
            elif e == ValueError:
                messages.error(request, 'Неправильный uuid')
            return redirect('joingame')
        return redirect('allgames/'+request.POST.get('gameid'))
    return render(request, 'pages/joingame.html')

@login_required
def allgames(request):
    games_id = []
    games_list = []
    games = Games.objects.filter(creator=CustomUser.objects.get(username=request.user.username))
    i = 1
    for game in games:
        games_id.append(game.id)
        games_list.append((i, game.id, game.friendlyname, game.creator, datetime.strptime(str(Games.objects.get(id=uuid.UUID(str(game.id))).enddate), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')))
        i += 1
    answers = Answers.objects.filter(user=CustomUser.objects.get(username=request.user.username))
    for answer in answers:
        if answer.gameid.id not in games_id:
            game = Games.objects.get(id=answer.gameid.id)
            games_list.append((i, game.id, game.friendlyname, game.creator, datetime.strptime(str(Games.objects.get(id=uuid.UUID(str(game.id))).enddate), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')))
            i += 1
    return render(request, 'pages/allgames.html', {'games':games_list})

@login_required
def game(request, game_code):
    try:
        game = Games.objects.get(id=uuid.UUID(game_code))
        if datetime.today() <= datetime.strptime(str(game.enddate), '%Y-%m-%d'):
            if request.method == 'POST':
                answer = float(request.POST.get('answer'))
                if answer == int(answer):
                    if answer > 0:
                        if Answers.objects.filter(gameid=game_code, user=request.user.username).count() == 0:
                            newanswer = Answers.objects.create(gameid=Games.objects.get(id=uuid.UUID(game_code)), answer=answer, user=CustomUser.objects.get(username=request.user.username))
                            newanswer.save()
                        else:
                            newanswer = Answers.objects.get(gameid=game_code, user=request.user.username)
                            newanswer.answer = answer
                            newanswer.save()
                    else:
                        messages.error(request, 'Число должно быть неотрицательным.')
                else:
                    messages.error(request, 'Число должно быть целым.')
        else:
            messages.success(request, 'Игра окончена!')
            answers = Answers.objects.filter(gameid=Games.objects.get(id=uuid.UUID(game_code))).order_by('answer')
            allanswers = []
            winner = {}
            for answer in answers:
                allanswers.append(answer.answer)
            for answer in reversed(allanswers):
                try:
                    answer = Answers.objects.get(gameid=Games.objects.get(id=uuid.UUID(game_code)), answer=answer)
                    winner['answer'] = answer.answer
                    winner['winner'] = answer.user
                except Exception:
                    winner['answer'] = ''
                    winner['winner'] = ''
            try:
                answer = Answers.objects.get(gameid=Games.objects.get(id=uuid.UUID(game_code)), user=CustomUser.objects.get(username=request.user.username)).answer
            except Exception:
                answer = ''
            
            if str(Games.objects.get(id=uuid.UUID(game_code)).creator) == request.user.username:
                text = 'Удалить игру'
            else:
                text = 'Выйти из игры'
                
            gamename = str(Games.objects.get(id=uuid.UUID(game_code)).friendlyname)
            return render(request, 'pages/game.html', {'answer': answer, 
                                                       'gamecode':game_code, 
                                                       'text':text, 
                                                       'gamename':gamename, 
                                                       'ended':True, 
                                                       'winner':winner})
    except Games.DoesNotExist:
        messages.error(request, 'Игра не найдена')
        return redirect('allgames')
    try:
        answer = Answers.objects.get(gameid=game_code, user=request.user.username).answer
    except Answers.DoesNotExist:
        answer = -1
    
    if str(Games.objects.get(id=uuid.UUID(game_code)).creator) == request.user.username:
        end = True
        text = 'Удалить игру'   
    else:
        end = False
        text = 'Выйти из игры'
    gamename = str(Games.objects.get(id=uuid.UUID(game_code)).friendlyname)
    return render(request, 'pages/game.html', {'answer': answer, 'enddate':datetime.strptime(str(Games.objects.get(id=uuid.UUID(game_code)).enddate), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'), 'gamecode':game_code, 'text':text, 'end':end, 'gamename':gamename, 'ended':False})

@login_required
def endgame(request, game_code):
    print(game_code)
    game = Games.objects.get(id=uuid.UUID(game_code))
    if str(game.creator) == request.user.username:
        game.enddate = game.startdate
        game.save()
    else:
        messages.error(request, 'Вы не созадатель игры')
    return redirect('/allgames/'+game_code)

@login_required
def deletegame(request, game_code):
    try:
        game = Games.objects.get(id=uuid.UUID(game_code))
        print(str(game.creator), request.user.username)
        if str(game.creator) == request.user.username:
            game.delete()
        elif Answers.objects.filter(gameid=Games.objects.get(id=uuid.UUID(game_code)), user=CustomUser.objects.get(username=request.user.username)).count() > 0:
            Answers.objects.get(gameid=Games.objects.get(id=uuid.UUID(game_code)), user=CustomUser.objects.get(username=request.user.username)).delete()
        else:
            messages.error(request, 'Вы не можете удалить эту игру.')
    except Games.DoesNotExist:
        messages.error(request, 'Игры не существует.')
    return redirect('allgames')