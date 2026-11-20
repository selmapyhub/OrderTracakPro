from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'customer_name',
        'equipment_model',
        'assigned_staff',
        'delivery_date',
        'status',
        'progress_percentage',
        'stage_cutting',
        'stage_welding',
        'stage_glass',
        'stage_finishing',
        'stage_qc',
    )
    list_filter = ('status', 'delivery_date', 'stage_cutting', 'stage_welding', 'stage_glass', 'stage_finishing', 'stage_qc')
    search_fields = ('order_id', 'customer_name', 'equipment_model', 'assigned_staff')
    ordering = ('-created_at',)
    readonly_fields = ('progress_percentage', 'created_at', 'updated_at')
    fieldsets = (
        ("Order Identification", {
            'fields': ('order_id', 'customer_name', 'equipment_model', 'assigned_staff')
        }),
        ("Schedule & Status", {
            'fields': ('delivery_date', 'status', 'progress_percentage', 'notes')
        }),
        ("Production Stages", {
            'fields': ('stage_cutting', 'stage_welding', 'stage_glass', 'stage_finishing', 'stage_qc')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
