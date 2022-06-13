from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart
from django.conf import settings
from django.core.mail import send_mail
from .models import Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
import os

import random
# Create your views here.
def index(request):
	return render(request,'index.html')
def signup(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			msg='email alredy register'
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					usertype=request.POST['usertype'],
					password=request.POST['password'],
					dob=request.POST['dob'],
					)
				msg='sign up sucessffuly'
				return render(request,'signup.html',{'msg':msg})
			else:
				msg='password and confirm password does not match'
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')


def home(request):
	products=Product.objects.all()
	return render(request,'home.html',{'products':products})

def login(request):
	if request.method=='POST':
		try:
			user=User.objects.get(
					email=request.POST['email'],
					password=request.POST['password'],
					)
			if user.usertype=='user':
				request.session['email']=user.email
				request.session['fname']=user.fname
				carts=Cart.objects.filter(user=user,status='pending')
				for i in carts:
					net_price=net_price+i.total_price
				return render(request,'home.html',{'user':user})
			else:
				request.session['email']=user.email
				request.session['fname']=user.fname
				return redirect('seller_home')

		except Exception as e:
			print(e)
			msg='email id and password does not match'
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.email=request.POST['email']
		user.mobile=request.POST['mobile']
		user.dob=request.POST['dob']
		user.save()
		msg='user update sucessffuly'
		return render(request,'profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'profile.html',{'user':user})

def seller_header(request):
	return render(request,'seller_header.html')



def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			print(user)
			subject = 'OTP For Forgot Password'
			otp=random.randint(1000,9999)
			message = 'Your OTP For Forgot Password Is '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email,]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'otp':otp,'email':user.email})
		except Exception as e:
			print(e)
			msg="Email Not Registered"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def verify_otp(request):
	otp=request.POST['otp']
	email=request.POST['email']
	uotp=request.POST['uotp']
	if otp==uotp:
		return render(request,'change_password.html',{'email':email})
	else:
		msg='otp does not match'
		return render(request,'verify_otp',{'msg':msg,'email':email,'otp':otp})
	
def change_password(request):
	npassword=request.POST['npassword']
	cpassword=request.POST['cpassword']
	email=request.POST['email']
	if request.POST['npassword']==request.POST['cpassword']:
		user=User.objects.get(email=request.POST['email'])
		user.password=npassword
		user.save()
		return render(request,'login.html')
	else:
		msg='password and confirm password does not match'
		return render(request,'change_password.html',{'user':user})
	
def single_product(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist_flag=False
	try:
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	cart_flag=False
	try:
		Cart.objects.get(user=user,product=product)
		cart_flag=True
	except:
		pass
	return render(request,'single_product.html',{'product':product,'wishlist_flag':wishlist_flag ,'cart_flag':cart_flag})	

def seller_home(request):
	products=Product.objects.all()
	return render(request,'seller_home.html',{'products':products})	

def seller_add_product(request):
	if request.method=='POST':
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
			seller=seller,
			product_name=request.POST['product_name'],
			product_price=request.POST['product_price'],
			product_width=request.POST['product_width'],
			product_hight=request.POST['product_hight'],
			product_depth=request.POST['product_depth'],
			product_category=request.POST['product_category'],
			product_pic=request.FILES['product_pic'],
			product_weight=request.POST['product_weight'],
			)
		msg='product add sucessffuly'
		return render(request,'seller_add_product.html',{'msg':msg})
	else:
		return render(request,'seller_add_product.html')

def seller_edit_product(request,pk):
	products=Product.objects.get(pk=pk)
	if request.method=='POST':
		products.product_name=request.POST['product_name']
		products.product_width=request.POST['product_width']
		products.product_weight=request.POST['product_weight']
		products.product_hight=request.POST['product_hight']
		products.product_depth=request.POST['product_depth']
		products.product_price=request.POST['product_price']
		products.product_category=request.POST['product_category']
		try:
			products.product_pic=request.FILES['product_pic']
		except:
			pass
		products.save()
		msg='product  update sucessffuly'
		return render(request,'seller_edit_product.html',{'products':products,'msg':msg})
	else:
		return render(request,'seller_edit_product.html',{'products':products})

def seller_product_details(request,pk):
	products=Product.objects.get(pk=pk)
	return render(request,'seller_product_details.html',{'products':products})

def seller_product_delete(request,pk):
	products=Product.objects.get(pk=pk)
	products.delete()
	return redirect('seller_home')

def add_to_wishlist(request,pk):
	if 'email' in request.session:
		product=Product.objects.get(pk=pk)
		user=User.objects.get(email=request.session['email'])
		Wishlist.objects.create(
			product=product,
			user=user,
					)
		return render(request,'wishlist.html')
	else:

		return render(request,'wishlist.html')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.filter(user=user)
	return render(request,'wishlist.html',{'wishlist':wishlist,'user':user})

def remove_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.filter(user=user)
	wishlist.delete()
	return redirect('wishlist')

def add_to_cart(request,pk):
	if 'email' in request.session:
		product=Product.objects.get(pk=pk)
		user=User.objects.get(email=request.session['email'])
		Cart.objects.create(
			product=product,
			user=user,
			product_price=product.product_price,
			total_price=product.product_price
					)
		return render(request,'cart.html')
	else:
		return render(request,'cart.html')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status='pending')
	for i in carts:
		net_price=net_price+i.total_price
	request.session['net_price']=net_price
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_to_cart(request,pk):
	products=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.filter(user=user)
	cart.delete()
	return redirect('home')


def change_qty(request,pk):
	carts=Cart.objects.get(pk=pk)
	product_qty=int(request.POST['product_qty'])
	carts.product_qty=product_qty
	carts.product_total=carts.product_price*product_qty
	carts.save()
	return redirect('cart')


def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	try:
		amount = int(request.POST['amount'])

	except:
		return render(request, 'cart.html', context={'error': 'Wrong Accound Details or amount'})

	transaction = Transaction.objects.create(made_by=user, amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY

	params = (
		('MID', settings.PAYTM_MERCHANT_ID),
		('ORDER_ID', str(transaction.order_id)),
		('CUST_ID', str('usahu3589@gmail.com')),
		('TXN_AMOUNT', str(transaction.amount)),
		('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
		('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
        )

	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)

	transaction.checksum = checksum
	transaction.save()
	carts=Cart.objects.filter(user=user)
	for i in carts:
		i.status='paid'
		i.save()

		paytm_params['CHECKSUMHASH'] = checksum
		print('SENT: ', checksum)
		return render(request, 'redirect.html', context=paytm_params)
@csrf_exempt
def callback(request):
	if request.method == 'POST':
		received_data = dict(request.POST)
		paytm_params = {}
		paytm_checksum = received_data['CHECKSUMHASH'][0]
		for key, value in received_data.items():
			if key == 'CHECKSUMHASH':
				paytm_checksum = value[0]
			else:
				paytm_params[key] = str(value[0])
		# Verify checksum
		is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
		if is_valid_checksum:
			received_data['message'] = "Checksum Matched"
		else:
			received_data['message'] = "Checksum Mismatched"
			return render(request, 'callback.html', context=received_data)
		return render(request, 'callback.html', context=received_data)
