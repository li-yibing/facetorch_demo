#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File   : video_demo.py
@Author : yb_li
@Date   : 2023/12/11
@Desc   : 从对象存储读取文件路径，从文件路径读取视频
"""

import gradio as gr
from loguru import logger
from filemanager import FileManager


def read_file_list(directory=None):
    file_manager = FileManager()
    logger.debug(f"read file list")
    files = file_manager.list_directory(directory)
    object_names = [file.object_name for file in files]
    return object_names


def read_video_url(filename):
    file_manager = FileManager()
    logger.debug(f"read video url from {filename}")
    video_url = file_manager.get_object_url(filename)
    return video_url


with gr.Blocks() as demo:
    gr.Markdown("# 对象存储文件列表")
    with gr.Row():
        path = gr.Textbox(label="输入对象存储文件夹路径")
        response = gr.Textbox(label="文件列表")
    predict_button = gr.Button(value="获取文件列表")
    predict_button.click(fn=read_file_list, inputs=path, outputs=response, api_name="read_video")

    gr.Markdown("# 对象存储读取视频")
    with gr.Row():
        path = gr.Textbox(label="输入视频路径")
        response = gr.Video(label="视频文件")
    predict_button = gr.Button(value="读取视频")
    predict_button.click(fn=read_video_url, inputs=path, outputs=response, api_name="file_list")

demo.launch()
