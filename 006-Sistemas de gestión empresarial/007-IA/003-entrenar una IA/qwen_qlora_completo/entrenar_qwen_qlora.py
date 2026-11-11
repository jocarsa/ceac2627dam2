
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JOCARSA | ENTRENAMIENTO QWEN CON QLORA

Entrenamiento supervisado (SFT) utilizando:
- Qwen2.5-3B-Instruct
- Cuantización NF4 de 4 bits
- LoRA / PEFT
- Hugging Face Transformers
- TRL SFTTrainer
- Dataset JSONL en formato messages

Optimizado para NVIDIA RTX 4060 8 GB VRAM.
"""

import os
import json
import argparse
import random

import torch

from pathlib import Path
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    set_seed,
)
from peft import (
    LoraConfig,
    prepare_model_for_kbit_training,
)
from trl import SFTConfig, SFTTrainer


# CONFIGURACIÓN ####################################################

MODELO_DEFAULT = "Qwen/Qwen2.5-3B-Instruct"

DATOS_DEFAULT = "jose_vicente_carratala_entrenamiento.jsonl"

SALIDA_DEFAULT = "./qwen-jocarsa-lora"

EPOCAS_DEFAULT = 5

SEMILLA = 42

MAX_LENGTH = 512

BATCH_SIZE = 1

GRADIENT_ACCUMULATION = 8

LORA_R = 8

LORA_ALPHA = 16

LORA_DROPOUT = 0.05

LEARNING_RATE = 1e-4

VALIDACION = 0.10


# ARGUMENTOS #######################################################

def argumentos():

    parser = argparse.ArgumentParser(
        description="JOCARSA | Entrenamiento Qwen QLoRA"
    )

    parser.add_argument(
        "--datos",
        default=DATOS_DEFAULT,
        help="Archivo JSONL de entrenamiento"
    )

    parser.add_argument(
        "--modelo",
        default=MODELO_DEFAULT,
        help="Modelo base de Hugging Face"
    )

    parser.add_argument(
        "--salida",
        default=SALIDA_DEFAULT,
        help="Directorio del adaptador LoRA"
    )

    parser.add_argument(
        "--epocas",
        type=int,
        default=EPOCAS_DEFAULT,
        help="Número de épocas"
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=MAX_LENGTH,
        help="Longitud máxima de secuencia"
    )

    return parser.parse_args()


# COMPROBAR GPU ####################################################

def comprobar_gpu():

    if not torch.cuda.is_available():
        raise RuntimeError(
            "QLoRA de 4 bits requiere una GPU NVIDIA CUDA "
            "compatible en esta configuración."
        )

    gpu = torch.cuda.get_device_properties(0)

    memoria = gpu.total_memory / (1024 ** 3)

    print("=" * 65)
    print("JOCARSA | ENTRENAMIENTO QWEN QLORA")
    print("=" * 65)

    print(f"GPU: {gpu.name}")
    print(f"VRAM: {memoria:.2f} GB")
    print(f"CUDA: {torch.version.cuda}")

    print("=" * 65)

    if memoria < 7:
        print("AVISO: memoria GPU muy limitada.")

    torch.cuda.empty_cache()


# CARGAR JSONL #####################################################

def cargar_jsonl(ruta):

    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe el dataset: {ruta}"
        )

    registros = []

    with ruta.open("r", encoding="utf-8") as archivo:

        for numero, linea in enumerate(archivo, 1):

            linea = linea.strip()

            if not linea:
                continue

            try:
                registro = json.loads(linea)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"JSON incorrecto en línea {numero}: {error}"
                )

            mensajes = registro.get("messages")

            if not isinstance(mensajes, list):
                raise ValueError(
                    f"Línea {numero}: falta 'messages'"
                )

            if not mensajes:
                raise ValueError(
                    f"Línea {numero}: lista messages vacía"
                )

            for mensaje in mensajes:

                if not isinstance(mensaje, dict):
                    raise ValueError(
                        f"Línea {numero}: mensaje incorrecto"
                    )

                if mensaje.get("role") not in (
                    "system",
                    "user",
                    "assistant",
                ):
                    raise ValueError(
                        f"Línea {numero}: rol no válido"
                    )

                if not isinstance(
                    mensaje.get("content"), str
                ):
                    raise ValueError(
                        f"Línea {numero}: contenido incorrecto"
                    )

            if not any(
                m["role"] == "assistant"
                for m in mensajes
            ):
                raise ValueError(
                    f"Línea {numero}: no hay respuesta assistant"
                )

            registros.append({
                "messages": mensajes
            })

    if len(registros) < 2:
        raise ValueError(
            "Se necesitan al menos dos registros."
        )

    print(f"Registros cargados: {len(registros)}")

    return registros


# DIVIDIR DATASET ##################################################

def dividir_dataset(registros):

    random.Random(SEMILLA).shuffle(registros)

    total = len(registros)

    cantidad_validacion = max(
        1,
        int(total * VALIDACION)
    )

    validacion = registros[:cantidad_validacion]

    entrenamiento = registros[cantidad_validacion:]

    print(f"Entrenamiento: {len(entrenamiento)}")
    print(f"Validación: {len(validacion)}")

    return (
        Dataset.from_list(entrenamiento),
        Dataset.from_list(validacion),
    )


# TOKENIZADOR ######################################################

def cargar_tokenizador(modelo):

    print("\nCargando tokenizador...")

    tokenizer = AutoTokenizer.from_pretrained(
        modelo,
        trust_remote_code=False,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    tokenizer.padding_side = "right"

    return tokenizer


# CUANTIZACIÓN #####################################################

def configurar_cuantizacion():

    tipo_calculo = (
        torch.bfloat16
        if torch.cuda.is_bf16_supported()
        else torch.float16
    )

    configuracion = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=tipo_calculo,
    )

    return configuracion, tipo_calculo


# CARGAR MODELO ####################################################

def cargar_modelo(nombre, cuantizacion, tipo_calculo):

    print("\nCargando modelo base...")
    print(f"Modelo: {nombre}")

    modelo = AutoModelForCausalLM.from_pretrained(
        nombre,
        quantization_config=cuantizacion,
        dtype=tipo_calculo,
        device_map={"": 0},
        low_cpu_mem_usage=True,
        trust_remote_code=False,
    )

    modelo.config.use_cache = False

    modelo = prepare_model_for_kbit_training(
        modelo,
        use_gradient_checkpointing=True,
    )

    print("Modelo cargado en 4 bits.")

    return modelo


# CONFIGURACIÓN LORA ###############################################

def configurar_lora():

    return LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
        ],
    )


# CONFIGURACIÓN ENTRENAMIENTO ######################################

def configurar_entrenamiento(salida, epocas, max_length):

    return SFTConfig(
        output_dir=salida,

        num_train_epochs=epocas,

        per_device_train_batch_size=BATCH_SIZE,

        per_device_eval_batch_size=1,

        gradient_accumulation_steps=GRADIENT_ACCUMULATION,

        gradient_checkpointing=True,

        gradient_checkpointing_kwargs={
            "use_reentrant": False
        },

        learning_rate=LEARNING_RATE,

        lr_scheduler_type="cosine",

        warmup_ratio=0.05,

        weight_decay=0.01,

        optim="paged_adamw_8bit",

        max_length=max_length,

        packing=False,

        completion_only_loss=True,

        bf16=torch.cuda.is_bf16_supported(),

        fp16=not torch.cuda.is_bf16_supported(),

        eval_strategy="epoch",

        save_strategy="epoch",

        save_total_limit=2,

        logging_steps=1,

        logging_first_step=True,

        report_to="none",

        seed=SEMILLA,

        data_seed=SEMILLA,

        dataloader_num_workers=0,

        remove_unused_columns=False,
    )


# ENTRENAMIENTO ####################################################

def entrenar(args):

    set_seed(SEMILLA)

    comprobar_gpu()

    registros = cargar_jsonl(args.datos)

    dataset_train, dataset_eval = dividir_dataset(
        registros
    )

    tokenizer = cargar_tokenizador(args.modelo)

    cuantizacion, tipo_calculo = configurar_cuantizacion()

    modelo = cargar_modelo(
        args.modelo,
        cuantizacion,
        tipo_calculo,
    )

    lora = configurar_lora()

    configuracion = configurar_entrenamiento(
        args.salida,
        args.epocas,
        args.max_length,
    )

    print("\nPreparando entrenador...")

    trainer = SFTTrainer(
        model=modelo,
        args=configuracion,
        train_dataset=dataset_train,
        eval_dataset=dataset_eval,
        processing_class=tokenizer,
        peft_config=lora,
    )

    print("\nParámetros entrenables:")

    trainer.model.print_trainable_parameters()

    print("\n" + "=" * 65)
    print("INICIANDO ENTRENAMIENTO")
    print("=" * 65)

    resultado = trainer.train()

    print("\nEntrenamiento terminado.")

    print(f"Train loss: {resultado.training_loss:.6f}")

    print("\nEvaluando modelo...")

    metricas = trainer.evaluate()

    print(
        json.dumps(
            metricas,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\nGuardando adaptador LoRA...")

    ruta_salida = Path(args.salida)

    ruta_salida.mkdir(
        parents=True,
        exist_ok=True,
    )

    trainer.save_model(str(ruta_salida))

    tokenizer.save_pretrained(str(ruta_salida))

    with (
        ruta_salida / "entrenamiento.json"
    ).open("w", encoding="utf-8") as archivo:

        json.dump(
            {
                "modelo_base": args.modelo,
                "dataset": args.datos,
                "epocas": args.epocas,
                "max_length": args.max_length,
                "lora_r": LORA_R,
                "lora_alpha": LORA_ALPHA,
                "train_samples": len(dataset_train),
                "eval_samples": len(dataset_eval),
                "metricas": metricas,
            },
            archivo,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print("\n" + "=" * 65)
    print("ENTRENAMIENTO FINALIZADO")
    print("=" * 65)

    print(f"Adaptador guardado en: {ruta_salida.resolve()}")

    print("\nArchivos principales:")
    print("  adapter_config.json")
    print("  adapter_model.safetensors")
    print("  tokenizer.json")
    print("  entrenamiento.json")


# PRINCIPAL ########################################################

if __name__ == "__main__":

    args = argumentos()

    try:
        entrenar(args)

    except torch.cuda.OutOfMemoryError:

        print("\nERROR: GPU sin memoria.")

        print(
            "Prueba --max-length 256 o utiliza "
            "Qwen2.5-1.5B-Instruct."
        )

        raise

    except KeyboardInterrupt:

        print("\nEntrenamiento interrumpido.")

    except Exception as error:

        print(f"\nERROR: {error}")

        raise
