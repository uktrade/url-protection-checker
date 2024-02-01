import requests

from django.shortcuts import render, redirect
from django.views import View


class home_page(View):
    template_name = 'home-page.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
