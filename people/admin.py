from django.contrib import admin

# Register your models here.
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Address, Residence, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Option, Answer, Role_History

admin.site.register(Person)
admin.site.register(Relationship_Type)
admin.site.register(Relationship)
admin.site.register(Family)
admin.site.register(Ethnicity)
admin.site.register(Role)
admin.site.register(Role_Type)
admin.site.register(Children_Centre)
admin.site.register(CC_Registration)
admin.site.register(Area)
admin.site.register(Ward)
admin.site.register(Post_Code)
admin.site.register(Address)
admin.site.register(Residence)
admin.site.register(Event)
admin.site.register(Event_Type)
admin.site.register(Event_Category)
admin.site.register(Event_Registration)
admin.site.register(Capture_Type)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Answer)
admin.site.register(Role_History)