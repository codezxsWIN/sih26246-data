class SeekerDashboardModule {
    constructor() {
        this.container = document.getElementById('main-content');
    }

    render() {
        this.container.innerHTML = `
            <div class="dashboard-header">
                <h2>Job Seeker Portal</h2>
                <p>Upload your resume to instantly see shortage matches and market advantages.</p>
                <button class="btn btn-secondary" onclick="app.auth.logout()">Logout</button>
            </div>
            
            <div class="card-glass upload-card">
                <h3>Upload Resume (PDF)</h3>
                <input type="file" id="resume-upload" accept=".pdf" class="file-input" />
                <button class="btn btn-primary" onclick="app.seeker.uploadResume()">Extract Skills & Match Jobs</button>
                <div id="upload-status" style="margin-top: 15px; color: var(--accent-blue);"></div>
            </div>
            
            <div id="seeker-results" style="display: none; margin-top: 20px;">
                <div class="grid-2">
                    <div class="card-glass">
                        <h3>Your Extracted Skills</h3>
                        <ul id="extracted-skills-list" class="skills-list"></ul>
                    </div>
                    <div class="card-glass">
                        <h3>Recommended Upskilling</h3>
                        <p class="text-muted">Skills you need to unlock critical shortage roles:</p>
                        <ul id="missing-skills-list" class="skills-list"></ul>
                    </div>
                </div>
                
                <h3 style="margin-top: 30px;">Top Matched Shortage Roles</h3>
                <div id="matched-roles-list" class="roles-grid"></div>
            </div>
        `;
    }

    async uploadResume() {
        const fileInput = document.getElementById('resume-upload');
        const statusDiv = document.getElementById('upload-status');
        
        if (!fileInput.files.length) {
            statusDiv.textContent = "Please select a PDF file first.";
            return;
        }
        
        const file = fileInput.files[0];
        statusDiv.textContent = "Uploading and extracting skills using AI...";
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('http://localhost:8000/api/seeker/resume/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error("Upload failed");
            
            const data = await response.json();
            statusDiv.textContent = "Analysis complete!";
            
            this.displayResults(data);
        } catch (error) {
            console.error("Upload error:", error);
            statusDiv.textContent = "Error processing resume.";
        }
    }
    
    displayResults(data) {
        document.getElementById('seeker-results').style.display = 'block';
        
        const skillsList = document.getElementById('extracted-skills-list');
        skillsList.innerHTML = data.extracted_skills.map(s => \`<li><span class="tag">\${s}</span></li>\`).join('');
        
        const missingList = document.getElementById('missing-skills-list');
        missingList.innerHTML = data.missing_skills_for_upskilling.map(s => \`<li><span class="tag tag-warning">\${s}</span></li>\`).join('');
        
        const rolesList = document.getElementById('matched-roles-list');
        rolesList.innerHTML = data.job_matches.map(job => \`
            <div class="card-glass role-card">
                <h4>\${job.occupation}</h4>
                <div class="role-meta">
                    <span class="badge badge-\${job.shortage_level.includes('Critical') ? 'critical' : 'warning'}">\${job.shortage_level}</span>
                    <span class="badge badge-success">Match: \${job.match_score}%</span>
                </div>
                <p>Demand Score: \${job.demand_score.toFixed(1)} / Gap: \${job.gap_volume.toLocaleString()}</p>
            </div>
        \`).join('');
    }
}

window.SeekerDashboardModule = SeekerDashboardModule;
