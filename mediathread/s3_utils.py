from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import get_storage_class


MediaRootS3BotoStorage = lambda: S3BotoStorage(
    bucket_name='mediathread-media'
)


class CachedStaticRootS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = 'mediathread-static'
        kwargs['reduced_redundancy'] = True
        kwargs['gzip'] = True
        super(CachedStaticRootS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedStaticRootS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name
