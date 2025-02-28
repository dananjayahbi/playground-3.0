import paddle
# Set the device to GPU (CUDA). Make sure your environment has CUDA configured.
paddle.set_device("gpu:0")

from paddleocr import PaddleOCR, draw_ocr
from PIL import Image

# Force GPU usage by passing use_gpu=True.
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)  # Downloads and loads model into GPU memory if available
img_path = './t7.png'
result = ocr.ocr(img_path, cls=True)

# Flatten result if necessary (PaddleOCR sometimes returns a nested list)
if len(result) == 1 and isinstance(result[0], list):
    result = result[0]

for line in result:
    print(line)

# Draw result
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]

scores = []
for line in result:
    text, conf = line[1]
    if isinstance(conf, (int, float)):
        score = conf
    elif isinstance(text, (int, float)):
        score = text
    else:
        raise ValueError(f"No numeric confidence found for: {line}")
    scores.append(float(score))

im_show = draw_ocr(image, boxes, txts, scores, font_path='./Roboto-VariableFont_wdth,wght.ttf')
im_show = Image.fromarray(im_show)
im_show.save('result.jpg')