import torch
from torchvision.transforms.functional import to_tensor, normalize
from sklearn.metrics import accuracy_score
import cv2
import os
from sklearn import svm
from sklearn.metrics import plot_confusion_matrix

mean, std = 42, 47
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
            else:
                self.dictionary[line_data[0]] = 0
        return self
    
    def load_images(self, folder):
        #citesc imaginiile si atribui intr-un tensor, o combinatie de forma [1, 50, 50], type ce poate avea valoarea de la 0, 1 sau 2
        images = [normalize(to_tensor(cv2.imread(os.path.join(folder, filename), 0)), [mean], [std]) for filename in os.listdir(folder)]
        type = [int(self.dictionary[filename]) for filename in os.listdir(folder)]
        return torch.unsqueeze(torch.cat(images, dim=0), dim=1).reshape(-1, 2500), torch.Tensor(type)
    
    def submit_prediction(self, filename, labels):
        #dam submit la predictie
        submit_data = [i + ", " + str(key) + "\n"  for i, key in self.dictionary.keys()]
        open(filename, "w").write("id_label\n".join(submit_data))


train = Files("data/train.txt")
train.load_list_of_data()
x_data_train, y_data_train = train.load_images("data/train/")
vald = Files("data/validation.txt")
vald.load_list_of_data()
x_data_val, y_data_val = vald.load_images("data/validation")
test = Files("data/test.txt")

def predict(model):
    data = open("data/test.txt", "r").read()
    images = []
    for filename in data.split("\n"):
        if filename != "":
            images.append(torch.unsqueeze(normalize(to_tensor(cv2.imread(os.path.join("data/test/", filename), 0)), [mean], [std]), dim=0))

	with torch.no_grad(): predictions = [int(model.predict(image.reshape(-1, 2500))) for image in images]
    return predictions

svm_model = svm.SVC(C=20)
svm_model.fit(x_data_train, y_data_train)
print(accuracy_score(y_data_val, svm_model.predict(x_data_val)) + " %")
preds = predict(svm_model)
test.submit_prediction("submisions.txt", preds)
