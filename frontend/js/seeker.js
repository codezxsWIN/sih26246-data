class SeekerDashboardModule {
    constructor() {
        this.container = document.getElementById('main-content');
    }

    render() {
        this.container.innerHTML = `
            <h1 class="page-title">Job Seeker Portal</h1>
            <p class="page-subtitle">Upload your resume to instantly see shortage matches and market advantages.</p>
            <div class="page-actions">
                <button class="btn btn-secondary" onclick="app.auth.logout()">Logout</button>
            </div>

            <section class="card upload-card">
                <div class="card__header"><span>Upload Resume (PDF)</span><span class="card__meta">Skill extraction · job matching</span></div>
                <div class="card__body upload-card__body">
                    <input type="file" id="resume-upload" accept=".pdf" class="file-input" />
                    <button class="btn btn-primary" onclick="app.seeker.uploadResume()">Extract Skills & Match Jobs</button>
                    <div id="upload-status" class="upload-status"></div>
                </div>
            </section>

            <div id="seeker-results" style="display: none;">
                <div class="grid-2">
                    <section class="card">
                        <div class="card__header">Your Extracted Skills</div>
                        <div class="card__body"><ul id="extracted-skills-list" class="skills-list"></ul></div>
                    </section>
                    <section class="card">
                        <div class="card__header">Recommended Upskilling</div>
                        <div class="card__body">
                            <p class="text-muted card__lede">Skills you need to unlock critical shortage roles:</p>
                            <ul id="missing-skills-list" class="skills-list"></ul>
                        </div>
                    </section>
                </div>

                <section class="card">
                    <div class="card__header">Top Matched Shortage Roles</div>
                    <div class="card__body"><div id="matched-roles-list" class="roles-grid"></div></div>
                </section>
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
        skillsList.innerHTML = (data.extracted_skills || []).map(s => `<li><span class="tag">${s}</span></li>`).join('');
        
        const missingList = document.getElementById('missing-skills-list');
        missingList.innerHTML = (data.missing_skills_for_upskilling || []).map(s => `<li><span class="tag tag-warning">${s}</span></li>`).join('');
        
        const rolesList = document.getElementById('matched-roles-list');
        rolesList.innerHTML = (data.job_matches || []).map(job => `
            <div class="role-card">
                <h4>${job.occupation}</h4>
                <div class="role-meta">
                    <span class="badge ${job.shortage_level && job.shortage_level.includes('Critical') ? 'badge--critical' : 'badge--moderate'}">${job.shortage_level}</span>
                    <span class="badge badge--balanced">Match: ${job.match_score}%</span>
                </div>
                <p>Demand Score: ${Number(job.demand_score || 0).toFixed(1)} / Gap: ${Number(job.gap_volume || 0).toLocaleString()}</p>
            </div>
        `).join('');
    }
}

window.SeekerDashboardModule = SeekerDashboardModule;
