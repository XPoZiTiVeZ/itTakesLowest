from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Games, Answers
from login.models import CustomUser
from datetime import datetime, timedelta
from random import choice


def gencode(length=6):
	letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890123456789"
	code = ''.join(choice(letters) for _ in range(length))
	while True:
		try:
			Games.objects.get(id = code)
			letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890123456789"
			code = ''.join(choice(letters) for _ in range(length))
		except Exception as e:
			break
	return code

def home(request):
	return render(request, 'pages/home.html')

@login_required(login_url='login')
def newgame(request):
	if request.method == 'POST':
		if len(request.POST.get('friendlyname')) > 0 and len(request.POST.get('friendlyname')) <= 24:
			if datetime.strptime(request.POST.get('end'), '%Y-%m-%dT%H:%M') > datetime.now():
				if Games.objects.filter(creator=request.user.username).count() < 10:
					code = gencode()
					Games.objects.create(id = code,
											creator = CustomUser.objects.get(username=request.user.username), 
											friendlyname = request.POST.get('friendlyname'),
											start = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M'),
											end = datetime.strptime(request.POST.get('end'), '%Y-%m-%dT%H:%M'))
					return redirect('allgames')
				else:
					messages.error(request, 'Количество ваших игр достигло максимума, удалите игру, чтобы создать новую.')
			else:
				messages.error(request, 'Дата  окончания должна быть хотя бы на 1 день позже даты начала.')
		else:
				messages.error(request, 'Название игры слишком длинное')
	return render(request, 'pages/newgame.html', {'today':(datetime.now()+timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')})

@login_required(login_url='login')
def joingame(request):
	if request.method == 'POST':
		if len(request.POST.get('gameid')) > 6:
			messages.error(request, 'Код игры состоит из 6 символов')
			return render(request, 'pages/joingame.html')
		for letter in request.POST.get('gameid'):
			if letter not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
				messages.error(request, 'В коде присутствуют недопустимые символы')
				return render(request, 'pages/joingame.html')
		try:
			Games.objects.get(id=request.POST.get('gameid'))
		except Games.DoesNotExist as e:
			messages.error(request, 'Игры не существует')
			return redirect('joingame')
		return redirect('allgames/'+request.POST.get('gameid'))
	return render(request, 'pages/joingame.html')

@login_required(login_url='login')
def allgames(request):
	games_id = []
	games_list = []
	games = Games.objects.filter(creator=CustomUser.objects.get(username=request.user.username))
	i = 1
	for game in games:
		games_id.append(game.id)
		games_list.append((i, game.id, game.friendlyname, game.creator, str(Games.objects.get(id=str(game.id)).end)))
		i += 1
	answers = Answers.objects.filter(user=CustomUser.objects.get(username=request.user.username))
	for answer in answers:
		if answer.gameid.id not in games_id:
			game = Games.objects.get(id=answer.gameid.id)
			games_list.append((i, game.id, game.friendlyname, game.creator, datetime.strptime(str(Games.objects.get(id=game.id).end), '%Y-%m-%d %H:%M:%S+00:00').strftime('%Y-%m-%d %H:%M:%S')))
			i += 1
	return render(request, 'pages/allgames.html', {'games':games_list})

@login_required(login_url='login')
def game(request, game_code):
	try:
		game = Games.objects.get(id=game_code)
		if datetime.now() < datetime.strptime(str(game.end), '%Y-%m-%d %H:%M:%S+00:00'):
			if request.method == 'POST':
				answer = float(request.POST.get('answer'))
				if answer == int(answer):
					if answer > 0:
						if Answers.objects.filter(gameid=game_code, user=request.user.username).count() == 0:
							newanswer = Answers.objects.create(gameid=Games.objects.get(id=game_code), answer=answer, user=CustomUser.objects.get(username=request.user.username))
							newanswer.save()
						else:
							newanswer = Answers.objects.get(gameid=game_code, user=request.user.username)
							newanswer.answer = answer
							newanswer.save()
						messages.success(request, 'Ответ зачтён')
					else:
						messages.error(request, 'Число должно быть неотрицательным.')
				else:
					messages.error(request, 'Число должно быть целым.')
		else:
			messages.success(request, 'Игра окончена!')
			answers = Answers.objects.filter(gameid=Games.objects.get(id=game_code)).order_by('answer')
			allanswers = []
			winner = {'answer': '',
						'winner':''}
			for answer in answers:
				allanswers.append(answer.answer)
			for answer in reversed(allanswers):
				try:
					answer = Answers.objects.get(gameid=Games.objects.get(id=game_code), answer=answer)
					winner['answer'] = answer.answer
					winner['winner'] = answer.user
				except Exception:
					winner['answer'] = ''
					winner['winner'] = ''

			if winner['winner'] != '' and Answers.objects.filter(gameid=Games.objects.get(id=game_code)).count() > 1 and not Games.objects.get(id=game_code).ended:
				user = CustomUser.objects.get(username = winner['winner'])
				user.wins += 1
				user.save()
				game = Games.objects.get(id=game_code)
				game.ended = 1
				game.save()
			try:
				answer = Answers.objects.get(gameid=Games.objects.get(id=game_code), user=CustomUser.objects.get(username=request.user.username)).answer
			except Exception:
				answer = ''
			
			if str(Games.objects.get(id=game_code).creator) == request.user.username:
				text = 'Удалить игру'
			else:
				text = 'Выйти из игры'
				
			game = Games.objects.get(id=game_code)
			return render(request, 'pages/game.html', {'answer': answer, 
													   'gamecode':game_code, 
													   'text':text, 
													   'gamename':game.friendlyname, 
													   'ended':True, 
													   'winner':winner})
	except Games.DoesNotExist:
		messages.error(request, 'Игра не найдена')
		return redirect('allgames')
	try:
		answer = Answers.objects.get(gameid=game_code, user=request.user.username).answer
	except Answers.DoesNotExist:
		answer = -1
	
	if str(game.creator) == request.user.username:
		creator = True
		text = 'Удалить игру'   
	else:
		creator = False
		text = 'Выйти из игры'
	gamename = str(Games.objects.get(id=game_code).friendlyname)
	return render(request, 'pages/game.html', {'answer': answer, 'end':datetime.strptime(str(Games.objects.get(id=game_code).end), '%Y-%m-%d %H:%M:%S+00:00').strftime('%Y-%m-%d %H:%M:%S'), 'gamecode':game_code, 'text':text, 'creator':creator, 'gamename':gamename, 'ended':False})

@login_required(login_url='login')
def endgame(request, game_code):
	print(game_code)
	game = Games.objects.get(id=game_code)
	if str(game.creator) == request.user.username:
		game.end = game.start
		game.save()
	else:
		messages.error(request, 'Вы не созадатель игры')
	return redirect('/allgames/'+game_code)

@login_required(login_url='login')
def deletegame(request, game_code):
	try:
		game = Games.objects.get(id=game_code)
		print(str(game.creator), request.user.username)
		if str(game.creator) == request.user.username:
			game.delete()
		elif Answers.objects.filter(gameid=Games.objects.get(id=game_code), user=CustomUser.objects.get(username=request.user.username)).count() > 0:
			Answers.objects.get(gameid=Games.objects.get(id=game_code), user=CustomUser.objects.get(username=request.user.username)).delete()
		else:
			messages.error(request, 'Вы не можете удалить эту игру.')
	except Games.DoesNotExist:
		messages.error(request, 'Игры не существует.')
	return redirect('allgames')