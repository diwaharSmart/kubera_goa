from asyncio import format_helpers
from datetime import date
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from .models import AgentWinning, User, Order, Ticket, AgentCollection, WebsiteInfo, TicketPrice, OrderCreation, Draw, CollectionAmount, BoardWinngPrice, AgentCollectionBalance, CustomerBalance
from django import forms
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

class CustomForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def rendered_output(self, name, value, *args):
        try:
            related_obj = self.rel.to._default_manager.get(pk=value)
            return related_obj.username  # Display the username
        except self.rel.to.DoesNotExist:
            return super().rendered_output(name, value, *args)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'user_type')}),
        ('Bank Information', {'fields': ('upi_id', 'paytm_number', 'phonepe_number', 'google_pay_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )


from .models import AgentUser
class AgentUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer_mobile_number', 'name')
    search_fields = ('user__username', 'name', 'customer_mobile_number')
    exclude = ["user"]

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            # Create a new User with username as mobile number and first name as name
            username = obj.customer_mobile_number
            first_name = obj.name
            password = User.objects.make_random_password()  # Generate a random password
            user = User.objects.create_user(username=username, first_name=first_name, password=password,upi_id=obj.upi_id,phonepe_number=obj.phonepe_number,paytm_number=obj.paytm_number,google_pay_number=obj.google_pay_number)
            # obj.user = user

            # Set user type as 'customer'
            user.user_type = 'customer'
            user.save()

        # Set the user field of AgentUser to the current logged-in user
        # if not obj.user:
        obj.user = request.user

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Filter the queryset based on the current logged-in user
        queryset = super().get_queryset(request)
        return queryset.filter(user=request.user)

class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = OrderCreation
        fields = "__all__"

    def clean_numbers(self):
        numbers_text = self.cleaned_data.get('numbers', '')
        items = numbers_text.split(',')
        
        all_conditions_met = True
        for item in items:
            item = item.strip()
            if '*' in item or '-' in item:
                item_parts = item.split('*') if '*' in item else item.split('-')
                if len(item_parts) == 2:
                    try:
                        number1 = int(item_parts[0])
                        number2 = int(item_parts[1])
                        # You can add more conditions here if needed
                    except ValueError:
                        all_conditions_met = False
                        break
                else:
                    all_conditions_met = False
                    break
            else:
                all_conditions_met = False
                break
        
        if not all_conditions_met:
            raise forms.ValidationError("Invalid format in OrderCreation")

        return numbers_text

class OrderCreationInline(admin.TabularInline):
    model = OrderCreation
    form = OrderCreationForm
    extra = 0 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_uuid", "agent","customer", "order_total", "order_date", "cancel_order"]
    list_filter = ["order_date"]
    search_fields= ["customer"]
    # exclude = ["agent"]
    readonly_fields = ["order_total","order_status","order_date"]
    inlines = [OrderCreationInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'draw':
            kwargs['queryset'] = Draw.objects.filter(is_active=True)

        if db_field.name == 'customer':
            user = request.user
            agent_customers = AgentUser.objects.filter(user=user).values_list('customer_mobile_number', flat=True)
            kwargs['queryset'] = get_user_model().objects.filter(username__in=agent_customers)
            kwargs['widget'] = CustomForeignKeyRawIdWidget(
                db_field.remote_field, self.admin_site, using=kwargs.get('using')
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def cancel_order(self, obj):
        cancel_url = reverse('cancel_order', args=[obj.pk])
        return format_html('<a class="button" href="{}">Cancel</a>', cancel_url)

    cancel_order.short_description = "Cancel"


    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        if order.pk:
            order.ticket_set.all().delete()
        for formset in formsets:
            if isinstance(formset, OrderCreationInline.formset):
                for form in formset.forms:
                    if form.is_valid():
                        # Retrieve relevant data from the form and related objects
                        numbers_text = form.cleaned_data.get('numbers', '')
                        order = form.instance.order
                        customer = order.customer
                        draw = order.draw

                        # Check if the order already exists
                        # if order.pk:
                        #     # Delete existing tickets associated with the order
                        #     order.ticket_set.all().delete()

                        # Split the numbers text and iterate through each item
                        items = numbers_text.split(',')
                        for item in items:
                            item_parts = [part.strip() for part in item.split('*')]  # Split and remove spaces
                            if len(item_parts) == 2:
                                try:
                                    choosen_number = int(item_parts[0])
                                    quantity = int(item_parts[1])
                                    board = form.instance.board

                                    # Calculate total_amount based on ticket value and quantity
                                    total_amount = board.ticket_value * quantity

                                    # Create a Ticket instance with calculated values
                                    ticket = Ticket(
                                        agent=request.user,
                                        draw=draw,
                                        customer=customer,
                                        board=board,
                                        choosen_number=choosen_number,
                                        quantity=quantity,
                                        total_price=total_amount,
                                        order=order  # Set the order for the ticket
                                    )
                                    if not form.instance.order.agent:
                                        ticket.agent = request.user
                                    ticket.save()
                                    
                                except ValueError:
                                    pass  # Handle invalid values

                # Calculate and update order_total based on ticket total prices
                order_total = sum(ticket.total_price for ticket in order.ticket_set.all())
                order.order_total = order_total
                if not form.instance.order.agent:
                    order.agent = request.user

                order.save()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.filter(order_status__in=["processing","cancelled","pending"])
        return queryset

    
                        

class CollectionAdmin(admin.TabularInline):
    model = CollectionAmount
    extra =1

class AgentCollectionAdmin(admin.ModelAdmin):
    list_display = ["agent","draw","collection_amount"]
    search_fields = ["agent__username"]
    inlines = [CollectionAdmin]

class DrawAdmin(admin.ModelAdmin):
    change_form_template = 'admin/order_change_form.html'

class BoardWinngPriceInline(admin.TabularInline):
    model = BoardWinngPrice
    extra =1

class TicketPriceAdmin(admin.ModelAdmin):
    inlines = [BoardWinngPriceInline]

class AgentWinningAdmin(admin.ModelAdmin):
    list_display = ["agent","draw","winning_amount"]
    search_fields = ["agent__username"]
   

admin.site.register(AgentUser, AgentUserAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(AgentCollection,AgentCollectionAdmin)
admin.site.register(WebsiteInfo)
admin.site.register(TicketPrice,TicketPriceAdmin)
admin.site.register(Ticket)
admin.site.register(Draw,DrawAdmin)
admin.site.register(AgentWinning,AgentWinningAdmin)

admin.site.register(AgentCollectionBalance)

admin.site.register(CustomerBalance)

