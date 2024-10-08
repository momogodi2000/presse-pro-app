from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordResetView
from .models import CustomUser, AbstractUser
from .forms import CustomUserCreationForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy, reverse
from .forms import RegistrationForm
import yagmail
from .models import Contact
from .forms import *
from django.contrib import messages
from .models import *
from .forms import PressingProfileForm, PhotoForm, VideoForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
import json
from campay.sdk import Client as CamPayClient
from .models import ChatMessage
from .forms import ChatMessageForm
from django.http import FileResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
from .models import PressingProfile, Region, Town, Quarter, Photo, Video
from .forms import PressingProfileForm, PhotoForm, VideoForm, MediaForm
from .models import Geolocation
from .models import Delivery, Invoice, Vehicle



# Authentication view


def home(request):
    return render(request, 'home/home.html')


def services(request):
    return render(request, 'home/services.html')




def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('contact')  # Redirect to the same page after saving
    else:
        form = ContactForm()
    
    return render(request, 'home/contact.html', {'form': form})

def about(request):
    return render(request, 'home/about.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful registration
        print(f"{form.errors}")
        return render(request, 'auth/register.html', {'errors': form.errors})
    else:
        form = RegistrationForm()
        return render(request, 'auth/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
          
            if user.role == 'admin':
                return redirect('admin_panel')  # Adjust this to match your URL pattern name
            elif user.role == 'deliver':
                return redirect('deliver_panel')  
            elif user.role == 'pressing_manager':
                return redirect('pressing_manager')  
            else:
                return redirect('clients_panel')  # Adjust this to match your URL pattern name
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = CustomPasswordResetView.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_reset_done')  # Redirect to success page
    else:
        form = CustomPasswordResetView.form_class()

    return render(request, 'auth/forgot_password.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'forgot_password.html'  # Specify your template here
    success_url = reverse_lazy('password_reset_done')  # Redirect after a successful reset request
    email_template_name = 'password_reset_email.html'  # Template for the password reset email



@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')



##  user dashboard

@login_required
def pressing_manager(request):
    return render(request, 'panel/manager/pressing_manager.html')

@login_required
def admin_panel(request):
    # Fetch all PressingProfile instances that are not approved yet
    pending_profiles = PressingProfile.objects.filter(status="pending")
    
    if request.method == 'POST':
        # Handle approval or rejection
        profile_id = request.POST.get('profile_id')
        action = request.POST.get('action')

        profile = get_object_or_404(PressingProfile, id=profile_id)

        if action == 'accepted':
            profile.status = action
            profile.save()
            messages.success(request, f'Pressing profile for {profile.business_name} has been approved.')
        elif action == 'rejected':
            profile.delete()
            messages.success(request, f'Pressing profile for {profile.business_name} has been rejected and deleted.')
        
        yag.send(to=[f"{profile.email}"], subject="Profile status update", contents=f"Hello your pressing has been {action}")
        return redirect('admin_panel')

    context = {
        'pending_profiles': pending_profiles,
    }

    return render(request, 'panel/admin/admin_panel.html', context)



@login_required
def clients_panel(request):
    return render(request, 'panel/clients/dashboard.html')

@login_required
def deliver_panel(request):
    return render(request, 'panel/deliver/deliver_panel.html')




## manager dashbaord

def about_us(request):
    return render(request, 'panel/manager/about/about_us.html')

def setting(request):
    return render(request, 'panel/manager/setting/setting.html')


# Replace with your Gmail credentials
username = "yvangodimomo@gmail.com"
password = "pzls apph esje cgdl"

# Create a yagmail object
yag = yagmail.SMTP(username, password)


@login_required
def customer_feedback(request):
    contacts = Contact.objects.all()

    if request.method == 'POST':
        if 'reply' in request.POST:
            contact_id = request.POST.get('contact_id')
            contact = Contact.objects.get(id=contact_id)
            reply_message = request.POST.get('message')
            yag = yagmail.SMTP('your_email@gmail.com', 'your_email_password')
            yag.send(to=contact.email, subject="Reply to your message", contents=reply_message)
            return redirect('customer_feedback')  # redirect after sending reply
        elif 'delete' in request.POST:
            contact_id = request.POST.get('delete')  # Use 'delete' here as it matches the button name
            Contact.objects.filter(id=contact_id).delete()
            return redirect('customer_feedback')

    return render(request, 'panel/manager/setting/customer_feedback.html', {'contacts': contacts, 'reply_form': ReplyForm()})


# Initialize CamPay client
campay = CamPayClient({
    "app_username": "JByBUneb4BceuEyoMu1nKlmyTgVomd-QfokOrs4t4B9tPJS7hhqUtpuxOx5EQ7zpT0xmYw3P6DU6LU0mH2DvaQ",
    "app_password": "m-Xuj9EQIT_zeQ5hSn8hLjYlyJT7KnSTHABYVp7tKeHKgsVnF0x6PEcdtZCVaDM0BN5mX-eylX0fhrGGMZBrWg",
    "environment": "PROD"  # use "DEV" for demo mode or "PROD" for live mode
})


@login_required
def apply_portfolio(request):
    if request.method == 'POST':
        photos = request.FILES.getlist('photos')
        videos = request.FILES.getlist('videos')
        pressing_count = int(request.POST.get('pressing_count', 1))

        for i in range(1, pressing_count + 1):
            print(f"{request.POST.get(f'region_{i}')}, {request.POST.get(f'town_{i}')}, {request.POST.get(f'quarter_{i}')}")
            region = Region.objects.get(pk=request.POST.get(f'region_{i}'))
            town = Town.objects.get(pk=request.POST.get(f'town_{i}'))
            quarter = Quarter.objects.get(pk=request.POST.get(f'quarter_{i}'))
            print(request.POST)
            profile_request = {
                "business_name": request.POST["business_name"],
                "telephone_number": request.POST["telephone_number"],
                "email": request.POST["email"],
                "services_offered": request.POST["services_offered"],
                "pricing": request.POST["pricing"],
                "about_us": request.POST["about_us"],
                "pressing_count": int(request.POST["pressing_count"]),
                "region" : region.pk,
                "town" : town.pk,
                "quarter" : quarter.pk, 
                "latitude": request.POST["latitude"],  
                "longitude": request.POST["longitude"]  
            }
            profile_files = {
                "photos": request.FILES[f"photos"],
                "videos": request.FILES[f"videos"]
            }
            profile_form = PressingProfileForm(profile_request, profile_files)
            profile = None
            if profile_form.is_valid():
                profile_form.save()
                region = Region.objects.get(pk=request.POST.get(f'region_{i}'))
                town = Town.objects.get(pk=request.POST.get(f'town_{i}'))
                quarter = Quarter.objects.get(pk=request.POST.get(f'quarter_{i}'))
                profile = PressingProfile.objects.get(business_name=profile_request['business_name'])
                profile.user = request.user
                profile.save()
                
                PressingLocation.objects.create(
                    pressing_profile=profile,
                    region=region,
                    town=town,
                    quarter=quarter
                )

                for file in photos:
                    Photo.objects.create(image=file, pressing_profile=profile)
                for file in videos:
                    Video.objects.create(video_file=file, pressing_profile=profile)
            else:
                print(f"Errors: {profile_form.errors}")
                return render(request, 'panel/manager/manage_order/apply_portfolio.html', {"errors": profile_form.errors})
        return render(request, 'panel/manager/manage_order/payment_page.html', {"pressing": profile})
    else:
        profile_form = PressingProfileForm()

        regions = Region.objects.all()
        towns = Town.objects.all()
        quarters = Quarter.objects.all()

        context = {
            'profile_form': profile_form,
            'regions': regions,
            'towns': towns,
            'quarters': quarters,
        }

        return render(request, 'panel/manager/manage_order/apply_portfolio.html', context)


def load_towns(request):
    region_id = request.GET.get('region_id')
    towns = Town.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(towns), safe=False)

def load_quarters(request):
    town_id = request.GET.get('town_id')
    quarters = Quarter.objects.filter(town_id=town_id).values('id', 'name')
    return JsonResponse(list(quarters), safe=False)

@csrf_exempt
@login_required
def payment_page(request):
    pressing_count = request.session.get('pressing_count', 1)
    mobile_number = request.session.get('mobile_number')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_total = pressing_count * 10  # Calculate total based on pressing count
            phone_number = data.get('phoneNumber')
            pressing_id = data.get("pressing_id")
            pressing_profile = PressingProfile.objects.get(pk=pressing_id)
            
            # Process payment with CamPay
            collect = campay.collect({
                "amount": str(cart_total),
                "currency": "XAF",
                "from": "237" + phone_number,
                "description": "Portfolio Payment",
                "external_reference": "",  # Optional: your unique transaction ID
            })

            if collect.get('status') == 'SUCCESSFUL':
                pressing_profile.paid=True
                pressing_profile.save()
                receipt = Receipt.objects.create(total=cart_total)
                payment = Payments.objects.create(user=request.user, motive="Pressing profile creation", status=True, receipt=receipt)
                context = {
                    'total': cart_total,
                    'id': receipt.pk,
                    "reference": collect.get("reference"),
                    "tel": "+237"+phone_number,
                    'business_name': pressing_profile.business_name,
                    'date': timezone.now(),
                }
                html = render_to_string('panel/manager/manage_order/receipt.html', {"receipt": context})
                result = BytesIO()
                
                pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)

                if not pdf.err:
                    receipt_file = ContentFile(result.getvalue())
                    receipt.pdf.save(f'receipt_{receipt.id}.pdf', receipt_file)
                    # response = FileResponse(open(receipt.pdf.path, 'rb'))
                    # file_name = receipt.pdf.name
                    # response['Content-Disposition'] = 'inline; filename=' + file_name
                    # return response
                    return JsonResponse({
                        'success': True,
                        'receiptId': receipt.pk,
                        'receiptUrl': reverse('download_receipt', args=[receipt.pk])
                    })
                return JsonResponse({
                        'success': False,
                        'message': pdf.err
                    })
            else:
                print(f"Error occured ! {collect}")
                payment = Payments.objects.create(user=request.user,motive="Pressing profile creation", receipt=None, status=False)
                return JsonResponse({'success': False, 'message': collect.get('reason', 'Payment failed')}, status=400)

        except Exception as e:
            print(f"Error occured !, exception {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return render(request, 'panel/manager/manage_order/payment_page.html', {
        'pressing_count': pressing_count,
        'mobile_number': mobile_number,
    })

    
@login_required
def generate_receipt(cart_total):
    receipt = Receipt.objects.create(total=cart_total)

    context = {
        'total': cart_total,
        'id': receipt.id,
        'business_name': "Your Business Name",
        'date': timezone.now(),
    }
    html = render_to_string('panel/manager/manage_order/receipt.html', {"receipt":context})
    result = BytesIO()
    
    pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)

    if not pdf.err:
        receipt_file = ContentFile(result.getvalue())
        receipt.pdf.save(f'receipt_{receipt.id}.pdf', receipt_file)
        return receipt.id

    return None

@login_required
def download_receipt(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id)
    html = render_to_string('panel/manager/manage_order/receipt.html', {'receipt': receipt})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response



@login_required
def view_portfolio(request, user_id):
    # Retrieve all PressingProfile objects for the given user_id
    pressing_profiles = PressingProfile.objects.filter(user=request.user)

    if not pressing_profiles.exists():
        return render(request, '404.html')  # Handle case where no profile exists

    context = {
        'pressing_profiles': pressing_profiles,
    }
    return render(request, 'panel/manager/manage_order/view_portfolio.html', context)

@login_required
def track_deliveries(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location_type = request.POST.get('location_type')
        
        # Save geolocation to the database
        Geolocation.objects.create(latitude=latitude, longitude=longitude, location_type=location_type)
        
        return redirect('track_deliveries')
    
    # Get the latest geolocation entry
    latest_geolocation = Geolocation.objects.last()
    
    context = {
        'latitude': latest_geolocation.latitude if latest_geolocation else None,
        'longitude': latest_geolocation.longitude if latest_geolocation else None,
        'location_type': latest_geolocation.get_location_type_display() if latest_geolocation else None,
    }
    return render(request, 'panel/manager/manage_order/track_deliveries.html', context)

def view_deliveries(request):
    deliveries = Delivery.objects.all()
    return render(request, 'panel/manager/manage_order/view_deliveries.html', {'deliveries': deliveries})

def schedule_pickup(request):
    if request.method == 'POST':
        # Logic to schedule a pickup, e.g., save to the database
        pass
    return render(request, 'panel/manager/manage_order/schedule_pickup.html')

def view_invoices(request):
    invoices = Invoice.objects.all()
    return render(request, 'panel/manager/manage_order/view_invoices.html', {'invoices': invoices})

def track_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    return render(request, 'panel/manager/manage_order/track_vehicle.html', {'vehicle': vehicle})

from .models import CustomUser, Contact, PressingProfile, Receipt, ChatMessage
from django.shortcuts import render, redirect, get_object_or_404
from .models import PressingProfile
from .forms import PressingProfileForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PressingProfile, PublicityCampaign
from .social_media_utils import post_to_social_media
from .social_media_utils import post_to_social_media
from .models import Receipt, PressingComments, ServiceBook, Payments
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CustomUser, Rating, DeliveryStats
from django.db.models import Q


@login_required
def chat_view(request):
    user = request.user
    
    # Only allow Deliver or Pressing Manager to access this chat
    if user.role not in ['deliver', 'pressing_manager']:
        return redirect('home')  # Redirect if they don't have permission
    
    # Retrieve messages exchanged between the current user and the other role
    if user.role == 'deliver':
        # Deliver can see messages exchanged with any Pressing Manager
        messages = ChatMessage.objects.filter(
            (Q(sender=user) & Q(receiver__role='pressing_manager')) |
            (Q(receiver=user) & Q(sender__role='pressing_manager'))
        ).order_by('timestamp')
    elif user.role == 'pressing_manager':
        # Pressing Manager can see messages exchanged with any Deliver
        messages = ChatMessage.objects.filter(
            (Q(sender=user) & Q(receiver__role='deliver')) |
            (Q(receiver=user) & Q(sender__role='deliver'))
        ).order_by('timestamp')
    else:
        messages = ChatMessage.objects.none()  # No messages if not authorized

    # Handle POST request for sending messages
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = user
            # Dynamically set the receiver based on the user's role
            if user.role == 'deliver':
                # Deliver sends a message to any Pressing Manager
                message.receiver = CustomUser.objects.filter(role='pressing_manager').first()
            elif user.role == 'pressing_manager':
                # Pressing Manager sends a message to any Deliver
                message.receiver = CustomUser.objects.filter(role='deliver').first()
            message.save()
            return redirect('chat')  # Redirect back to the chat page after sending
    else:
        form = ChatMessageForm()

    # Pass the messages and form to the template
    context = {
        'messages': messages,
        'form': form,
    }
    return render(request, 'panel/manager/chat/chat.html', context)

##admin panel


@login_required
def user_management(request):
    users = CustomUser.objects.all()
    return render(request, 'panel/admin/manage_user/user_management.html', {'users': users})

@login_required
def add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = RegistrationForm()
    return render(request, 'panel/admin/manage_user/user_management.html', {'form': form})

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = RegistrationForm(instance=user)
    return render(request, 'panel/admin/manage_user/edit_user.html', {'form': form})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_management')
    return render(request, 'panel/admin/manage_user/confirm_delete.html', {'user': user})

def about_us_dev(request):
    return render(request, 'panel/admin/about/about_us_dev.html')

@login_required
def marketing_promotions(request):
    if request.method == 'POST':
        pressing_id = request.POST.get('pressing_id')
        pressing = get_object_or_404(PressingProfile, id=pressing_id)
        
        # Handle photo uploads
        photos = request.FILES.getlist('photos')
        for photo in photos:
            photo_instance = Photo.objects.create(image=photo)
            pressing.photos.add(photo_instance)

        # Handle video uploads
        videos = request.FILES.getlist('videos')
        for video in videos:
            video_instance = Video.objects.create(video_file=video)
            pressing.videos.add(video_instance)
        
        # Handle social media links
        if 'facebook' in request.POST:
            pressing.facebook_url = request.POST.get('facebook')
            pressing.instagram_url = request.POST.get('instagram')
            pressing.tiktok_url = request.POST.get('tiktok')
            pressing.youtube_url = request.POST.get('youtube')
            pressing.save()
        
        return redirect('marketing_promotions')

    pressings = PressingProfile.objects.all()
    return render(request, 'panel/admin/marketing/marketing_promotions.html', {'pressings': pressings})

@login_required
def add_pressing(request):
    if request.method == 'POST':
        profile_form = PressingProfileForm(request.POST, request.FILES)
        photo_form = PhotoForm(request.POST, request.FILES)
        video_form = VideoForm(request.POST, request.FILES)

        if profile_form.is_valid() and photo_form.is_valid() and video_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.predefined = True
            # Save photos
            photos = request.FILES.getlist('photos')
            for photo in photos:
                new_photo = Photo(image=photo)
                new_photo.save()
                profile.photos.add(new_photo)

            # Save videos
            videos = request.FILES.getlist('videos')
            for video in videos:
                new_video = Video(video_file=video)
                new_video.save()
                profile.videos.add(new_video)

            profile.save()

            messages.success(request, "Pressing added successfully!")
            return render(request,'panel/admin/platform_management/add_pressing.html',{"success": "Pressing added successfully !"})
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request,'panel/admin/platform_management/add_pressing.html',{"success": profile.errors})
    else:
        profile_form = PressingProfileForm()
        photo_form = PhotoForm()
        video_form = VideoForm()

    return render(request, 'panel/admin/platform_management/add_pressing.html', {
        'profile_form': profile_form,
        'photo_form': photo_form,
        'video_form': video_form,
    })

def predefined_portfolios(request):
    if (request.method == "GET"):
        predefined_list = PressingProfile.objects.filter(predefined=True)
        return render(request, "panel/manager/portfolios/predefined_portfolios.html", {"predefined": predefined_list})

def selected_portfolio(request, id):
    if request.method == "GET":
        portfolio = PressingProfile.objects.get(pk=id)
        return render(request, "panel/manager/portfolios/selected_portfolio.html", {"selected":portfolio})
    
    amount = 10
    tel = request.POST["tel"]
    collect = campay.collect({
                "amount": amount,
                "currency": "XAF",
                "from": "237" + tel,
                "description": "Portfolio Payment",
                "external_reference": "",  # Optional: your unique transaction ID
            })
    if collect.get('status') == 'SUCCESSFUL':
        receipt = Receipt.objects.create(total=amount)
        payment = Payments.objects.create(user=request.user, motive="Portfolio payments", status=True, receipt=receipt)
        context = {
            'total': amount,
            'id': receipt.id,
            'business_name': PressingProfile.objects.get(pk=id).business_name,
            'date': timezone.now(),
        }
        html = render_to_string('panel/manager/manage_order/receipt.html', {"receipt": context})
        result = BytesIO()
        
        pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)

        if not pdf.err:
            receipt_file = ContentFile(result.getvalue())
            receipt.pdf.save(f'receipt_{receipt.id}.pdf', receipt_file)
            response = FileResponse(open(receipt.pdf.path, 'rb'))
            file_name = receipt.pdf.name
            response['Content-Disposition'] = 'inline; filename=' + file_name
            return response
        return render(request, "panel/manager/portfolios/selected_portfolio.html", {"errors": f"An error occured {pdf.err}"})
    else:
        payment = Payments.objects.create(user=request.user, motive="Payment for a portfolio")
        print(f"Error occured ! {collect}")
        return render(request, "panel/manager/portfolios/selected_portfolio.html", {"errors": f"An error occured {collect}"})
    
@login_required
def chat_room(request, room_name):
    room, created = ChatRoom.objects.get_or_create(name=room_name)
    room.participants.add(request.user)
    return render(request, 'panel/admin/chat/chat_room.html', {'room_name': room_name})

@login_required
def send_message(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        content = request.POST.get('content')
        room = get_object_or_404(ChatRoom, name=room_name)
        message = Message.objects.create(room=room, user=request.user, contents=content)
        return JsonResponse({'message': message.content, 'user': message.user.username, 'timestamp': message.timestamp.isoformat()})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_messages(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    messages = room.messages.order_by('-timestamp').values('user__username', 'content', 'timestamp')
    return JsonResponse(list(messages), safe=False)


def analytics_view(request):
    user_count = CustomUser.objects.count()
    contact_count = Contact.objects.count()
    pressing_profile_count = PressingProfile.objects.count()
    receipt_count = Receipt.objects.count()
    chat_message_count = ChatMessage.objects.count()

    context = {
        'user_count': user_count,
        'contact_count': contact_count,
        'pressing_profile_count': pressing_profile_count,
        'receipt_count': receipt_count,
        'chat_message_count': chat_message_count,
    }
    return render(request, 'panel/admin/analytics/analytics.html', context)

def get_pressings(request):
    pressings = PressingProfile.objects.all()
    return render(request, "panel/admin/platform_management/edit_pressing_status.html", {"pressings": pressings})

def edit_pressing_status(request, id, response):
    pressing = get_object_or_404(PressingProfile, pk=id)
    pressing.status = response
    subject = "Pressing creation update"
    message = f"Hello your pressing has been {response}"
    yag.send(to=[f"{pressing.email}"], subject=subject, contents=message)
    pressing.save()
    return render(request, "panel/admin/platform_management/edit_pressing_status.html", {"messages": f"Pressing {response} successfully !"})

def payment_status_view(request):
    if request.method == "GET":
        all_payments = Payments.objects.all()
        payments = []
        for payment in all_payments:
            payment_map = {
                "motive": payment.motive,
                "id": payment.pk,
                "user": CustomUser.objects.get(pk=payment.user.pk).username,
                "role": CustomUser.objects.get(pk=payment.user.pk).role,
                "status": payment.status
            }
            payments.append(payment_map)
        return render(request, "panel/admin/payments/view_payments.html", {"payments":payments})


@login_required
def pending(request):
    # Fetch all PressingProfile instances that are not approved yet
    pending_profiles = PressingProfile.objects.filter(status="pending")
    
    if request.method == 'POST':
        # Handle approval or rejection
        profile_id = request.POST.get('profile_id')
        action = request.POST.get('action')

        profile = get_object_or_404(PressingProfile, id=profile_id)

        if action == 'accepted':
            profile.status = action
            profile.save()
            messages.success(request, f'Pressing profile for {profile.business_name} has been approved.')
        elif action == 'rejected':
            profile.delete()
            messages.success(request, f'Pressing profile for {profile.business_name} has been rejected and deleted.')
        
        yag.send(to=[f"{profile.email}"], subject="Profile status update", contents=f"Hello your pressing has been {action}")
        return redirect('admin_panel')

    context = {
        'pending_profiles': pending_profiles,
    }

    return render(request, 'panel/admin/pending/pending.html', context)



# List all PressingProfiles
def pressing_list(request):
    profiles = PressingProfile.objects.all()
    return render(request, 'panel/admin/pressing/pressing_list.html', {'profiles': profiles})

# Add a new PressingProfile
def pressing_add(request):
    if request.method == 'POST':
        form = PressingProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pressing profile added successfully!')
            return redirect('pressing_list')
    else:
        form = PressingProfileForm()
    return render(request, 'panel/admin/pressing/pressing_form.html', {'form': form})

# Edit an existing PressingProfile
def pressing_edit(request, pk):
    profile = get_object_or_404(PressingProfile, pk=pk)
    if request.method == 'POST':
        form = PressingProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pressing profile updated successfully!')
            return redirect('pressing_list')
    else:
        form = PressingProfileForm(instance=profile)
    return render(request, 'panel/admin/pressing/pressing_form.html', {'form': form, 'edit_mode': True})

# Delete a PressingProfile
def pressing_delete(request, pk):
    profile = get_object_or_404(PressingProfile, pk=pk)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Pressing profile deleted successfully!')
        return redirect('pressing_list')
    return render(request, 'panel/admin/pressing/pressing_confirm_delete.html', {'profile': profile})


@login_required
def manage_publicity(request):
    if request.method == 'POST':
        profile_selection = request.POST.get('profile_selection')
        specific_profile_id = request.POST.get('specific_profile')
        message = request.POST.get('message')
        duration = request.POST.get('duration')
        platforms = request.POST.getlist('platform')

        if profile_selection == 'all':
            profiles = PressingProfile.objects.all()
        else:
            profiles = PressingProfile.objects.filter(id=specific_profile_id)

        for profile in profiles:
            campaign = PublicityCampaign.objects.create(
                pressing_profile=profile,
                message=message,
                duration=duration,
                platforms=','.join(platforms),
                created_by=request.user
            )
            
            # Post to social media (implement this function as needed)
            success = post_to_social_media(profile, message, platforms)
            
            if success:
                messages.success(request, f"Publicity campaign created for {profile.business_name}")
            else:
                messages.error(request, f"Failed to post to some platforms for {profile.business_name}")

        return redirect('manage_publicity')

    pressing_profiles = PressingProfile.objects.all()
    recent_campaigns = PublicityCampaign.objects.order_by('-created_at')[:5]

    context = {
        'pressing_profiles': pressing_profiles,
        'recent_campaigns': recent_campaigns,
    }

    return render(request, 'panel/admin/pub/manage_publicity.html', context)


def post_to_social_media(profile, message, platforms):
    for platform in platforms:
        if platform == 'facebook' and profile.facebook_url:
            # Use Facebook API to post
            pass
        elif platform == 'instagram' and profile.instagram_url:
            # Use Instagram API to post
            pass
        elif platform == 'tiktok' and profile.tiktok_url:
            # Use TikTok API to post
            pass
        elif platform == 'youtube' and profile.youtube_url:
            # Use YouTube API to post
            pass
        elif platform == 'intra':
            # Post to your intra-network
            pass
    
    # Return success or failure status
    return True


from django.db.models import Avg

@login_required
def deliver_statistics(request):
    delivery_users = CustomUser.objects.filter(role='deliver')
    delivery_stats = []

    for user in delivery_users:
        try:
            ratings = Rating.objects.filter(delivery_user=user)
            average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] if ratings.exists() else None

            stats = {
                'user': user,
                'ratings': ratings,
                'stats': DeliveryStats.objects.get(delivery_user=user),
                'average_rating': average_rating,  # Add average rating to stats
            }
        except DeliveryStats.DoesNotExist:
            stats = {
                'user': user,
                'ratings': Rating.objects.filter(delivery_user=user),
                'stats': None,  # Handle missing stats
                'average_rating': None,  # No average rating if stats are missing
            }
        delivery_stats.append(stats)

    context = {
        'delivery_stats': delivery_stats,
    }
    
    return render(request, 'panel/admin/analytics/deliver_statistics.html', context)

import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def give_bonus(request, user_id):
    delivery_user = CustomUser.objects.get(id=user_id)
    delivery_stats = DeliveryStats.objects.get(delivery_user=delivery_user)

    # Calculate bonus
    bonus_percentage = random.randint(1, 10)
    bonus_amount = delivery_stats.salary * (bonus_percentage / 100)
    new_salary = delivery_stats.salary + bonus_amount

    # Update the salary
    delivery_stats.salary = new_salary
    delivery_stats.save()

    return JsonResponse({'new_salary': new_salary})

## clients view


def pressing_view(request):
    if request.method == "GET":
        return render(request, "panel/clients/book/pressing_booking.html")

def pressing_fetch_by_location(request):
    if request.method == "GET":
        regions = Region.objects.all()
        return render(request, "panel/clients/book/pressing_search.html", {"regions": regions})
    
    region = request.POST["region_id"]
    quarter = request.POST["quarter"]
    city = request.POST["city"]
    all_pressings = PressingProfile.objects.filter(region=region, town=city, quarter=quarter)
    return render(request, "panel/clients/book/pressing_booking.html", {"pressings": all_pressings})

def pressing_comment(request):
    if request.method == "GET":
        pressings = PressingProfile.objects.all()
        return render(request, "panel/clients/comment/pressing_comment.html", {"pressings": pressings})
    else:
        pressings = PressingProfile.objects.all()
        profile = PressingProfile.objects.get(pk=request.POST["pressing_id"])
        pressing = PressingComments.objects.create(user=request.user, comment=request.POST["comment"], pressing=profile)
        return render(request, "panel/clients/comment/pressing_comment.html", {"success": "Comment sent successfully !", "pressings": pressings})
    

def pressing_appointment(request, id):
    if request.method == "GET":
        pressing = PressingProfile.objects.get(pk=id)
        return render(request, "panel/clients/appoint/pressing_appointment.html", {"pressing": pressing})
    else:
        pressing = PressingProfile.objects.get(pk=id)
        tel = request.POST["tel"]
        motive = request.POST["service"]
        amount = 10
        collect = campay.collect({
                "amount": str(amount),
                "currency": "XAF",
                "from": "237" + tel,
                "description": "Payment for pressing service",
                "external_reference": "",  # Optional: your unique transaction ID
            })
            
        if collect.get('status') == 'SUCCESSFUL':
            receipt = Receipt.objects.create(total=amount)
            payment = Payments.objects.create(user=request.user, motive=motive, status=True, receipt=receipt)
            service_book = ServiceBook.objects.create(pressing=pressing, service=motive, payment=payment)
            context = {
                'total': amount,
                'id': receipt.id,
                "reference": collect.get("reference"),
                "tel": "+237"+tel,
                'business_name': pressing.business_name,
                'date': timezone.now(),
            }
            html = render_to_string('panel/manager/manage_order/receipt.html', {"receipt": context})
            result = BytesIO()
            
            pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)

            if not pdf.err:
                receipt_file = ContentFile(result.getvalue())
                receipt.pdf.save(f'receipt_{receipt.id}.pdf', receipt_file)
                response = FileResponse(open(receipt.pdf.path, 'rb'))
                file_name = receipt.pdf.name
                response['Content-Disposition'] = 'inline; filename=' + file_name
                return response
            return render(request, "panel/clients/appoint/pressing_appointment.html", {"errors": f"An error occured {pdf.err}"})
        else:
            payment = Payments.objects.create(user=request.user, motive=motive)
            print(f"Error occured ! {collect}")
            return render(request, "panel/clients/appoint/pressing_appointment.html", {"errors": f"An error occured {collect}"})

def render_pressing_map(request, id):
    if request.method=="GET":
        pressing = PressingProfile.objects.get(pk=id)
        return render(request, "panel/clients/map/pressing_map_details.html", {"pressing":pressing})

@login_required
def setting_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')
        profile_picture = request.FILES.get('profile_picture')

        # Update name and email
        request.user.name = name
        request.user.email = email

        # Check current password for security
        if not request.user.check_password(current_password):
            context = {'error': 'Current password is incorrect'}
        else:
            # Update password if provided and valid
            if new_password and new_password == confirm_password:
                request.user.set_password(new_password)

            # Update profile picture if provided
            if profile_picture:
                request.user.profile_picture = profile_picture

            request.user.save()
            context = {'success': 'Settings updated successfully'}
            # Redirect to avoid resubmission on refresh
            return redirect('clients_panel')
    else:
        context = {}

    return render(request, 'panel/clients/profile/setting_user.html', context)

@login_required
def profile_user(request):
    return render(request, 'panel/clients/profile/profile_user.html', {'user': request.user})


def benefits_view(request):
    return render(request, 'panel/clients/benefit/benefits.html')

@login_required
def account_history(request):
    # Query the Payments model to get all payments related to the current user
    payments = Payments.objects.filter(user=request.user)

    # Get the related receipts through the Payments model
    receipts = Receipt.objects.filter(payments__in=payments)

    # Get the comments and service books
    comments = PressingComments.objects.filter(user=request.user)
    service_books = ServiceBook.objects.filter(payment__user=request.user)

    context = {
        'receipts': receipts,
        'comments': comments,
        'service_books': service_books,
        'payments': payments,
    }
    
    return render(request, 'panel/clients/history/account_history.html', context)

@login_required
def rate_deliveries(request):
    if request.method == 'POST':
        delivery_user_id = request.POST.get('delivery_user')
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Create a new Rating
        Rating.objects.create(
            user=request.user,
            delivery_user_id=delivery_user_id,
            rating=rating_value,
            comment=comment,
        )
        return redirect('rate_deliveries')  # Redirect to the same page

    # Fetch all delivery users
    delivery_users = CustomUser.objects.filter(role='deliver')
    user_ratings = Rating.objects.filter(user=request.user)

    context = {
        'delivery_users': delivery_users,
        'user_ratings': user_ratings,
    }
    return render(request, 'panel/clients/rate/rate_services.html', context)
    
# deliver panel

@login_required
def setting_deliver(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')
        profile_picture = request.FILES.get('profile_picture')

        # Update name and email
        request.user.name = name
        request.user.email = email

        # Check current password for security
        if not request.user.check_password(current_password):
            context = {'error': 'Current password is incorrect'}
        else:
            # Update password if provided and valid
            if new_password and new_password == confirm_password:
                request.user.set_password(new_password)

            # Update profile picture if provided
            if profile_picture:
                request.user.profile_picture = profile_picture

            request.user.save()
            context = {'success': 'Settings updated successfully'}
            # Redirect to avoid resubmission on refresh
            return redirect('deliver_panel')
    else:
        context = {}

    return render(request, 'panel/deliver/profile/setting_deliver.html', context)


from .models import ServiceBook

def manage_deliver_view(request):
    service_books = ServiceBook.objects.select_related('payment', 'pressing').all()
    context = {
        'service_books': service_books,
    }
    return render(request, 'panel/deliver/track/manage_deliver.html', context)

