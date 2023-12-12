#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   minio_data_repo.py
@Author  :   wangj
@Date    :   2021/2/8
@Desc    :   
"""
from .data_repo import DataRepo
import logging
from pathlib import Path
from minio import Minio, S3Error


def parse_minio_config(cp):
    return {"endpoint": cp.get("minio", "endpoint"),
            "access_key": cp.get("minio", "accessKey"),
            "secret_key": cp.get("minio", "secretKey"),
            "secure": cp.getboolean("minio", "secure"),
            "bucket": cp.get("minio", "bucket")}


class MinIODataRepo(DataRepo):
    def __init__(self, cp):
        super().__init__(cp)
        self.logger = logging.getLogger(__name__)
        self.config = parse_minio_config(cp)
        self.default_bucket = self.config.pop("bucket")
        self.minio_client = Minio(**self.config)
        if not self.minio_client.bucket_exists(self.default_bucket):
            self.minio_client.make_bucket(self.default_bucket)
        self.logger.info("Connection to minio server")

    def store_file(self, remote_path: str, local_file: str, metadata=None):
        self.logger.info(f'Storing file to Minio: {remote_path} from local: {local_file}')
        if not Path(local_file).is_file():
            self.logger.error(f'Error, provided path {local_file} is not a file, please use store_directory instead')
            raise RuntimeError('Please provide file path instead of directory')
        self.minio_client.fput_object(self.default_bucket, self._format_path(remote_path),
                                      self._format_path(local_file), metadata=metadata)
        self.logger.info(f'Finished storing file to Minio: {remote_path} from local: {local_file}')

    def store_directory(self, remote_path: str, local_dir: str, metadata=None):
        self.logger.info(f'Storing directory to Minio: {remote_path} from local: {local_dir}')
        p = Path(local_dir)
        if not p.is_dir():
            self.logger.error(f'Error, provided path {local_dir} is not a directory.')
            raise RuntimeError('Please provide directory that exists locally')
        for file in p.rglob("*"):
            if file.is_file():
                remote_file_path = str(Path(remote_path, str(file).replace(local_dir, "").lstrip("/")))
                # TODO: metadata list?
                self.store_file(str(file), remote_file_path, metadata=metadata)
        self.logger.info(f'Finished storing directory to Minio: {remote_path} from local: {local_dir}')

    def retrieve_file(self, remote_path: str, local_file: str):
        self.logger.info(f'Retrieving file from Minio: {remote_path} to local: {local_file}')
        if not self._check_file(remote_path):
            self.logger.error(
                f'Error, provided path {remote_path} is not a file, please use retrieve_directory instead')
            raise RuntimeError('Please provide file path instead of directory')
        self.minio_client.fget_object(self.default_bucket, self._format_path(remote_path),
                                      self._format_path(local_file))

    def retrieve_directory(self, remote_path: str, local_dir: str):
        self.logger.info(f'Retrieving directory from Minio: {remote_path} to local: {local_dir}')
        if self._check_file(remote_path):
            self.logger.error(
                f'Error, provided path {remote_path} is not a directory, please use retrieve_file instead')
            raise RuntimeError('Please provide directory instead of file path')
        for obj in self.list_directory(remote_path):
            local_obj_dir = Path(local_dir, obj.object_name.replace(remote_path, ""))
            if obj.is_dir:
                if not local_obj_dir.exists():
                    local_obj_dir.mkdir()
            else:
                self.retrieve_file(obj.object_name, str(local_obj_dir))

    def list_directory(self, remote_path: str):
        formatted_path = self._format_path(remote_path)
        object_list = self.minio_client.list_objects(self.default_bucket, prefix=formatted_path)
        return [obj for obj in object_list]

    def delete_file(self, remote_path: str):
        self.logger.info(f'Deleting object from Minio: {remote_path}.')
        if not self._check_file(remote_path):
            self.logger.error(f'Given object does not exists')
            pass
        else:
            try:
                self.minio_client.remove_object(self.default_bucket, self._format_path(remote_path))
                self.logger.info(f'Object {remote_path} deleted from Minio.')
            except S3Error as e:
                self.logger.error(f'Error deleting Object {remote_path} from Minio. {e}')
                pass

    def get_object(self, remote_path):
        return self.minio_client.get_object(self.default_bucket, self._format_path(remote_path))

    def get_object_url(self, remote_path):
        return self.minio_client.presigned_get_object(self.default_bucket, self._format_path(remote_path))

    def _check_file(self, remote_path: str):
        try:
            if self.minio_client.stat_object(self.default_bucket, self._format_path(remote_path)):
                return True
        except S3Error:
            return False
        return False

    def _format_path(self, path: str):
        # 如果是空字符串，直接返回
        if not path:
            return path
        # 如果是文件路径，加上/后缀
        path = path.replace('\\', '/')
        if Path(path).is_dir() and not path.endswith('/'):
            path = path + '/'
        return path
