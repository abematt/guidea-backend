from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

from .models import Document, Location
from .serializers import DocumentSerializer, UserRegistrationSerializer, UserSerializer
from .utils.markdown_parser import extract_locations_from_document

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    @action(detail=True, methods=['post'], url_path='parse-locations')
    def parse_locations(self, request, pk=None):
        try:
            document = self.get_object()
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        dry_run = request.query_params.get('dry_run') == 'true'
        locations_data = extract_locations_from_document(document.raw_md)

        if dry_run:
            return Response({
                'dry_run': True,
                'parsed_locations': locations_data,
                'message': 'No locations saved. This was a dry run.'
            }, status=status.HTTP_200_OK)

        # Clear old and save new
        Location.objects.filter(document=document).delete()

        for loc in locations_data:
            Location.objects.create(
                document=document,
                name=loc['name'],
                latlon_json=loc.get('latlon_json', {}),
            )

        return Response({
            'created': len(locations_data),
            'saved': True,
            'locations': locations_data
        }, status=status.HTTP_200_OK)

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
            # Get user data
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
