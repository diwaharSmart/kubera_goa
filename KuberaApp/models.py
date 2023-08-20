from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('supervisor', 'Supervisor'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    paytm_number = models.CharField(max_length=15, blank=True, null=True)
    phonepe_number = models.CharField(max_length=15, blank=True, null=True)
    google_pay_number = models.CharField(max_length=15, blank=True, null=True)
    bank_holder_name = models.CharField(max_length=255,blank=True,null=True)
    bank_account_number = models.CharField(max_length=255,blank=True,null=True)
    bank_ifsc_code = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return self.username

    

class AgentUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_mobile_number = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    paytm_number = models.CharField(max_length=15, blank=True, null=True)
    phonepe_number = models.CharField(max_length=15, blank=True, null=True)
    google_pay_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

# Signal to delete the associated User when an AgentUser is deleted
@receiver(pre_delete, sender=AgentUser)
def delete_related_user(sender, instance, **kwargs):
    try:
        user = User.objects.get(username=instance.customer_mobile_number)
        user.delete()
    except User.DoesNotExist:
        pass

# Signal to update associated User when an AgentUser is updated
@receiver(post_save, sender=AgentUser)
def update_related_user(sender, instance, **kwargs):
    try:
        user = User.objects.get(username=instance.customer_mobile_number)
        user.first_name = instance.name
        user.upi_id = instance.upi_id
        user.paytm_number = instance.paytm_number
        user.phonepe_number = instance.phonepe_number
        user.google_pay_number = instance.google_pay_number
        user.save()
    except User.DoesNotExist:
        pass


class Draw(models.Model):
    draw_uuid          = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    draw_date          = models.DateField()
    draw_time          = models.TimeField()
    result_number      = models.PositiveIntegerField(default=0)
    released           = models.BooleanField(default=False)
    winning_percentage = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    loot_amount        = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    is_active          = models.BooleanField(default=False)
    result_generated   = models.BooleanField(default=False)
    orders_accepted   = models.BooleanField(default=False)

    def __str__(self):
        draw_time_str = self.draw_time.strftime("%I:%M %p")
        return f"Draw {self.id} - {self.draw_date} {draw_time_str}"
    


class TicketPrice(models.Model):
    ticket_name = models.CharField(max_length=50, unique=True)
    ticket_value = models.DecimalField(max_digits=10, decimal_places=2)
    commision = models.DecimalField(default=0.00,max_digits=10, decimal_places=2)
    price_after_commision = models.DecimalField(default=0.00,max_digits=10, decimal_places=2)
    def __str__(self):
        return self.ticket_name
    
class BoardWinngPrice(models.Model):
    ticket_price  = models.ForeignKey(TicketPrice,blank=True,null=True,on_delete=models.CASCADE)
    board_name    = models.CharField(max_length=255,blank=True,null=True)
    winning_price = models.DecimalField(default=0.00,max_digits=10, decimal_places=2)
    
class Ticket(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE,blank=True,null=True) 
    order = models.ForeignKey('Order', on_delete=models.CASCADE,blank=True,null=True) 
    ticket_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    board = models.ForeignKey(TicketPrice, on_delete=models.CASCADE,blank=True,null=True)
    choosen_number = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_bought',blank=True,null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    winner = models.BooleanField(default=False)
    settled = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    winning_amount = models.DecimalField(default=0.00,max_digits=10, decimal_places=2)
    winning_board = models.CharField(max_length=255,blank=True,null=True)
     # Foreign key to Draw model

    def __str__(self):
        return f"Ticket {self.ticket_uuid}"

# Signal to set agent as the current logged-in user before saving

ORDER_STATUS =(
    ('pending','pending'),
    ('not_verified','not_verified'),
    ('processing','processing'),
    ('accepted','accepted'),
    ('cancelled','cancelled'),
    ('settled','settled'),
)

# Order model
class  Order(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE,blank=True,null=True) 
    customer       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_ticket',blank=True,null=True)
    upi_transaction_reference_id = models.CharField(max_length=50,blank=True,null=True)
    payment_upi_id = models.CharField(max_length=200,blank=True,null=True)
    order_uuid     = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order_status   = models.CharField(choices=ORDER_STATUS,default="processing",max_length=30)
    order_total    = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    order_date     = models.DateField(default=timezone.now)
    winning_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    def __str__(self):
        return f"Order {self.order_uuid}"
    
class OrderCreation(models.Model):
    order = models.ForeignKey(Order,blank=True,null=True,on_delete=models.CASCADE)
    board = models.ForeignKey(TicketPrice,blank=True,null=True,on_delete=models.CASCADE)
    numbers = models.TextField(blank=True)

class AgentCollection(models.Model):
    DRAW_STATUS_CHOICES = (
        ('partial', 'Partial'),
        ('full', 'Full'),
    )
    
    draw       = models.ForeignKey(Draw, on_delete=models.CASCADE,blank=True,null=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    collection_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    amount_to_collect = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    collection_status = models.CharField(default="partial",max_length=10, choices=DRAW_STATUS_CHOICES,blank=True,null=True)

    def __str__(self):
        return f"Agent Collection ({self.draw}) - {self.agent.username}"


class CollectionAmount(models.Model):
    agent_collection = models.ForeignKey(AgentCollection,on_delete=models.CASCADE,blank=True,null=True)
    amount_recieved  = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    collection_date  = models.DateField(default=timezone.now)


class AgentWinning(models.Model):
    agent = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    draw = models.ForeignKey(Draw,on_delete=models.CASCADE,blank=True,null=True)
    winning_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    settled = models.BooleanField(default=False)
    

class WebsiteInfo(models.Model):
    whatsapp_number = models.CharField(max_length=250,blank=True,null=True)
    upi_id = models.CharField(max_length=250,blank=True,null=True)
    upi_qr_code = models.ImageField(upload_to="qr_code",blank=True,null=True)
    gpay = models.CharField(max_length=250,blank=True,null=True)
    phonepe = models.CharField(max_length=250,blank=True,null=True)
    paytm = models.CharField(max_length=250,blank=True,null=True)
    logo  = models.ImageField(upload_to="logo",blank=True,null=True)
    banner = models.ImageField(upload_to="logo",blank=True,null=True)
    background = models.ImageField(upload_to="logo",blank=True,null=True)
    loader_image = models.ImageField(upload_to="logo",blank=True,null=True)
    loader_image_two = models.ImageField(upload_to="logo",blank=True,null=True)
    additional_info = models.TextField(blank=True)
    title = models.CharField(max_length=250,blank=True,null=True)
    theme_color_one = models.CharField(max_length=250,blank=True,null=True)
    theme_color_two = models.CharField(max_length=250,blank=True,null=True)
    button_color = models.CharField(max_length=250,blank=True,null=True)


class AgentCollectionBalance(models.Model):
    agent = models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True)
    total_collection_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
   
class AgentCollectionAmount(models.Model):
    agent_collection = models.ForeignKey(AgentCollectionBalance,on_delete=models.CASCADE,blank=True,null=True)
    amount_recieved  = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    collection_date  = models.DateField(default=timezone.now)

class CustomerBalance(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True)
    balance = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

class CustomerBalanceHistory(models.Model):
    TRANSACTION_STATUS=(
        ("pending","pending"),
        ("rejected","rejected"),
        ("approved","approved"),
    )
    wallet = models.ForeignKey(CustomerBalance, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_approved = models.BooleanField(default=False)
    transaction_id = models.CharField(blank=True, null=True, max_length=255)
    upi_address = models.CharField(blank=True, null=True, max_length=255)
    transaction_date  = models.DateField(default=timezone.now)
    transaction_status= models.CharField(max_length=25,default="pending",choices=TRANSACTION_STATUS)
    class Meta:
        unique_together = ['transaction_id', 'upi_address']