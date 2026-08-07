import re

with open("progress.md", "r") as f:
    content = f.read()

# Update current status
content = re.sub(
    r"## Current Status:.*?\n\*\*Best result so far:.*?\*\*",
    "## Current Status: Cycle 16\n**Best result so far: 15 wins / 20 losses (43%), median $102,745**",
    content
)

# Add row to the table
if "| C16 ⭐ |" not in content:
    table_row = "| C16 ⭐ | **15** | **43%** | **$102,745** | 7-wheat cap, +40 fertilizer hoarding | **Highest win rate and bank! Ready for upload!** |\n"
    content = content.replace("| C15+sheep | ? | ? | ? | C15 + sheep batch 2 only | Running now... |", "| C15+sheep | ? | ? | ? | C15 + sheep batch 2 only | Running now... |\n" + table_row)

# Replace the messy appended text with a clean Tournament Results section
content = re.sub(
    r"### Cycle 16 \(Current\).*?as a milestone\.\*\*",
    "### Cycle 16 (Current)\n- Re-implemented strict WHEAT target (7 units) and hoarding to prevent WHEAT from monopolizing fields and crowding out premium crops like STRAWBERRY.\n- Implemented `FERTILIZER` hoarding (40 units) to drastically increase premium crop yields during peak STRAWBERRY season.\n\n### Tournament Results\n- **Win Rate:** Improved from 34% (in cycle 15) to **43%**.\n- **Median Bank Balance:** Increased to **$102,745**!\n\n**Agent is now in a highly stable state and is recommended for Kaggle upload as a milestone.**",
    content,
    flags=re.DOTALL
)

with open("progress.md", "w") as f:
    f.write(content)
