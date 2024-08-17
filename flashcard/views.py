from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.contrib.messages import constants
from django.contrib import messages
from django.http import HttpResponse


def novo_flashcard(request):

    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    match request.method:
        case 'GET':
            categorias = Categoria.objects.all()
            dificuldades = Flashcard.DIFICULDADE_CHOICES
            flashcards = Flashcard.objects.filter(user=request.user)

            categoria_filtrada = request.GET.get('categoria')
            dificuldade_filtrada = request.GET.get('dificuldade')

            if categoria_filtrada:
                flashcards = flashcards.filter(
                    categoria__id=categoria_filtrada)

            if dificuldade_filtrada:
                flashcards = flashcards.filter(
                    dificuldade=dificuldade_filtrada)

            return render(request, 'novo_flashcard.html', {'categorias': categorias,
                                                           'dificuldades': dificuldades,
                                                           'flashcards': flashcards})
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


def deletar_flashcard(request, id):
    # Fazer a validação de segurança
    # dica: request.user
    flashcard = Flashcard.objects.get(id=id)
    flashcard.delete()
    messages.add_message(
        request, constants.SUCCESS,
        'Flashcard excluído com sucesso')
    return redirect('/flashcard/novo_flashcard')


def iniciar_desafio(request):
    match request.method:
        case 'GET':
            categorias = Categoria.objects.all()
            dificuldades = Flashcard.DIFICULDADE_CHOICES
            return render(request, 'iniciar_desafio.html', {'categorias': categorias, 'dificuldades': dificuldades})

        case 'POST':
            titulo = request.POST.get('titulo')
            categorias = request.POST.getlist('categoria')
            dificuldade = request.POST.get('dificuldade')
            qtd_perguntas = request.POST.get('qtd_perguntas')

            desafio = Desafio(
                user=request.user,
                titulo=titulo,
                quantidade_perguntas=qtd_perguntas,
                dificuldade=dificuldade
            )

            desafio.save()

            desafio.categoria.add(*categorias)

            flashcards = (
                Flashcard.objects.filter(user=request.user)
                .filter(dificuldade=dificuldade)
                .filter(categoria_id__in=categorias)
                .order_by('?')
            )

            if flashcards.count() < qtd_perguntas:
                # TODO: tratar para escolher depois
                return redirect('/flashcard/iniciar_desafio/')

            flashcards = flashcards[: int(qtd_perguntas)]

            for f in flashcards:
                flashcard_desafio = FlashcardDesafio(
                    flashcard=f,
                )
                flashcard_desafio.save()
                desafio.flashcards.add(flashcard_desafio)

            desafio.save()

            return HttpResponse("teste")
