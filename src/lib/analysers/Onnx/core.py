from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype, Union, Array
import json
import onnx
import cv2
import onnxruntime as rt
import numpy as np

class Onnx(Analyser):
    """ Code adapted from https://thenewstack.io/tutorial-using-a-pre-trained-onnx-model-for-inferencing/ """
    in_etype = Union(Array(Etype.Image), Etype.Json)
    out_etype = Etype.Json

    def pre_analyse(self, config):
        print(f"pre-analysing with onnx...")
        self.session = rt.InferenceSession(f"/mtriage/{self.config['model']}")
        print(f"The model expects input shape: {self.session.get_inputs()[0].shape}")

    def analyse_element(self, element, config):
        p = element.paths[0] # assume one image for now
        img = cv2.imread(str(p))
        img = img[..., :3]
        img = cv2.resize(img, dsize=(640,640), interpolation=cv2.INTER_AREA) # TODO: this size from onnx model
        img.resize((1,3,640,640))

        data = json.dumps({'data': img.tolist()})
        data = np.array(json.loads(data)['data']).astype('float32')

        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name

        result = session.run([output_name], {input_name: data})
        # TODO: now what? how to extract the predictions?

        return element


module = Onnx
