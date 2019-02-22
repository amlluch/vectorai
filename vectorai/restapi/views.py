from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .serializers import UploadSerializer
from .models import Document
from .utils import Ocr, ResponseException

import datetime
import os

# Create your views here.

# Uploads the file tu server
class UploadFile(APIView):

    serializer_class = UploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            dato = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Checks passport on a previously uploaded image
class CheckPassport(APIView):


    def get(self, request, filename = None, format = None):
        # add "/" for disambiguation
        doc = Document.objects.filter(image__contains = '/' + filename).first()
        if not doc:
            return Response('File doesn\'t exist', status=status.HTTP_404_NOT_FOUND)
        extract = Ocr(doc.image.path)
        try:
            serialized = extract.check_passport()
        except ResponseException as error:
            return Response(error.message, status=error.status)

        return Response(serialized, status=status.HTTP_200_OK)

    def delete(self, request, filename = None, format = None):

        Document.objects.filter(image__contains = filename).delete()
        return Response('Image deleted', status=status.HTTP_200_OK)

# Uploads image, check passport and deletes the image after reading
class CheckUpload(APIView):

    serializer_class = UploadSerializer

    def post(self, request):
        # First upload file using the serializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            dato = serializer.save()
            # reads uploaded data
            doc = Document.objects.filter(image__contains = os.path.basename(dato.image.url)).first()
            if not doc:
                return Response('File {file} doesn\'t exist'.format(file=dato.image.url), status=status.HTTP_404_NOT_FOUND)
            extract = Ocr(doc.image.path)

            # reads passport data and deletes image on server
            try:
                serialized = extract.check_passport()
            except ResponseException as error:
                doc.delete()
                return Response(error.message, status=error.status)

            doc.delete()
            return Response(serialized, status=status.HTTP_200_OK)

        else:
            return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
