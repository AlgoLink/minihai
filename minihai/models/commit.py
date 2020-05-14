import os
import shutil
import tempfile

from fastapi import UploadFile
from valohai_cli.utils.hashing import get_fp_sha256

from minihai.conf import settings
from minihai.models.base import BaseModel


class Commit(BaseModel):
    kind = "commit"

    @property
    def tarball_path(self):
        return self.path / "tarball"

    @property
    def exists(self) -> bool:
        return super().exists and self.tarball_path.exists()

    @classmethod
    def create_from_data(cls, data: UploadFile, description: str = "") -> "Commit":
        file = data.file
        commit_identifier = "~{hash}".format(hash=get_fp_sha256(file))
        fd, tarball_temp_path = tempfile.mkstemp(
            dir=settings.data_path, prefix="upload-"
        )
        # TODO: validate tarball?
        with open(fd, "wb") as outf:
            data.file.seek(0)
            shutil.copyfileobj(data.file, outf)
            size = outf.tell()

        commit = cls.create_with_metadata(
            id=commit_identifier,
            data={
                "size": size,
                "identifier": commit_identifier,
                "description": description,
            },
        )
        os.rename(tarball_temp_path, commit.tarball_path)
        return commit
