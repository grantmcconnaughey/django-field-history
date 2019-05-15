import django.dispatch


post_field_history_bulk_create = django.dispatch.Signal(
	providing_args=['tracked_instance', 'field_history_instances'])
