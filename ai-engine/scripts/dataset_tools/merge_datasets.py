import shutil
from pathlib import Path
import yaml
from tqdm import tqdm
import random

class DatasetMerger:
    """
    Merge Roboflow dataset with converted Kaggle dataset
    Maintains proper train/valid/test split
    """
    
    def __init__(self, roboflow_dir, kaggle_dir, output_dir, split_ratio=None):
        self.roboflow_dir = Path(roboflow_dir)
        self.kaggle_dir = Path(kaggle_dir)
        self.output_dir = Path(output_dir)
        
        # Default split: 70% train, 20% valid, 10% test
        self.split_ratio = split_ratio or {'train': 0.7, 'valid': 0.2, 'test': 0.1}
        
        # Create output structure
        for split in ['train', 'valid', 'test']:
            (self.output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
            (self.output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'roboflow': {'train': 0, 'valid': 0, 'test': 0},
            'kaggle': {'train': 0, 'valid': 0, 'test': 0},
            'total': {'train': 0, 'valid': 0, 'test': 0}
        }
    
    def copy_roboflow_data(self):
        """Copy existing Roboflow dataset structure"""
        print("📦 Copying Roboflow dataset...")
        
        for split in ['train', 'valid', 'test']:
            src_img_dir = self.roboflow_dir / split / 'images'
            src_lbl_dir = self.roboflow_dir / split / 'labels'
            
            if not src_img_dir.exists():
                print(f"⚠️  {split} split not found in Roboflow data, skipping...")
                continue
            
            dst_img_dir = self.output_dir / split / 'images'
            dst_lbl_dir = self.output_dir / split / 'labels'
            
            # Copy images
            images = list(src_img_dir.glob('*'))
            for img in tqdm(images, desc=f"Roboflow {split} images", leave=False):
                shutil.copy2(img, dst_img_dir / img.name)
            
            # Copy labels
            labels = list(src_lbl_dir.glob('*.txt'))
            for lbl in tqdm(labels, desc=f"Roboflow {split} labels", leave=False):
                shutil.copy2(lbl, dst_lbl_dir / lbl.name)
            
            count = len(images)
            self.stats['roboflow'][split] = count
            self.stats['total'][split] += count
            print(f"  ✓ {split}: {count} files")
    
    def split_kaggle_data(self):
        """Split Kaggle converted data into train/valid/test"""
        print("\n📦 Splitting Kaggle dataset...")
        
        kaggle_img_dir = self.kaggle_dir / 'images'
        kaggle_lbl_dir = self.kaggle_dir / 'labels'
        
        if not kaggle_img_dir.exists():
            print("❌ Kaggle converted directory not found!")
            return
        
        # Get all image files
        all_images = list(kaggle_img_dir.glob('*'))
        random.shuffle(all_images)
        
        total = len(all_images)
        train_end = int(total * self.split_ratio['train'])
        valid_end = train_end + int(total * self.split_ratio['valid'])
        
        splits = {
            'train': all_images[:train_end],
            'valid': all_images[train_end:valid_end],
            'test': all_images[valid_end:]
        }
        
        for split, images in splits.items():
            dst_img_dir = self.output_dir / split / 'images'
            dst_lbl_dir = self.output_dir / split / 'labels'
            
            for img in tqdm(images, desc=f"Kaggle {split}", leave=False):
                # Copy image
                shutil.copy2(img, dst_img_dir / img.name)
                
                # Copy corresponding label
                lbl_name = img.stem + '.txt'
                lbl_path = kaggle_lbl_dir / lbl_name
                
                if lbl_path.exists():
                    shutil.copy2(lbl_path, dst_lbl_dir / lbl_name)
            
            count = len(images)
            self.stats['kaggle'][split] = count
            self.stats['total'][split] += count
            print(f"  ✓ {split}: {count} files")
    
    def create_data_yaml(self, class_names):
        """Create data.yaml configuration file"""
        yaml_path = self.output_dir / 'data.yaml'
        
        config = {
            'path': str(self.output_dir.absolute()),
            'train': 'train/images',
            'val': 'valid/images',
            'test': 'test/images',
            'nc': len(class_names),
            'names': class_names
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n📄 Created data.yaml at: {yaml_path}")
    
    def merge(self, class_names):
        """Execute full merge pipeline"""
        print("="*60)
        print("🔗 DATASET MERGER")
        print("="*60)
        print(f"Output: {self.output_dir}")
        print(f"Split ratio: {self.split_ratio}")
        print()
        
        # Copy Roboflow data
        self.copy_roboflow_data()
        
        # Split and copy Kaggle data
        self.split_kaggle_data()
        
        # Create configuration
        self.create_data_yaml(class_names)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print merge summary"""
        print("\n" + "="*60)
        print("📊 MERGE SUMMARY")
        print("="*60)
        
        print("\n📌 Dataset Sources:")
        for split in ['train', 'valid', 'test']:
            print(f"\n{split.upper()}:")
            print(f"  Roboflow: {self.stats['roboflow'][split]:,} files")
            print(f"  Kaggle:   {self.stats['kaggle'][split]:,} files")
            print(f"  Total:    {self.stats['total'][split]:,} files")
        
        grand_total = sum(self.stats['total'].values())
        print(f"\n🎯 GRAND TOTAL: {grand_total:,} images")
        print("="*60)


def main():
    # Configuration
    BASE_DIR = Path(__file__).parent
    ROBOFLOW_DIR = BASE_DIR / "source_roboflow"
    KAGGLE_DIR = BASE_DIR / "converted_kaggle_yolo"
    OUTPUT_DIR = BASE_DIR / "merged_dataset"
    
    # Class names from Roboflow Construction dataset
    CLASS_NAMES = [
        'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest',
        'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle'
    ]
    
    # Merge
    merger = DatasetMerger(
        roboflow_dir=ROBOFLOW_DIR,
        kaggle_dir=KAGGLE_DIR,
        output_dir=OUTPUT_DIR,
        split_ratio={'train': 0.7, 'valid': 0.2, 'test': 0.1}
    )
    
    merger.merge(CLASS_NAMES)
    
    print("\n✨ Merge complete!")
    print("Next step: Run visual_validator.py to verify dataset quality")


if __name__ == "__main__":
    main()
