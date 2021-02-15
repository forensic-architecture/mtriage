import torch
import torchvision
from torch.autograd import Variable
from torchvision import transforms
from PIL import Image
from lib.common.analyser import Analyser
from lib.common.etypes import Etype


class PytorchFasterRcnn(Analyser):
    in_etype = Etype.Any
    out_etype = Etype.Any

    def pre_analyse(self, config):
        # NB: in future this could be configurable.
        model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False, num_classes=6)
        if torch.cuda.is_available():
            model.cuda()
            self.device = torch.device("cuda:0")
        else:
            self.device = torch.device("cpu")
        state_dict = torch.load(self.base_path/config["model"], map_location=torch.device(self.device))
        model.load_state_dict(state_dict)
        model.eval()
        self.model = model
        self.transforms = transforms.Compose([transforms.Resize(224), transforms.ToTensor()])
        self.threshold = config.get('threshold') if config.get('threshold') else 0.5

    def analyse_element(self, element, config):
        def get_preds(img):
            img = Image.open(img).convert('RGB')
            image_tensor = self.transforms(img).float().unsqueeze_(0)
            inp = Variable(image_tensor).to(self.device)
            output = self.model(inp)[0]
            labels = [config['class_map'][i.item()] for i in output.get('labels')]
            scores = output.get('scores')
            preds = [(x, y.item()) for x,y in zip(labels, scores) if y.item() > self.threshold]
            return preds

        self.logger(f"Running inference for {element.id}...")
        return Etype.CvJson.from_preds(element, get_preds)

module = PytorchFasterRcnn
