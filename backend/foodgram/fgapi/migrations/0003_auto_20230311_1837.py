# Generated by Django 3.2.18 on 2023-03-11 15:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fgapi', '0002_auto_20230311_1824'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriterecipe',
            options={'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientamount',
            options={'verbose_name': 'Количество ингридиента', 'verbose_name_plural': 'Количество ингридиентов'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='favoriterecipe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fgapi.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=50, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='ingredientamount',
            name='amount',
            field=models.FloatField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='ingredientamount',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fgapi.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientamount',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_amounts', to='fgapi.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='images/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='fgapi.IngredientAmount', to='fgapi.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='fgapi.Tag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='time_minutes',
            field=models.IntegerField(verbose_name='Время приготовления (мин)'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='recipes',
            field=models.ManyToManyField(blank=True, related_name='shopping_lists', to='fgapi.Recipe', verbose_name='Рецепты'),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
