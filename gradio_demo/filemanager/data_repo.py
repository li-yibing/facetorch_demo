#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   data_repo.py
@Author  :   wangj
@Date    :   2021/2/8
@Desc    :   
"""
from abc import abstractmethod, ABCMeta
from typing import List


class DataRepo:
    __metaclass__ = ABCMeta

    def __init__(self, cp):
        self.cp = cp

    def open_file(self, path: str):
        pass

    @abstractmethod
    def store_file(self, remote_path: str, local_file: str, metadata=None):
        pass

    @abstractmethod
    def store_directory(self, remote_path: str, local_dir: str, metadata=None):
        pass

    @abstractmethod
    def retrieve_file(self, remote_path: str, local_file: str):
        pass

    @abstractmethod
    def retrieve_directory(self, remote_path: str, local_dir: str):
        pass

    def create_directory(self, remote_path: str):
        pass

    @abstractmethod
    def delete_file(self, remote_path: str):
        pass

    @abstractmethod
    def list_directory(self, remote_path: str) -> List:
        pass

    def _is_directory(self, remote_path: str):
        listing = self.list_directory(remote_path)
        return len(listing) > 0

