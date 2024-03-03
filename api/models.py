import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_products')
    product_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    num_groups = models.PositiveIntegerField(default=1)
    min_users = models.PositiveIntegerField(default=1)
    max_users = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product_name

    class Meta:
        unique_together = ('creator', 'product_name', 'start_date')

    @staticmethod
    def distribute_users_to_groups(pairs, K):
        sorted_pairs = sorted(pairs, key=lambda arr: (arr[1], arr[2]))

        sum_of_mins = sum([pair[1] for pair in pairs])
        sum_of_maxs = sum([pair[2] for pair in pairs])

        if sum_of_mins > K:
            print(f'Свободных человек - {K}, минимальное количество - {sum_of_mins}')
            return
        if sum_of_maxs < K:
            print(f'Свободных человек - {K}, максимальное количество - {sum_of_maxs}')
            return

        K -= sum_of_mins
        indx = 0
        cnt = []
        while K > 0:
            if indx < len(sorted_pairs) - 1:
                limit = sorted_pairs[indx + 1][1]
            else:
                limit = min([pair[2] for pair in sorted_pairs if pair[0] not in cnt])

            if sorted_pairs[indx][1] == sorted_pairs[indx][2] and sorted_pairs[indx][0] not in cnt:
                cnt += [sorted_pairs[indx][0]]
            else:
                while sorted_pairs[indx][1] < limit:
                    for pair in sorted_pairs[:indx + 1]:
                        if pair[0] not in cnt:
                            pair[1] += 1
                            K -= 1

                            if pair[1] == pair[2]:
                                cnt += [pair[0]]

                            if K <= 0:
                                return sorted_pairs
            if indx < len(sorted_pairs) - 1:
                indx += 1

        return sorted_pairs


class EnrollmentRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Product, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)


class UserProductAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_access')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_access')
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Lesson(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=255)
    video_link = models.URLField()


class Group(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=255)
    min_users = models.PositiveIntegerField()
    max_users = models.PositiveIntegerField()
    students = models.ManyToManyField(User, related_name='groups_joined')

    def clean(self):
        if self.min_users > self.max_users:
            raise ValidationError("Min users should be less than or equal to max users.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
