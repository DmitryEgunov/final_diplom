from django.utils.translation import gettext_lazy as _

from django.db import models
from django_rest_passwordreset.tokens import get_token_generator


class User(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Имя', )
    email = models.EmailField(_('email address'),
                              unique=True)
    password = models.CharField(max_length=10,
                                verbose_name='Пароль')
    company = models.CharField(max_length=100,
                               verbose_name='Компания')
    position = models.CharField(max_length=50,
                                verbose_name='Должность')


class Shop(models.Model):
    name = models.CharField(max_length=40,
                            verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка',
                          null=True,
                          blank=True)
    state = models.BooleanField()


class Category(models.Model):
    shops = models.ManyToManyField(Shop,
                                   verbose_name='Магазины',
                                   related_name='category',
                                   blank=True)
    name = models.CharField(max_length=40,
                            verbose_name='Название')


class Product(models.Model):
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 related_name='products',
                                 blank=True,
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=80,
                            verbose_name='Название')


class ProductInfo(models.Model):
    product = models.ForeignKey(Product,
                                verbose_name='Продукт',
                                related_name='product_info',
                                blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             related_name='product_info',
                             blank=True,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100,
                            verbose_name='Название')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')


class Parameter(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название')


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo,
                                     verbose_name='Информация о продукте',
                                     related_name='product_parameters',
                                     blank=True,
                                     on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter,
                                  verbose_name='Параметр',
                                  related_name='product_parameters',
                                  blank=True,
                                  on_delete=models.CASCADE)
    value = models.CharField(max_length=50,
                             verbose_name='Значение')


class Order(models.Model):
    STATUS_CHOICES = (
        ('basket', 'В корзине'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             related_name='orders',
                             blank=True,
                             on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(verbose_name='Статус',
                                 choices=STATUS_CHOICES,
                                 max_length=10)


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name='Заказ',
                              related_name='orders_item',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(ProductInfo,
                                verbose_name='Информация о продукте',
                                related_name='orders_item',
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             related_name='orders_item',
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class Contact(models.Model):
    user = models.ForeignKey(User,
                             related_name='contacts',
                             on_delete=models.CASCADE)
    city = models.CharField(max_length=100,
                            verbose_name='Город')
    street = models.CharField(max_length=100,
                              verbose_name='Улица')
    building = models.CharField(max_length=100,
                                verbose_name='Дом',
                                blank=True)
    apartment = models.CharField(max_length=50,
                                 verbose_name='Квартира',
                                 blank=True)
    phone = models.CharField(max_length=50,
                             verbose_name='Номер телефона')


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'ТОкены подтверждения Email'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE,
                             verbose_name='The user which is associated to this password reset token')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Time when the token was generated')
    key = models.CharField('Key', max_length=64, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
