from django import forms
from .models import Recipe, Ingredient


class RecipeForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Ингредиенты'
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['ingredients'].initial = \
                self.instance.ingredients.values_list('pk', flat=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        if instance.pk:
            instance.ingredients.set(self.cleaned_data['ingredients'])
            self.save_m2m()
        return instance
