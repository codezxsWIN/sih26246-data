class AuthModule {
    constructor() {
        this.container = document.getElementById('main-content');
    }

    render() {
        this.container.innerHTML = `
            <div class="auth">
                <div class="auth__intro">
                    <p class="eyebrow">SIH26246 · Skillcast Labour Market Intelligence Engine</p>
                    <h2 class="auth-title">Welcome to Skillcast.</h2>
                    <p class="auth-subtitle">Select your portal to continue.</p>
                </div>

                <section class="card auth-card">
                    <div class="card__header"><span>Select portal</span><span class="card__meta">3 roles</span></div>
                    <div class="auth-roles">
                        <button class="btn-role" onclick="app.auth.login('policymaker')">
                            <span class="role-icon">01</span>
                            <span class="role-text">
                                <span class="role-name">Policymaker</span>
                                <span class="role-desc">Overview · demand · supply · gap · forecast · risk · policy · copilot</span>
                            </span>
                            <span class="role-arrow" aria-hidden="true">→</span>
                        </button>
                        <button class="btn-role" onclick="app.auth.login('seeker')">
                            <span class="role-icon">02</span>
                            <span class="role-text">
                                <span class="role-name">Job Seeker</span>
                                <span class="role-desc">Upload a resume · extracted skills · matched shortage roles</span>
                            </span>
                            <span class="role-arrow" aria-hidden="true">→</span>
                        </button>
                        <button class="btn-role" onclick="app.auth.login('employer')">
                            <span class="role-icon">03</span>
                            <span class="role-text">
                                <span class="role-name">Employer</span>
                                <span class="role-desc">Regional talent pools · hiring difficulty · sourcing advice</span>
                            </span>
                            <span class="role-arrow" aria-hidden="true">→</span>
                        </button>
                    </div>
                </section>
            </div>
        `;
    }

    async login(role, redirectRoute = null) {
        try {
            const res = await fetch('http://localhost:8000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: role + "@example.com",
                    password: "password",
                    role: role
                })
            });
            if (!res.ok) throw new Error("Login failed with status " + res.status);
            const data = await res.json();
            
            localStorage.setItem('lmi_token', data.token);
            localStorage.setItem('lmi_role', data.role);
            
            // Redirect based on role or specific redirectRoute
            app.state.setRole(data.role);
            const defaultRoute = data.role === 'seeker' ? '/seeker' : (data.role === 'employer' ? '/employer' : '/dashboard');
            let targetRoute = defaultRoute;
            if (redirectRoute) {
                targetRoute = '/' + redirectRoute.replace(/^#?\/?/, '');
            }
            app.router.navigate(targetRoute);
        } catch (error) {
            console.error("Login failed:", error);
            alert("Login failed. Check console.");
        }
    }
    
    logout() {
        localStorage.removeItem('lmi_token');
        localStorage.removeItem('lmi_role');
        app.state.setRole(null);
        app.router.navigate('/auth');
    }
}

window.AuthModule = AuthModule;
