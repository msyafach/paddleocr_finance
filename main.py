from paddleocr import PPStructureV3
import os
import requests
import json

model_list= json.loads(open("ocr_models.json", "r").read())

if not os.path.exists("ocr_models"):
    os.makedirs("ocr_models")
    os.system("wget -P ocr_models https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv5_mobile_det_infer.tar")

ocr = PPStructureV3(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    use_seal_recognition=False,
    use_formula_recognition=False,
    use_chart_recognition=False,
    layout_detection_model_name=model_list["models"]["layout_detection"][0]["name"],
    layout_detection_model_dir=model_list["models"]["layout_detection"][0]["dir"],
    text_detection_model_name=model_list["models"]["text_detection"]["name"],
    text_detection_model_dir=model_list["models"]["text_detection"]["dir"],
    text_recognition_model_name=model_list["models"]["text_recognition"]["name"],
    text_recognition_model_dir=model_list["models"]["text_recognition"]["dir"],
    table_classification_model_name=model_list["models"]["table_classification"]["name"],
    table_classification_model_dir=model_list["models"]["table_classification"]["dir"],
    wired_table_structure_recognition_model_name=model_list["models"]["wired_table_structure_recognition"]["name"],
    wired_table_structure_recognition_model_dir=model_list["models"]["wired_table_structure_recognition"]["dir"],
    wireless_table_structure_recognition_model_name=model_list["models"]["wireless_table_structure_recognition"]["name"],
    wireless_table_structure_recognition_model_dir=model_list["models"]["wireless_table_structure_recognition"]["dir"],
    wired_table_cells_detection_model_name=model_list["models"]["wired_table_cells_detection"]["name"],
    wired_table_cells_detection_model_dir=model_list["models"]["wired_table_cells_detection"]["dir"],
    wireless_table_cells_detection_model_name=model_list["models"]["wireless_table_cells_detection"]["name"],
    wireless_table_cells_detection_model_dir=model_list["models"]["wireless_table_cells_detection"]["dir"],

)

input_file = "data_split/FinancialStatement-2025-I-AALI_page_8.pdf"
result = ocr.predict(input=input_file,
                     use_wireless_table_cells_trans_to_html=True,
                     use_wired_table_cells_trans_to_html=True)

for res in result:
    res.print()
    res.save_to_img("output_2")
    res.save_to_json("output_2")
    res.save_to_markdown("output_2")
    res.save_to_xlsx("output_2")
    res.save_to_html("output_2")