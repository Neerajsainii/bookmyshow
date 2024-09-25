from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import serializers, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import NotFound
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Event, Booking  # Adjust the import based on your project structure
from .serializers import EventSerializer, RegisterSerializer  # Assuming you have a serializer for Event
import logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request,'register.html')

def login_as(request):
    return render(request,'login.html')

def createvent(request):
    return render(request,'create-event.html')

User = get_user_model()  # Use the custom User model if one is set



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return render(request,'index.html')

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        print('token = ', token)
        return token

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return render(request,'home.html')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({"detail": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    logger.info(f"User authenticated: {request.user.is_authenticated}")
    logger.info(f"User role: {request.user.role if request.user.is_authenticated else 'Not authenticated'}")
    
    if not request.user.is_authenticated:
        logger.warning("Unauthorized access attempt to create-event")
        return Response({"error": "User is not authenticated"}, status=401)

    if request.user.role != 'manager':
        return Response({"error": "Only event managers can create events."}, status=status.HTTP_403_FORBIDDEN)
    
    # Validate input data
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save(created_by=request.user)  # Save the event with the current user
        return Response({"message": "Event created successfully", "event_id": event.id}, status=status.HTTP_201_CREATED)
    
    # If validation fails, return errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_ticket(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise NotFound(detail="Event not found.")

    tickets_booked = request.data.get('tickets_booked')
    
    # Validate tickets_booked
    if tickets_booked <= 0:
        return Response({"error": "Number of tickets must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)
    
    if event.available_tickets < tickets_booked:
        return Response({"error": "Not enough tickets available"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        booking = Booking.objects.create(user=request.user, event=event, tickets_booked=tickets_booked)
        event.available_tickets -= tickets_booked
        event.save()

    return Response({"message": "Booking successful", "booking_id": booking.id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.payment_status = "Completed"
    booking.save()
    return Response({"message": "Payment successful"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    booking_data = []
    
    for booking in bookings:
        booking_data.append({
            "id": booking.id,
            "event": booking.event.title,
            "tickets_booked": booking.tickets_booked,
            "booking_date": booking.booking_date,
            "payment_status": booking.payment_status,
        })
    
    return Response(booking_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    # Optionally, you can restore tickets back to the event
    event = booking.event
    event.available_tickets += booking.tickets_booked
    event.save()

    booking.delete()
    return Response({"message": "Booking canceled successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    if request.user.role != 'manager':
        return Response({"error": "Only event managers can create events."}, status=status.HTTP_403_FORBIDDEN)

    title = request.data.get('title')
    description = request.data.get('description')
    date = request.data.get('date')
    time = request.data.get('time')
    location = request.data.get('location')
    available_tickets = request.data.get('available_tickets')
    
    # Validate input data
    if not all([title, description, date, time, location, available_tickets]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    event = Event.objects.create(
        title=title,
        description=description,
        date=date,
        time=time,
        location=location,
        available_tickets=available_tickets,
        created_by=request.user,
    )

    return Response({"message": "Event created successfully", "event_id": event.id}, status=status.HTTP_201_CREATED)


