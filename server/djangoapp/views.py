import json
from datetime import date
from functools import wraps
from urllib.parse import quote
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from .models import CarModel
from . import restapis

def api_errors(fn):
    @wraps(fn)
    def wrapped(request, *args, **kwargs):
        try:
            return fn(request, *args, **kwargs)
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            return JsonResponse({'error':'Please provide valid values for every required field.'}, status=400)
        except requests.RequestException:
            return JsonResponse({'error':'A service is temporarily unavailable. Please try again.'}, status=503)
    return wrapped

@require_GET
@ensure_csrf_cookie
def session(request):
    return JsonResponse({'userName': request.user.username if request.user.is_authenticated else None})

@require_POST
@api_errors
def login_user(request):
    data=json.loads(request.body)
    user=authenticate(request, username=data['userName'], password=data['password'])
    if user is None:
        return JsonResponse({'error':'Incorrect username or password.'}, status=401)
    login(request,user)
    return JsonResponse({'userName':user.username, 'status':'Authenticated'})

@require_POST
def logout_user(request):
    logout(request)
    return JsonResponse({'status':'Logged out'})

@require_POST
@api_errors
def registration(request):
    data=json.loads(request.body)
    username=data['userName'].strip()
    if not username or len(username)>150:
        raise ValueError()
    user=User(username=username, email=data.get('email','').strip(), first_name=data.get('firstName','')[:150], last_name=data.get('lastName','')[:150])
    try:
        user.full_clean(exclude=['password'])
        validate_password(data['password'],user)
    except ValidationError as exc:
        return JsonResponse({'error':' '.join(exc.messages)},status=400)
    user.set_password(data['password'])
    try:
        user.save()
    except IntegrityError:
        return JsonResponse({'error':'This username is already in use.'},status=409)
    login(request,user)
    return JsonResponse({'userName':user.username},status=201)

@require_GET
@api_errors
def dealers(request):
    state=request.GET.get('state','')
    endpoint='fetchDealers' + ('/'+quote(state, safe='') if state else '')
    return JsonResponse({'dealers':restapis.get_request(endpoint)})

@require_GET
@api_errors
def dealer(request,dealer_id):
    result=restapis.get_request(f'fetchDealer/{dealer_id}')
    return JsonResponse({'dealer':result})

@require_GET
@api_errors
def reviews(request,dealer_id):
    rows=restapis.get_request(f'fetchReviews/dealer/{dealer_id}')
    for row in rows:
        row['sentiment']=restapis.analyze_review_sentiments(row['review'])
    return JsonResponse({'reviews':rows})

@require_GET
def cars(request):
    return JsonResponse({'cars':list(CarModel.objects.values('id','name','year','type','car_make__name'))})

@require_POST
@api_errors
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error':'Please sign in to post a review.'},status=401)
    data=json.loads(request.body)
    text=data['review'].strip()
    if not 3<=len(text)<=4000:
        return JsonResponse({'error':'Reviews must contain 3–4000 characters.'},status=400)
    dealer_id=int(data['dealership'])
    if not restapis.get_request(f'fetchDealer/{dealer_id}'):
        return JsonResponse({'error':'Dealer not found.'},status=404)
    car=CarModel.objects.get(pk=int(data['car_id'])) if CarModel.objects.filter(pk=int(data['car_id'])).exists() else None
    if car is None:
        return JsonResponse({'error':'Select a valid car.'},status=400)
    purchased=data.get('purchase') is True
    purchase_date=data.get('purchase_date','')
    if purchased and (not purchase_date or date.fromisoformat(purchase_date)>date.today()):
        return JsonResponse({'error':'Choose a valid purchase date.'},status=400)
    payload={'name':request.user.get_full_name() or request.user.username,'dealership':dealer_id,'review':text,'purchase':purchased,'purchase_date':purchase_date if purchased else 'Not purchased','car_make':car.car_make.name,'car_model':car.name,'car_year':car.year}
    return JsonResponse({'review':restapis.post_review(payload)},status=201)
