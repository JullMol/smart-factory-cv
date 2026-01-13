from ultralytics import YOLO
import argparse


def train_model(
    data_yaml: str = "../../data/merged_dataset/data.yaml",
    model_size: str = "n",
    epochs: int = 100,
    batch_size: int = 16,
    imgsz: int = 640,
    device: str = "0",
    project: str = "../models",
    name: str = "ppe_detection"
):
    model_name = f"yolov8{model_size}.pt"
    model = YOLO(model_name)
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        project=project,
        name=name,
        patience=20,
        save=True,
        save_period=10,
        cache=False,
        workers=4,
        verbose=True,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
    )
    
    metrics = model.val()
    
    return model, results, metrics


def export_model(model_path: str, format: str = "onnx"):
    model = YOLO(model_path)
    model.export(format=format)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8 PPE Detection Model")
    
    parser.add_argument("--data", type=str, default="../../data/merged_dataset/data.yaml")
    parser.add_argument("--model", type=str, default="n", choices=["n", "s", "m", "l", "x"])
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument("--name", type=str, default="ppe_detection")
    parser.add_argument("--export", type=str, default=None)
    
    args = parser.parse_args()
    
    model, results, metrics = train_model(
        data_yaml=args.data,
        model_size=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        name=args.name
    )
    
    if args.export:
        best_model_path = f"../models/{args.name}/weights/best.pt"
        export_model(best_model_path, format=args.export)
