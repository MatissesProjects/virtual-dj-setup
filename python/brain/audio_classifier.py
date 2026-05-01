import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class AudioCNN(nn.Module):
    """
    A lightweight CNN for audio classification based on spectrogram images.
    Input shape expected: (Batch, 1, TimeFrames, FreqBins)
    """
    def __init__(self, num_classes=3):
        super(AudioCNN, self).__init__()
        # Input shape: (Batch, 1, 128, 1024)
        # Using strided convolutions instead of pooling for efficiency
        self.conv1 = nn.Conv2d(1, 16, kernel_size=5, stride=2, padding=2) # -> (16, 64, 512)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1) # -> (32, 32, 256)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1) # -> (64, 16, 128)
        self.bn3 = nn.BatchNorm2d(64)
        
        # Global Average Pooling to make it input-size invariant
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(64, num_classes)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.gap(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

class AudioClassifier:
    """
    High-level wrapper for the AudioCNN model.
    """
    def __init__(self, model_path="python/brain/models/audio_cnn.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AudioCNN().to(self.device)
        self.model.eval()
        
        self.classes = ["Vocals", "Drums", "Other"]
        
        if os.path.exists(model_path):
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                print(f"[CNN] Loaded model from {model_path}")
            except Exception as e:
                print(f"[CNN] Failed to load model: {e}. Running with random weights.")
        else:
            # Ensure directory exists for future saving
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            print("[CNN] No model found at {model_path}. Running with uninitialized weights.")

    def predict(self, cnn_input):
        """
        Performs inference on a pre-processed CNN input.
        cnn_input: (1, 1, H, W) numpy array or torch tensor
        """
        with torch.no_grad():
            if isinstance(cnn_input, np.ndarray):
                cnn_input = torch.FloatTensor(cnn_input).to(self.device)
            
            outputs = self.model(cnn_input)
            probabilities = F.softmax(outputs, dim=1)
            
            top_p, top_class = probabilities.topk(1, dim=1)
            
            result = {
                "class": self.classes[top_class.item()],
                "confidence": top_p.item(),
                "probabilities": {self.classes[i]: probabilities[0][i].item() for i in range(len(self.classes))}
            }
            return result
