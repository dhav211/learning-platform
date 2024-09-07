from django.urls import path
from lessons import views

urlpatterns = [
    path('<int:lesson_id>/', views.show_lesson, name="show_lesson"),
    path('form/<int:lesson_id>/', views.lesson_creation, name="lesson_creation"),
    path('new/', views.new, name="new_lesson"),
    path('new_block/<int:lesson_id>/', views.new_block, name="new_block"),
    path('remove/<int:lesson_id>/<int:content_block_id>', views.remove_block, name="remove_block"),
    path('change_table/<int:lesson_id>/<int:content_block_id>/', views.change_table, name="change_table"),
]