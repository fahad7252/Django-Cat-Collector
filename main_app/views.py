import requests
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from main_app.models import Cat, Toy
from .forms import FeedingForm

# Create your views here.

class Home(LoginView):
  template_name = 'home.html'

def about(request):
  response = requests.get('https://catfact.ninja/fact')
  return render(request, 'about.html', {'fact': response.json().get('fact')})

@login_required
def cat_index(request):
  cats = Cat.objects.filter(user=request.user)
  return render(request, 'cats/index.html', { 'cats': cats })

@login_required
def cat_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  # Obtain toys that the cat does not have...
  # Get a list of toy ids that the cat Does have
  toy_ids_cat_has = cat.toys.all().values_list('id')
  # Query for toys that have ids that are NOT in the above list
  toys = Toy.objects.exclude(id__in=toy_ids_cat_has)
  # toys = Toy.objects.all()
  feeding_form = FeedingForm()
  return render(request, 'cats/detail.html', {
     'cat': cat,
     'toys': toys,
     'feeding_form': feeding_form
  })

class CatCreate(CreateView, LoginRequiredMixin):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']
  # success_url = '/cats/{id}'

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CatUpdate(UpdateView, LoginRequiredMixin):
  model = Cat
  fields = ['breed', 'description', 'age']

class CatDelete(DeleteView, LoginRequiredMixin):
  model = Cat
  success_url = '/cats/'

@login_required
def add_feeding(request, cat_id):
  # request.POST contains the input info
  # submitted in the <form>
  form = FeedingForm(request.POST)
  if form.is_valid():
    new_feeding = form.save(commit=False)
    new_feeding.cat_id = cat_id
    new_feeding.save()
  return redirect('cat-detail', cat_id=cat_id)

class ToyCreate(CreateView, LoginRequiredMixin):
  model = Toy
  fields = '__all__'

class ToyList(ListView, LoginRequiredMixin):
  model = Toy

class ToyDetail(DetailView, LoginRequiredMixin):
  model = Toy

class ToyUpdate(UpdateView, LoginRequiredMixin):
  model = Toy
  fields = ['name', 'color']

class ToyDelete(DeleteView, LoginRequiredMixin):
  model = Toy
  success_url = '/toys/'

@login_required
def associate_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.add(toy_id)
  return redirect('cat-detail', cat_id=cat_id)

@login_required
def remove_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.remove(toy_id)
  return redirect('cat-detail', cat_id=cat_id)

def signup(request):
  error_message = '&nbsp;'
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('cat-index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'signup.html', context)