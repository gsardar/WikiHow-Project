import re

with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Paper Container width
html = html.replace('''        .paper-container {
            max-width: 1000px;
            margin: 0 auto;''', '''        .paper-container {
            max-width: 100%;
            margin: 0;''')

# 2. Extract Figure 3 block
fig3_pattern = re.compile(r'(<div class="tabula-card">\s*<h4>Figure 3\. Contributor Drop-off by Tenure</h4>.*?</div>\s*</div>)', re.DOTALL)
fig3_match = fig3_pattern.search(html)

if fig3_match:
    fig3_html = fig3_match.group(1)
    
    # We want to extract JUST the inner .tabula-card for Fig 3 and remove it from 1.1
    # Actually, the div ends with two </div> because it might be the end of tabula-grid.
    # Let me just carve exactly what I need.
    
html = html.replace('''                <div class="tabula-card">
                    <h4>Figure 3. Contributor Drop-off by Tenure</h4>
                    <p class="desc-text">Visualizes the account dormancy lifecycle, highlighting the "churn rate" and
                        establishing the long-term "Super-User" base.</p>
                    <div class="chart-container">
                        <canvas id="decayChart"></canvas>
                    </div>
                </div>''', '')

# Figure 4 -> Figure 3
html = html.replace('<h4>Figure 4. Macro-Continuum Contribution Breakdown</h4>', '<h4>Figure 3. Macro-Continuum Contribution Breakdown</h4>')
# Figure 5 -> Figure 4
html = html.replace('Figure 5a', 'Figure 4a').replace('Figure 5b', 'Figure 4b').replace('Figure 5c', 'Figure 4c').replace('Figure 5d', 'Figure 4d').replace('Figure 5e', 'Figure 4e')

# Figure 9 -> Figure 6
html = html.replace('''                <div class="tabula-card">
                    <h4>Figure 9. Temporal Friction in Platform Promotion</h4>
                    <p class="desc-text">Measures the average months of active tenure required for varying demographics to earn authoritative versus social badges.</p>
                    <div class="chart-container">
                        <canvas id="promotionChart"></canvas>
                    </div>
                </div>''', '')

# Put Fig 5 (Drop-off) and Fig 6 (Promotion) into 1.3
new_1_3_html = '''            <h3>1.3 Contributions, Gatekeeping & Toxicity</h3>
            <div class="tabula-grid">
                <div class="tabula-card">
                    <h4>Figure 5. Contributor Drop-off by Tenure</h4>
                    <p class="desc-text">Visualizes the account dormancy lifecycle, highlighting the "churn rate" and
                        establishing the long-term "Super-User" base.</p>
                    <div class="chart-container">
                        <canvas id="decayChart"></canvas>
                    </div>
                </div>
                <div class="tabula-card">
                    <h4>Figure 6. Temporal Friction in Platform Promotion</h4>
                    <p class="desc-text">Measures the average months of active tenure required for varying demographics to earn authoritative versus social badges.</p>
                    <div class="chart-container">
                        <canvas id="promotionChart"></canvas>
                    </div>
                </div>'''

html = html.replace('            <h3>1.3 Contributions, Gatekeeping & Toxicity</h3>\n            <div class="tabula-grid">', new_1_3_html)

# Update remaining figures
html = html.replace('Figure 6a.', 'Figure 7a.').replace('Figure 6b.', 'Figure 7b.')
html = html.replace('Figure 7. The Perpetrator', 'Figure 8. The Perpetrator')
html = html.replace('Figure 8. Average Reversion Rate', 'Figure 9. Average Reversion Rate')
html = html.replace('Figure 10. Ideological', 'Figure 10. Ideological')

# Now for the Shifts section, we need 3 charts. Let's fix the HTML for Figure 10 to have 3 charts.
html = html.replace('''                    <div class="chart-container medium">
                        <canvas id="shiftChart"></canvas>
                    </div>''', '''                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                        <div class="chart-container medium"><canvas id="shiftChart1"></canvas></div>
                        <div class="chart-container medium"><canvas id="shiftChart2"></canvas></div>
                        <div class="chart-container medium"><canvas id="shiftChart3"></canvas></div>
                    </div>''')

with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'w', encoding='utf-8') as f:
    f.write(html)
