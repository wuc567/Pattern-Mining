# from multiprocessing import process
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, \
    precision_recall_curve, auc
from collections import Counter
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE
import warnings
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from datetime import datetime
import random
import psutil
import os


def set_seed(seed):
    torch.manual_seed(seed)  # 为CPU设置随机种子
    torch.cuda.manual_seed(seed)  # 为当前GPU设置随机种子
    torch.cuda.manual_seed_all(seed)  # 如果使用多个GPU，也要设置随机种子
    np.random.seed(seed)  # 设置numpy的随机种子
    random.seed(seed)  # 设置Python内置随机数生成器的随机种子
    torch.backends.cudnn.deterministic = True  # 确保卷积等操作的结果确定
    torch.backends.cudnn.benchmark = False  # 禁用cudnn的自动优化算法选择


# set_seed(42)  # 设置为固定的随机种子，例如42
set_seed(12)  # 设置为固定的随机种子，例如42

warnings.filterwarnings('ignore')

# 读取CSV文件
print("正在读取数据...")
df = pd.read_csv('TravelTime_387.csv')

# 添加一个名为 'label' 的新列，值全为 0
df['label'] = 0

# 查看前几行数据
print(df.head())

# 指定要标记的时间
target_times = [
    "2015-07-30 12:29:00",
    "2015-08-18 16:26:00",
    "2015-09-01 05:34:00"
]

# 假设时间是第一列，列名可能是默认的，也可能需要指定，例如 df.columns[0]
time_column = df.columns[0]

# 将匹配到的行的 'label' 设为 1
df.loc[df[time_column].isin(target_times), 'label'] = 1

# 查看结果
print(f"异常样本数量: {df['label'].sum()}")
print(df[df['label'] == 1])

# 数据预处理
print("正在进行数据预处理...")
# 对值进行标准化处理
scaler = StandardScaler()
df['normalized_value'] = scaler.fit_transform(df[['value']])


# 添加一些统计特征
def add_statistical_features(df, window_sizes=[5, 10]):
    # 为不同窗口大小计算统计特征
    for window in window_sizes:
        # 滑动窗口统计量
        df[f'rolling_mean_{window}'] = df['normalized_value'].rolling(window).mean()
        df[f'rolling_std_{window}'] = df['normalized_value'].rolling(window).std()
        df[f'rolling_max_{window}'] = df['normalized_value'].rolling(window).max()
        df[f'rolling_min_{window}'] = df['normalized_value'].rolling(window).min()

    # 差分特征
    df['diff_1'] = df['normalized_value'].diff()
    df['diff_2'] = df['normalized_value'].diff(2)

    # 填充NaN
    df = df.fillna(method='bfill').fillna(method='ffill')
    return df


# 添加统计特征
df = add_statistical_features(df)

# 查看添加的特征
print("添加的特征:")
print(df.columns.tolist())

# 选择要使用的特征
feature_columns = [col for col in df.columns if col not in [time_column, 'label', 'value']]
print(f"使用的特征: {feature_columns}")

# 准备数据
features = df[feature_columns].values
labels = df['label'].values

# 设置滑动窗口长度
WINDOW_SIZE = 4
STRIDE = 1


# 构造窗口序列
def create_windows(features, labels, window_size, stride):
    X, y = [], []
    for i in range(0, len(features) - window_size + 1, stride):
        window_features = features[i:i + window_size]
        window_labels = labels[i:i + window_size]
        X.append(window_features)
        # 如果窗口中包含任何异常点（label=1），窗口整体就标为异常
        y.append(int(np.any(window_labels == 1)))
    return np.array(X), np.array(y)


class TimeSeriesDataset(Dataset):
    def __init__(self, data, labels):
        self.data = torch.tensor(data, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]


# 创建窗口化数据
print("正在创建窗口化数据...")
X, y = create_windows(features, labels, WINDOW_SIZE, STRIDE)

# 查看数据形状
print(f"X shape: {X.shape}, y shape: {y.shape}")
print(f"类别分布: {Counter(y)}")

# 划分训练和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# 打印类别分布
print("训练集类别分布:", Counter(y_train))
print("测试集类别分布:", Counter(y_test))

# 展平数据以应用SMOTE过采样
print("正在应用SMOTE过采样...")
n_samples, n_timesteps, n_features = X_train.shape
X_train_flat = X_train.reshape(n_samples, n_timesteps * n_features)

# 应用SMOTE过采样
smote = SMOTE(random_state=42, k_neighbors=min(5, Counter(y_train)[1] - 1))
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_flat, y_train)

# 将过采样后的数据转回原始形状
X_train_resampled = X_train_resampled.reshape(-1, n_timesteps, n_features)

# 打印过采样后的类别分布
print("过采样后的训练集类别分布:", Counter(y_train_resampled))

# 创建DataLoader
train_dataset = TimeSeriesDataset(X_train_resampled, y_train_resampled)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_dataset = TimeSeriesDataset(X_test, y_test)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)


# 自编码器和分类器联合模型
class TimeSeriesAutoencoderClassifier(nn.Module):
    def __init__(self, seq_len, n_features, hidden_dim=64, latent_dim=32):
        super().__init__()
        self.seq_len = seq_len
        self.n_features = n_features
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim

        # Encoder LSTM
        self.encoder_lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )

        # 编码器全连接层
        self.encoder_fc = nn.Sequential(
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU()
        )

        # 解码器LSTM
        self.decoder_lstm = nn.LSTM(
            input_size=latent_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )

        # 解码器全连接层
        self.decoder_fc = nn.Linear(hidden_dim, n_features)

        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(16, 2)
        )

    def encode(self, x):
        # 编码过程
        _, (h_n, _) = self.encoder_lstm(x)
        # 使用最后一层的隐藏状态
        h = h_n[-1]
        # 编码为潜在表示
        latent = self.encoder_fc(h)
        return latent

    def decode(self, latent):
        # 将潜在表示重复seq_len次
        repeated_latent = latent.unsqueeze(1).repeat(1, self.seq_len, 1)
        # 解码
        outputs, _ = self.decoder_lstm(repeated_latent)
        reconstructed = self.decoder_fc(outputs)
        return reconstructed

    def forward(self, x):
        # 编码
        latent = self.encode(x)
        # 解码
        reconstructed = self.decode(latent)
        # 分类
        logits = self.classifier(latent)
        return reconstructed, logits


# 训练函数
def train_model(model, train_loader, test_loader, epochs=10, lr=1e-3, device='cpu'):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    reconstruction_criterion = nn.MSELoss()
    classification_criterion = nn.CrossEntropyLoss()

    history = {
        'train_loss': [],
        'train_rec_loss': [],
        'train_cls_loss': [],
        'train_accuracy': [],
        'test_loss': [],
        'test_rec_loss': [],
        'test_cls_loss': [],
        'test_accuracy': [],
        'test_f1': []
    }

    best_f1 = 0
    best_model_state = None

    for epoch in range(epochs):
        # 训练阶段
        model.train()
        train_loss = 0
        train_rec_loss = 0
        train_cls_loss = 0
        correct = 0
        total = 0

        for x_batch, y_batch in train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            reconstructed, logits = model(x_batch)

            # 计算重构损失
            rec_loss = reconstruction_criterion(reconstructed, x_batch)
            # 计算分类损失
            cls_loss = classification_criterion(logits, y_batch)
            # 总损失 - 可以调整权重
            loss = 0.3 * rec_loss + 0.7 * cls_loss

            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            train_rec_loss += rec_loss.item()
            train_cls_loss += cls_loss.item()

            # 计算准确率
            _, predicted = torch.max(logits, 1)
            total += y_batch.size(0)
            correct += (predicted == y_batch).sum().item()

        train_accuracy = correct / total

        # 测试阶段
        model.eval()
        test_loss = 0
        test_rec_loss = 0
        test_cls_loss = 0
        correct = 0
        total = 0
        y_true = []
        y_pred = []

        with torch.no_grad():
            for x_batch, y_batch in test_loader:
                x_batch, y_batch = x_batch.to(device), y_batch.to(device)

                reconstructed, logits = model(x_batch)

                # 计算重构损失
                rec_loss = reconstruction_criterion(reconstructed, x_batch)
                # 计算分类损失
                cls_loss = classification_criterion(logits, y_batch)
                # 总损失
                loss = 0.3 * rec_loss + 0.7 * cls_loss

                test_loss += loss.item()
                test_rec_loss += rec_loss.item()
                test_cls_loss += cls_loss.item()

                # 计算准确率
                _, predicted = torch.max(logits, 1)
                total += y_batch.size(0)
                correct += (predicted == y_batch).sum().item()

                y_true.extend(y_batch.cpu().numpy())
                y_pred.extend(predicted.cpu().numpy())

        test_accuracy = correct / total
        test_f1 = f1_score(y_true, y_pred)

        # 记录历史
        history['train_loss'].append(train_loss / len(train_loader))
        history['train_rec_loss'].append(train_rec_loss / len(train_loader))
        history['train_cls_loss'].append(train_cls_loss / len(train_loader))
        history['train_accuracy'].append(train_accuracy)
        history['test_loss'].append(test_loss / len(test_loader))
        history['test_rec_loss'].append(test_rec_loss / len(test_loader))
        history['test_cls_loss'].append(test_cls_loss / len(test_loader))
        history['test_accuracy'].append(test_accuracy)
        history['test_f1'].append(test_f1)

        # 保存最佳模型
        if test_f1 > best_f1:
            best_f1 = test_f1
            best_model_state = model.state_dict().copy()

    model.load_state_dict(best_model_state)

    return model, history


# 评估函数
def evaluate_model(model, data_loader, device='cpu'):
    model.eval()
    y_true = []
    y_pred = []
    y_scores = []

    with torch.no_grad():
        for x_batch, y_batch in data_loader:
            x_batch = x_batch.to(device)

            _, logits = model(x_batch)
            probs = torch.softmax(logits, dim=1)

            _, predicted = torch.max(logits, 1)

            y_true.extend(y_batch.cpu().numpy())
            y_pred.extend(predicted.cpu().numpy())
            y_scores.extend(probs[:, 1].cpu().numpy())  # 取正类概率作为分数

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_scores = np.array(y_scores)

    # 计算评估指标
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    conf_matrix = confusion_matrix(y_true, y_pred)

    # 计算ROC AUC
    try:
        roc_auc = roc_auc_score(y_true, y_scores)
    except:
        roc_auc = 0

    # 计算PR AUC
    precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_scores)
    pr_auc = auc(recall_curve, precision_curve)

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'pr_auc': pr_auc,
        'confusion_matrix': conf_matrix,
        'y_true': y_true,
        'y_pred': y_pred,
        'y_scores': y_scores
    }


# 主程序
if __name__ == "__main__":

    # baseline_memory = process.memory_info().rss
    device = torch.device("cpu")
    print(f"使用设备: {device}")

    # 初始化模型
    model = TimeSeriesAutoencoderClassifier(
        seq_len=WINDOW_SIZE,
        n_features=X_train_resampled.shape[2],
        hidden_dim=64,
        latent_dim=32
    ).to(device)

    # 训练模型
    process = psutil.Process(os.getpid())
    start_time = datetime.now()
    start_memory = process.memory_info().rss
    trained_model, history = train_model(
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        epochs=20,
        lr=1e-3,
        device=device
    )

    # 保存模型
    # torch.save(trained_model.state_dict(), 'autoencoder_classifier_model.pth')
    # 对测试集进行评估
    test_results = evaluate_model(trained_model, test_loader, device)
    end_time = datetime.now()
    end_memory = process.memory_info().rss

    # 计算时间差
    time_diff = end_time - start_time
    print("Time Difference:", time_diff)

    # 内存差
    memory_diff = end_memory - start_memory
    print(f"Memory Difference: {memory_diff * 8 / 1024 / 1024:.2f} Mb")

    # 评估模型后，显式删除模型和相关变量
    del trained_model, model, history
    # 如果您使用了CUDA，清除缓存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # 强制垃圾回收
    import gc

    gc.collect()
