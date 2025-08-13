// 登录页面JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.querySelector('.login-btn');
    const btnText = document.querySelector('.btn-text');
    const btnLoading = document.querySelector('.btn-loading');

    // 表单提交处理
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        
        // 表单验证
        if (!username || !password) {
            showNotification('请填写用户名和密码', 'error');
            return;
        }
        
        // 显示加载状态
        setLoadingState(true);
        
        // 发送登录请求
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('登录成功，正在跳转...', 'success');
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            } else {
                showNotification(data.message || '登录失败', 'error');
                setLoadingState(false);
            }
        })
        .catch(error => {
            console.error('登录请求失败:', error);
            showNotification('网络错误，请稍后重试', 'error');
            setLoadingState(false);
        });
    });

    // 设置加载状态
    function setLoadingState(loading) {
        if (loading) {
            loginBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
        } else {
            loginBtn.disabled = false;
            btnText.style.display = 'block';
            btnLoading.style.display = 'none';
        }
    }

    // 显示通知
    function showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        const notificationMessage = document.getElementById('notificationMessage');
        
        notificationMessage.textContent = message;
        
        // 设置通知类型样式
        notification.className = `notification notification-${type}`;
        
        // 显示通知
        notification.style.display = 'block';
        
        // 自动隐藏通知（除了错误类型）
        if (type !== 'error') {
            setTimeout(() => {
                hideNotification();
            }, 3000);
        }
    }

    // 隐藏通知
    window.hideNotification = function() {
        const notification = document.getElementById('notification');
        notification.style.display = 'none';
    };

    // 输入框焦点效果
    const inputs = document.querySelectorAll('.input-wrapper input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // 回车键快速登录
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !loginBtn.disabled) {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });

    // 页面加载动画
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);
}); 