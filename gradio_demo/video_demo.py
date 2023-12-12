#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File   : interface_demo1.py
@Author : yb_li
@Date   : 2023/12/11
@Desc   : 
"""

import gradio as gr
import joblib
from loguru import logger
from io import BytesIO
from filemanager import FileManager


def read_video(inp):
    file_manager = FileManager()
    logger.debug(f"read video from {inp}")
    with file_manager.get_object(inp) as reader:
        video_file = joblib.load(BytesIO(reader.read()))
    return video_file


with gr.Blocks() as demo:
    gr.Markdown("# 对象存储读取视频")
    with gr.Row():
        image_path = gr.Textbox(label="输入视频路径")
        response = gr.Video(label="视频预览")
    predict_button = gr.Button(value="分析")
    predict_button.click(fn=read_video, inputs=image_path, outputs=response, api_name="read_video")

demo.launch()
