import os
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')
from rango.models import Category, Page
import django

django.setup()

# Category List
cat_list = ['Python', 'Django', 'Other Frameworks']

# dictionary of pages and urls associated with their categories
page_dict = {
		'Python' : [	 # list of tuples
			('Official Python Tutorial', 'http://docs.python.org/2/tutorial/'),
			('How to Think Like a Computer Scientist', 'http://www.greenteapress.com/thinkpython/'),
			('Learn Python in 10 Minutes', 'http://www.korokithakis.net/tutorials/python/')
		],

		'Django' : [
			('Official Django Tutorial', 'https://docs.djangoproject.com/en/1.5/intro/tutorial101/'),
			('Django Rocks', 'http://www.djangorocks.com/'),
			('How to Tango with Django', 'http://www.tangowithdjango.com')
		],

		'Other Frameworks' : [
			('Bottle', 'http://bottlepy.org/docs/dev/'),
			('Flask', 'http://flask.pocoo.org')
		]
	}

def populate(cat_list, page_dict):
	''' Will re-write this to make it more DRY maybe 
		original can be found at 
		********************************
		http://www.tangowithdjango.com/book17/chapters/models.html
		
		'''
	Category.objects.all().delete()
	print("Wiped categories")
	for cat in cat_list:
		print("Category -- {0}".format(cat)) 	
		c = Category.objects.get_or_create(name=cat)[0]
		if cat == 'Python':
			c.views = 128
			c.likes = 64
		elif cat == 'Django':
			c.views = 64
			c.likes = 32
		elif cat == 'Other Frameworks':
			c.views = 32
			c.likes = 16
		''' Returns a tuple of (object, created), where object is the retrieved or 
			created object and created is a boolean specifying whether a new object
			was created. Hence the [0] at the end.
			************************************************************
			https://docs.djangoproject.com/en/1.7/ref/models/querysets/#get-or-create
			**************************************************************
			'''
		c.save()
		add_page(cat, page_dict, c.id) # pass entire page_dict to add_page

def add_page(cat, page_list, category_id, views=0):
	''' should check to see if cat matches with category before entering loop to fill '''
	resources = page_list[cat] # a list of tuples
	# populate random view counts
	
	for r in resources:
		p = Page.objects.get_or_create(category_id=category_id, title=r[0])[0] 
		p.url = r[1] 
		p.views = random.randrange(10000)
		p.save()

		print("{0} page in the {1} category was created.\nIt contains {2} views."\
			.format(p.title, cat, p.views))

	
if __name__ == "__main__":
	print("Starting rango db population script...")
	# clear table because some corruption happend
	# Then populate
	Page.objects.all().delete()
	print("Page table cleared")
	populate(cat_list, page_dict)
	print("Population script complete.\n\nHave a nice day!")
