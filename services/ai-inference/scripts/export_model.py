import argparse
import time
from pathlib import Path
import sys

try:
    from ultralytics import YOLO
except ImportError:
    print("Error: ultralytics not installed. Run: pip install ultralytics")
    sys.exit(1)


def export_onnx(
    model_path: str,
    output_dir: str = "../models",
    imgsz: int = 640,
    half: bool = False,
    simplify: bool = True,
    dynamic: bool = False
):
    print(f"Loading model from {model_path}...")
    model = YOLO(model_path)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    model_name = Path(model_path).stem
    output_path = Path(output_dir) / f"{model_name}.onnx"
    
    print(f"Exporting to ONNX...")
    print(f"  Image size: {imgsz}")
    print(f"  Half precision (FP16): {half}")
    print(f"  Simplify: {simplify}")
    print(f"  Dynamic batch: {dynamic}")
    
    start = time.time()
    
    model.export(
        format="onnx",
        imgsz=imgsz,
        half=half,
        simplify=simplify,
        dynamic=dynamic
    )
    
    export_time = time.time() - start
    
    exported_path = Path(model_path).with_suffix('.onnx')
    if exported_path.exists():
        exported_path.rename(output_path)
    
    print(f"\nExport completed in {export_time:.2f}s")
    print(f"Saved to: {output_path}")
    
    return str(output_path)


def export_tensorrt(
    model_path: str,
    output_dir: str = "../models",
    imgsz: int = 640,
    half: bool = True,
    int8: bool = False,
    workspace: int = 4
):
    print(f"Loading model from {model_path}...")
    model = YOLO(model_path)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    model_name = Path(model_path).stem
    suffix = "_int8" if int8 else "_fp16" if half else "_fp32"
    output_path = Path(output_dir) / f"{model_name}{suffix}.engine"
    
    print(f"Exporting to TensorRT...")
    print(f"  Image size: {imgsz}")
    print(f"  Precision: {'INT8' if int8 else 'FP16' if half else 'FP32'}")
    print(f"  Workspace: {workspace}GB")
    
    start = time.time()
    
    model.export(
        format="engine",
        imgsz=imgsz,
        half=half,
        int8=int8,
        workspace=workspace
    )
    
    export_time = time.time() - start
    
    print(f"\nExport completed in {export_time:.2f}s")
    print(f"Model exported successfully")
    
    return str(output_path)


def benchmark(
    model_paths: list,
    test_image: str = None,
    iterations: int = 100,
    warmup: int = 10
):
    import numpy as np
    import cv2
    
    if test_image:
        frame = cv2.imread(test_image)
    else:
        frame = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    print(f"\nBenchmarking with {iterations} iterations (warmup: {warmup})")
    print("-" * 60)
    
    results = {}
    
    for model_path in model_paths:
        if not Path(model_path).exists():
            print(f"Skipping {model_path} (not found)")
            continue
        
        model = YOLO(model_path)
        
        print(f"\nWarming up {Path(model_path).name}...")
        for _ in range(warmup):
            model(frame, verbose=False)
        
        print(f"Benchmarking {Path(model_path).name}...")
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            model(frame, verbose=False)
            times.append((time.perf_counter() - start) * 1000)
        
        avg = np.mean(times)
        std = np.std(times)
        fps = 1000 / avg
        
        results[Path(model_path).name] = {
            'avg_ms': avg,
            'std_ms': std,
            'fps': fps
        }
        
        print(f"  Average: {avg:.2f}ms ± {std:.2f}ms")
        print(f"  FPS: {fps:.1f}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, r in sorted(results.items(), key=lambda x: x[1]['avg_ms']):
        print(f"{name:30} | {r['avg_ms']:6.2f}ms | {r['fps']:6.1f} FPS")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export YOLOv8 model to ONNX/TensorRT")
    parser.add_argument("action", choices=["onnx", "tensorrt", "benchmark"], help="Export format or benchmark")
    parser.add_argument("--model", "-m", default="../models/best.pt", help="Input model path")
    parser.add_argument("--output", "-o", default="../models", help="Output directory")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--half", action="store_true", help="Use FP16")
    parser.add_argument("--int8", action="store_true", help="Use INT8 (TensorRT only)")
    parser.add_argument("--simplify", action="store_true", default=True, help="Simplify ONNX")
    parser.add_argument("--iterations", type=int, default=100, help="Benchmark iterations")
    
    args = parser.parse_args()
    
    if args.action == "onnx":
        export_onnx(
            args.model,
            args.output,
            args.imgsz,
            args.half,
            args.simplify
        )
    elif args.action == "tensorrt":
        export_tensorrt(
            args.model,
            args.output,
            args.imgsz,
            args.half,
            args.int8
        )
    elif args.action == "benchmark":
        models = [
            args.model,
            args.model.replace('.pt', '.onnx'),
            args.model.replace('.pt', '_fp16.engine'),
        ]
        benchmark(models, iterations=args.iterations)
