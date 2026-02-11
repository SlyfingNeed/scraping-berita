import os
import pandas as pd
from typing import List, Dict
from datetime import datetime
import config
from utils import get_date_string, ensure_output_folder


class Exporter:
    
    def __init__(self, output_format: str = None):
        self.output_format = output_format or config.OUTPUT_FORMAT
        ensure_output_folder()
    
    def get_output_filename(self) -> str:
  
        date_str = get_date_string()
        filename = f"{config.OUTPUT_FILENAME_PREFIX}_{date_str}.{self.output_format}"
        return os.path.join(config.OUTPUT_FOLDER, filename)
    
    def save_articles(self, articles: List[Dict]) -> str:
        
        if not articles:
            print("No articles to save")
            return None
        
        # Prepare dataframe
        df = pd.DataFrame(articles)
        
        # Ensure columns are in correct order
        column_order = [
            'title',
            'content',
            'matched_keyword',
            'source',
            'category',
            'published_date',
            'url',
            'scraped_at'
        ]
        
        # Add missing columns with empty values
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns
        df = df[column_order]
        
        # Get output filename
        output_path = self.get_output_filename()
        
        # Check if file exists for appending
        file_exists = os.path.exists(output_path)
        
        try:
            if self.output_format == 'csv':
                self._save_csv(df, output_path, file_exists)
            elif self.output_format == 'xlsx':
                self._save_xlsx(df, output_path, file_exists)
            else:
                raise ValueError(f"Unsupported format: {self.output_format}")
            
            print(f"\nSaved {len(articles)} articles to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    def _save_csv(self, df: pd.DataFrame, filepath: str, file_exists: bool):
      
        if file_exists:
            
            df.to_csv(filepath, mode='a', header=False, index=False, encoding='utf-8-sig')
            print(f"  Appended to existing CSV")
        else:
          
            df.to_csv(filepath, mode='w', header=True, index=False, encoding='utf-8-sig')
            print(f"  Created new CSV")
    
    def _save_xlsx(self, df: pd.DataFrame, filepath: str, file_exists: bool):
        
        if file_exists:
         
            try:
                existing_df = pd.read_excel(filepath, engine='openpyxl')
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.to_excel(filepath, index=False, engine='openpyxl')
                print(f"  Appended to existing XLSX")
            except Exception as e:
                print(f"  Could not append to XLSX: {e}")
                print(f"  Creating backup and saving...")
                
                backup_path = filepath.replace('.xlsx', f'_backup_{int(datetime.now().timestamp())}.xlsx')
                if os.path.exists(filepath):
                    os.rename(filepath, backup_path)
                
                df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            # Create new file
            df.to_excel(filepath, index=False, engine='openpyxl')
            print(f"  Created new XLSX")
    
    def get_existing_article_count(self) -> int:
       
        output_path = self.get_output_filename()
        
        if not os.path.exists(output_path):
            return 0
        
        try:
            if self.output_format == 'csv':
                df = pd.read_csv(output_path, encoding='utf-8-sig')
            elif self.output_format == 'xlsx':
                df = pd.read_excel(output_path, engine='openpyxl')
            else:
                return 0
            
            return len(df)
        except Exception:
            return 0


if __name__ == "__main__":
    
    from datetime import datetime
    
    test_articles = [
        {
            'title': 'Bitcoin Naik 10 Persen',
            'content': 'Harga Bitcoin mengalami kenaikan signifikan sebesar 10 persen dalam 24 jam terakhir...',
            'matched_keyword': 'bitcoin',
            'source': 'Test News',
            'category': 'Teknologi',
            'published_date': '2024-01-15',
            'url': 'https://example.com/bitcoin-naik',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'title': 'Startup AI Indonesia Raih Pendanaan',
            'content': 'Sebuah startup AI lokal berhasil mendapatkan pendanaan Seri A...',
            'matched_keyword': 'AI, startup',
            'source': 'Test News',
            'category': 'Bisnis',
            'published_date': '2024-01-15',
            'url': 'https://example.com/startup-ai',
            'scraped_at': datetime.now().isoformat()
        }
    ]
    
    print("Testing CSV export...")
    exporter_csv = Exporter(output_format='csv')
    exporter_csv.save_articles(test_articles)
    
    print("\nTesting XLSX export...")
    exporter_xlsx = Exporter(output_format='xlsx')
    exporter_xlsx.save_articles(test_articles)
    
    print("\n Test complete!")
