from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, CompanyMapping, ConnectWiseSite
from harmony.connectwise import *
from harmony.dataverse import *

### Version 1 is a one-way sync from ConnectWise to Dataverse.  This is for creating a new environment, not for an existing one with duplicate data.  Create new Accounts and Contacts if none are locally mapped in the database.
### Attempt to map the new CustomerAddress to a ConnectWise Site.  