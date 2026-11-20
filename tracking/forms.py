from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """
    Form for adding and editing Commercial Kitchen Equipment production orders.
    Configured with Bootstrap 5 input classes and responsive widgets.
    """

    class Meta:
        model = Order
        fields = [
            'order_id',
            'customer_name',
            'equipment_model',
            'assigned_staff',
            'delivery_date',
            'status',
            'notes',
            'stage_cutting',
            'stage_welding',
            'stage_glass',
            'stage_finishing',
            'stage_qc',
        ]
        widgets = {
            'order_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. #101, ORD-2026-01',
                'required': 'required'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Royal Palace Hotel, Spice Symphony Cafe',
                'required': 'required'
            }),
            'equipment_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 4-Burner Gas Range with Oven, 6-Pan Bain Marie',
                'required': 'required'
            }),
            'assigned_staff': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. David Chen (Floor Lead), Alex Rivera',
                'required': 'required'
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Gauge specifications (SS 304 / 16-gauge), custom dimensions, burner BTU ratings, glass thickness...'
            }),
            'stage_cutting': forms.Select(attrs={'class': 'form-select'}),
            'stage_welding': forms.Select(attrs={'class': 'form-select'}),
            'stage_glass': forms.Select(attrs={'class': 'form-select'}),
            'stage_finishing': forms.Select(attrs={'class': 'form-select'}),
            'stage_qc': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_order_id(self):
        order_id = self.cleaned_data.get('order_id', '').strip()
        # If user didn't prefix with # or ORD, that's fine, but let's keep it clean
        if not order_id:
            raise forms.ValidationError("Order ID cannot be empty.")
        return order_id
