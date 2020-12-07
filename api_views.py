# -*- coding: utf-8 -*-
from rest_framework import generics
from url_shortner.serializers import (
    URLInfoSerializer,
    URLClicksSerializer,
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from ipware import get_client_ip
from django.shortcuts import (
    render,
    get_object_or_404,
    )
from url_shortner.models import (
    URLClicks,
    URLInfo,
    )

# TODO: class names to be change to more self devenitive ones
class URLInfoList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = URLInfoSerializer

    def perform_create(self, serializer):
       serializer.save(creator=self.request.user)

    def get_queryset(self):
        """
        This view will just return a list of all the URLInfos
        created by the currently authenticated user.
        """
        user = self.request.user
        return URLInfo.objects.filter(creator=user)


class ClickInformation(generics.ListAPIView):
    serializer_class = URLClicksSerializer

    def get_queryset(self):
        """
        This view restricts the returned information to the authorized user.
        """
        user = self.request.user
        short_code = self.request.query_params.get('short_code', None)
        if short_code is not None:
            urlinfo = get_object_or_404(URLInfo, short_code=short_code)
        if urlinfo.creator == user:
            # TODO: permission for groups ?
            #a = URLClicks.objects.filter(clicked_url_info = urlinfo)#.groupby['clicker_ip'].count()
            ip_counts = URLClicks.objects.filter(clicked_url_info__original_url=urlinfo.original_url) \
            .values('clicker_ip').annotate(ip_entries=Count('clicker_ip'))
            # TODO: required statistics to be discussed and implermented
        return ip_counts
