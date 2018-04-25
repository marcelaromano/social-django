from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, Choice, get_access_token, save_and_print_posts, get_posts_from_fanpage, Comment, FanPage, \
    Palabra, ExtractorPalabras, Website
from .forms import ResearcherForm


def index(request):
    return HttpResponse("Hola, mundo.")


def contact(request):
    return HttpResponse("<h1>Contactanos.</h1><p>Ahora.</p>")


def about(request):
    return render(request, 'about.html')


def results(request):
    questions = Question.objects.all()
    context = {
        'template_questions': questions
    }
    return render(request, 'results.html', context)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('results', args=()))


def facebook_fanpage(request, page_id):
    Comment.objects.filter(post__fanpage__page_id=page_id).delete()

    access_token = get_access_token()
    posts_json = get_posts_from_fanpage(page_id, access_token)
    save_and_print_posts(page_id, posts_json, access_token)

    # obtener todos los posts de la base de datos, e incluirlos en el contexto del template a renderizar
    comments = Comment.objects.all()
    context = {
        'comments': comments
    }
    return render(request, 'facebook/listar_posts.html', context)


def saludo(request):
    context = {
        'name': 'Juan',
        'es_manana': False,
        'amigos': ['Pedro', 'Lorena', 'Pepe', 'Romina']
    }
    return render(request, 'saludo.html', context)


def researcher(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ResearcherForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required

            # 1. Obtengo la URL que el usuario ingreso en el formulario
            url = form.cleaned_data['url']

            # 2. Creo un objeto extractor y le digo que extraiga de la URL
            extractor_palabras = ExtractorPalabras()
            website = extractor_palabras.extraer(url)

            # 3. Redirect a pagina de resultados
            return HttpResponseRedirect('/researcher/results/{}/'.format(website.id))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ResearcherForm()

    return render(request, 'researcher.html', {'form': form})


def researcher_results(request):
    palabras = Palabra.objects.filter(ocurrencias__gt=1).order_by('-ocurrencias')
    context = {
        'palabras': palabras
    }
    return render(request, 'researcher-results.html', context)


def researcher_results_by_website(request, website_id):
    palabras = Palabra.objects.filter(oracion__website__id=website_id, ocurrencias__gt=1).order_by('-ocurrencias')
    context = {
        'palabras': palabras
    }
    return render(request, 'researcher-results.html', context)
