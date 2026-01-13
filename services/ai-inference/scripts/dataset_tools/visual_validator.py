import cv2
import numpy as np
from pathlib import Path
import random
from tqdm import tqdm
import yaml

class VisualValidator:
    """
    Visual validation tool for YOLO dataset
    Draws bounding boxes on sample images to verify conversions
    """
    
    def __init__(self, dataset_dir, output_dir, class_names, sample_size=50):
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.class_names = class_names
        self.sample_size = sample_size
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Color palette for different classes (BGR format)
        self.colors = [
            (0, 255, 0),      # Green - Hardhat
            (255, 0, 255),    # Magenta - Mask
            (0, 0, 255),      # Red - NO-Hardhat
            (0, 165, 255),    # Orange - NO-Mask
            (0, 100, 255),    # Dark Orange - NO-Safety Vest
            (255, 255, 0),    # Cyan - Person
            (0, 255, 255),    # Yellow - Safety Cone
            (0, 200, 0),      # Dark Green - Safety Vest
            (128, 128, 128),  # Gray - machinery
            (255, 0, 0)       # Blue - vehicle
        ]
        
        self.stats = {
            'total_samples': 0,
            'valid': 0,
            'invalid': 0,
            'empty_labels': 0
        }
    
    def yolo_to_bbox(self, yolo_coords, img_width, img_height):
        """Convert YOLO format to pixel coordinates"""
        x_center, y_center, width, height = yolo_coords
        
        x_center *= img_width
        y_center *= img_height
        width *= img_width
        height *= img_height
        
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        
        return x1, y1, x2, y2
    
    def draw_boxes(self, image, label_file):
        """Draw bounding boxes on image"""
        if not label_file.exists():
            return image, 0
        
        img_height, img_width = image.shape[:2]
        box_count = 0
        
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            
            class_id = int(parts[0])
            coords = list(map(float, parts[1:5]))
            
            # Convert to pixel coordinates
            x1, y1, x2, y2 = self.yolo_to_bbox(coords, img_width, img_height)
            
            # Get color and class name
            color = self.colors[class_id % len(self.colors)]
            class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"Class_{class_id}"
            
            # Draw box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            label = f"{class_name}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(image, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
            cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            box_count += 1
        
        return image, box_count
    
    def validate_split(self, split_name):
        """Validate samples from a specific split"""
        print(f"\n📸 Validating {split_name} split...")
        
        img_dir = self.dataset_dir / split_name / 'images'
        lbl_dir = self.dataset_dir / split_name / 'labels'
        
        if not img_dir.exists():
            print(f"⚠️  {split_name} directory not found")
            return
        
        # Get all images
        all_images = list(img_dir.glob('*'))
        
        if len(all_images) == 0:
            print(f"⚠️  No images found in {split_name}")
            return
        
        # Sample random images
        sample_count = min(self.sample_size, len(all_images))
        sampled_images = random.sample(all_images, sample_count)
        
        output_split_dir = self.output_dir / split_name
        output_split_dir.mkdir(exist_ok=True)
        
        for img_path in tqdm(sampled_images, desc=f"  Processing {split_name}", leave=False):
            # Read image
            image = cv2.imread(str(img_path))
            
            if image is None:
                self.stats['invalid'] += 1
                continue
            
            # Get corresponding label file
            label_file = lbl_dir / (img_path.stem + '.txt')
            
            # Draw boxes
            annotated_image, box_count = self.draw_boxes(image.copy(), label_file)
            
            if box_count == 0:
                self.stats['empty_labels'] += 1
            
            # Save annotated image
            output_path = output_split_dir / img_path.name
            cv2.imwrite(str(output_path), annotated_image)
            
            self.stats['valid'] += 1
            self.stats['total_samples'] += 1
        
        print(f"  ✓ Saved {sample_count} annotated images to {output_split_dir}")
    
    def create_legend(self):
        """Create a legend image showing class colors"""
        legend_height = 30 * len(self.class_names) + 40
        legend_width = 400
        legend = np.ones((legend_height, legend_width, 3), dtype=np.uint8) * 255
        
        # Title
        cv2.putText(legend, "Class Color Legend", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Draw each class
        for idx, class_name in enumerate(self.class_names):
            y = 50 + idx * 30
            color = self.colors[idx % len(self.colors)]
            
            # Draw color box
            cv2.rectangle(legend, (10, y - 15), (40, y + 5), color, -1)
            cv2.rectangle(legend, (10, y - 15), (40, y + 5), (0, 0, 0), 1)
            
            # Draw class name
            cv2.putText(legend, f"{idx}: {class_name}", (50, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Save legend
        legend_path = self.output_dir / "legend.png"
        cv2.imwrite(str(legend_path), legend)
        print(f"\n🎨 Legend saved to: {legend_path}")
    
    def validate_all(self):
        """Run validation on all splits"""
        print("="*60)
        print("🔍 VISUAL VALIDATOR")
        print("="*60)
        print(f"Dataset: {self.dataset_dir}")
        print(f"Sample size per split: {self.sample_size}")
        print(f"Output: {self.output_dir}")
        print()
        
        # Validate each split
        for split in ['train', 'valid', 'test']:
            self.validate_split(split)
        
        # Create legend
        self.create_legend()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        print(f"Total samples validated: {self.stats['total_samples']}")
        print(f"✅ Valid images: {self.stats['valid']}")
        print(f"📄 Images with no annotations: {self.stats['empty_labels']}")
        print(f"❌ Invalid/corrupted: {self.stats['invalid']}")
        print(f"\n📁 Annotated images saved to: {self.output_dir}")
        print("\n💡 Review the images to verify:")
        print("   - Bounding boxes align correctly with objects")
        print("   - Class labels are accurate")
        print("   - No coordinate normalization errors")
        print("="*60)


def main():
    # Configuration
    BASE_DIR = Path(__file__).parent
    DATASET_DIR = BASE_DIR / "merged_dataset"
    OUTPUT_DIR = BASE_DIR / "validation_visual"
    
    # Class names from Roboflow Construction dataset
    CLASS_NAMES = [
        'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest',
        'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle'
    ]
    
    # Validate
    validator = VisualValidator(
        dataset_dir=DATASET_DIR,
        output_dir=OUTPUT_DIR,
        class_names=CLASS_NAMES,
        sample_size=50  # Adjust based on your needs
    )
    
    validator.validate_all()
    
    print("\n✨ Validation complete!")
    print("📝 Next steps:")
    print("   1. Review images in validation_visual/ folder")
    print("   2. Check if bounding boxes are correctly placed")
    print("   3. If everything looks good, proceed with training!")


if __name__ == "__main__":
    main()
