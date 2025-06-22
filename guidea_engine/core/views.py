from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, Location
from .serializers import DocumentSerializer
from .utils.markdown_parser import extract_locations_from_document

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

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
                slug=loc['slug'],
            )

        return Response({
            'created': len(locations_data),
            'saved': True,
            'locations': locations_data
        }, status=status.HTTP_200_OK)
