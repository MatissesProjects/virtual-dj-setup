import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
from audio_classifier import AudioCNN

class SyntheticAudioDataset(Dataset):
    """
    A synthetic dataset generator for testing the training pipeline.
    In a real scenario, this would load .npy spectrograms or raw audio files.
    """
    def __init__(self, num_samples=1000, time_frames=128, freq_bins=1024, num_classes=3):
        self.num_samples = num_samples
        self.time_frames = time_frames
        self.freq_bins = freq_bins
        self.num_classes = num_classes

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        # Generate random spectrogram-like data
        # Class 0: Vocals (represented by random harmonics)
        # Class 1: Drums (represented by random noise bursts)
        # Class 2: Other (represented by low-frequency hums)
        
        label = np.random.randint(0, self.num_classes)
        data = np.random.rand(1, self.time_frames, self.freq_bins).astype(np.float32) * 0.1
        
        if label == 0: # Vocals
            for i in range(5):
                freq = np.random.randint(200, 800)
                data[0, :, freq] += 0.5
        elif label == 1: # Drums
            for i in range(10):
                t = np.random.randint(0, self.time_frames)
                data[0, t, :] += 0.4
        else: # Other
            data[0, :, :50] += 0.3
            
        return torch.from_numpy(data), torch.tensor(label, dtype=torch.long)

class RealAudioDataset(Dataset):
    """
    Loads real spectrogram samples collected by collect_data.py.
    """
    def __init__(self, data_dir="python/brain/data"):
        self.samples = []
        self.labels = []
        self.label_map = {"vocals": 0, "drums": 1, "other": 2}
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(".npy"):
                    label_str = filename.split("_")[0]
                    if label_str in self.label_map:
                        filepath = os.path.join(data_dir, filename)
                        self.samples.append(filepath)
                        self.labels.append(self.label_map[label_str])
        
        print(f"Loaded {len(self.samples)} real samples.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        data = np.load(self.samples[idx])
        # Add channel dimension
        data = data.reshape(1, data.shape[0], data.shape[1]).astype(np.float32)
        return torch.from_numpy(data), torch.tensor(self.labels[idx], dtype=torch.long)

def train():
    # ...
    # Dataset & Loader
    real_dataset = RealAudioDataset()
    if len(real_dataset) > 10:
        print("Using real dataset.")
        dataset = real_dataset
    else:
        print("Using synthetic dataset (not enough real samples).")
        dataset = SyntheticAudioDataset()
        
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Model, Loss, Optimizer
    model = AudioCNN(num_classes=3).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Training Loop
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        print(f"Epoch {epoch+1}/{epochs} | Loss: {running_loss/len(train_loader):.4f} | Acc: {100.*correct/total:.2f}%")

    # Save the model
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    torch.save(model.state_dict(), model_save_path)
    print(f"Model saved to {model_save_path}")

if __name__ == "__main__":
    train()
