#!/usr/bin/env python3
"""Inferencia con Qwen base y un adaptador QLoRA entrenado."""
import argparse
from pathlib import Path
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

parser = argparse.ArgumentParser()
parser.add_argument("--adaptador", default="./qwen-jocarsa-lora")
parser.add_argument("--pregunta", default="¿Quién es José Vicente Carratalá Sanchis?")
args = parser.parse_args()
base = Path(args.adaptador, "modelo_base.txt").read_text(encoding="utf-8").strip()
if not torch.cuda.is_available():
    raise SystemExit("Se necesita CUDA para cargar este modelo en 4 bits")
bf16 = torch.cuda.is_bf16_supported()
cuantizacion = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16 if bf16 else torch.float16)
tokenizer = AutoTokenizer.from_pretrained(args.adaptador)
modelo = AutoModelForCausalLM.from_pretrained(base, quantization_config=cuantizacion, device_map="auto")
modelo = PeftModel.from_pretrained(modelo, args.adaptador)
modelo.eval()
mensajes = [{"role": "user", "content": args.pregunta}]
entrada = tokenizer.apply_chat_template(mensajes, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(modelo.device)
with torch.inference_mode():
    salida = modelo.generate(entrada, max_new_tokens=256, do_sample=False, pad_token_id=tokenizer.eos_token_id)
print(tokenizer.decode(salida[0][entrada.shape[-1]:], skip_special_tokens=True))
