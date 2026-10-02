class AuthModule {
    constructor() {
        this.container = document.getElementById('main-content');
    }

    render() {
        this.container.innerHTML = `
            <div class="auth-container">
                <div class="card-glass auth-card">
                    <h2 class="auth-title">Welcome to LMI Engine</h2>
                    <p class="auth-subtitle">Select your portal to continue</p>
                    
                    <div class="auth-roles">
                        <button class="btn-role" onclick="app.auth.login('policymaker')">
                            <span class="role-icon">🏛️</span>
                            <span class="role-name">Policymaker</span>
                        </button>
                        <button class="btn-role" onclick="app.auth.login('seeker')">
                            <span class="role-icon">🧑‍💻</span>
                            <span class="role-name">Job Seeker</span>
                        </button>
                        <button class="btn-role" onclick="app.auth.login('employer')">
                            <span class="role-icon">🏢</span>
                            <span class="role-name">Employer</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    async login(role) {
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
            
            // Redirect based on role
            app.state.setRole(data.role);
            const targetRoute = data.role === 'seeker' ? '/seeker' : (data.role === 'employer' ? '/employer' : '/dashboard');
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
