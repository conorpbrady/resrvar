from django.urls import path
from .views import *

urlpatterns = [
    path('requests', RequestListView.as_view(), name='requests'),
    path('requests/create', RequestCreateView.as_view(), name='request-create'),
    path('reuqests/<int:pk>/update', RequestUpdateView.as_view(), name='request-update'),

    path('venues', VenueListView.as_view(), name='venues'),
    path('venues/create', VenueCreateView.as_view(), name='venue-create'),
    path('venues/<int:pk>/update', VenueUpdateView.as_view(), name='venue-update'),

    path('preferences', PreferenceListView.as_view(), name='preferences'),
    path('preferences/create', PreferenceCreateView.as_view(), name='preference-create'),
    path('preferences/<int:pk>/update', PreferenceUpdateView.as_view(), name='preference-update'),

    path('scheduling', SchedulingView.as_view(), name='scheduling'),
    path('scheduling/create', SchedulingCreateView.as_view(), name='scheduling-create'),
    path('scheduling/<int:pk>/update', SchedulingUpdateView.as_view(), name='scheduling-update'),

    path('accountinfo', AccountInfoListView.as_view(), name='accountinfo'),
    path('accountinfo/create', AccountInfoCreateView.as_view(), name='accountinfo-create'),
    path('accountinfo/<int:pk>/update', AccountInfoUpdateView.as_view(), name='accountinfo-update'),

    path('history', HistoryListView.as_view(), name='history')
             ]
