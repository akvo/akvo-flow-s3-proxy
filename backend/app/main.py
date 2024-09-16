from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, UploadFile, status
from starlette.responses import StreamingResponse

from app.dependencies import bucket_factory
from app.flow_config import get_config
from app.messages import ResultMessage
from app.s3 import S3Bucket

FormIdParam = Annotated[str, Path(pattern=r"^\d+$")]
app = FastAPI()


def validate_form_id(form_id: str) -> None:
    # TODO: form id validation
    if not form_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)  # pragma: no cover


def get_config_for(instance: str) -> dict[str, str]:
    config = get_config(instance)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return config


async def upload(
    instance: str,
    form_id: str,
    file: UploadFile,
    folder: str,
    make_bucket: Callable[[str, str, str], S3Bucket],
) -> ResultMessage:
    config = get_config_for(instance)
    validate_form_id(form_id)
    bucket = make_bucket(
        str(config.get("awsBucket")),
        str(config.get("awsAccessKeyId")),
        str(config.get("awsSecretKey")),
    )
    extra_args = {"ContentType": file.content_type}
    if folder == "images":
        extra_args["ACL"] = "public-read"
    file_key = f"{folder}/{str(file.filename)}"
    bucket.upload(file.file, file_key, extra_args)
    return ResultMessage.success("OK!")


@app.put("/{instance}/devicezip/{form_id}/", status_code=status.HTTP_201_CREATED)
async def put_devicezip(
    instance: str,
    form_id: FormIdParam,
    file: UploadFile,
    make_bucket: Annotated[
        Callable[[str, str, str], S3Bucket], Depends(bucket_factory)
    ],
) -> ResultMessage:
    return await upload(instance, form_id, file, "devicezip", make_bucket)


@app.put("/{instance}/images/{form_id}/", status_code=status.HTTP_201_CREATED)
async def put_images(
    instance: str,
    form_id: FormIdParam,
    file: UploadFile,
    make_bucket: Annotated[
        Callable[[str, str, str], S3Bucket], Depends(bucket_factory)
    ],
) -> ResultMessage:
    return await upload(instance, form_id, file, "images", make_bucket)


@app.get("/{instance}/surveys/{form_id}.zip")
async def get_survey_form(
    instance: str,
    form_id: FormIdParam,
    make_bucket: Annotated[
        Callable[[str, str, str], S3Bucket], Depends(bucket_factory)
    ],
) -> StreamingResponse:
    config = get_config_for(instance)
    validate_form_id(form_id)
    bucket = make_bucket(
        str(config.get("awsBucket")),
        str(config.get("awsAccessKeyId")),
        str(config.get("awsSecretKey")),
    )

    try:
        res = bucket.download(f"surveys/{form_id}.zip")
        return StreamingResponse(
            content=res["Body"].iter_chunks(), media_type=res["ContentType"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@app.get("/{instance}/images/{filename}")
async def get_image(
    instance: str,
    filename: str,
    make_bucket: Annotated[
        Callable[[str, str, str], S3Bucket], Depends(bucket_factory)
    ],
) -> StreamingResponse:
    config = get_config_for(instance)
    bucket = make_bucket(
        str(config.get("awsBucket")),
        str(config.get("awsAccessKeyId")),
        str(config.get("awsSecretKey")),
    )

    try:
        res = bucket.download(f"images/{filename}")
        return StreamingResponse(
            content=res["Body"].iter_chunks(), media_type=res["ContentType"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@app.get("/healtz", include_in_schema=False)
async def healt_check() -> ResultMessage:
    return ResultMessage.success("OK!")
