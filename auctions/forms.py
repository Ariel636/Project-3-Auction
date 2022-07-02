from django import forms

from .models import User, Category, Listing

class AddListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=64,
                            widget=forms.TextInput(attrs={'placeholder': 'Add a title *', 'class': 'form-control shadow-sm', 'autofocus': 'True'}))
    description = forms.CharField(max_length=128,
                            widget=forms.Textarea(attrs={'placeholder': 'Add a description *', 'rows':2, 'class':'form-control shadow-sm'}))
    bid = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder': 'Add a starting bid ($) *', 'min': '0', 'class': 'form-control shadow-sm'}))
    image = forms.CharField(label="Image", max_length=256, required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'Drag or enter an URL address to add an image (optional)', 'blank': 'True','class': 'form-control shadow-sm'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="Select category (optional)",
                            widget=forms.Select(attrs={'class': 'form-control'}))


class AddCommentForm(forms.Form):
    comment = forms.CharField(label="", max_length=256,
                            widget=forms.Textarea(attrs={'placeholder': 'Enter your comment here...', 'rows': 2, 'class': 'form-control shadow-sm'}))



