from my_admin.service.sites import ModelMyAdmin,site
from rbac.models import User,Permission,Role


site.register(User)


class RoleConfig(ModelMyAdmin):
    search_fields = ["name"]
    list_filter = ["permissions"]


site.register(Role,RoleConfig)


class PermissionConfig(ModelMyAdmin):
    list_display = ["title","url","code"]
    list_display_links = ["title"]


site.register(Permission,PermissionConfig)