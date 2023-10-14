from mathpix.mathpix import MathPix

mathpix = MathPix(app_id="aicerta_dba064_cf8251", app_key="1edb871fea6133e08b718918bdfa84093d4bdeade502e3e0eb461d600ad9def7")

ocr = mathpix.process_image(image_url="https://static.vecteezy.com/system/resources/previews/008/561/498/original/quadratic-equation-formula-solution-of-solving-quadratic-equations-background-education-getting-grades-higher-school-math-programs-handwritten-math-text-grouped-and-isolated-on-white-free-vector.jpg")
print(ocr.latex)
print(ocr.latex_confidence)