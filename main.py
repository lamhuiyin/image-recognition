from features.processor import process_images_in_batches
from search.similarity import search_similar_images, get_similar_items

def main():
    # Process existing images (only need to do this once)
    print("Processing images to extract features...")
    process_images_in_batches()
    
    # Example usage after processing
    print("\nFinding similar items to a specific item...")
    similar_items = get_similar_items("03ES3wphjCBxxAwmWasc")
    print("Similar items:", similar_items)
    
    print("\nSearching for similar images based on a query image...")
    search_results = search_similar_images("/content/800x.jpg")
    print("Search results:", search_results)

if __name__ == "__main__":
    main()
