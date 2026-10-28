import json
from functools import wraps
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from . import restapis
from .models import CarMake, CarModel


def api_errors(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except (ValueError, KeyError, ValidationError) as error:
            return JsonResponse({'status': 400, 'message': str(error)}, status=400)
        except requests.RequestException:
            return JsonResponse({'status': 502, 'message': 'A backend service is unavailable. Please retry.'}, status=502)
    return wrapped


@csrf_exempt
@require_POST
@api_errors
def login_user(request):
    data = json.loads(request.body)
    user = authenticate(request, username=data.get('userName', data.get('username', '')), password=data.get('password', ''))
    if user is None:
        return JsonResponse({'status': 'Unauthenticated', 'message': 'Invalid username or password'}, status=401)
    login(request, user)
    return JsonResponse({'status': 'Authenticated', 'userName': user.username, 'firstname': user.first_name, 'lastname': user.last_name})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def logout_request(request):
    logout(request)
    return JsonResponse({'status': 200, 'userName': '', 'message': 'Successfully logged out'})


@csrf_exempt
@require_POST
@api_errors
def registration(request):
    data = json.loads(request.body)
    username = data.get('username', '').strip()
    if not username or len(username) > 150 or not data.get('first_name') or not data.get('last_name'):
        raise ValueError('Username, first name and last name are required')
    validate_email(data.get('email', ''))
    validate_password(data.get('password', ''))
    try:
        with transaction.atomic():
            user = User.objects.create_user(username=username, password=data['password'], first_name=data['first_name'], last_name=data['last_name'], email=data['email'])
    except IntegrityError:
        return JsonResponse({'status': 409, 'message': 'Username already exists'}, status=409)
    login(request, user)
    return JsonResponse({'status': 200, 'userName': user.username, 'firstname': user.first_name, 'lastname': user.last_name}, status=201)


@require_GET
def current_user(request):
    return JsonResponse({'userName': request.user.username if request.user.is_authenticated else None})


@require_GET
@api_errors
def get_dealerships(request, state='All'):
    endpoint = 'fetchDealers' if state == 'All' else f'fetchDealers/{requests.utils.quote(state, safe="")}'
    return JsonResponse({'status': 200, 'dealers': restapis.get_request(endpoint)})


@require_GET
@api_errors
def get_dealer_details(request, dealer_id):
    return JsonResponse({'status': 200, 'dealer': restapis.get_request(f'fetchDealer/{dealer_id}')})


@require_GET
@api_errors
def get_dealer_reviews(request, dealer_id):
    reviews = restapis.get_request(f'fetchReviews/dealer/{dealer_id}')
    for review in reviews:
        review['sentiment'] = restapis.analyze_review_sentiments(review['review'])['sentiment']
    return JsonResponse({'status': 200, 'reviews': reviews})


@require_GET
def get_cars(request):
    models = list(CarModel.objects.select_related('car_make').all())
    return JsonResponse({'status': 200, 'CarMakes': list(CarMake.objects.values('id', 'name', 'description')), 'CarModels': [{'id': x.id, 'CarMake': x.car_make.name, 'CarModel': x.name, 'year': x.year, 'type': x.type} for x in models]})


@csrf_exempt
@require_POST
@api_errors
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 401, 'message': 'Please log in before posting a review'}, status=401)
    data = json.loads(request.body)
    if not isinstance(data.get('review'), str) or not data['review'].strip():
        raise ValueError('Review text is required')
    data['dealership'] = int(data['dealership'])
    data['car_year'] = int(data['car_year'])
    if not 2015 <= data['car_year'] <= 2026:
        raise ValueError('Car year must be between 2015 and 2026')
    data['name'] = request.user.get_full_name() or request.user.username
    data['purchase'] = bool(data.get('purchase', False))
    result = restapis.post_review(data)
    return JsonResponse({'status': 200, 'review': result}, status=201)
