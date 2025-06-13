"""
Document converter using Docling with macOS MPS acceleration
"""

import os
from pathlib import Path
from typing import Optional, List
import torch
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PipelineOptions, EasyOcrOptions


class DoclingMPSConverter:
    """Convert documents using Docling with macOS MPS acceleration"""
    
    def __init__(self, use_mps: bool = True):
        """
        Initialize Docling converter with MPS acceleration
        
        Args:
            use_mps: Whether to use MPS acceleration (default: True on macOS)
        """
        self.use_mps = use_mps and torch.backends.mps.is_available()
        self.supported_formats = [
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
            '.html', '.htm', '.png', '.jpg', '.jpeg'
        ]
        
        print(f"MPS Available: {torch.backends.mps.is_available()}")
        print(f"Using MPS: {self.use_mps}")
        
        # Configure pipeline options for MPS
        self.pipeline_options = self._configure_pipeline_options()
        
        # Initialize converter with MPS configuration
        self.converter = DocumentConverter(
            pipeline_options=self.pipeline_options
        )
    
    def _configure_pipeline_options(self) -> PipelineOptions:
        """Configure pipeline options for MPS acceleration"""
        
        # Configure EasyOCR options for MPS
        ocr_options = EasyOcrOptions(
            lang=['en', 'zh'],  # English and Chinese language support
            use_gpu=self.use_mps,  # Use GPU (MPS) if available
            download_enabled=True,  # Allow model downloads
        )
        
        # Create pipeline options
        pipeline_options = PipelineOptions(
            do_ocr=True,  # Enable OCR
            do_table_structure=True,  # Extract table structure
            ocr_options=ocr_options,
        )
        
        return pipeline_options
    
    def set_mps_environment(self):
        """Set environment variables for MPS acceleration"""
        if self.use_mps:
            # Set PyTorch to use MPS
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            
            # Configure MPS memory management
            if hasattr(torch.mps, 'set_per_process_memory_fraction'):
                torch.mps.set_per_process_memory_fraction(0.8)  # Use 80% of GPU memory
            
            print("✅ MPS environment configured")
        else:
            print("⚠️  MPS not available, using CPU")
    
    def convert_file(self, file_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convert a single file to HTML with MPS acceleration
        
        Args:
            file_path: Path to the input file
            output_dir: Output directory (optional, defaults to same dir as input)
            
        Returns:
            Path to the generated HTML file
        """
        # Set MPS environment
        self.set_mps_environment()
        
        input_path = Path(file_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        # Set output directory
        if output_dir is None:
            output_dir = input_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Converting {input_path.name} with {'MPS' if self.use_mps else 'CPU'} acceleration...")
        
        try:
            # Convert document
            result = self.converter.convert(input_path)
            
            # Generate HTML content
            html_content = result.document.export_to_html()
            
            # Save HTML file
            output_file = output_dir / f"{input_path.stem}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Conversion completed: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"❌ Error converting {file_path}: {str(e)}")
            raise
    
    def convert_batch(self, file_paths: List[str], output_dir: Optional[str] = None) -> List[str]:
        """
        Convert multiple files to HTML with MPS acceleration
        
        Args:
            file_paths: List of input file paths
            output_dir: Output directory
            
        Returns:
            List of generated HTML file paths
        """
        html_files = []
        
        print(f"Starting batch conversion of {len(file_paths)} files...")
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                print(f"\n[{i}/{len(file_paths)}] Processing: {Path(file_path).name}")
                html_file = self.convert_file(file_path, output_dir)
                html_files.append(html_file)
            except Exception as e:
                print(f"❌ Error converting {file_path}: {str(e)}")
                continue
        
        print(f"\n✅ Batch conversion completed: {len(html_files)}/{len(file_paths)} files successful")
        return html_files
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats
    
    def get_system_info(self) -> dict:
        """Get system information for debugging"""
        return {
            "pytorch_version": torch.__version__,
            "mps_available": torch.backends.mps.is_available(),
            "mps_enabled": self.use_mps,
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "current_device": "mps" if self.use_mps else "cpu"
        }