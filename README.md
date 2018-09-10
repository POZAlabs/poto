# poto
boto3 wrapper

## config.json contains
```
{
    "service_name" : "s3",
    "endpoint_url" : "https://kr.objectstorage.ncloud.com",
    "region_name" : "kr-standard",
    "access_key" : "...",
    "secret_key" : "..."
}
```

## BUCKET 규칙
BUCKET 아래에는 단 하나의 디렉토리 오브젝트만 가질 수 있다.
e.g.) ok
```
BUCKET
    dir1
        object1
        object2
        object3
        ...
    dir2
        object1
        object2
        object3
        ...
```
e.g.) `Not acceptable`
```
BUCKET
    dir1
        sub dir1
            object1
            object2
            object3
            ...
```

