from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


# Create your models here.
class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	dob=models.DateField()
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	usertype=models.CharField(max_length=100)
	password=models.CharField(max_length=100,default='')

	def __str__(self):
		return self.fname +'='+ self.lname

class Product(models.Model):
	seller=models.ForeignKey(User,on_delete=models.CASCADE)
	product_name=models.CharField(max_length=100)
	product_price=models.CharField(max_length=100)
	product_category=models.CharField(max_length=100)
	product_width=models.CharField(max_length=100)
	product_hight=models.CharField(max_length=100)
	product_depth=models.CharField(max_length=100)
	product_weight=models.CharField(max_length=100)
	product_pic=models.ImageField(upload_to='prouct_pic')

	def __str__(self):
		return self.seller.fname +'='+ self.product_name

class Wishlist(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	time=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+ '='+self.product.product_name

class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	time=models.DateTimeField(default=timezone.now)
	product_qty=models.IntegerField(default=1)
	product_price=models.IntegerField()
	total_price=models.IntegerField()
	status=models.CharField(max_length=100,default='pending')
	def __str__(self):
		return self.user.fname+ '='+self.product.product_name

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
