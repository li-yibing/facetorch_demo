#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   sftp_data_repo.py
@Author  :   wangj
@Date    :   2021/2/8
@Desc    :   
"""
from pathlib import Path
from stat import S_ISDIR, S_ISREG

import logging
import pysftp

from .data_repo import DataRepo


def parse_sftp_config(cp) -> dict:
    return {"host": cp.get('sftp', 'host'),
            "port": cp.getint('sftp', 'port'),
            "username": cp.get('sftp', 'user'),
            "password": cp.get('sftp', 'passwd'),
            "basePath": cp.get('sftp', 'basePath')
            }


class SFTPDataRepo(DataRepo):
    def __init__(self, cp):
        super().__init__(cp)
        self.logger = logging.getLogger(__name__)
        self.config = parse_sftp_config(cp)
        self.base_path = self.config.pop('basePath')
        self.sftp = pysftp.Connection(**self.config)
        self.logger.info("Connection to sftp server")

    def store_file(self, local_file, remote_path, metadata=None):
        self.logger.info(f'Storing file to SFTP: {remote_path} from local: {local_file}')
        if not Path(local_file).is_file():
            self.logger.error(f'Error, provided path {local_file} is not a file, please use store_directory instead')
            raise RuntimeError('Please provide file path instead of directory')

        remote_dir_name = str(Path(remote_path).parents[0])
        if not '.' == remote_dir_name:
            self.logger.info(f'Checking if remote parent directory exists')
            if not self._check_directory(remote_dir_name):
                self.create_directory(remote_dir_name)
        self.sftp.put(local_file, str(Path(self.base_path) / remote_path), preserve_mtime=True)
        self.logger.info(f'Finished storing file to SFTP: {remote_path} from local: {local_file}')

    def store_directory(self, local_dir, remote_path, metadata=None):
        self.logger.info(f'Storing directory to SFTP: {remote_path} from local: {local_dir}')
        if not Path(local_dir).is_dir():
            self.logger.error(f'Error, provided path {local_dir} is not a directory.')
            raise RuntimeError('Please provide directory that exists locally')
        for entry in Path(local_dir).iterdir():
            tmp_remote_path = Path(remote_path) / entry.name
            tmp_local_path = Path(local_dir) / entry.name
            if not tmp_local_path.is_file():
                try:
                    self.create_directory(str(tmp_remote_path))
                except OSError:
                    pass
                self.store_directory(str(tmp_local_path), str(tmp_remote_path))
            else:
                self.store_file(str(tmp_local_path), str(tmp_remote_path))

        self.logger.info(f'Finished storing directory to SFTP: {remote_path} from local: {local_dir}')

    def retrieve_file(self, remote_path, local_file, with_base_path=False):
        self.logger.info(f'Retrieving file from SFTP: {remote_path} to local: {local_file}')
        if not self._check_file(remote_path, with_base_path):
            self.logger.error(
                f'Error, provided path {remote_path} is not a file, please use retrieve_directory instead')
            raise RuntimeError('Please provide file path instead of directory')

        if with_base_path:
            self.sftp.get(remote_path, local_file, preserve_mtime=True)
        else:
            self.sftp.get(str(Path(self.base_path) / remote_path), local_file, preserve_mtime=True)

    def retrieve_directory(self, remote_path, local_dir):
        self.logger.info(f'Retrieving directory from SFTP: {remote_path} to local: {local_dir}')
        if not self._check_directory(remote_path):
            self.logger.error(f'Error, provided path {remote_path} does not exist in remote server.')
            raise RuntimeError('Please provide directory that exists in remote server')
        elif self._check_file(remote_path):
            self.logger.error(
                f'Error, provided path {remote_path} is not a directory, please use retrieve_file instead')
            raise RuntimeError('Please provide directory instead of file path')
        if not Path(local_dir).exists():
            Path(local_dir).mkdir()
        self._retrieve_directory(str(Path(self.base_path) / remote_path), local_dir)

    def _retrieve_directory(self, remote_path, local_dir):
        for entry in self.sftp.listdir_attr(remote_path):
            tmp_remote_path = remote_path + "/" + entry.filename
            tmp_local_path = Path(local_dir) / entry.filename
            mode = entry.st_mode
            if S_ISDIR(mode):
                try:
                    tmp_local_path.mkdir()
                except OSError:
                    pass
                self._retrieve_directory(tmp_remote_path, tmp_local_path)
            elif S_ISREG(mode):
                self.retrieve_file(tmp_remote_path, tmp_local_path, with_base_path=True)

    def list_directory(self, remote_path):
        if self._check_file(remote_path):
            self.logger.error(
                f'Error, provided path {remote_path} is not a directory')
            raise RuntimeError('Please provide directory instead of file path')
        return self.sftp.listdir(str(Path(self.base_path) / remote_path))

    def create_directory(self, remote_path):
        if not Path(remote_path).parts[0] == self.base_path:
            remote_path = str(Path(self.base_path) / remote_path)
        self.sftp.makedirs(remote_path, 777)

    def delete_file(self, remote_path: str):
        self.logger.info(f'Deleting object from SFTP: {remote_path}.')
        if not self._check_file(remote_path):
            self.logger.error(f'Given object does not exists')
            pass
        else:
            self.sftp.remove(remote_path)
            self.logger.info(f'Object {remote_path} deleted from SFTP.')

    def _check_directory(self, remote_path, with_base_path=False):
        if not with_base_path:
            remote_path = str(Path(self.base_path) / remote_path)
        try:
            if self.sftp.isdir(remote_path):
                return True
        except IOError:
            return False
        return False

    def _check_file(self, remote_file, with_base_path=False):
        if not with_base_path:
            remote_file = str(Path(self.base_path) / remote_file)
        try:
            if self.sftp.isfile(remote_file):
                return True
        except IOError:
            return False
        return False
