from paddleocr import PPStructureV3
import os
import requests
import json

model_list= json.loads(open("ocr_models.json", "r").read())

if not os.path.exists("ocr_models"):
    os.makedirs("ocr_models")
    os.system("wget -P ocr_models https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv5_mobile_det_infer.tar")

ocr = PPStructureV3(
    paddlex_config="PPStructureV3.yaml"
)

input_file = "aali_combine.pdf"
result = ocr.predict_iter(input=input_file,
                     use_wireless_table_cells_trans_to_html=True,
                     use_wired_table_cells_trans_to_html=True)

output_dir="output_aali"
for res in result:
    res.print()
    res.save_to_img(output_dir)
    res.save_to_json(output_dir)
    res.save_to_markdown(output_dir)
    res.save_to_xlsx(output_dir)
    res.save_to_html(output_dir)