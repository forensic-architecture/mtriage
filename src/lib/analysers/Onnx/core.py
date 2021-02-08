from lib.common.analyser import Analyser
from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype, Union, Array
from pathlib import Path
import json
import onnx
import onnxruntime
from torchvision import transforms
from PIL import Image

def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

class Onnx(Analyser):
    """ Code adapted from https://thenewstack.io/tutorial-using-a-pre-trained-onnx-model-for-inferencing/ """
    in_etype = Union(Array(Etype.Image), Etype.Json)
    out_etype = Etype.Json

    def pre_analyse(self, config):
        print(f"pre-analysing with onnx...")
        self.model_path = self.base_path / self.config["model"]
        onnx_model = onnx.load(str(self.model_path))
        onnx.checker.check_model(onnx_model)
        self.session = onnxruntime.InferenceSession(str(self.model_path))
        self.input_layer_name = self.session.get_inputs()[0].name
        # print(f"The model expects input shape: {self.session.get_inputs()[0].shape}")

    def infer(self, input_tensor):
        inputs = {self.input_layer_name: input_tensor}
        outs = self.session.run(None, inputs)
        import pdb; pdb.set_trace();
        return outs[0]

    def analyse_element(self, element, config):
        # input needs to be a numpy array with the right shape
        for pth in element.paths:
            img = Image.open(pth)
            # NB: default crop in torchvision.transforms in bilinear interpoloation
            # TODO: experiment with other resizing heuristics such as croping the source
            # image multiple times and average over the predictions.
            # See https://docs.fast.ai/vision.augment.html
            resize = transforms.Resize([224, 224])
            img = resize(img)
            to_tensor = transforms.ToTensor()
            img_y = to_tensor(img)
            img_y.unsqueeze_(0)
            input_tensor = to_numpy(img_y)
            preds = self.infer(input_tensor)
            self.logger(preds.shape)
            # TODO: do something with `preds`

        return element


module = Onnx
