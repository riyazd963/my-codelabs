import os
import sys
import re

html_file = 'bigquery-data-engineering-codelab/index.html'

if not os.path.exists(html_file):
    print("Error: index.html not found.")
    sys.exit(1)

with open(html_file, 'r') as f:
    content = f.read()

# 1. Clean up previous injections if they exist to prevent duplicates
if '<!-- custom-ui-script -->' in content:
    content = content.split('<!-- custom-ui-script -->')[0] + "</body>"
elif '<!-- copy-button-script -->' in content:
    content = content.split('<!-- copy-button-script -->')[0] + "</body>"

# 2. Wrap all instances of &lt;YOUR_PROJECT_ID&gt; in a span so JS can easily find them
# claat exports HTML entities, so <YOUR_PROJECT_ID> becomes &lt;YOUR_PROJECT_ID&gt;
content = re.sub(
    r'&lt;YOUR_PROJECT_ID&gt;', 
    r'<span class="project-id-placeholder" style="color: #ea4335; font-weight: bold;">&lt;YOUR_PROJECT_ID&gt;</span>', 
    content
)

# claat sometimes outputs inline code blocks with literal angle brackets instead of escaping them
content = re.sub(
    r'<YOUR_PROJECT_ID>', 
    r'<span class="project-id-placeholder" style="color: #ea4335; font-weight: bold;">&lt;YOUR_PROJECT_ID&gt;</span>', 
    content
)

# 3. Inject the UI (Input Box + Copy Buttons)
injection = """
<!-- custom-ui-script -->
<div id="project-id-container" style="position: fixed; top: 15px; right: 15px; z-index: 9999; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #dadce0; display: flex; align-items: center; gap: 10px; font-family: Roboto, sans-serif;">
    <label for="project-id-input" style="font-size: 13px; font-weight: 500; color: #3c4043;">GCP Project ID:</label>
    <input type="text" id="project-id-input" placeholder="my-gcp-project" style="padding: 6px 10px; border: 1px solid #dadce0; border-radius: 4px; font-size: 13px; outline: none; width: 150px;">
    <button id="project-id-apply" style="padding: 6px 12px; background: #1a73e8; color: white; border: none; border-radius: 4px; font-size: 13px; cursor: pointer; font-weight: 500;">Apply</button>
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
    // 1. Dynamic Project ID Logic
    const applyBtn = document.getElementById('project-id-apply');
    const inputField = document.getElementById('project-id-input');
    
    applyBtn.onclick = () => {
        const newVal = inputField.value.trim() || '&lt;YOUR_PROJECT_ID&gt;';
        document.querySelectorAll('.project-id-placeholder').forEach(el => {
            el.innerText = newVal;
            el.style.color = newVal === '&lt;YOUR_PROJECT_ID&gt;' ? '#ea4335' : '#1a73e8';
        });
        applyBtn.innerText = 'Applied!';
        applyBtn.style.background = '#0f9d58';
        setTimeout(() => {
            applyBtn.innerText = 'Apply';
            applyBtn.style.background = '#1a73e8';
        }, 2000);
    };

    // 2. Copy Buttons Logic
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

print("Successfully injected dynamic Project ID UI and Copy buttons!")
