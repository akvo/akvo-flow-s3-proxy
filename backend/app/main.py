from collections.abc import Awaitable, Callable
from functools import partial
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, UploadFile, status
from starlette.responses import StreamingResponse

from app.dependencies import provide_make_bucket, provide_make_form_validator
from app.flow_config import (
    get_config,
)
from app.form_validator import FormValidator
from app.messages import ResultMessage
from app.s3 import S3Bucket

FormIdParam = Annotated[str, Path(pattern=r"^\d+$")]
VersionedFormIdParam = Annotated[str, Path(pattern=r"^\d+(v\d+.0)?$")]
app = FastAPI()


def validate_form_id(form_id: int, validator: FormValidator) -> None:
    form_exists = validator.validate(form_id)
    if not form_id or not form_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def get_config_for(instance: str) -> dict[str, str]:
    config = get_config(instance)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return config


async def upload(
    instance: str,
    form_id: str,
    filename: str,
    file: UploadFile,
    folder: str,
    make_bucket: Callable[[dict[str, str]], S3Bucket],
    make_form_validator: Callable[[dict[str, str]], FormValidator],
) -> ResultMessage:
    config = get_config_for(instance)
    form_validator = make_form_validator(config)
    validate_form_id(int(form_id), form_validator)
    bucket = make_bucket(config)
    extra_args = {"ContentType": file.content_type}
    if folder == "images":
        extra_args["ACL"] = "public-read"
    file_key = f"{folder}/{str(filename)}"
    bucket.upload(file.file, file_key, extra_args)
    return ResultMessage.success("OK!")


def provide_upload(
    make_bucket: Annotated[
        Callable[[dict[str, str]], S3Bucket], Depends(provide_make_bucket)
    ],
    make_form_validator: Annotated[
        Callable[[dict[str, str]], FormValidator], Depends(provide_make_form_validator)
    ],
) -> Callable[[str, str, str, UploadFile, str], Awaitable[ResultMessage]]:
    return partial(
        upload, make_bucket=make_bucket, make_form_validator=make_form_validator
    )


@app.put(
    "/{instance}/devicezip/{form_id}/{filename}", status_code=status.HTTP_201_CREATED
)
async def put_devicezip(
    instance: str,
    form_id: FormIdParam,
    filename: str,
    file: UploadFile,
    upload: Annotated[
        Callable[[str, str, str, UploadFile, str], Awaitable[ResultMessage]],
        Depends(provide_upload),
    ],
) -> ResultMessage:
    return await upload(instance, form_id, filename, file, "devicezip")


@app.put("/{instance}/images/{form_id}/{filename}", status_code=status.HTTP_201_CREATED)
async def put_images(
    instance: str,
    form_id: FormIdParam,
    filename: str,
    file: UploadFile,
    upload: Annotated[
        Callable[[str, str, str, UploadFile, str], Awaitable[ResultMessage]],
        Depends(provide_upload),
    ],
) -> ResultMessage:
    return await upload(instance, form_id, filename, file, "images")


@app.get("/{instance}/surveys/{versioned_form_id}.zip")
async def get_survey_form(
    instance: str,
    versioned_form_id: VersionedFormIdParam,
    make_bucket: Annotated[
        Callable[[dict[str, str]], S3Bucket], Depends(provide_make_bucket)
    ],
    make_form_validator: Annotated[
        Callable[[dict[str, str]], FormValidator], Depends(provide_make_form_validator)
    ],
) -> StreamingResponse:
    config = get_config_for(instance)
    form_id = versioned_form_id.split("v")[0]
    form_validator = make_form_validator(config)
    validate_form_id(int(form_id), form_validator)
    bucket = make_bucket(config)

    try:
        res = bucket.download(f"surveys/{versioned_form_id}.zip")
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
        Callable[[dict[str, str]], S3Bucket], Depends(provide_make_bucket)
    ],
) -> StreamingResponse:
    config = get_config_for(instance)
    bucket = make_bucket(config)

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
