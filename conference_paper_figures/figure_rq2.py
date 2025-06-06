import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib as mpl
from adjustText import adjust_text  # You may need to install this: pip install adjustText

# Configure matplotlib for high-quality output
mpl.rcParams['pdf.fonttype'] = 42  # Ensures fonts are embedded properly
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'serif'  # Serif fonts are common in academic publications
mpl.rcParams['font.serif'] = ['Times New Roman']  # Common journal font
mpl.rcParams['axes.linewidth'] = 0.8  # Slightly thinner lines for a cleaner look
mpl.rcParams['xtick.major.width'] = 0.8
mpl.rcParams['ytick.major.width'] = 0.8

# Set a professional style with minimal gridlines
plt.style.use('seaborn-v0_8')
sns.set_style("whitegrid", {'grid.linestyle': ':'})

# Load the data
df = pd.read_csv('llm_pt_sdp_f1_harmonic_means.csv', delimiter='\t')

# Get unique values for categorical variables
llms = df['llm'].unique()
prompts = df['prompt'].unique()
decision_points = df['ssvc_decision_point'].unique()

# Create abbreviations for prompting techniques using first letter of each word
prompt_abbrev = {}
for prompt in prompts:
    # Split by underscore and take first letter of each word
    words = prompt.split('_')
    abbrev = ''.join([word[0].upper() for word in words])
    prompt_abbrev[prompt] = abbrev

# Create a mapping of prompts to numeric values for x-axis
prompt_mapping = {prompt: i for i, prompt in enumerate(sorted(prompts))}
df['prompt_numeric'] = df['prompt'].map(prompt_mapping)

# Filter to keep only the top 5 F1 scores for each prompting technique
top_df = pd.DataFrame()
for prompt in prompts:
    prompt_data = df[df['prompt'] == prompt]
    # Get top 5 combinations of LLM and decision point for this prompt
    top_5_prompt = prompt_data.nlargest(5, 'f1_harmonic_mean')
    top_df = pd.concat([top_df, top_5_prompt])

# Get the unique LLMs and decision points that appear in the top 5
top_llms = top_df['llm'].unique()
top_decision_points = top_df['ssvc_decision_point'].unique()

# Define marker shapes for LLMs - using a variety of distinct shapes
markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h', 'H', 'X']
llm_markers = {llm: markers[i % len(markers)] for i, llm in enumerate(sorted(top_llms))}

# Define a professional color palette for decision points
# Using a colorblind-friendly palette from seaborn
colors = sns.color_palette("colorblind", len(top_decision_points))
decision_colors = {dp: colors[i] for i, dp in enumerate(sorted(top_decision_points))}

# Create the figure with appropriate dimensions
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

# Create scatter plot with different colors and shapes
texts = []  # To store text objects for adjust_text
for llm in sorted(top_llms):
    for decision in sorted(top_decision_points):
        subset = top_df[(top_df['llm'] == llm) & (top_df['ssvc_decision_point'] == decision)]
        if not subset.empty:
            ax.scatter(
                subset['prompt_numeric'], 
                subset['f1_harmonic_mean'],
                c=[decision_colors[decision]] * len(subset),
                marker=llm_markers[llm],
                s=100,  # Slightly larger markers for better visibility
                alpha=0.8,
                label=f"{llm.split('/')[-1]} - {decision}",
                edgecolors='black',  # Add black edge to markers for better definition
                linewidth=0.5
            )
            
            # Add data value labels for each point
            for _, row in subset.iterrows():
                # Format the F1 score to 2 decimal places
                label_text = f"{row['f1_harmonic_mean']:.2f}"
                
                # Create text object with a white background for better visibility
                text = ax.text(
                    row['prompt_numeric'] + 0.15,  # Position to the right of the point
                    row['f1_harmonic_mean'],
                    label_text,
                    fontsize=8,
                    ha='left',
                    va='center',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1),
                    zorder=5  # Ensure text is above other elements
                )
                texts.append(text)

# Use adjust_text to prevent overlapping labels
adjust_text(
    texts,
    arrowprops=dict(arrowstyle='->', color='gray', lw=0.5),
    expand_points=(1.5, 1.5),
    force_points=(0.1, 0.1)
)

# Create custom legend elements for LLMs and decision points only
legend_elements = []

# Add markers for LLMs that appear in the top 5
for llm in sorted(top_llms):
    # Use just the model name (after the last slash) for cleaner labels
    model_name = llm.split('/')[-1]
    
    # Extract the first word before the first hyphen
    if '-' in model_name:
        model_name = model_name.split('-', 1)[0]
    
    # Capitalize the first letter
    if model_name:
        model_name = model_name[0].upper() + model_name[1:]
    
    legend_elements.append(plt.Line2D([0], [0], marker=llm_markers[llm], color='w', 
                          markerfacecolor='gray', markersize=8, label=model_name))

# Add colors for decision points that appear in the top 5
for decision in sorted(top_decision_points):
    # Replace underscores with spaces for better readability
    readable_decision = decision.replace('_', ' ')
    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=decision_colors[decision], markersize=8, label=readable_decision))

# Create two separate legends with appropriate font sizes
llm_legend = ax.legend(handles=legend_elements[:len(top_llms)], 
                     title="LLM Model", 
                     loc='upper left', 
                     bbox_to_anchor=(1.01, 1),
                     fontsize=8,
                     title_fontsize=9)
ax.add_artist(llm_legend)

decision_legend = ax.legend(handles=legend_elements[len(top_llms):], 
                           title="SSVC Decision Point", 
                           loc='upper left', 
                           bbox_to_anchor=(1.01, 0.5),
                           fontsize=8,
                           title_fontsize=9)

# Set x-axis ticks to prompting technique names with diagonal labels
ax.set_xticks(range(len(prompts)))
ax.set_xticklabels([prompt_abbrev[prompt] for prompt in sorted(prompts)], 
                   rotation=45,  # Diagonal labels
                   ha='right',   # Horizontal alignment
                   fontsize=9)

# Set y-axis limits to start from 0.5 for better focus on the data range
y_min = 0.5
y_max = max(top_df['f1_harmonic_mean']) * 1.05  # Slight padding at the top
ax.set_ylim(y_min, y_max)

# Add labels with appropriate font sizes
ax.set_xlabel('Prompting Technique', fontsize=10)
ax.set_ylabel('Harmonic Mean of Trial F1-Scores', fontsize=10)

# Customize grid for better readability - horizontal lines only, lighter color
ax.grid(True, axis='y', linestyle=':', alpha=0.7, color='lightgray')
ax.grid(False, axis='x')  # Remove vertical grid lines

# Adjust layout to make room for the legends
plt.tight_layout()
fig.subplots_adjust(right=0.75)  # Only adjust right margin for legends, no bottom adjustment needed

# Save the figure in multiple formats suitable for publications
plt.savefig('prompt_top5_performance_plot.pdf', bbox_inches='tight', dpi=600)
plt.savefig('prompt_top5_performance_plot.png', bbox_inches='tight', dpi=600)
plt.savefig('prompt_top5_performance_plot.tiff', bbox_inches='tight', dpi=600)
plt.savefig('prompt_top5_performance_plot.eps', bbox_inches='tight', dpi=600)

print("Professional figure with data value labels saved in multiple formats.")
