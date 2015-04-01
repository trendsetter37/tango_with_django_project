from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from datetime import datetime


def index(request):
	

	# request.session.set_test_cookie() Successfull

	# Construct a dictionary to pass as context to the index template
	# Note that the key 'boldmessage' is the same as {{ boldmessage }}
	# in the template
	category_list = Category.objects.order_by('-likes')[:5]
	top_five_pages = Page.objects.order_by('-views')[:5]
	context_dict = {'home_page'		 : True,
					'categories'     : category_list,
					'top_five_pages' : top_five_pages}

	# Get the number of visists to the site.
	# We use the COOKIES.get() function to obtain the visits cookie.
	# If the cookie exists, the value returned is casted to an integer.
	# If the cookie doesn't exist, we default to zero and cast that.

	visits = request.session.get('visits')


	reset_last_visit_time = False
	#response = render(request, 'rango/index.html', context_dict, context_instance=context)
	# Does the cookie last_visit exist?
	'''
	if 'last_visit' in request.COOKIES:
		last_visit = request.COOKIES['last_visit']
		# Cast the value to a Python date/time object.
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		# If it's been more than a day since the last visit...
		if (datetime.now() - last_visit_time).seconds > 5:
			visits += 1
			# ... and flag that the cookie last visit needs to be updated
			reset_last_visit_time = True

		context_dict['visits'] = visits
		context_dict['last_visit_time'] = last_visit_time
	else:
		# Cookie last_visit doesn't exist, so flag that it should be set.
		reset_last_visit_time = True

		context_dict['visits'] = visits

		# Obtain our Response object early so we can add cookie information.
		response = render(request, 'rango/index.html', context_dict)

	if reset_last_visit_time:
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', visits)

		# Return response back to the user, updating any cookies that need changed.'''
	if not visits:
		visits = 1
	reset_last_visit_time = False

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).seconds > 0:
			visits += 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True

	if reset_last_visit_time == True:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits
	context_dict['visits'] = visits
	response = render(request, 'rango/index.html', context_dict)

	return response
	
	

def about(request):
	context = { 'title' : 'About Page'}

	return render(request, 'rango/about.html', context)

def category(request, category_name_slug):

	context_dict = {}

	try:
		category = Category.objects.get(slug=category_name_slug)
		
		context_dict['category_name'] = category.name

		# Now get associated pages
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages

		# will also add category object
		context_dict['category'] = category
		context_dict['category_name_slug'] = category_name_slug
	except Category.DoesNotExist:
		
		context_dict = { 'category' : category_name_slug }
		return render_to_response('rango/category_does_not_exist.html', context_dict)
		

	return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request, placeholder=''):
	# HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# valid form provided?
		if form.is_valid():
			# Save the new category to the database
			form.save(commit=True)

			# Now call the index() view.
			# The user will be shown the homepage
			# return index(request) deprecated
			return redirect('rango:index')
		else:
			# The supplied form contained errors
			print(form.errors)
	else:
		# If the request was not a POST, display the form to enter details.
		if placeholder == '':
			form = CategoryForm()
		else:
			form = CategoryForm(initial={ 'name' : placeholder })
		# form = CategoryForm()
	return render(request, 'rango/add_category.html', {'form':form})

@login_required
def add_page(request, category_name_slug):

	try:
		cat = Category.objects.get(slug=category_name_slug)
		
	except Category.DoesNotExist:
		cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():

			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				# probably better to use redirect here.
			return category(request, category_name_slug)

		else:
			print(form.errors)
	else:
		#If the request was not a post show form so that you can enter
		# the details
		form = PageForm()
		context_dict = {'form':form, 'category':cat, 'category_name_slug': category_name_slug}
		return render(request, 'rango/add_page.html', context_dict)
	
def register(request):
	''' A boolean value for telling the template the 
		registration was successful. Set to False
		initially. Code changes value to True when 
		registration succeeds.
		'''

	registered = False

	# If it's a HTTP POST, we're interested in processing form
	# information
	if request.method == 'POST':

		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm

		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance.
			# Since we neet to set the user attribute ourselves, we set commit=False.
			# This delays saving the model until we're ready to avoid integrity problems.

			profile = profile_form.save(commit=False)
			profile.user = user

			# did the user provide a profile picture?
			# If so, we need to get it from the input from and put it in the UserProfile
			# model.

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance
			profile.save()

			# Update our variable to tell the template registration was successful
			registered = True
		else:
			print(user_form.errors, profile_form.errors)

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		user_form = UserForm()
		profile_form = UserProfileForm

	# Render the template depending on the context.
	context_dict = { 'user_form'    : user_form,
					 'profile_form' : profile_form,
					 'registered'   : registered }

	return render(request, 'rango/register.html', context_dict)

def user_login(request):

	# If the request is a HTTP POST, try to pull out relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
			# We use request.POST.get('<variable>') as opposed to 
			# request.POST['<variable>'], because the request.POST.get('<variable>')
			# returns None, if the value does not exist,
			# while the reques.POST['<variable>'] will raise an error exception
		username = request.POST.get('username')
		password = request.POST.get('password')

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.

		if user:
			# Is the account active? I could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				# An inactive account was used - no loggin in!
				return HttpResponseRedirect('Your Rango account is disabled.')
		else:
			# Bad login details were provided. So we can't log the user in.
			print("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")

	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'rango/login.html', {})

def user_logout(request):
	# Since we know the user is logged in, we can now just Log them out.
	logout(request)

	# Take the user back to the homepage
	return HttpResponseRedirect('/rango/')

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")
