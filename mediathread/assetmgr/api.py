from mediathread.api import ClassLevelAuthentication, UserResource, \
    ToManyFieldEx, TagResource
from mediathread.assetmgr.models import Asset
from tagging.models import Tag
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
import simplejson


class AssetAuthorization(Authorization):

    def apply_limits(self, request, object_list):

        invisible = []
        for asset in object_list:
            if not asset.course.is_member(request.user):
                invisible.append(asset.id)

        object_list = object_list.exclude(id__in=invisible)
        return object_list.order_by('id')


class AssetResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    sherdnote_set = ToManyFieldEx(
        'mediathread.djangosherd.api.SherdNoteResource',
        'sherdnote_set',
        blank=True, null=True, full=True)

    class Meta:
        queryset = Asset.objects.all().order_by('id')
        excludes = ['added', 'modified', 'course', 'active', 'metadata_blob']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = AssetAuthorization()

        ordering = ['id', 'title']

        filtering = {
            'author': ALL_WITH_RELATIONS,
            'sherdnote_set': ALL_WITH_RELATIONS
        }

    def apply_filters(self, request, applicable_filters):
        qs = self.get_object_list(request).filter(**applicable_filters)
        return qs.distinct()

    def dehydrate(self, bundle):
        bundle.data['thumb_url'] = bundle.obj.thumb_url
        bundle.data['primary_type'] = bundle.obj.primary.label
        bundle.data['local_url'] = bundle.obj.get_absolute_url()
        bundle.data['media_type_label'] = bundle.obj.media_type()

        try:
            metadata = simplejson.loads(bundle.obj.metadata_blob)
            metadata = [{'key': k, 'value': v} for k, v in metadata.items()]
            bundle.data['metadata'] = metadata
        except ValueError:
            pass

        sources = {}
        for s in bundle.obj.source_set.all():
            sources[s.label] = {'label': s.label,
                                'url': s.url_processed(bundle.request),
                                'width': s.width,
                                'height': s.height,
                                'primary': s.primary}
        bundle.data['sources'] = sources

        tags = Tag.objects.usage_for_queryset(bundle.obj.sherdnote_set.all(),
                                              counts=True)
        bundle.data['tags'] = TagResource().render_list(bundle.request, tags)

        return bundle

    def render_one(self, request, item):
        bundle = self.build_bundle(obj=item, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)

    def render_list(self, request, lst):
        data = []
        for item in lst:
            bundle = self.build_bundle(obj=item, request=request)
            dehydrated = self.full_dehydrate(bundle)
            data.append(dehydrated.data)
        return data