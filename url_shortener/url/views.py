from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
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
import string
import random


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
    fields = ["long_url", "validity_period"]
    template_name = 'url/home.html'
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        long_url = form.cleaned_data['long_url']
        validity_period = form.cleaned_data['validity_period']
        existing_url = CustomURL.objects.filter(long_url=long_url).first()
        if existing_url:
            existing_url.short_url = generate_short_url()
            existing_url.validity_period = validity_period
            existing_url.save()
            form.instance = existing_url
        else:
            form.instance.validity_period = validity_period
            form.instance.short_url = generate_short_url()
            form.instance.created_by = self.request.user
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
    print(f"URL found: {custom_url.short_url}, Expired: {custom_url.is_expired}")
    if custom_url.is_expired or not custom_url.is_active:
        return redirect('link_expired')
    return redirect(custom_url.long_url)


def link_expired(request):
    return render(request, 'url/expired.html')


def deactivate_url(request, short_url):
    url = get_object_or_404(CustomURL, short_url=short_url)
    print(url)
    url.is_active = False
    url.save()
    return redirect('user_urls')


def extend_url_validity(request, short_url):
    if request.method == 'POST':
        url = get_object_or_404(CustomURL, short_url=short_url)
        new_validity_date = request.POST.get('new_validity_date')
        if new_validity_date:
            try:
                new_validity = datetime.strptime(new_validity_date, '%Y-%m-%d')
                new_validity = make_aware(new_validity)
                if new_validity > timezone.now():
                    url.validity_period = new_validity
                    url.save()
                else:
                    pass
            except ValueError:
                pass
    return redirect('user_urls')
