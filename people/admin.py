from django.contrib import admin

# Register your models here.
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Trained_Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Option, Answer, Role_History, \
					ABSS_Type, Age_Status, Street, Answer_Note, Site, Activity_Type, Activity, Filter_Spec, \
					Panel_Column, Panel_Column_In_Panel, Panel, \
					Column, Panel_In_Column, Dashboard, Column_In_Dashboard

class PersonAdmin(admin.ModelAdmin):
    search_fields = ['first_name','last_name']

class EventAdmin(admin.ModelAdmin):
    search_fields = ['name']

class AnswerAdmin(admin.ModelAdmin):
	list_display = ['person','__str__']
	search_fields = ['person__last_name']

admin.site.register(Person, PersonAdmin)
admin.site.register(Relationship_Type)
admin.site.register(Relationship)
admin.site.register(Family)
admin.site.register(Ethnicity)
admin.site.register(Trained_Role)
admin.site.register(Role_Type)
admin.site.register(Children_Centre)
admin.site.register(CC_Registration)
admin.site.register(Area)
admin.site.register(Ward)
admin.site.register(Post_Code)
admin.site.register(Event, EventAdmin)
admin.site.register(Event_Type)
admin.site.register(Event_Category)
admin.site.register(Event_Registration)
admin.site.register(Capture_Type)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Role_History)
admin.site.register(ABSS_Type)
admin.site.register(Age_Status)
admin.site.register(Street)
admin.site.register(Answer_Note)
admin.site.register(Site)
admin.site.register(Activity_Type)
admin.site.register(Activity)
admin.site.register(Filter_Spec)
admin.site.register(Panel_Column)
admin.site.register(Panel_Column_In_Panel)
admin.site.register(Panel)
admin.site.register(Column)
admin.site.register(Panel_In_Column)
admin.site.register(Dashboard)
admin.site.register(Column_In_Dashboard)