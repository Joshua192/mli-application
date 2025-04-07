from torchvision import transforms
# from fastapi import FastAPI, Request 
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

classifications = ('0','1','2','3','4','5','6','7','8','9')

# cuda is av on device but not in prod, forcing cpu
# device = torch.device('cuda' if torch.cuda.is_available else 'cpu')
device = torch.device(  'cpu') 

class ConvNet(nn.ModuleList):

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)
        self.softmax = nn.LogSoftmax(dim=1)
        # self.double()
    
    def forward(self, inputs):
        inputs = inputs.view(-1, 28 * 28)  # Flatten the input
        inputs = self.fc1(inputs)
        inputs = self.relu(inputs)
        inputs = self.fc2(inputs)
        return self.softmax(inputs)


model = ConvNet().to(device) #passed to GPU/CPU

model.load_state_dict(torch.load( "./saved_models/mid_train_model", weights_only = True, map_location=torch.device('cpu')))
model.eval()


# @app.post("/predict")
def predictor(picture) -> tuple:
    _ = image_processing(picture)
    return model_call(_)


def image_processing(picture):
    
    # picture = cv2.cvtColor(picture, cv2.COLOR_BGRA2BGR)

    
    if len(picture.shape) == 3:  # If the image has 3 channels (RGB)
        picture = cv2.cvtColor(picture, cv2.COLOR_RGB2GRAY)
    
    picture = cv2.resize(picture, (28,28), interpolation=cv2.INTER_LINEAR)
    picture = torch.from_numpy(picture).float()
    picture = transforms.functional.resize(picture, (28,28))
    # picture = picture / 255 #forgot to normalise...
    
    print("Min:", picture.min().item(), "Max:", picture.max().item())
    
    picture = picture.unsqueeze(0).unsqueeze(0)
    
    output = model(picture.to(device))
    
    print("Raw logits:", output)

    return picture
    

def model_call(picture) -> tuple: 
    
    output = model(picture.to(device))
    
    prob = torch.nn.functional.softmax(output, dim=1)
    
    conf, classes = torch.max(prob, 1)
    return (int(classifications[classes.item()]), float("%.2f" % conf.item()))