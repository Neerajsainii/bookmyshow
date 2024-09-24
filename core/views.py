from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def index(request):
    return render(request,'register.html')
User = get_user_model()  # Use the custom User model if one is set

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return render(request, 'index.html')
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims if needed
        return token

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    if request.user.role != 'manager':
        return Response({"error": "Only event managers can create events."}, status=403)
    # Logic for event creation

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_ticket(request, event_id):
    event = Event.objects.get(id=event_id)
    if event.available_tickets < request.data['tickets_booked']:
        return Response({"error": "Not enough tickets available"}, status=400)
    booking = Booking.objects.create(user=request.user, event=event, tickets_booked=request.data['tickets_booked'])
    event.available_tickets -= request.data['tickets_booked']
    event.save()
    return Response({"message": "Booking successful", "booking_id": booking.id}, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.payment_status = "Completed"
    booking.save()
    return Response({"message": "Payment successful"}, status=200)
