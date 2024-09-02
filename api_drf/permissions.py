from rest_framework import permissions

from DRF_DIAP.settings import ALLOW_IP_API


class IplistPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']
        for i in ALLOW_IP_API:
            for k, v in i.items():
                if v == ip_addr:
                    return True
        return False

