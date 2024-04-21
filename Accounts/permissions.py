from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import BusManager,BusOwner

def createPermissions():
    admin_permissions=[ 
    'can_manage_users'
    ]
    owner_permissions=['can_manage_managers','can_view_buses']
    manager_permissions=['can_manage_bus','can_manage_drivers','can_manage_passengers']
    
    bus_owner_content_type = ContentType.objects.get_for_model(BusOwner)
    bus_manager_content_type = ContentType.objects.get_for_model(BusManager)
    
    for permission in owner_permissions:
        if not Permission.objects.filter(content_type=bus_owner_content_type).exists():
            Permission.objects.create(
                codename=permission,
                name=permission.replace('_', ' ').capitalize(),
                content_type=bus_owner_content_type,
            )
    for permission in manager_permissions:
        if not Permission.objects.filter(content_type=bus_manager_content_type).exists():
            Permission.objects.create(
                codename=permission,
                name=permission.replace('_', ' ').capitalize(),
                content_type=bus_manager_content_type,
            )
    