import sys
import os
import shutil
import fnmatch
from .data_repo_registry import get_data_repo

CFG_PATH = os.path.join(os.path.dirname(__file__), "config.cfg")


class FileManager:

    def __init__(self):
        self.data_repo = get_data_repo(CFG_PATH)

    # Wrapper
    def list_directory(self, path: str):
        files = self.data_repo.list_directory(path)
        return files

    def create_directory(self, path: str):
        self.data_repo.create_directory(path)

    def delete_directory(self, path: str):
        self.data_repo.delete_directory(path)

    def store_file(self, remote_path: str, local_path: str):
        self.data_repo.store_file(remote_path, local_path)

    def retrieve_file(self, remote_path: str, local_path: str):
        self.data_repo.retrieve_file(remote_path, local_path)

    def delete_file(self, path: str, filename: str):
        self.data_repo.delete_file(path, filename)

    def get_object(self, remote_path):
        return self.data_repo.get_object(remote_path)

    # Parkinson
    def list_remote(self, path: str):
        files = self.data_repo.list_directory(path)
        return [os.path.basename(item.object_name) for item in files]

    def copy_single_file(self, src_path: str, det_path: str):  # 将文件拷贝到远端，且保证远端仅有一个文件，用于推理
        flag_copy = True
        self.data_repo.create_directory(det_path)
        video_filenames = sorted(fnmatch.filter(
            self.list_remote(det_path), '*.mp4'))
        if len(video_filenames) > 0:
            for video_filename in video_filenames:
                if os.path.basename(src_path) != video_filename:
                    self.data_repo.delete_file(os.path.join(det_path, video_filename))
                    print("Delete {}".format(os.path.join(det_path, video_filename)))
                else:
                    flag_copy = False
        if flag_copy:
            self.data_repo.store_file(os.path.join(det_path, os.path.basename(src_path)), src_path)
            print('{}--->>>{}'.format(src_path, det_path))

    def push_data(self, src_path: str, det_path: str):  # 将文件增量上传
        srcs = os.listdir(src_path)
        srcs = list(filter(lambda x: x.endswith('mp4'), srcs))
        dets = self.list_remote(det_path)
        diff_adds = list(set(srcs).difference(set(dets)))
        diff_dels = list(set(dets).difference(set(srcs)))

        for add_item in diff_adds:
            self.data_repo.store_file(os.path.join(det_path, add_item), os.path.join(src_path, add_item))
            print('{}--->>>{}'.format(src_path, det_path))

        for del_item in diff_dels:
            self.data_repo.delete_file(os.path.join(det_path, del_item))

    # local operate functions
    def label2det(self, src_path: str, det_path: str):
        flag_copy = True
        if not os.path.exists(det_path):
            os.makedirs(det_path)
        shutil.move(src_path, os.path.join(det_path, os.path.basename(src_path)))
        print('{}--->>>{}'.format(src_path, det_path))
