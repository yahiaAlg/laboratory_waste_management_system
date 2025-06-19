from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserLoginForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
        
    form = UserLoginForm()
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
    
    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('authentication:login')

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('authentication:login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Compte créé avec succès. Vous pouvez maintenant vous connecter.')
        return super().form_valid(form)

@login_required
def profile_view(request):
    return render(request, 'authentication/profile.html')