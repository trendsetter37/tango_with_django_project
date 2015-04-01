from django.contrib import admin
from rango.models import Category, Page, UserProfile

# Register your models here.

class PageInline(admin.TabularInline):
	model = Page
	extra = 1
	

class PageAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields':['title','category']}),

		('Information', {'fields':['title', 'url','views'],
						 'classes': ['collapse']})
	]
	list_display = ('title','category', 'url')

class CategoryAdmin(admin.ModelAdmin):
	# fields = ['name', 'views', 'likes']

	# Or fieldsets for organization
	fieldsets = [
		(None, {'fields' : ['name', 'slug']}),
		('Popularity', {'fields' : ['views', 'likes'],
						'classes': ['collapse']})
	]

	inlines = [PageInline]
	list_display = ('name', 'views', 'likes')
	search_fields = ['name']
	prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)