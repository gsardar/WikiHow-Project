import pandas as pd
import matplotlib.pyplot as plt
import os

MASTER_CSV = r"C:\Users\Admin\Documents\WikiHow Project\data\discovery\domestic\cleaned_domestic_master.csv"
OUTPUT_PLOT = r"C:\Users\Admin\Documents\WikiHow Project\data\discovery\domestic\domestic_spectrum_volume.png"

def main():
    if not os.path.exists(MASTER_CSV):
        print(f"[ERROR] Cleaned master CSV not found at {MASTER_CSV}")
        return

    # Load data
    df = pd.read_csv(MASTER_CSV)
    
    # Check if we have data
    if df.empty:
        print("[ERROR] CSV is empty.")
        return

    # Group by Category and Score to get volumes
    # Note: We want unique categories, so we'll group by both to keep the score context
    volume_df = df.groupby(['Category', 'Spectrum Score']).size().reset_index(name='Article Count')
    
    # Sort by Spectrum Score to ensure the plot flows correctly (0 to 9)
    volume_df = volume_df.sort_values('Spectrum Score')
    
    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Using a color map that transitions (e.g., from warm to cool)
    colors = plt.cm.viridis(volume_df['Spectrum Score'] / 10.0)
    
    bars = plt.bar(volume_df['Category'], volume_df['Article Count'], color=colors)
    
    # Formatting
    plt.title('Article Volume Across the Domestic Spectrum (0-9)', fontsize=16, fontweight='bold')
    plt.xlabel('Category (Ordered by Spectrum Score 0 \u2192 9)', fontsize=12)
    plt.ylabel('Total Unique Articles', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add counts on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, int(yval), ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    
    # Save the plot
    plt.savefig(OUTPUT_PLOT)
    print(f"\n[SUCCESS] Spectrum Visualization saved to: {OUTPUT_PLOT}")

if __name__ == "__main__":
    main()
