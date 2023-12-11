#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File   : interface_demo1.py
@Author : yb_li
@Date   : 2023/12/11
@Desc   : 
"""

import gradio as gr


def image_classifier(inp):
    return {'cat': 0.3, 'dog': 0.7}


inputs_examples = []

demo = gr.Interface(fn=image_classifier, inputs="image", outputs="label", examples=inputs_examples)
demo.launch()
