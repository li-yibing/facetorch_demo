#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   data_repo_registry.py
@Author  :   wangj
@Date    :   2021/2/8
@Desc    :   
"""
from .minio_data_repo import MinIODataRepo
from .sftp_data_repo import SFTPDataRepo
from configparser import ConfigParser
from pathlib import Path


class DataRepoRegistry:
    def __init__(self):
        self._registry = {}
        self.cfg_path = ''

    def register(self, store_type, repo):
        self._registry[store_type] = repo

    def set_cfg_path(self, cfg_path):
        self.cfg_path = cfg_path

    def get_data_repo(self):
        cp = ConfigParser()
        # cp.read(Path(__file__).parent.parent.parent.joinpath("config.cfg").resolve(), encoding='utf-8')
        cp.read(self.cfg_path, encoding='utf-8')
        store_type = cp.get('control', 'storage')
        if store_type is None:
            raise RuntimeError('store type not found in config.cfg')
        return self._registry[store_type](cp)


_data_repo_registry = DataRepoRegistry()

_data_repo_registry.register('minio', MinIODataRepo)
_data_repo_registry.register('sftp', SFTPDataRepo)


def get_data_repo(cfg_path):
    _data_repo_registry.set_cfg_path(cfg_path)
    return _data_repo_registry.get_data_repo()
