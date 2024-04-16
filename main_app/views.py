from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Travel, Checklist
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .forms import CheckingForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.dateparse import parse_datetime
import os, requests, json, datetime, random
from django.conf import settings
from decouple import config

# Create your views here.

class TravelCreate(LoginRequiredMixin, CreateView):
    model = Travel
    fields = ['name', 'country', 'city', 'description', 'image']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class TravelUpdate(LoginRequiredMixin, UpdateView):
    model = Travel
    fields = ['name', 'country', 'city', 'description', 'image']


class TravelDelete(LoginRequiredMixin, DeleteView):
    model = Travel
    success_url = '/travels/'


def home(request):
    os.getenv('NAME')
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def travels_index(request):
    travels = Travel.objects.filter(user = request.user)
    return render(request, 'travels/index.html', {'travels': travels})

def get_weather(city_name):
    try:
        # Make an API request to AccuWeather
        api_key = config('ACCUWEATHER_API')
        url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={api_key}&q={city_name}'
        response = requests.get(url)
        data = response.json()
        print(data)
        location_key = data[0]['Key']
        print(location_key)
        url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={api_key}&details=false&metric=true'
        response = requests.get(url)
        data = response.json()
        # Extract relevant weather info (e.g., daily forecasts)
        daily_forecasts = data['DailyForecasts']
        # Process the data as needed

        return daily_forecasts

    except Exception as e:
        print(e)
        return {"api_error":True}

@login_required
def travels_detail(request, travel_id):
    checking_form = CheckingForm
    travel = Travel.objects.get(id=travel_id)
    daily_forecasts = get_weather(travel.city)
    if "api_error" not in daily_forecasts:
        print(json.dumps(daily_forecasts))
        weather_data = []
        for day in daily_forecasts:
            # Convert ISO date to DDMMYYYY format
            iso_date = day["Date"]
            parsed_date = datetime.datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S%z")
            formatted_date = parsed_date.strftime("%d/%m/%Y")

            # Create the weather data dictionary
            data = {
                "date": formatted_date,
                "min_temperature": day["Temperature"]["Minimum"]["Value"],
                "max_temperature": day["Temperature"]["Maximum"]["Value"],
                "unit": day["Temperature"]["Minimum"]["Unit"],
                "day_icon": day["Day"]["Icon"],
                "night_icon": day["Night"]["Icon"]
            }
            weather_data.append(data)


    else: 

        weather_data = []

    checklists_travel_for_planning = Checklist.objects.filter(user = request.user).exclude(id__in = travel.checklists.all().values_list('id'))
    return render(request, 'travels/details.html', {'travel': travel, 
    'title': "Travels Details Page", 'checking_form': checking_form, 
    'checklists': checklists_travel_for_planning, 'weather_data':weather_data})

@login_required
def add_checking(request, travel_id):
    form = CheckingForm(request.POST)

    if form.is_valid():
        new_checking = form.save(commit=False)
        new_checking.travel_id = travel_id
        new_checking.save()
        return redirect('detail', travel_id = travel_id)

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CheckingFormSerializer

class AddCheckingAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, travel_id):
        serializer = CheckingFormSerializer(data=request.data)
        if serializer.is_valid():
            new_checking = serializer.save()  # Associate with travel
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Log validation errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCityAPI(APIView):
    permission_classes = [IsAuthenticated]
    # http_method_names = ["POST"]

    def post(self, request):
        print(request.data)
        anywhere = request.data.get("anywhere", True)
        country = request.data.get("country", None)

        print(anywhere,country)

        if anywhere==True or anywhere=="True":
            # Read countrylist.json
            with open(settings.STATIC_ROOT+"\json\countrylist.json", "r") as file:
                country_data = json.load(file)
            
            # Choose a random country key
            random_country = random.choice(list(country_data.keys()))
            # Choose a random city from the list associated with the chosen country
            random_city = random.choice(country_data[random_country])

            return Response({"status":200,"country":random_country,"city": random_city})

        else:
            # Read countrylist2.json
            with open(settings.STATIC_ROOT+"\json\countrylist2.json", "r") as file:
                country_data = json.load(file)
            
            if country in country_data:
                # Choose a random city from the list associated with the specified country
                random_city = random.choice(country_data[country])
                return Response({"status":200,"country":country,"city": random_city})
            else:
                return Response({"status":400,"error": "Country didn't match"})


class ChecklistDetail(LoginRequiredMixin, DetailView):
    model = Checklist

class ChecklistCreate(LoginRequiredMixin, CreateView):
    model = Checklist
    fields = ['name', 'description']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ChecklistUpdate(LoginRequiredMixin, UpdateView):
    model = Checklist
    fields = ['name', 'description']

class ChecklistDelete(LoginRequiredMixin, DeleteView):
    model = Checklist
    success_url = '/checklists/'

@login_required
def checklists_index(request):
    checklists_list = Checklist.objects.filter(user = request.user)
    return render(request, 'main_app/checklist_list.html', {'checklists_list': checklists_list})

@login_required
def assoc_checklist(request, travel_id, checklist_id):
    Travel.objects.filter(user = request.user)
    Travel.objects.get(id=travel_id).checklists.add(checklist_id)
    return redirect('detail', travel_id = travel_id)

@login_required
def unassoc_checklist(request, travel_id, checklist_id):
    Travel.objects.filter(user = request.user)
    Travel.objects.get(id=travel_id).checklists.remove(checklist_id)
    return redirect('detail', travel_id = travel_id)


def signup(request):
    error_message = ''

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid signup, please check your password validation and try again.'

    form = UserCreationForm()
    ctx = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', ctx)