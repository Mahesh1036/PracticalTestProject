from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product
from .serializers import ProductSerializer, CustomUserSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework import status
from django_ratelimit.decorators import ratelimit


# Product CRUD API
class ProductViewSet(ModelViewSet):
    
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']  # Enables keyword search across title and description
    filterset_fields = ['price']
    ordering_fields = ['created_on', 'updated_on']

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_create(self, request):
        products_data = request.data.get('products', [])
        if not products_data:
            return Response({'error': 'No products provided'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=products_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Products created successfully'}, status=status.HTTP_201_CREATED)
    
    @ratelimit(key='ip', rate='10/m', method='GET', block=True)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @ratelimit(key='ip', rate='5/m', method='PATCH', block=True)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @ratelimit(key='ip', rate='5/m', method='DELETE', block=True)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# User Registration API
class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'})
        return Response(serializer.errors, status=400)

# User Login API
class LoginView(APIView):
    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=401)
