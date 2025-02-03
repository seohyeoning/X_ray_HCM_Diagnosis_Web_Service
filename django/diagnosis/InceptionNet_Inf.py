# import os
# import torch
# import torch.nn as nn
# import numpy as np
# from torchvision import models, transforms
# from PIL import Image
# import cv2
# from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, ConfusionMatrixDisplay
# import matplotlib.pyplot as plt


# class InceptionNetInference:
#     def __init__(self, model_path, classes, input_size, using_clahe, device="cpu"):
#         self.device = torch.device(device)
#         self.classes = classes
#         self.inp = input_size
#         self.clahe = using_clahe
#         self.img_clahe = None
        
#         self.model = self.make_model()
#         checkpoint = torch.load(model_path, map_location=self.device)
#         if 'model_state_dict' in checkpoint:
#             self.model.load_state_dict(checkpoint['model_state_dict'])
#         else:
#             self.model.load_state_dict(checkpoint)

#         self.model = self.model.to(self.device)
#         self.model.eval()

#         self.transform = transforms.Compose([
#             transforms.Resize((input_size, input_size)),
#             transforms.ToTensor(),
#             transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#         ])

#     def make_model(self):
#         base_model = models.inception_v3(weights=models.Inception_V3_Weights.DEFAULT, aux_logits=True)
#         in_features = base_model.fc.in_features
#         base_model.fc = nn.Sequential(
#             nn.Linear(in_features, 1024),
#             nn.ReLU(),
#             nn.Linear(1024, len(self.classes)),
#             nn.Softmax(dim=1)
#         )
#         base_model.aux_logits = False
#         return base_model

#     def apply_clahe(self, gray_img, clip_limit=2.0, tile_grid_size=(8, 8)):
#         clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
#         gray_img_uint8 = (gray_img * 255).astype(np.uint8)
#         clahe_img = clahe.apply(gray_img_uint8)
#         clahe_img_normalized = clahe_img / 255.0
#         return clahe_img_normalized

#     def preprocess_image(self, img_path):
#         img = Image.open(img_path).convert('RGB')
#         if self.clahe:
#             img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
#             img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
#             self.img_clahe = self.apply_clahe(img_gray)
#             img_cv_clahe = cv2.cvtColor((self.img_clahe * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
#             img = Image.fromarray(img_cv_clahe)

#         img_tensor = self.transform(img).unsqueeze(0)
#         return img_tensor, self.img_clahe

#     def predict(self, img_path):
#         input_tensor, self.img_clahe = self.preprocess_image(img_path)
#         input_tensor = input_tensor.to(self.device)  # input_tensor에만 .to(self.device) 호출
#         with torch.no_grad():
#             outputs = self.model(input_tensor)
#             probabilities = outputs.squeeze().cpu().numpy()
#         _, predicted = torch.max(outputs, 1)
#         label = self.classes[predicted.item()]
        
#         # 각 클래스의 확률값을 반환
#         normal_prob = probabilities[0] * 100
#         hcm_prob = probabilities[1] * 100
        
#         return label, normal_prob, hcm_prob



# # TEST
# if __name__ == "__main__":
#     model_path = r"C:\Users\user\Desktop\팀프로젝트\Cat_HCM\Cat_HCM\django\all_train_InceptionNet.pth"
#     test_dirs = {
#         "Normal": "C:/Users/user/Desktop/팀프로젝트/Cat_HCM/Data/raw/test_files/Normal",
#         "HCM": "C:/Users/user/Desktop/팀프로젝트/Cat_HCM/Data/raw/test_files/HCM"
#     }
#     classes = ['Normal', 'HCM']

#     model_inference = InceptionNetInference(model_path=model_path, classes=classes, input_size=299, using_clahe=True)

#     y_true = []
#     y_pred = []

#     for label, test_dir in test_dirs.items():
#         image_paths = [
#             os.path.join(test_dir, img) for img in os.listdir(test_dir) if img.endswith(('.jpg', '.png'))
#         ]
#         for img_path in image_paths:
#             pred_label, normal_prob, hcm_prob, img_clahe = model_inference.predict(img_path)
#             y_true.append(label)
#             y_pred.append(pred_label)

#     # 성능 지표 계산
#     acc = accuracy_score(y_true, y_pred)
#     f1 = f1_score(y_true, y_pred, average='weighted')
#     cm = confusion_matrix(y_true, y_pred, labels=classes)

#     print(f"Accuracy: {acc:.4f}")
#     print(f"F1 Score: {f1:.4f}")

#     # Confusion Matrix 시각화
#     disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
#     disp.plot(cmap=plt.cm.Blues, values_format="d")
#     plt.title("Confusion Matrix")
#     plt.show()


import os
import torch
import torch.nn as nn
import numpy as np
from torchvision import models, transforms
from PIL import Image
import cv2
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt


class InceptionNetInference:
    def __init__(self, model_path, classes, input_size, using_clahe, device="cpu"):
        self.device = torch.device(device)
        self.classes = classes
        self.inp = input_size
        self.clahe = using_clahe

        self.model = self.make_model()
        checkpoint = torch.load(model_path, map_location=self.device)

        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)

        self.model = self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((input_size, input_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def make_model(self):
        base_model = models.inception_v3(weights=models.Inception_V3_Weights.DEFAULT, aux_logits=True)
            
        # 모델의 분류기(fc) 정의
        base_model.fc = nn.Sequential(
            nn.Linear(base_model.fc.in_features, 128),  # 입력 크기 -> 128
            nn.ReLU(),
            nn.Dropout(p=0.5),                    # Dropout 추가
            nn.Linear(128, 2)                     # 출력 크기 -> 2 (클래스 수)
        )

        
        base_model.aux_logits = False
        return base_model

    def apply_clahe(self, gray_img, clip_limit=2.0, tile_grid_size=(8, 8)):
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        gray_img_uint8 = (gray_img * 255).astype(np.uint8)
        clahe_img = clahe.apply(gray_img_uint8)
        clahe_img_normalized = clahe_img / 255.0
        return clahe_img_normalized

    def preprocess_image(self, img_path):
        img = Image.open(img_path).convert('RGB')
        if self.clahe:
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            img_clahe = self.apply_clahe(img_gray)
            img_cv_clahe = cv2.cvtColor((img_clahe * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
            img = Image.fromarray(img_cv_clahe)
            
            # # Plot the images
            # plt.figure(figsize=(12, 6))
            # plt.subplot(1, 2, 1)
            # plt.title("Grayscale Image (Before CLAHE)")
            # plt.imshow(img_gray, cmap='gray')
            # plt.axis('off')

            # plt.subplot(1, 2, 2)
            # plt.title("CLAHE Applied Image")
            # plt.imshow(img_clahe, cmap='gray')
            # plt.axis('off')
            
            # plt.show()
        img_tensor = self.transform(img).unsqueeze(0)
        return img_tensor

    def predict(self, img_path):
        input_tensor = self.preprocess_image(img_path).to(self.device)
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)  # Softmax 적용
            probabilities = probabilities.squeeze().cpu().numpy()
        _, predicted = torch.max(outputs, 1)  # 가장 높은 확률의 클래스 인덱스
        label = self.classes[predicted.item()]  # 예측된 클래스 이름
            
        # 각 클래스의 확률값을 반환
        normal_prob = probabilities[0] * 100
        print(normal_prob)
        
        hcm_prob = probabilities[1] * 100
        print(hcm_prob)
        return label, normal_prob, hcm_prob


# TEST
if __name__ == "__main__":
    
    model_path = r"C:\Users\user\Desktop\팀프로젝트\Cat_HCM\Cat_HCM\django\all_train_InceptionNet.pth" 


    
    test_dirs = {
        "Normal": "C:/Users/Starlab/Desktop/psh/Cat_HCM/test_val/HCM",
        
        "HCM": "C:/Users/Starlab/Desktop/psh/Cat_HCM/test_val/NORMAL"
    }
    classes = ['Normal', 'HCM']

    model_inference = InceptionNetInference(model_path=model_path, classes=classes, input_size=299, using_clahe=True)

    y_true = []
    y_pred = []

    for label, test_dir in test_dirs.items():
        image_paths = [
            os.path.join(test_dir, img) for img in os.listdir(test_dir) if img.endswith(('.jpg', '.jpeg'))
        ]
        for img_path in image_paths:
            pred_label, normal_prob, hcm_prob = model_inference.predict(img_path)
            y_true.append(label)
            y_pred.append(pred_label)

    # 성능 지표 계산
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted')
    cm = confusion_matrix(y_true, y_pred, labels=classes)

    print(f"Accuracy: {acc:.4f}")
    print(f"F1 Score: {f1:.4f}")

    # Confusion Matrix 시각화
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    # disp.plot(cmap=plt.cm.Blues, values_format="d")
    # plt.title("Confusion Matrix")
    # plt.show()
    # Confusion Matrix를 출력 형태로 변환
    print("\n Confusion Matrix:")
    print(f"{'':<10}{classes[0]:<10}{classes[1]:<10}")
    print(f"{classes[0]:<10}{cm[0, 0]:<10}{cm[0, 1]:<10}")
    print(f"{classes[1]:<10}{cm[1, 0]:<10}{cm[1, 1]:<10}")

    # 총 샘플 수와 올바르게 예측된 샘플 수
    total_samples = len(y_true)
    correct_predictions = np.trace(cm)  # 대각선의 합
    print(f"\nTotal test samples: {total_samples}")
    print(f"Correctly predicted samples: {correct_predictions}")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1 Score: {f1:.4f}")