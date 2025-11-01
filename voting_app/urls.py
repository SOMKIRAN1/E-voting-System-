from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('voter_login/', views.voter_login, name='voter_login'),
    path('voter_register/', views.voter_register, name='voter_register'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('candidate_register/', views.candidate_register, name='candidate_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('results/', views.results, name='election_results'),
    path('vote/<int:candidate_id>/', views.vote_candidate, name='vote_candidate'),
    path('voter_login/', views.voter_login, name='voter_login'),
    path('voter_logout/', views.voter_logout, name='voter_logout'),
    # path('vote/<int:candidate_id>/', views.cast_vote, name='cast_vote'),
    path('voter_dashboard/', views.voter_dashboard, name='voter_dashboard'),
    # path('vote/<int:candidate_id>/', views.vote_candidate, name='vote_candidate'),
    path('vote/<int:candidate_id>/', views.vote_candidate, name='vote_candidate'),
    path('view_candidates/', views.view_candidates, name='view_candidates'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('results/', views.election_results, name='election_results'),
    path('eci_login/', views.eci_login, name='eci_login'),
    path('eci_dashboard/', views.eci_dashboard, name='eci_dashboard'),




]
