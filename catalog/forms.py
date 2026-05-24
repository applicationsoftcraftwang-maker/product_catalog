from django import forms
from .models import Category, Tag, Product


class ProductFilterForm(forms.Form):
    query = forms.CharField(
        required=False,
        label="Search by material description",
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. MC cable, conduit, prefab…",
            "class": "search-input",
            "autofocus": True,
        }),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All categories",
        label="Material category",
        widget=forms.Select(attrs={"class": "filter-select"}),
    )

    status = forms.ChoiceField(
        choices=[("", "All statuses")] + Product.STATUS_CHOICES,
        required=False,
        label="Availability status",
        widget=forms.Select(attrs={"class": "filter-select"}),
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Jobsite tags",
        widget=forms.CheckboxSelectMultiple(attrs={"class": "tag-checkbox"}),
    )
