from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import hashlib

from .models import Location, TextSnippet, AudioSnippet, Tour
from .serializers import (
    LocationSerializer, TextSnippetSerializer, AudioSnippetSerializer, 
    TourSerializer, UserRegistrationSerializer, UserSerializer
)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='generate-snippets')
    def generate_snippets(self, request, pk=None):
        """Generate text snippets of different lengths from the location's raw_text"""
        try:
            location = self.get_object()
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        # Clear existing snippets for this location
        TextSnippet.objects.filter(location=location).delete()

        # Generate snippets (this is a placeholder - you'd implement actual text processing)
        snippets_created = []
        raw_text = location.raw_text

        for length_choice, length_display in TextSnippet.LENGTH_CHOICES:
            # Simple text truncation logic (you'd want more sophisticated processing)
            if length_choice == 'short':
                text = raw_text[:200] + '...' if len(raw_text) > 200 else raw_text
            elif length_choice == 'medium':
                text = raw_text[:500] + '...' if len(raw_text) > 500 else raw_text
            else:  # long
                text = raw_text

            # Create hash for change detection
            text_hash = hashlib.md5(text.encode()).hexdigest()

            snippet = TextSnippet.objects.create(
                location=location,
                length=length_choice,
                text=text,
                hash=text_hash,
                is_current=True
            )
            snippets_created.append({
                'id': snippet.id,
                'length': length_choice,
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            })

        return Response({
            'message': f'Generated {len(snippets_created)} text snippets',
            'snippets': snippets_created
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='snippets')
    def get_snippets(self, request, pk=None):
        """Get all text snippets for this location"""
        try:
            location = self.get_object()
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        snippets = TextSnippet.objects.filter(location=location).order_by('length')
        serializer = TextSnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby_locations(self, request):
        """Get locations near specified coordinates (placeholder for future implementation)"""
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        radius = request.query_params.get('radius', 10)  # km

        if not lat or not lon:
            return Response({'error': 'lat and lon parameters required'}, status=status.HTTP_400_BAD_REQUEST)

        # Placeholder - you'd implement actual geographic search here
        locations = Location.objects.all()[:10]  # Return first 10 for now
        serializer = LocationSerializer(locations, many=True)
        return Response({
            'message': f'Locations within {radius}km of ({lat}, {lon})',
            'locations': serializer.data
        })


class TextSnippetViewSet(viewsets.ModelViewSet):
    queryset = TextSnippet.objects.all()
    serializer_class = TextSnippetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = TextSnippet.objects.all()
        location_id = self.request.query_params.get('location_id')
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        return queryset.order_by('-created')


class AudioSnippetViewSet(viewsets.ModelViewSet):
    queryset = AudioSnippet.objects.all()
    serializer_class = AudioSnippetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AudioSnippet.objects.all()
        location_id = self.request.query_params.get('location_id')
        if location_id:
            queryset = queryset.filter(text_snippet__location_id=location_id)
        return queryset.order_by('-created')


class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='add-location')
    def add_location(self, request, pk=None):
        """Add a location to the tour"""
        tour = self.get_object()
        location_id = request.data.get('location_id')
        
        if not location_id:
            return Response({'error': 'location_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        # Add location to tour order
        location_order = tour.location_order_json or []
        if location_id not in location_order:
            location_order.append(location_id)
            tour.location_order_json = location_order
            tour.save()

        return Response({
            'message': f'Added location "{location.name}" to tour',
            'location_order': location_order
        })


# Keep existing authentication views
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                user_data = UserSerializer(user).data
                response.data['user'] = user_data
                response.data['message'] = 'Login successful'
            except User.DoesNotExist:
                pass
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    """
    Simple endpoint to get current user information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_data = {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        return Response(user_data)
