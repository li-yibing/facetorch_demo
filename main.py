from facetorch import FaceAnalyzer
from omegaconf import OmegaConf
from torch.nn.functional import cosine_similarity
from typing import Dict
import operator
import torchvision
from loguru import logger

# 加载配置
path_img_input = "./test.jpg"
path_img_output = "/test_output.jpg"
path_config = "config.yml"

cfg = OmegaConf.load(path_config)

# 启动模型
# initialize
analyzer = FaceAnalyzer(cfg.analyzer)


# 嵌入向量余弦相似度
def compute_embed_similarity(predictor_name: str = "verify", base_face_id: int = 0) -> Dict:
    base_emb = response.faces[base_face_id].preds[predictor_name].logits
    sim_dict = {face.indx: cosine_similarity(base_emb, face.preds[predictor_name].logits, dim=0).item() for face in
                response.faces}
    sim_dict_sorted = dict(sorted(sim_dict.items(), key=operator.itemgetter(1), reverse=True))
    return sim_dict_sorted


if __name__ == "__main__":
    # 预热模型
    response = analyzer.run(
        path_image=path_img_input,
        batch_size=cfg.batch_size,
        fix_img_size=cfg.fix_img_size,
        return_img_data=False,
        include_tensors=cfg.include_tensors,
        path_output=path_img_output,
    )

    # 按照配置文件的设置进行推理
    response = analyzer.run(
        path_image=path_img_input,
        batch_size=cfg.batch_size,
        fix_img_size=cfg.fix_img_size,
        return_img_data=cfg.return_img_data,
        include_tensors=cfg.include_tensors,
        path_output=path_img_output,
    )
    logger.debug(f"inference response: {response}")

    # 输出图像
    pil_image = torchvision.transforms.functional.to_pil_image(response.img)
    pil_image.show()

    # 面部表情
    fer_dict = {face.indx: face.preds["fer"].label for face in response.faces}
    logger.info(f"face expression recognition: {fer_dict}")

    # 人脸表征学习
    compute_embed_similarity(predictor_name="embed")

    # 人脸识别
    compute_embed_similarity(predictor_name="verify")

    # AU识别
    au_dict = {face.indx: face.preds["au"].label for face in response.faces}
    logger.info(f"action unit recognition: {au_dict}")
