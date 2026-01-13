import xml.etree.ElementTree as ET
import os
from pathlib import Path
from PIL import Image
from tqdm import tqdm

class XMLtoYOLOConverter:
    """
    Convert Pascal VOC XML annotations to YOLO format
    Mapping: helmet -> 0 (Hardhat), head -> 2 (NO-Hardhat)
    """
    
    def __init__(self, xml_dir, images_dir, output_dir, label_mapping):
        self.xml_dir = Path(xml_dir)
        self.images_dir = Path(images_dir)
        self.output_dir = Path(output_dir)
        self.label_mapping = label_mapping
        
        # Create output directories
        self.output_labels = self.output_dir / "labels"
        self.output_images = self.output_dir / "images"
        self.output_labels.mkdir(parents=True, exist_ok=True)
        self.output_images.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'converted': 0,
            'empty_annotations': 0,
            'skipped': 0,
            'errors': []
        }
    
    def parse_xml(self, xml_path):
        """Parse XML file and extract bounding boxes"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Get image dimensions
            size = root.find('size')
            width = int(size.find('width').text)
            height = int(size.find('height').text)
            
            # Extract all objects
            objects = []
            for obj in root.findall('object'):
                class_name = obj.find('name').text
                
                # Skip if class not in mapping
                if class_name not in self.label_mapping:
                    continue
                
                class_id = self.label_mapping[class_name]
                
                # Get bounding box
                bndbox = obj.find('bndbox')
                xmin = int(bndbox.find('xmin').text)
                ymin = int(bndbox.find('ymin').text)
                xmax = int(bndbox.find('xmax').text)
                ymax = int(bndbox.find('ymax').text)
                
                # Convert to YOLO format (normalized)
                x_center = ((xmin + xmax) / 2) / width
                y_center = ((ymin + ymax) / 2) / height
                bbox_width = (xmax - xmin) / width
                bbox_height = (ymax - ymin) / height
                
                objects.append({
                    'class_id': class_id,
                    'x_center': x_center,
                    'y_center': y_center,
                    'width': bbox_width,
                    'height': bbox_height
                })
            
            return objects, width, height
            
        except Exception as e:
            self.stats['errors'].append(f"{xml_path.name}: {str(e)}")
            return None, None, None
    
    def convert_file(self, xml_filename):
        """Convert single XML file to YOLO format"""
        xml_path = self.xml_dir / xml_filename
        
        # Parse XML
        objects, width, height = self.parse_xml(xml_path)
        
        if objects is None:
            self.stats['skipped'] += 1
            return False
        
        # Get corresponding image filename
        image_filename = xml_filename.replace('.xml', '.png')
        image_path = self.images_dir / image_filename
        
        # Check if image exists
        if not image_path.exists():
            # Try .jpg extension
            image_filename = xml_filename.replace('.xml', '.jpg')
            image_path = self.images_dir / image_filename
            
            if not image_path.exists():
                self.stats['errors'].append(f"Image not found: {image_filename}")
                self.stats['skipped'] += 1
                return False
        
        # Create YOLO annotation file
        txt_filename = xml_filename.replace('.xml', '.txt')
        txt_path = self.output_labels / txt_filename
        
        # Write annotations (even if empty - for negative samples)
        with open(txt_path, 'w') as f:
            for obj in objects:
                line = f"{obj['class_id']} {obj['x_center']:.6f} {obj['y_center']:.6f} {obj['width']:.6f} {obj['height']:.6f}\n"
                f.write(line)
        
        # Copy image to output directory
        import shutil
        shutil.copy2(image_path, self.output_images / image_filename)
        
        self.stats['converted'] += 1
        if len(objects) == 0:
            self.stats['empty_annotations'] += 1
        
        return True
    
    def convert_all(self):
        """Convert all XML files in directory"""
        xml_files = list(self.xml_dir.glob('*.xml'))
        self.stats['total_files'] = len(xml_files)
        
        print(f"🔄 Converting {len(xml_files)} XML files to YOLO format...")
        print(f"   Label Mapping: {self.label_mapping}")
        print()
        
        for xml_file in tqdm(xml_files, desc="Converting", unit="file"):
            self.convert_file(xml_file.name)
        
        self.print_summary()
    
    def print_summary(self):
        """Print conversion summary"""
        print("\n" + "="*60)
        print("📊 CONVERSION SUMMARY")
        print("="*60)
        print(f"Total files processed: {self.stats['total_files']}")
        print(f"✅ Successfully converted: {self.stats['converted']}")
        print(f"📄 Empty annotations (negative samples): {self.stats['empty_annotations']}")
        print(f"❌ Skipped/Failed: {self.stats['skipped']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            print("First 5 errors:")
            for error in self.stats['errors'][:5]:
                print(f"  - {error}")
        
        print(f"\n📁 Output saved to:")
        print(f"   Labels: {self.output_labels}")
        print(f"   Images: {self.output_images}")
        print("="*60)


def main():
    # Configuration
    BASE_DIR = Path(__file__).parent
    XML_DIR = BASE_DIR / "source_kaggle" / "annotations"
    IMAGES_DIR = BASE_DIR / "source_kaggle" / "images"
    OUTPUT_DIR = BASE_DIR / "converted_kaggle_yolo"
    
    # Label mapping: Kaggle -> Roboflow Construction IDs
    LABEL_MAPPING = {
        'helmet': 0,    # Hardhat
        'head': 2       # NO-Hardhat
    }
    
    # Convert
    converter = XMLtoYOLOConverter(
        xml_dir=XML_DIR,
        images_dir=IMAGES_DIR,
        output_dir=OUTPUT_DIR,
        label_mapping=LABEL_MAPPING
    )
    
    converter.convert_all()
    
    print("\n✨ Conversion complete!")
    print("Next step: Run merge_datasets.py to combine with Roboflow data")


if __name__ == "__main__":
    main()
