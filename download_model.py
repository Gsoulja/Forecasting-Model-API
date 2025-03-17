# download_model.py
# pip install transformers requests

import os
import argparse
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

def download_model(model_name, model_type="base", save_path=None):
    """
    Download and save a model from Hugging Face
    
    Args:
        model_name (str): Name of the model on Hugging Face
        model_type (str): Type of model (base, sequence_classification, etc.)
        save_path (str): Path to save the model
    """
    print(f"Downloading model: {model_name}")
    
    # Create save path if not exists
    if save_path and not os.path.exists(save_path):
        os.makedirs(save_path)
    
    try:
        # Download tokenizer
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Download model based on type
        print(f"Downloading {model_type} model...")
        if model_type == "sequence_classification":
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
        else:
            model = AutoModel.from_pretrained(model_name)
        
        # Save if path provided
        if save_path:
            tokenizer_path = os.path.join(save_path, "tokenizer")
            model_path = os.path.join(save_path, "model")
            
            print(f"Saving tokenizer to {tokenizer_path}")
            tokenizer.save_pretrained(tokenizer_path)
            
            print(f"Saving model to {model_path}")
            model.save_pretrained(model_path)
        
        print(f"Successfully downloaded {model_name}")
        return True
    
    except Exception as e:
        print(f"Error downloading model: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a Hugging Face model")
    parser.add_argument("--model", type=str, required=True, help="Model name on Hugging Face")
    parser.add_argument("--type", type=str, default="base", help="Model type (base, sequence_classification)")
    parser.add_argument("--save_path", type=str, default="./models", help="Path to save the model")
    
    args = parser.parse_args()
    download_model(args.model, args.type, args.save_path)
