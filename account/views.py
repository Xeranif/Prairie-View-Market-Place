from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.text import slugify
#from orders.views import user_orders

from .forms import Registration, UserEditForm, ProductForm
from .models import UserBase
from .tokens import account_activation_token

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if forms.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(product.title)
            product.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'account/user/add_product.html', {'form': form})



@login_required
def dashboard(request):
    return render(request,
                  'account/user/dashboard.html')


@login_required
def edit_details(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    return render(request,
                  'account/user/edit_details.html', {'user_form': user_form})


@login_required
def delete_user(request):
    user = UserBase.objects.get(user_name=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect('account:delete_confirmation')


def acct_reg(request):

    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        registerform = Registration(request.POST)
        if registerform.is_valid():
            user = registerform.save(commit=False)
            user.email = registerform.cleaned_data['email']
            user.set_password(registerform.cleaned_data['password'])
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate your Account'
            message = render_to_string('account/registration/account_activation_email.html', {
                'user': user, 'domain': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(user.pk)), 'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return HttpResponse('registered successfully and activation sent')
    else:
        registerform = Registration()

    return render(request, 'account/registration/register.html', {'form': registerform})


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserBase.objects.get(pk=uid)
    except():
        pass
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('account:dashboard')
    else:
        return render(request, 'account/registration/activation_invalid.html')

