from django.test import TestCase
from people.forms import ProfileForm

class ProfileFormTest(TestCase):

	def test_active_champion_not_trained_champion(self):
		# create the form
		profileform = ProfileForm(
									data={
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'english_is_second_language' : '',
											'pregnant' : '',
											'due_date' : '01/01/2020',
											'role_type' : '2',
											'ethnicity' : '2',
											'ABSS_type' : '2',
											'age_status' : '2',
											'trained_champion' : '',
											'active_champion' : 'on'
											}
									)
		# validate the form
		profileform.is_valid()
		# now check that we got an error
		self.assertTrue(profileform.errors) 
