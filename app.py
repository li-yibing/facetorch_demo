import gradio as gr
import torchvision

from main import logger, analyzer, compute_embed_similarity
from facetorch.datastruct import Response, ImageData


class FaceTorch:
    def __init__(self):
        self.image_path = None
        self.response = None

    def analyze_face(self, image_path: str = "test.jpg"):
        self.image_path = image_path
        self.response = analyzer.run(
            path_image=image_path,
            batch_size=1,
            fix_img_size=True,
            return_img_data=True,
            include_tensors=True,
            path_output=None,
        )
        # logger.debug(f"inference response: {self.response}")
        result = self.response
        return result

    def parser_face(self):
        # 如果不是是ImageData类型
        if isinstance(self.response, ImageData):
            # 从输入图像的路径读取图像PIL
            input_image = torchvision.transforms.functional.to_pil_image(torchvision.io.read_image(self.image_path))
            # 输出图像
            pil_image = torchvision.transforms.functional.to_pil_image(self.response.img)
            return [input_image, pil_image]
        else:
            logger.error("没有返回人脸图像数据")
            return [None, None]


face_torch = FaceTorch()

with gr.Blocks() as demo:
    gr.Markdown("# 人脸分析算法接口")
    with gr.Row():
        image_path = gr.File(label="选择图片")
        response = gr.Json(label="检测结果")
    predict_button = gr.Button(value="分析")
    predict_button.click(fn=face_torch.analyze_face, inputs=image_path, outputs=response, api_name="analyze_face")

    with gr.Row():
        origin_image = gr.Image(label="原始图像")
        face_image = gr.Image(label="绘制图像")
    parser_button = gr.Button(value="解析结果")
    parser_button.click(fn=face_torch.parser_face, inputs=None, outputs=[origin_image, face_image],
                        api_name="parser_face")

# 启动 Gradio 服务，并创建共享链接
demo.launch()
