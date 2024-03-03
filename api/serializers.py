from django.db.models import Max, Min
from rest_framework import serializers
from api.models import Product, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'product', 'name', 'video_link']


class ProductSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    min_users = serializers.SerializerMethodField()
    max_users = serializers.SerializerMethodField()
    enrolled_users_count = serializers.SerializerMethodField()

    @staticmethod
    def get_lessons_count(obj):
        return obj.lessons.count()

    @staticmethod
    def get_min_users(obj):
        return obj.groups.aggregate(Min('min_users'))['min_users__min']

    @staticmethod
    def get_max_users(obj):
        return obj.groups.aggregate(Max('max_users'))['max_users__max']

    @staticmethod
    def get_enrolled_users_count(obj):
        return obj.user_access.count()

    class Meta:
        model = Product
        fields = ['id', 'creator', 'product_name', 'start_date', 'cost', 'num_groups',
                  'min_users', 'max_users', 'enrolled_users_count', 'lessons_count',
                  'lessons']
