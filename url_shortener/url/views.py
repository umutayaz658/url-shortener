from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import check_password, make_password
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.utils.timezone import make_aware
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from .models import CustomURL
from django import forms
from rest_framework import viewsets
import string
import random
from .models import CustomURL
from rest_framework import generics
from .serializers import URLSerializer


def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class URLListView(ListView):
    model = CustomURL
    template_name = 'url/user_urls.html'
    context_object_name = 'urls'

    def get_queryset(self):
        return CustomURL.objects.filter(created_by=self.request.user)


class URLCreateView(CreateView):
    model = CustomURL
    fields = ["long_url", "validity_period", "password", "one_time_only"]
    template_name = 'url/home.html'
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        long_url = form.cleaned_data['long_url']
        validity_period = form.cleaned_data['validity_period']
        password = form.cleaned_data.get('password', None)
        one_time_only = form.cleaned_data.get('one_time_only', False)
        existing_url = CustomURL.objects.filter(long_url=long_url).first()
        form.instance.short_url = generate_short_url()
        form.instance.validity_period = validity_period
        form.instance.one_time_only = one_time_only
        form.instance.created_by = self.request.user
        if password:
            form.instance.password = password
        self.request.session['short_url'] = form.instance.short_url
        self.request.session['long_url'] = form.instance.long_url
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['short_url'] = self.request.session.get('short_url', '')
        context['long_url'] = self.request.session.get('long_url', '')
        return context


def redirect_to_long_url(request, short_url):
    custom_url = get_object_or_404(CustomURL, short_url=short_url)
    if custom_url.is_expired or not custom_url.is_active:
        return redirect('link_expired')
    if custom_url.password:
        if request.method == 'POST':
            entered_password = request.POST.get('password', '')
            if check_password(entered_password, custom_url.password):
                if custom_url.one_time_only:
                    custom_url.is_active = False
                    custom_url.save()
                return redirect(custom_url.long_url)
            else:
                return render(request, 'url/security.html', context={"msg": "Invalid Password", "short_url": short_url})
        return render(request, 'url/security.html', context={"msg": "", "short_url": short_url})
    if custom_url.one_time_only:
        custom_url.is_active = False
        custom_url.save()
    return redirect(custom_url.long_url)


def link_expired(request):
    return render(request, 'url/expired.html')


def deactivate_url(request, short_url):
    url = get_object_or_404(CustomURL, short_url=short_url)
    url.is_active = False
    url.save()
    return redirect('user_urls')


def extend_url_validity(request, short_url):
    if request.method == 'POST':
        url = get_object_or_404(CustomURL, short_url=short_url)
        new_validity_date = request.POST.get('new_validity_date')
        if new_validity_date:
            try:
                new_validity = datetime.strptime(new_validity_date, '%Y-%m-%d %H:%M')
                new_validity = make_aware(new_validity, timezone.get_current_timezone())
                if new_validity > timezone.now():
                    url.validity_period = new_validity
                    url.save()
                else:
                    pass
            except ValueError:
                pass
    return redirect('user_urls')


def delete_url(request, short_url):
    url = get_object_or_404(CustomURL, short_url=short_url)
    url.is_deleted = True
    url.save()
    return redirect('user_urls')


class URLListCreateView(generics.ListCreateAPIView):
    queryset = CustomURL.objects.all()
    serializer_class = URLSerializer


class URLDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomURL.objects.all()
    serializer_class = URLSerializer
