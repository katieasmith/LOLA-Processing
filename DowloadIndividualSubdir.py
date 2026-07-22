import urllib.request
from html.parser import HTMLParser
import os
import time

#  Which subdirectory you want downloaded
folder_name = 'SM_01'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(SCRIPT_DIR, 'bin')
print(BIN_DIR)

class PDSDirectoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    self.links.append(value)

def get_links(url):
    """Get all links from a URL"""
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
        parser = PDSDirectoryParser()
        parser.feed(html)
        return parser.links
    except Exception as e:
        print(f"Error: {e}")
        return []

def load_processed_files(filename='processed_files.txt'):
    """
    Load list of already processed files from text file
    Returns a set for fast lookup
    """
    filepath = os.path.join(BIN_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            # Read lines and strip whitespace, skip empty lines
            processed = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(processed)} processed files from {filename}")
        return processed
    else:
        print(f"No {filename} found - will download all files")
        return set()

def download_all_lola_rdr():
    """Download all LOLA RDR .DAT files"""
    
    lola_dir = os.path.join(BIN_DIR, 'lola_data')
    os.makedirs(lola_dir, exist_ok=True)
    
    # Load list of already processed files
    processed_files = load_processed_files('processed_files.txt')
    
    # Start with the lola_rdr directory
    rdr_url = "https://imbrium.mit.edu/DATA/LOLA_RDR/"
    
    print("\nAccessing LOLA RDR directory...")
    print(f"URL: {rdr_url}\n")
    
    total_downloaded = 0
    total_skipped_exists = 0
    total_skipped_processed = 0
    total_failed = 0
    
    subdir_url = rdr_url + "LRO_" + folder_name
    
    print(f"\n{'='*60}")
    print(f"Processing: {folder_name}")
    print(f"URL: {subdir_url}")
    print('='*60)
    
    # Get files in this directory
    files = get_links(subdir_url)
    
    # Filter for .DAT files
    DAT_files = [f for f in files if f.endswith('.DAT')]
    
    print(f"Found {len(DAT_files)} .DAT files\n")
    
    if len(DAT_files) == 0:
        print("No .DAT files found, skipping...\n")
    
    # Download each file
    for DAT_filename in DAT_files:
        # Extract just the filename
        if '/' in DAT_filename:
            DAT_filename = DAT_filename.split('/')[-1]
        
        # Construct full URL
        DAT_url = subdir_url + "/" + DAT_filename
        
        DAT_local = os.path.join(lola_dir, DAT_filename)
        
        # Check if file is in processed list
        if DAT_filename in processed_files:
            print(f"⊘ {DAT_filename} - already processed (in processed_files.txt)")
            total_skipped_processed += 1
            continue
        
        # Check if file already exists locally
        if os.path.exists(DAT_local):
            file_size = os.path.getsize(DAT_local) / (1024 * 1024)
            print(f"↷ {DAT_filename} ({file_size:.1f} MB) - already exists locally")
            total_skipped_exists += 1
            continue
        
        print(f"Downloading {DAT_filename}...")
        
        try:
            # Download .DAT file
            urllib.request.urlretrieve(DAT_url, DAT_local + '.tmp')
            os.rename(DAT_local + '.tmp', DAT_local)
            
            file_size = os.path.getsize(DAT_local) / (1024 * 1024)
            
            print(f"  ✓ {file_size:.1f} MB")
            total_downloaded += 1
            
            total_files = total_downloaded + total_skipped_exists + total_skipped_processed
            print(f"Progress: Downloaded {total_downloaded} | Skipped {total_skipped_exists + total_skipped_processed} | Total {total_files}")
            
            # Be polite
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            total_failed += 1
            
            # Cleanup
            if os.path.exists(DAT_local + '.tmp'):
                os.remove(DAT_local + '.tmp')
            if os.path.exists(DAT_local):
                os.remove(DAT_local)
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)
    print(f"Downloaded:            {total_downloaded}")
    print(f"Skipped (local):       {total_skipped_exists}")
    print(f"Skipped (processed):   {total_skipped_processed}")
    print(f"Failed:                {total_failed}")
    print(f"Total:                 {total_downloaded + total_skipped_exists + total_skipped_processed}")
    
    # Calculate total size
    if os.path.exists(lola_dir):
        total_size = sum(os.path.getsize(os.path.join(lola_dir, f)) 
                        for f in os.listdir(lola_dir) if f.endswith('.DAT'))
        total_size_gb = total_size / (1024 * 1024 * 1024)
        print(f"\nTotal data size: {total_size_gb:.2f} GB")

if __name__ == "__main__":
    download_all_lola_rdr()