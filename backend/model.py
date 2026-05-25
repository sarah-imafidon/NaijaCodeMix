import torch
import torch.nn as nn
import joblib
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

# ----------------------------
# Hybrid Model Definition
# ----------------------------
class HybridClassifier(nn.Module):
    def __init__(self, transformer, feature_dim, hidden_dim=32, num_labels=2):
        super(HybridClassifier, self).__init__()
        self.transformer = transformer
        cls_dim = transformer.config.hidden_size

        self.fc1 = nn.Linear(cls_dim + feature_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_labels)

    def forward(self, input_ids, attention_mask, features):
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        combined = torch.cat([cls_embedding, features], dim=1)
        x = self.fc1(combined)
        x = self.relu(x)
        logits = self.fc2(x)
        return logits


# ----------------------------
# Load Models Function
# ----------------------------
def load_models():
    model_path = "baseline_afroxlm_model"

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Baseline model
    baseline_model = AutoModelForSequenceClassification.from_pretrained(model_path)
    baseline_model.eval()

    # Transformer (for hybrid)
    transformer = AutoModel.from_pretrained(model_path)

    # Hybrid model
    hybrid_model = HybridClassifier(transformer, feature_dim=6)
    hybrid_model.load_state_dict(
        torch.load("hybrid_afroxlm_model.pt", map_location="cpu")
    )
    hybrid_model.eval()

    # Scaler
    scaler = joblib.load("scaler.pkl")

    return tokenizer, baseline_model, hybrid_model, scaler