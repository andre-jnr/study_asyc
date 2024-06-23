from django.shortcuts import render, redirect
from .models import Categoria, Flashcard
from django.contrib.messages import constants
from django.contrib import messages


def novo_flashcard(request):

    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    match request.method:
        case 'GET':
            categorias = Categoria.objects.all()
            dificuldades = Flashcard.DIFICULDADE_CHOICES
            return render(request, 'novo_flashcard.html', {'categorias': categorias, 'dificuldades': dificuldades},)
        case 'POST':
            pergunta = request.POST.get('pergunta')
            resposta = request.POST.get('resposta')
            categoria = request.POST.get('categoria')
            dificuldade = request.POST.get('dificuldade')

            if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
                messages.add_message(
                    request, constants.ERROR,
                    'Preenchar os campos de pergunta e resposta')
                return redirect('/flashcard/novo_flashcard/')

            flashcard = Flashcard(
                user=request.user,
                pergunta=pergunta,
                resposta=resposta,
                categoria_id=categoria,
                dificuldade=dificuldade
            )

            flashcard.save()

            messages.add_message(
                request, constants.SUCCESS,
                'Flashcard cadastrado com sucesso')
            return redirect('/flashcard/novo_flashcard')
