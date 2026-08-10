import os
import sys

html_file = 'bigquery-data-engineering-codelab/index.html'

if not os.path.exists(html_file):
    print("Error: index.html not found.")
    sys.exit(1)

with open(html_file, 'r') as f:
    content = f.read()

# Check if already injected
if 'copy-button-script' in content:
    print("Script already injected.")
    sys.exit(0)

injection = """
<!-- copy-button-script -->
<script>
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('pre').forEach(pre => {
        let btn = document.createElement('button');
        btn.innerText = 'Copy';
        btn.style.position = 'absolute';
        btn.style.right = '10px';
        btn.style.top = '10px';
        btn.style.padding = '4px 8px';
        btn.style.border = 'none';
        btn.style.borderRadius = '4px';
        btn.style.background = '#4285f4';
        btn.style.color = '#fff';
        btn.style.cursor = 'pointer';
        btn.style.fontSize = '12px';
        btn.style.fontFamily = 'Roboto, sans-serif';
        btn.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
        
        btn.onclick = () => {
            // Get all text content EXCEPT the button's own text
            let code = Array.from(pre.childNodes)
                .filter(node => node !== btn)
                .map(node => node.textContent)
                .join('');
            navigator.clipboard.writeText(code).then(() => {
                btn.innerText = 'Copied!';
                btn.style.background = '#0f9d58';
                setTimeout(() => {
                    btn.innerText = 'Copy';
                    btn.style.background = '#4285f4';
                }, 2000);
            });
        };
        pre.style.position = 'relative';
        pre.appendChild(btn);
    });
});
</script>
</body>
"""

content = content.replace('</body>', injection)

with open(html_file, 'w') as f:
    f.write(content)

print("Successfully injected copy buttons!")
