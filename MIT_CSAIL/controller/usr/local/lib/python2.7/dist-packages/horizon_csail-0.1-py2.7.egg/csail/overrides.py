import logging

from django.utils.text import normalize_newlines  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import forms
from horizon import exceptions

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances import views
from openstack_dashboard.dashboards.project.instances.workflows import \
    create_instance


LOG = logging.getLogger(__name__)


class CSAIL_SetInstanceDetailsAction(create_instance.SetInstanceDetailsAction):
    class Meta:
        name = _("Details")
        help_text_template = ("project/instances/"
                              "_launch_details_help.html")

    def __init__(self, request, context, *args, **kwargs):
        super(CSAIL_SetInstanceDetailsAction, self).__init__(
            request, context, *args, **kwargs)
        fixed_ip = forms.CharField(
            widget=forms.TextInput, label=_("eth0 Fixed IP"), max_length=15,
            required=False, help_text=_("Fixed IP you registered in WebDNS"))
        self.fields.insert(4, 'fixed_ip', fixed_ip)


class CSAIL_SetInstanceDetails(create_instance.SetInstanceDetails):
    action_class = CSAIL_SetInstanceDetailsAction
    contributes = ("source_type", "source_id",
                   "availability_zone", "name", "count", "flavor",
                   "device_name",  # Can be None for an image.
                   "delete_on_terminate", "fixed_ip")


class CSAIL_LaunchInstance(create_instance.LaunchInstance):
    def __init__(self, *args, **kwargs):
        steps = list(self.default_steps)
        replace_index = None
        for i, step in enumerate(steps):
            if step.__name__ == 'SetInstanceDetails':
                replace_index = i
                break
        if replace_index is not None:
            steps[i] = CSAIL_SetInstanceDetails
            self.default_steps = tuple(steps)
        return super(CSAIL_LaunchInstance, self).__init__(*args, **kwargs)

    @sensitive_variables('context')
    def handle(self, request, context):
        custom_script = context.get('customization_script', '')
        dev_mapping_1 = None
        dev_mapping_2 = None
        image_id = ''
        # Determine volume mapping options
        source_type = context.get('source_type', None)
        if source_type in ['image_id', 'instance_snapshot_id']:
            image_id = context['source_id']
        elif source_type in ['volume_id', 'volume_snapshot_id']:
            dev_mapping_1 = {
                context['device_name']: '%s::%s' %
                (context['source_id'],
                 int(bool(context['delete_on_terminate'])))}
        elif source_type == 'volume_image_id':
            dev_mapping_2 = [
                {'device_name': str(context['device_name']),
                 'source_type': 'image',
                 'destination_type': 'volume',
                 'delete_on_termination':
                 int(bool(context['delete_on_terminate'])),
                 'uuid': context['source_id'],
                 'boot_index': '0',
                 'volume_size': context['volume_size']
                 }
            ]
        netids = context.get('network_id', None)
        fixed_ip = context.get('fixed_ip', None)
        if netids:
            nics = [{"net-id": netid, "v4-fixed-ip": fixed_ip}
                    for netid in netids]
        else:
            nics = None

        avail_zone = context.get('availability_zone', None)

        # Create port with Network Name and Port Profile
        # for the use with the plugin supporting port profiles.
        # neutron port-create <Network name> --n1kv:profile <Port Profile ID>
        # for net_id in context['network_id']:
        ## HACK for now use first network
        if api.neutron.is_port_profiles_supported():
            net_id = context['network_id'][0]
            LOG.debug("Horizon->Create Port with %(netid)s %(profile_id)s",
                      {'netid': net_id, 'profile_id': context['profile_id']})
            try:
                port = api.neutron.port_create(request, net_id,
                                               policy_profile_id=
                                               context['profile_id'])
            except Exception:
                msg = (_('Port not created for profile-id (%s).') %
                       context['profile_id'])
                exceptions.handle(request, msg)
            if port and port.id:
                nics = [{"port-id": port.id}]

        try:
            api.nova.server_create(request,
                                   context['name'],
                                   image_id,
                                   context['flavor'],
                                   context['keypair_id'],
                                   normalize_newlines(custom_script),
                                   context['security_group_ids'],
                                   block_device_mapping=dev_mapping_1,
                                   block_device_mapping_v2=dev_mapping_2,
                                   nics=nics,
                                   availability_zone=avail_zone,
                                   instance_count=int(context['count']),
                                   admin_pass=context['admin_pass'])
            return True
        except Exception:
            exceptions.handle(request)
            return False

views.LaunchInstanceView.workflow_class = CSAIL_LaunchInstance
