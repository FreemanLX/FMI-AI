from numpy import matrix
import torch
from torch import nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from torchvision.transforms.functional import to_tensor, normalize
import cv2
import os
import matplotlib.pyplot as plt
from sklearn.metrics import plot_confusion_matrix


mean, std = 42, 47
if(torch.cuda.is_available() == False): Exception()
torch.manual_seed(1)
device = torch.device("cuda")

class Files:
    def __init__(self, text_file):
         self.text_file = text_file

    def load_list_of_data(self):
        #citesc din fisierele text: nume si denumire, mi-l baga intr-un dictionar ai dictionar[filename] = 0, 1 sau 2
        self.dictionary = {} 
        f = open(self.text_file, "r")
        content = f.read()
        for line in content.split("\n"):
            line_data = line.split(",")
            if len(line_data) == 2: self.dictionary[line_data[0]] = line_data[1]
        return self
    
    def load_images(self, folder):
        #citesc imaginiile si atribui intr-un tensor, o combinatie de forma [1, 50, 50], type ce poate avea valoarea de la 0, 1 sau 2
        images = [normalize(to_tensor(cv2.imread(os.path.join(folder, filename), 0)), [mean], [std]) for filename in os.listdir(folder)]
        type = [int(self.dictionary[filename]) for filename in os.listdir(folder)]
        return torch.unsqueeze(torch.cat(images, dim=0), dim=1), torch.Tensor(type)
    
    def submit_prediction(self, filename, labels):
        #dam submit la predictie
        submit_data = [i + ", " + str(key) + "\n"  for i, key in self.dictionary.keys()]
        open(filename, "w").write("id_label\n".join(submit_data))


class ProjectDataset(Dataset):
    def __init__(self, x): self.x, self.y = x
    def __len__(self): return len(self.x)
    def __getitem__(self, item): return self.x[item], self.y[item]


train = Files("../input/ai-unibuc-23-31-2021/train.txt")
train.load_list_of_data()
validation = Files("../input/ai-unibuc-23-31-2021/validation.txt")
validation.load_list_of_data()
train_loader = DataLoader(dataset=ProjectDataset(train.load_images("../input/ai-unibuc-23-31-2021/train")), \
    batch_size=64, shuffle=False, **{'num_workers': 0, 'pin_memory': True})
valid_loader = DataLoader(dataset=ProjectDataset(validation.load_images("../input/ai-unibuc-23-31-2021/validation")), \
    batch_size=1, shuffle=False, **{'num_workers': 0, 'pin_memory': True})

class NeuralNetwork(nn.Module):

    def __init__(self, n = 3, channels_conv = [1, 1024, 512, 512], features = [8192, 2048, 1024, 1024], kernel_size = (5, 5), padding = (1, 1)):
        #clasa neuralnetwork
        #self.n reprezinta cate layere doresc sa am 
        #channels_conv reprezinta conventiile pentru fiecare layer in parte
        #features reprezinta numarul de noduri din CNN
        #kernel_size reprezinta dimensiunea convolutiei, default (5, 5)
        #padding iti extinde sa zicem imaginea pentru a nu pierde datele din colturi (la inceput nu e nevoie)
        #am considerat ca dropout-ul sa fie 0.005
        super().__init__()
        self.n = n
        self.kernel_size = kernel_size
        self.channels_conv = channels_conv 
        self.padding = padding
        self.features = features
        #fiindca am facut automatizat aceste convolutii, trebuie sa definesc un modulelist care in limba incepatoriilor ar fi o lista de functii.
        self.layer = nn.ModuleList()
        self.linear = nn.ModuleList()
        self.norm = nn.ModuleList()
        for index in range(self.n):
            if(index == 0): self.layer.append(nn.Conv2d(in_channels=self.channels_conv[index], out_channels=self.channels_conv[index + 1], kernel_size=self.kernel_size))
            else: self.layer.append(nn.Conv2d(in_channels=self.channels_conv[index], out_channels=self.channels_conv[index + 1], kernel_size=self.kernel_size, padding = self.padding))
            self.linear.append(nn.Linear(self.features[index], self.features[index + 1]))
            self.norm.append(nn.BatchNorm2d(self.channels_conv[index + 1], eps=10 ** (-34)))
        
        self.linear.append(nn.Linear(self.features[self.n], self.n)) 

    def forward(self, output):
        #aplicam progresia liniara
        for i in range(self.n): output = nn.Dropout(0.005)(F.relu(self.norm[i](nn.MaxPool2d(2, 2)(self.layer[i](output)))))
        output = nn.Flatten()(output)
        for i in range(self.n + 1): output = nn.Dropout(0.005)(self.linear[i](output))
        return nn.Softmax(dim = 1)(output)



network = NeuralNetwork().to(device)
scaler = torch.cuda.amp.GradScaler()
torch.backends.cudnn.benchmark = True

def train(epochs: int, train_loader: DataLoader, validation_loader: DataLoader, model: nn.Module, learning_rate = 10 ** (-6)):
    acur_max = 0
    optimizer = optim.Adam(network.parameters(), lr=learning_rate)
    optimizer.zero_grad(set_to_none = True)
    floss = nn.CrossEntropyLoss()   
    print("The training is started... Please wait!")
    for epoch in range(epochs):
        for images, labels in train_loader:
            loss = floss(model(images.to(device)), labels.to(device).long())
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
        
        model.eval()
        with torch.no_grad():
            count = sum([1 if torch.argmax(model(validation_image.cuda())) == validation_label.cuda() else 0 for validation_image, validation_label in validation_loader])
        
        relative_error = 1 - (abs(count - len(validation_loader)) / max(count, len(validation_loader)) * 100)
        print(f"The accuracy of {epoch + 1} is { relative_error }%")
        if relative_error > acur_max:
            acur_max = relative_error
            torch.save(model.state_dict(), "temp.pth")


def predict(model: nn.Module):
    data_to_predict = open("../input/ai-unibuc-23-31-2021/test.txt", "r").read()
    images = []
    for filename in data_to_predict.split("\n"):
       if filename != 0: images.append(torch.unsqueeze(normalize(to_tensor(cv2.imread(os.path.join("../input/ai-unibuc-23-31-2021/test", filename), 0)), [mean], [std]), dim=0))
    model.dropout = nn.Dropout(0)
    with torch.no_grad(): return [torch.argmax(model(image.cuda())).detach().cpu().numpy() for image in images]


train(15, train_loader, valid_loader, network)
generate_predict_model = NeuralNetwork().to(device)
torch_t = torch.load("temp.pth");
generate_predict_model.load_state_dict(torch_t)
preds = predict(generate_predict_model)
test = Files("../input/ai-unibuc-23-31-2021/test.txt")
test.submit("submisions.txt", preds)