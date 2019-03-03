from django.shortcuts import render, HttpResponse


def index(request):
    return HttpResponse("Hello everybody! This is a place for people to live!")