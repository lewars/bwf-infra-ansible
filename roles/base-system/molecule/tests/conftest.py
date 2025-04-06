import os
import pytest

@pytest.fixture(scope="module")
def host(request):
    from testinfra.backend.ansible import AnsibleBackend
    inventory = os.environ.get('MOLECULE_INVENTORY_FILE')
    if inventory is None:
        pytest.skip("No ansible inventory file was found")
    return AnsibleBackend(inventory).get_host('all')
