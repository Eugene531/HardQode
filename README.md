# Построение архитектуры
## Описание задачи №1
У нас была поставлена задача создания сущности продукта. Каждый продукт должен иметь своего создателя, название, дату и время старта, а также стоимость.

### Решение задачи №1
Для решения данной задачи я создал класс Product, который представляет собой модель продукта. Однако, помимо основных полей, я решил расширить функционал этого класса для удобства и гибкости использования.

### Основные поля класса Product
**creator**  
В этом поле хранится информация о создателе продукта (авторе или преподавателе).  

**product_name**  
Поле для хранения названия продукта.  

**start_date**  
Дата и время начала продажи продукта.  

**cost**  
Стоимость продукта.  

**num_groups**  
Количество групп, предназначенных для этого продукта.  

**min_users**  
Минимальное количество пользователей в группе.  

**max_users**  
Максимальное количество пользователей в группе.  

### Дополнительный функционал класса Product
Для удобства использования и обеспечения более гибкой работы с группами пользователей, я добавил в класс Product следующий статический метод:

`def distribute_users_to_groups(pairs, K):  
    # Реализация алгоритма распределения пользователей по группам`

Этот метод позволяет равномерно (чтобы в каждой группе количество участников не отличалось больше, чем на 1) распределить пользователей по группам продукта, учитывая их количество и требования к минимальному и максимальному количеству участников в группе.

### Обоснование расширения класса Product
Добавление дополнительного функционала в виде метода distribute_users_to_groups позволяет управлять процессом распределения пользователей по группам непосредственно из экземпляра класса Product. Это делает код более читаемым и модульным, а также обеспечивает более гибкую архитектуру приложения.



## Описание задачи №2
Необходимо придумать определение наличия доступа у пользователя (клиента или студента) к конкретному продукту.

### Решение задачи №2
Для решения этой задачи я использовал модель данных, включающую следующие ключевые элементы:

```
class UserProductAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_access')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_access')
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
```
Эта модель представляет собой отношение между пользователями и продуктами, при этом запись в этой таблице означает, что у пользователя есть доступ. Момент предоставления доступа фиксируется в поле granted_at.

### Пример использования в коде
Пример из кода демонстрирует, как можно узнать, имеет ли пользователь доступ к определенному продукту. Например:

```
user = request.user
product = Product.objects.get(pk=1)  # Предположим, что продукт с id=1 существует

if UserProductAccess.objects.filter(user=user, product=product).exists():
    print(f"Пользователь {user.username} имеет доступ к продукту {product.product_name}")
else:
    print(f"Пользователь {user.username} не имеет доступа к продукту {product.product_name}")
```
Этот код проверяет наличие записи в таблице UserProductAccess для указанного пользователя и продукта. Если такая запись существует, то пользователь имеет доступ к продукту.


## Описание задачи №3
Необходимо создать сущность "Урок", которая должна быть связана с определенным продуктом и содержать базовую информацию, такую как название и ссылки на видеоурок.

### Решение задачи №3
Для решения этой задачи я расширил модель данных, добавив новую сущность "Урок":

```
class Lesson(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=255)
    video_link = models.URLField()
```
Эта модель представляет собой урок, который принадлежит определенному продукту. В уроке хранится название и ссылки на видео.

## Описание задачи №4
При создании приложения возникла потребность в организации пользователей внутри каждого продукта. Для этого была добавлена сущность "Группа". Группа позволяет управлять учениками, их численностью, а также связывать их с конкретным продуктом.

### Решение задачи №4
```
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
```
Сущность "Группа" представляет собой гибкий инструмент для группировки пользователей внутри каждого продукта. В ней определены следующие поля:  

**product**  
Внешний ключ, связывающий группу с конкретным продуктом.  

**name**  
Название группы, позволяющее легко идентифицировать ее.  

**min_users и max_users**  
Определяют минимальное и максимальное количество участников в группе.  

**students**  
Множество пользователей, связанных с данной группой.  

### Проверка валидности данных
Добавлены методы clean и save для проверки корректности данных перед сохранением в базу. В случае нарушения условия (минимальное количество участников больше максимального), генерируется исключение.

# Написание запросов и реализация логики распределения
## Алгоритм распределения по группам
```
def distribute_space(pairs, K):
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
```
Алгоритм нацелен на распределение свободного места между парами, где каждая пара представлена тремя значениями: идентификатор группы, минимальное и максимальное количество участников. Это достигается путем сортировки пар по минимальному количеству участников. Затем алгоритм последовательно увеличивает количество людей в группах, начиная с тех, у которых минимальное число участников меньше. При этом он учитывает максимальное количество людей в группе, чтобы не превысить это значение. Алгоритм продолжает распределять участников до тех пор, пока не будет достигнуто заданное общее количество участников (K) или пока не заполнены все группы до максимального значения.

## API на список продуктов
```
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
```
Пример использования представлен на рисунке ниже
![image](https://github.com/Eugene531/HardQode/assets/94804642/ecf125f1-895c-4895-8516-cc8e1a1363ff)


## API с выведением списка уроков по конкретному продукту
```


# ПРИЛОЖЕНИЕ
Для большего удобства был написал очень простой front/back для возможности создавать курсы и регистрироваться на них. Ниже представлено подробное описание этого процесса:
1. Окно для регистрации
![image](https://github.com/Eugene531/HardQode/assets/94804642/787ca610-e813-447a-a02b-2bcf5ad6281a)

2. После регистрации можно создать свой курс:
![image](https://github.com/Eugene531/HardQode/assets/94804642/f5c2173e-4285-4fc5-9ab2-bf04a5e4645b)

3. Также ваши курсы появляются в специальном меню:
![image](https://github.com/Eugene531/HardQode/assets/94804642/4be10594-fc09-47a5-83dc-2c2f4a0d05c8)



class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'product', 'name', 'video_link']
```
