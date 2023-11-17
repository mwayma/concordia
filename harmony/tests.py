from django.test import TestCase
from .models import ConnectWiseConfig
from .forms import ConnectWiseConfigForm

class ConnectWiseConfigTestCase(TestCase):
    def setUp(self):
        # Create a ConnectWiseConfig instance for testing
        self.config = ConnectWiseConfig.objects.create(
            base_url='https://example.com',
            company_id='example_company',
            api_public_key='public_key',
            api_private_key='initial_private_key',
        )

    def test_private_key_not_saved_as_null(self):
        # Simulate editing the form with a null private key
        form_data = {
            'base_url': 'https://example.com',
            'company_id': 'example_company',
            'api_public_key': 'public_key',
            'api_private_key': None,  # Simulating null private key
        }

        # Instantiate the form with the instance data
        form = ConnectWiseConfigForm(data=form_data, instance=self.config)

        # Validate the form
        self.assertTrue(form.is_valid())

        # Save the form
        form.save()

        # Reload the instance from the database
        updated_config = ConnectWiseConfig.objects.get(pk=self.config.pk)

        # Ensure that the private key is not saved as null
        self.assertNotEqual(updated_config.api_private_key, None)
